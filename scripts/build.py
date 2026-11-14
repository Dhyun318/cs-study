# 배포 폴더 app/ 의 생성물을 다시 만든다: app/data/notes.json, app/sims/(사본), app/illustrations/(사본).
# app/ 의 손으로 쓴 파일(index.html, app.css, app.js, 아이콘, manifest)은 건드리지 않는다.
# 책 원문(content/), PDF, 책 그림은 읽지도 복사하지도 않는다(CLAUDE.md 저작권, 2026-11-14 버셀 공개 배포 결정).
# 실행: python3 scripts/build.py  (어디서 실행해도 된다, 표준 라이브러리만)
# design/p-flow/make-data.py 를 앱용으로 옮긴 것: 그림 주소, [[sim:id]] 아래 "동작으로 보기" 링크, JSON 출력만 다르다.
import json, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
ILL = ROOT / "illustrations/a"

# 과목 파일과 질문 id (책 순서, 과목별 12/10/9/9). 시뮬레이션의 data-q 는 content 파일 이름/순번이라 그 이름도 둔다
SUBJECTS = [
    ("ds", "자료구조", "01-data-structure.md", "02-data-structure", ["ds-array", "ds-dynamic-array", "ds-linked-list", "ds-array-vs-ll", "ds-queue", "ds-stack", "ds-stack-queue", "ds-queue-stack", "ds-pq", "ds-bst", "ds-hash", "ds-collision"]),
    ("os", "운영체제", "02-os.md", "03-os", ["os-process", "os-multi-process", "os-multi-thread", "os-mp-vs-mt", "os-ipc", "os-sync", "os-deadlock", "os-paging", "os-segmentation", "os-virtual-memory"]),
    ("db", "데이터베이스", "03-database.md", "04-database", ["db-pk", "db-nm", "db-join", "db-rdb-nosql", "db-transaction", "db-deadlock", "db-index", "db-index-column", "db-bplus"]),
    ("net", "네트워크", "04-network.md", "05-network", ["net-osi", "net-tcp-udp", "net-handshake", "net-http", "net-get-post", "net-status", "net-google", "net-cookie", "net-cookie-login"]),
]

# 시뮬레이션 순서(과목 안은 연결 질문의 책 순서)와 연결 질문. hash-storage + hash-collision 은 hash-table 하나
SIM_Q = {
    "dynamic-array": ["ds-dynamic-array"], "linked-list": ["ds-linked-list"], "queue-stack": ["ds-queue", "ds-stack"],
    "heap": ["ds-pq"], "bst-structure": ["ds-bst"], "bst-search": ["ds-bst"], "hash-table": ["ds-collision", "ds-hash"],
    "process-memory": ["os-process", "os-multi-thread", "ds-array-vs-ll"], "context-switch": ["os-multi-process"], "ipc": ["os-ipc"],
    "race-condition": ["os-sync"], "mutex": ["os-sync"], "semaphore": ["os-sync"], "deadlock": ["os-deadlock", "db-deadlock"],
    "paging": ["os-paging"], "segmentation": ["os-segmentation"], "virtual-memory": ["os-virtual-memory"],
    "db-keys": ["db-pk"], "er-relationship": ["db-nm"], "join-types": ["db-join"], "transaction-lock": ["db-transaction"],
    "index-search": ["db-index"], "bplus-tree": ["db-bplus"],
    "encapsulation": ["net-osi", "net-tcp-udp"], "tcp-udp-header": ["net-tcp-udp"], "tcp-udp-order": ["net-tcp-udp"],
    "tcp-handshake": ["net-handshake"], "http-message": ["net-http", "net-get-post"], "google-request": ["net-google"],
    "cookie-session": ["net-cookie", "net-cookie-login"],
}
SIM_OF = {"hash-storage": "hash-table", "hash-collision": "hash-table"}  # 그림 id → 시뮬레이션 id
PLAY = '<svg class="ti" width="20" height="20" aria-hidden="true"><use href="#t-player-play"/></svg>'


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)


def ill(name):
    # 일러스트 <img>: svg 의 크기와 <title> 을 읽어 자리를 미리 잡고 대체 글로 쓴다
    svg = (ILL / f"{name}.svg").read_text()
    w, h = re.search(r'width="(\d+)" height="(\d+)"', svg).groups()
    t = re.search(r"<title[^>]*>([^<]+)</title>", svg)
    return f'<img src="illustrations/{name}.svg" alt="{esc(t.group(1) if t else "개념 그림")}" width="{w}" height="{h}" loading="lazy">'


