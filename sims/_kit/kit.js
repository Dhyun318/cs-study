// 시뮬레이션 공통 엔진. 쓰는 법은 sims/CLAUDE.md
// 단계 = { caption: '한 줄 설명', ...그림에 필요한 값 }, render(단계, stage)가 그림을 그린다
// 주소 끝 ?embed=1 이면 앱 안(iframe)에 담긴 것: 머리·설명·조작은 앱이 그리고, kit 은 단계마다 바뀐 물체 자리를 Sim.onShow 로 알린다
const Sim = (() => {
  const $ = s => document.querySelector(s);
  const EMBED = new URLSearchParams(location.search).has('embed');
  if (EMBED) document.documentElement.classList.add('sim-embed');
  const icon = d => `<svg class="sim-ic" viewBox="0 0 24 24" aria-hidden="true"><path d="${d}"/></svg>`;
  const PLAY = icon('M7 4v16l13 -8z') + '재생';
  const PAUSE = icon('M6 5h4v14h-4z M14 5h4v14h-4z') + '일시정지';
  // ponytail: 질문 화면 주소가 아직 없어 원문 md로 보낸다. 앱 질문 주소가 정해지면 이 한 줄만 바꾼다
  const qUrl = id => `../../content/${id.split('/')[0]}.md`;
  let render, modes, mode, steps = [], i = 0, timer = null, tried = false;
  // 자동 재생 간격: 설명 글자 수 x 120ms, 3초에서 6초 사이 (spec 05 6절)
  const delay = () => Math.min(6000, Math.max(3000, steps[i].caption.length * 120));

  // n번째 단계를 그리고 설명, 번호, 버튼 상태를 맞춘다. 앱 안이면 바뀐 물체 자리도 잰다
  function show(n) {
    i = Math.max(0, Math.min(n, steps.length - 1));
    const stage = $('#sim-stage'), before = EMBED && stage.firstChild ? snap(stage) : null;
    render(steps[i], stage);
    $('.sim-count').textContent = `${i + 1} / ${steps.length}`;
    $('.sim-cap').textContent = steps[i].caption;
    $('[data-act=prev]').disabled = i === 0;
    $('[data-act=next]').disabled = i === steps.length - 1;
    tell(before ? diff(before, snap(stage)) : null);
  }

  // 앱에 지금 상태를 알린다 (앱이 Sim.onShow 를 달아 둔다)
  const state = () => ({ i, n: steps.length, caption: steps[i] ? steps[i].caption : '', mode, modes: Object.keys(modes), playing: !!timer, tried });
  const tell = changed => { if (Sim.onShow) Sim.onShow({ ...state(), changed }); };

  // 자동 재생: 끝 단계에 닿으면 멈춘다. 끝에서 누르면 처음부터
  function play(on = !timer) {
    clearTimeout(timer);
    timer = null;
    on = on && steps.length > 1;
    if (on) {
      if (i === steps.length - 1) show(0);
      const tick = () => { show(i + 1); if (i < steps.length - 1) timer = setTimeout(tick, delay()); else play(false); };
      timer = setTimeout(tick, delay());
    }
    $('[data-act=play]').innerHTML = on ? PAUSE : PLAY;
    tell(null);
  }

  // 단계 목록을 바꾸고 첫 단계부터 보여 준다 (직접 해 보기에서 쓴다)
  function load(list, own) { play(false); tried = !own; steps = list; show(0); }

  // 모드 고르기: 탭 표시, data-mode 요소 보이기/숨기기, 그 모드 단계 불러오기
  function pick(name) {
    mode = name;
    document.querySelectorAll('.sim-tabs button').forEach(b => b.setAttribute('aria-pressed', b.textContent === name));
    document.querySelectorAll('[data-mode]').forEach(el => { el.hidden = el.dataset.mode !== name; });
    load(modes[name], true);
  }

  // 시작: 탭, 단계 설명, 버튼을 그림 둘레에 붙이고 연결한다
  function start(o) {
    render = o.render;
    modes = o.modes || { '': o.steps };
    const stage = $('#sim-stage'), names = Object.keys(modes);
    stage.classList.add('sim-stage');
    if (names.length > 1) stage.insertAdjacentHTML('beforebegin',
      `<div class="sim-tabs" role="group" aria-label="보기 고르기">${names.map(n => `<button type="button">${n}</button>`).join('')}</div>`);
    stage.insertAdjacentHTML('afterend', `
      <p class="sim-say" aria-live="polite"><span class="sim-count num"></span><span class="sim-cap"></span></p>
      <div class="sim-ctrl">
        <button type="button" data-act="prev">${icon('M15 6l-6 6l6 6')}이전</button>
        <button type="button" data-act="play" class="main"></button>
        <button type="button" data-act="next">다음${icon('M9 6l6 6l-6 6')}</button>
      </div>`);
    document.querySelectorAll('.sim-q[data-q]').forEach(a => { a.href = qUrl(a.dataset.q); });
    $('.sim-tabs')?.addEventListener('click', e => { const b = e.target.closest('button'); if (b) pick(b.textContent); });
    $('.sim-ctrl').addEventListener('click', e => {
      const act = e.target.closest('button')?.dataset.act;
      if (act === 'play') play();
      else if (act) { play(false); show(i + (act === 'next' ? 1 : -1)); }
    });
    // ←/→ 키로 이전/다음 (입력 칸에 있을 때는 무시)
    addEventListener('keydown', e => {
      if (e.target.closest('input, textarea, select') || !['ArrowLeft', 'ArrowRight'].includes(e.key)) return;
      play(false);
      show(i + (e.key === 'ArrowRight' ? 1 : -1));
    });
    // 화면이 꺼지거나 떠나면 자동 재생을 멈춘다
    document.addEventListener('visibilitychange', () => { if (document.hidden) play(false); });
    addEventListener('pagehide', () => play(false));
    document.querySelectorAll('form.sim-try').forEach(wireErrors);
    pick(names[0]);
  }

  // 직접 해 보기 입력 오류: 오류 글을 입력 칸 줄 바로 아래로 옮기고, 틀린 칸에 aria-invalid + aria-describedby. 고치면 뗀다
  function wireErrors(form) {
    const err = form.querySelector('[role=alert]'), ins = [...form.querySelectorAll('input')];
    if (!err || !ins.length) return;
    err.id = err.id || 'sim-err';
    const last = ins[ins.length - 1];
    (last.closest('.sim-row') || last.closest('label') || last).after(err);
    const on = () => !err.hidden && err.textContent.trim();
    const set = (el, bad) => { if (bad) { el.setAttribute('aria-invalid', 'true'); el.setAttribute('aria-describedby', err.id); } else { el.removeAttribute('aria-invalid'); el.removeAttribute('aria-describedby'); } };
    // 규칙에 어긋난 칸만. 다른 규칙으로 막았으면(모든 칸이 규칙에 맞음) 모든 칸
    const mark = () => { const bad = on() ? ins.filter(x => !x.checkValidity()) : [], list = on() && !bad.length ? ins : bad; ins.forEach(x => set(x, list.includes(x))); };
    new MutationObserver(mark).observe(err, { attributes: true, childList: true, characterData: true, subtree: true });
    ins.forEach(x => x.addEventListener('input', () => { if (x.checkValidity()) set(x, false); }));
  }

  // ===== 바뀐 물체 찾기 (앱 안일 때만): 무대에서 무언가를 그리는 요소를 트리 자리로 맞춰 단계 전후를 비교한다 =====
  // 보임(조상 opacity 곱, visibility, 크기), 글, 색(채널 차 24 넘게), 자리·크기. 부모 class 로 드러난 것도 잡고, 사라진 것은 직전 자리
  const rgb = s => (s.match(/[\d.]+/g) || [0, 0, 0, 0]).map(Number).concat([1]).slice(0, 4);
  const cdist = (a, b) => Math.max(...[0, 1, 2].map(k => Math.abs(a[k] - b[k])));
  function snap(stage) {
    // 들어오는 움직임(sim-pop) 중간이 아니라 끝 모습으로 잰다: 같은 순간 안에서 끝으로 돌렸다가 되돌리므로 깜빡이지 않음
    const anims = stage.getAnimations({ subtree: true }).filter(a => isFinite(a.effect.getComputedTiming().endTime)), keep = anims.map(a => a.currentTime);
    anims.forEach(a => { a.currentTime = a.effect.getComputedTiming().endTime; });
    const m = new Map(), s0 = stage.getBoundingClientRect();
    let base = [255, 255, 255, 1];
    for (let x = stage; x; x = x.parentElement) { const c = rgb(getComputedStyle(x).backgroundColor); if (c[3] > .5) { base = c; break; } }
    (function walk(el, path, op, bg) {
      [...el.children].forEach((c, k) => {
        const p = path + '/' + k, cs = getComputedStyle(c), o = op * +cs.opacity, own = rgb(cs.backgroundColor);
        const eff = own[3] > .5 ? own : bg, texts = [...c.childNodes].filter(n => n.nodeType === 3 && n.data.trim());
        const pse = ['::before', '::after'].map(x => { const s = getComputedStyle(c, x); return s.content === 'none' ? '' : s.content + s.backgroundColor + s.borderTopColor; }).join('');
        const side = ['Top', 'Right', 'Bottom', 'Left'].find(d => parseFloat(cs['border' + d + 'Width']) > 0), bc = rgb(cs['border' + (side || 'Top') + 'Color']);
        const svg = c instanceof SVGGeometryElement || c instanceof SVGTextContentElement || /^(IMG|CANVAS|INPUT|image|use)$/.test(c.tagName);
        const boxy = svg || own[3] > .05 || cs.backgroundImage !== 'none' || cs.boxShadow !== 'none' || (side && bc[3] > .05) || !!pse;
        if (boxy || texts.length) {
          const r = c.getBoundingClientRect(), vis = cs.visibility !== 'hidden' && o > .05 && (r.width > 0 || r.height > 0);
          let tr = null;
          texts.forEach(n => { const g = document.createRange(); g.selectNode(n); const q = g.getBoundingClientRect(); if (q.height) tr = tr ? { top: Math.min(tr.top, q.top), bottom: Math.max(tr.bottom, q.bottom), left: Math.min(tr.left, q.left), right: Math.max(tr.right, q.right) } : { top: q.top, bottom: q.bottom, left: q.left, right: q.right }; });
          // 바탕과 거의 같은 색(채널 차 24 이하) 판·선만 있는 것은 눈에 안 띔
          const ink = svg || texts.length || cs.backgroundImage !== 'none' || cs.boxShadow !== 'none' || !!pse || (side && bc[3] > .05 && cdist(bc, bg) > 24) || (own[3] > .05 && cdist(own, bg) > 24);
          m.set(p, { vis, r, tr, boxy, ink, op: o, bg: eff, ownBg: own[3] > .05, bc: side && bc[3] > .05 ? bc : null, sh: cs.boxShadow, pse, paint: svg ? cs.fill + cs.stroke : '',
            txt: texts.map(n => n.data).join('').trim(), color: rgb(cs.color), fw: cs.fontWeight, geo: [r.left - s0.left, r.top - s0.top, r.width, r.height].map(Math.round).join(','), pop: !!c.closest('.sim-pop') });
        }
        walk(c, p, o, eff);
      });
    })(stage, '', 1, base);
    anims.forEach((a, k) => { a.currentTime = keep[k]; });
    return m;
  }
  // 바뀐 곳 모음 → 위아래 6 여유를 더한 세 상자: u 전체, pop 새 물체(.sim-pop), low 가장 아래 바뀐 것. 바뀐 것이 없으면 null
  function diff(prev, now) {
    const ch = [], pop = [], add = (r, v) => { if (!r) return; ch.push(r); if (v && v.pop) pop.push(r); };
    const gone = o => o.ink && add(o.boxy ? o.r : o.tr || o.r);
    now.forEach((v, p) => {
      const o = prev.get(p);
      if (!v.vis) { if (o && o.vis) gone(o); return; }
      if (!o || !o.vis) return v.ink && add(v.r, v);
      const moved = v.geo !== o.geo, opCh = Math.abs(v.op - o.op) > .1;
      const boxCh = (v.boxy || o.boxy) && (moved || opCh || v.sh !== o.sh || v.pse !== o.pse || v.paint !== o.paint || ((v.ownBg || o.ownBg) && cdist(v.bg, o.bg) > 24) || (!v.bc !== !o.bc) || (v.bc && o.bc && cdist(v.bc, o.bc) > 24));
      if (boxCh && (v.ink || o.ink)) { add(v.r, v); if (moved) add(o.r); return; }
      if (v.txt && (moved || v.txt !== o.txt || v.fw !== o.fw || opCh || cdist(v.color, o.color) > 24)) { add(v.tr || v.r, v); if (moved || v.txt !== o.txt) add(o.tr); }
    });
    prev.forEach((o, p) => { if (o.vis && !now.has(p)) gone(o); });
    if (!ch.length) return null;
    const box = rs => ({ top: Math.min(...rs.map(r => r.top)) - 6, bottom: Math.max(...rs.map(r => r.bottom)) + 6, left: Math.min(...rs.map(r => r.left)), right: Math.max(...rs.map(r => r.right)) });
    const low = ch.reduce((x, r) => (r.bottom > x.bottom ? r : x));
    return { u: box(ch), pop: pop.length ? box(pop) : null, low: box([low]) };
  }

  return { start, load, play, go: n => { play(false); show(n); }, pick, state, step: () => steps[i], reset: () => pick(mode), onShow: null };
})();
window.Sim = Sim;
