// 시뮬레이션 공통 엔진. 쓰는 법은 sims/CLAUDE.md
// 단계 = { caption: '한 줄 설명', ...그림에 필요한 값 }, render(단계, stage)가 그림을 그린다
const Sim = (() => {
  const DELAY = 2200; // 자동 재생 간격(ms)
  const $ = s => document.querySelector(s);
  const icon = d => `<svg class="sim-ic" viewBox="0 0 24 24" aria-hidden="true"><path d="${d}"/></svg>`;
  const PLAY = icon('M7 4v16l13 -8z') + '재생';
  const PAUSE = icon('M6 5h4v14h-4z M14 5h4v14h-4z') + '일시정지';
  // ponytail: 질문 화면 주소가 아직 없어 원문 md로 보낸다. 앱 질문 주소가 정해지면 이 한 줄만 바꾼다
  const qUrl = id => `../../content/${id.split('/')[0]}.md`;
  let render, modes, mode, steps = [], i = 0, timer = null;

  // n번째 단계를 그리고 설명, 번호, 버튼 상태를 맞춘다
  function show(n) {
    i = Math.max(0, Math.min(n, steps.length - 1));
    render(steps[i], $('#sim-stage'));
    $('.sim-count').textContent = `${i + 1} / ${steps.length}`;
    $('.sim-cap').textContent = steps[i].caption;
    $('[data-act=prev]').disabled = i === 0;
    $('[data-act=next]').disabled = i === steps.length - 1;
  }

  // 자동 재생: 끝 단계에 닿으면 멈춘다. 끝에서 누르면 처음부터
  function play(on = !timer) {
    clearInterval(timer);
    timer = null;
    on = on && steps.length > 1;
    if (on) {
      if (i === steps.length - 1) show(0);
      timer = setInterval(() => { show(i + 1); if (i === steps.length - 1) play(false); }, DELAY);
    }
    $('[data-act=play]').innerHTML = on ? PAUSE : PLAY;
  }

  // 단계 목록을 바꾸고 첫 단계부터 보여 준다 (직접 해 보기에서 쓴다)
  function load(list) { play(false); steps = list; show(0); }

  // 모드 고르기: 탭 표시, data-mode 요소 보이기/숨기기, 그 모드 단계 불러오기
  function pick(name) {
    mode = name;
    document.querySelectorAll('.sim-tabs button').forEach(b => b.setAttribute('aria-pressed', b.textContent === name));
    document.querySelectorAll('[data-mode]').forEach(el => { el.hidden = el.dataset.mode !== name; });
    load(modes[name]);
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
    pick(names[0]);
  }

  return { start, load, play, step: () => steps[i], reset: () => pick(mode) };
})();