def convert(lines):
    """md 몇 줄을 HTML로. 표, 코드, 인용(핵심), 목록, 굵은 소제목, [[sim:id]] 그림만 다룬다."""
    out, i, n = [], 0, len(lines)
    while i < n:
        ln = lines[i]
        s = ln.strip()
        if not s:
            i += 1
        elif s.startswith("```"):
            j = i + 1
            while j < n and not lines[j].strip().startswith("```"):
                j += 1
            out.append("<pre><code>" + esc("\n".join(lines[i + 1:j])) + "</code></pre>")
            i = j + 1
        elif m := re.fullmatch(r"\[\[sim:([a-z0-9-]+)\]\]", s):
            name = m.group(1)
            sid = SIM_OF.get(name, name)
            assert (ROOT / "sims" / sid / "index.html").exists(), sid
            out.append(f'<figure class="ill">{ill(name)}<a class="ill-go" href="#/sim/{sid}">{PLAY}동작으로 보기</a></figure>')
            i += 1
        elif s.startswith(">"):
            j = i
            while j < n and lines[j].strip().startswith(">"):
                j += 1
            inner = [re.sub(r"^\s*>\s?", "", x) for x in lines[i:j]]
            if inner[0].startswith("핵심:"):
                inner[0] = inner[0][3:].strip()
                out.append(f'<div class="core">{convert(inner)}</div>')
            else:
                out.append(f'<aside class="tip">{convert(inner)}</aside>')
            i = j
        elif s.startswith("|"):
            j = i
            while j < n and lines[j].strip().startswith("|"):
                j += 1
            rows = [r.strip().strip("|").split("|") for r in lines[i:j] if not re.fullmatch(r"\|[\s\-:|]+\|", r.strip())]
            head = "".join(f"<th>{inline(c.strip())}</th>" for c in rows[0])
            body = "".join("<tr>" + "".join(f"<td>{inline(c.strip())}</td>" for c in r) + "</tr>" for r in rows[1:])
            out.append(f'<div class="tbl"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')
            i = j
        elif re.fullmatch(r"\*\*[^*]+\*\*", s):
            out.append(f"<h3>{inline(s[2:-2])}</h3>")
            i += 1
        elif re.match(r"(- |\d+\. )", s) and ln == ln.lstrip():
            # 목록: 들여쓴 줄은 바로 앞 항목에 붙인다(하위 목록, 이어지는 문단)
            tag = "ol" if s[0].isdigit() else "ul"
            items, j = [], i
            while j < n:
                x = lines[j]
                if re.match(r"(- |\d+\. )", x):
                    items.append([re.sub(r"^(- |\d+\. )", "", x), []])
                elif x.strip() and x.startswith(" ") and items:
                    items[-1][1].append(x.strip())
                elif not x.strip() and j + 1 < n and lines[j + 1].startswith(" ") and lines[j + 1].strip():
                    pass
                else:
                    break
                j += 1
            html = ""
            for head, subs in items:
                sub_li = [re.sub(r"^(- |\d+\. )", "", x) for x in subs if re.match(r"(- |\d+\. )", x)]
                paras = [x for x in subs if not re.match(r"(- |\d+\. )", x)]
                html += "<li>" + inline(head) + "".join(f"<p>{inline(p)}</p>" for p in paras)
                if sub_li:
                    html += "<ul>" + "".join(f"<li>{inline(x)}</li>" for x in sub_li) + "</ul>"
                html += "</li>"
            out.append(f"<{tag}>{html}</{tag}>")
            i = j
        else:
            j = i
            while j < n and lines[j].strip() and not re.match(r"\s*(\||```|>|\[\[sim:|- |\d+\. |\*\*[^*]+\*\*$)", lines[j]):
                j += 1
            j = max(j, i + 1)
            out.append("<p>" + " ".join(inline(x.strip()) for x in lines[i:j]) + "</p>")
            i = j
    return "".join(out)


def title_of(h):
    t = re.sub(r"^#+\s*Q[.)]\s*", "", h).strip()
    return t.replace("⭐", "").strip(), t.count("⭐")


def parse_question(lines):
    # 맨 앞 인용(> 핵심:)이 핵심 답변, 그 뒤가 해설, #### 부터 꼬리질문
    k = next((x for x, l in enumerate(lines) if l.startswith("#### ")), len(lines))
    main, tail_lines = lines[:k], lines[k:]
    a = next(x for x, l in enumerate(main) if l.strip())
    assert main[a].startswith("> 핵심:"), main[a]
    b = a
    while b < len(main) and main[b].startswith(">"):
        b += 1
    core = [re.sub(r"^>\s?", "", x) for x in main[a:b]]
    core[0] = core[0][3:].strip()
    tails, cur = [], None
    for l in tail_lines:
        if l.startswith("#### "):
            cur = [title_of(l)[0], []]
            tails.append(cur)
        elif cur:
            cur[1].append(l)
    return {"core": convert(core), "body": convert(main[b:]), "tails": [{"q": q, "a": convert(ls)} for q, ls in tails]}


