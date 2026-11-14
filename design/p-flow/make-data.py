# notes/*.md(우리 말 해설)와 docs/simulations.md 를 읽어 프로토타입용 data.js 를 만든다.
# 책 원문(content/)과 책 그림은 쓰지 않는다(CLAUDE.md 저작권, 2026-11-14 버셀 공개 배포 결정).
# 실행: python3 design/p-flow/make-data.py  (프로젝트 루트에서)
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ILL = "illustrations/a"  # 일러스트 A안(정돈된 도식). B로 정해지면 여기만 바꾼다

# 과목 파일과 질문 id (책 순서, 과목별 12/10/9/9)
SUBJECTS = [
    ("ds", "자료구조", "01-data-structure.md", ["ds-array", "ds-dynamic-array", "ds-linked-list", "ds-array-vs-ll", "ds-queue", "ds-stack", "ds-stack-queue", "ds-queue-stack", "ds-pq", "ds-bst", "ds-hash", "ds-collision"]),
    ("os", "운영체제", "02-os.md", ["os-process", "os-multi-process", "os-multi-thread", "os-mp-vs-mt", "os-ipc", "os-sync", "os-deadlock", "os-paging", "os-segmentation", "os-virtual-memory"]),
    ("db", "데이터베이스", "03-database.md", ["db-pk", "db-nm", "db-join", "db-rdb-nosql", "db-transaction", "db-deadlock", "db-index", "db-index-column", "db-bplus"]),
    ("net", "네트워크", "04-network.md", ["net-osi", "net-tcp-udp", "net-handshake", "net-http", "net-get-post", "net-status", "net-google", "net-cookie", "net-cookie-login"]),
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
ILL_OF = {"hash-table": "hash-collision"}  # 묶은 시뮬레이션의 대표 그림


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)


def ill(name):
    # 일러스트 <img>: svg 의 크기와 <title> 을 읽어 자리를 미리 잡고 대체 글로 쓴다
    svg = (ROOT / ILL / f"{name}.svg").read_text()
    w, h = re.search(r'width="(\d+)" height="(\d+)"', svg).groups()
    t = re.search(r"<title[^>]*>([^<]+)</title>", svg)
    return f'<img src="../../{ILL}/{name}.svg" alt="{esc(t.group(1) if t else "개념 그림")}" width="{w}" height="{h}" loading="lazy">'


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
            out.append(f'<figure class="ill">{ill(m.group(1))}</figure>')
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


def main():
    questions, subjects = [], []
    for key, name, fname, ids in SUBJECTS:
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

    # 시뮬레이션 표 두 개(2절, 3절)에서 id 와 제목(우리가 쓴 계획 문서)
    sim_md = (ROOT / "docs/simulations.md").read_text()
    titles = {m.group(1): m.group(2).strip() for m in re.finditer(r"^\| ([a-z][a-z0-9-]+) \| [^|]+\| ([^|]+)\|", sim_md, re.M) if m.group(1) != "id"}
    assert len(titles) == 31, len(titles)
    titles.pop("hash-storage"), titles.pop("hash-collision")
    titles["hash-table"] = "Hash 저장과 충돌"
    qs = {q["id"]: q for q in questions}
    sims = [{"id": sid, "s": qs[qids[0]]["s"], "title": titles[sid], "qs": qids,
             "ready": (ROOT / "sims" / sid / "index.html").exists(), "ill": ill(ILL_OF.get(sid, sid))}
            for sid, qids in SIM_Q.items()]
    assert len(sims) == 30 and set(titles) == set(SIM_Q)
    for q in questions:
        q["sims"] = [s["id"] for s in sims if q["id"] in s["qs"]]

    data = {"subjects": subjects, "questions": questions, "sims": sims}
    out = "// make-data.py 가 만든 파일. 직접 고치지 않는다.\nwindow.DATA = " + json.dumps(data, ensure_ascii=False) + ";\n"
    (Path(__file__).parent / "data.js").write_text(out)
    print(len(questions), "questions,", sum(len(q["tails"]) for q in questions), "tails,", len(sims), "sims,", len(out), "bytes")


main()