def notes_json():
    questions, subjects = [], []
    for key, name, fname, _, ids in SUBJECTS:
        sub, cur, blocks = None, None, []
        for l in (ROOT / "notes" / fname).read_text().splitlines():
            if l.startswith("## "):
                sub = l[3:].strip()
            elif l.startswith("### "):
                cur = {"sub": sub, "h": l, "lines": []}
                blocks.append(cur)
            elif cur:
                cur["lines"].append(l)
        assert len(blocks) == len(ids), (fname, len(blocks))
        subs = []
        for qid, b in zip(ids, blocks):
            title, stars = title_of(b["h"])
            q = {"id": qid, "s": key, "sub": b["sub"], "title": title, "stars": stars}
            q.update(parse_question(b["lines"]))
            questions.append(q)
            if b["sub"] not in subs:
                subs.append(b["sub"])
        subjects.append({"key": key, "name": name, "subs": subs})

    # 시뮬레이션 제목: 우리가 쓴 계획 문서(docs/simulations.md)의 표 두 개(2절, 3절)
    sim_md = (ROOT / "docs/simulations.md").read_text()
    titles = {m.group(1): m.group(2).strip() for m in re.finditer(r"^\| ([a-z][a-z0-9-]+) \| [^|]+\| ([^|]+)\|", sim_md, re.M) if m.group(1) != "id"}
    assert len(titles) == 31, len(titles)
    titles.pop("hash-storage"), titles.pop("hash-collision")
    titles["hash-table"] = "Hash 저장과 충돌"
    assert set(titles) == set(SIM_Q)
    qs = {q["id"]: q for q in questions}
    sims = [{"id": sid, "s": qs[qids[0]]["s"], "title": titles[sid], "qs": qids} for sid, qids in SIM_Q.items()]
    for q in questions:
        q["sims"] = [s["id"] for s in sims if q["id"] in s["qs"]]
    return {"subjects": subjects, "questions": questions, "sims": sims}


def copy_sims():
    # sims/ 사본: 시뮬레이션 폴더 전부 + _kit(실행에 필요한 kit.js, kit.css만) + 목록. 검사·템플릿·문서는 빼고
    shutil.copytree(ROOT / "sims", APP / "sims", ignore=shutil.ignore_patterns("CLAUDE.md", "check.py", "template.html", "test*", "*.png", "__pycache__", ".*"))
    dirs = [p for p in (APP / "sims").iterdir() if p.is_dir() and p.name != "_kit"]
    assert sorted(p.name for p in dirs) == sorted(SIM_Q), "sims 폴더와 SIM_Q 가 다름"
    # 사본의 kit.js 만: 관련 질문 링크를 원문 md 대신 앱 질문 화면으로(위 창 전체를 이동)
    qid = {f"{cfile}/{n}": q for _, _, _, cfile, ids in SUBJECTS for n, q in enumerate(ids, 1)}
    kit = APP / "sims/_kit/kit.js"
    js = kit.read_text()
    old_url = re.search(r"(^\s*//.*\n)?^.*const qUrl = .*$", js, re.M)  # 앞줄 설명 주석까지
    old_link = "a.href = qUrl(a.dataset.q); "
    assert old_url and js.count(old_link) == 1, "kit.js 의 qUrl 줄이 바뀌었다. build.py 를 맞춘다"
    js = js.replace(old_url.group(0), "  // 앱 사본(scripts/build.py 가 바꿈): data-q(content 파일/질문 순번) → 앱 질문 화면\n"
                    f"  const QID = {json.dumps(qid, separators=(',', ':'))};\n"
                    "  const qUrl = id => `../../#/q/${QID[id]}`;")
    js = js.replace(old_link, old_link + "a.target = '_top'; ")
    kit.write_text(js)
    # 시뮬레이션이 쓰는 data-q 가 모두 앱 질문으로 이어지는지
    used = {m for p in dirs for m in re.findall(r'data-q="([^"]+)"', (p / "index.html").read_text())}
    assert used <= set(qid), used - set(qid)


def main():
    for d in ("data", "sims", "illustrations"):
        shutil.rmtree(APP / d, ignore_errors=True)
    (APP / "data").mkdir(parents=True)
    data = notes_json()
    (APP / "data/notes.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    shutil.copytree(ILL, APP / "illustrations", ignore=shutil.ignore_patterns("*.png", ".*"))
    copy_sims()
    q = data["questions"]
    print(len(q), "questions,", sum(len(x["tails"]) for x in q), "tails,", len(data["sims"]), "sims,",
          (APP / "data/notes.json").stat().st_size, "bytes notes.json")


main()
