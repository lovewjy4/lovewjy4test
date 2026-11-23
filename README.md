<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>레일뷰 · 빈자리 시뮬레이터</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#edf1f6;color:#162940;font:16px/1.55 "Inter","Apple SD Gothic Neo","Malgun Gothic",sans-serif;word-break:keep-all}header{background:#13283f;color:white;padding:17px max(5vw,calc((100vw - 1010px)/2));display:flex;align-items:center;justify-content:space-between}header strong{font-size:22px}header span{font-size:14px;color:#c2d3e2}main{max-width:1050px;margin:auto;padding:36px 20px}h1{font-size:clamp(32px,5vw,50px);letter-spacing:-.065em;margin:0}p{margin:7px 0;color:#475c70}h2{font-size:21px;letter-spacing:-.04em;margin:0 0 14px}.grid{display:grid;grid-template-columns:1.35fr 1fr;gap:18px;margin-top:24px}.card,.map{background:white;border:1px solid #cdd7e1;border-radius:18px;padding:24px}.map{background:#163752;color:white}.map p{color:#c7dbe8}.tag{display:inline-block;font-size:14px;font-weight:700;color:#096153;background:#d5f4e9;padding:3px 11px;border-radius:20px}.train{display:flex;gap:5px;margin:22px 0 12px;align-items:center}.car{flex:1;background:#294a63;border:1px solid #698499;border-bottom:4px solid #738ea5;padding:7px 0;text-align:center;border-radius:6px;font-weight:bold}.car:first-child{border-radius:16px 5px 5px 5px}.car:last-child{border-radius:5px 16px 5px 5px}.target{outline:2px dashed #ffce77;outline-offset:1px}.here{background:#a7f1d9;color:#133e36;border-color:#a7f1d9}.plan{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;padding:16px;border:2px solid #96aec0;border-radius:16px;background:#213e56;margin:14px 0}.seat{background:#3d576c;border-radius:5px;border-bottom:3px solid #8094a3;text-align:center;color:white;font:14px/25px monospace}.seat:nth-child(n+11):nth-child(-n+15){margin-top:12px}.chosen{background:#ffce77;color:#352b13;border-color:#daaa59}.legend{font-size:14px}.action{margin-top:16px;width:100%;font:inherit;font-weight:bold;padding:14px;border:1px solid #b2c8ca;background:#fff;color:#174b47;border-radius:10px;cursor:pointer}.action.primary{background:#0b6057;color:white;border-color:#0b6057}.action:hover{filter:brightness(.94)}button:focus-visible{outline:3px solid #c7871c;outline-offset:3px}button:disabled{opacity:.5;cursor:default}.lower{margin-top:18px}#stats{display:grid;grid-template-columns:1fr 1fr;gap:12px}.stat{padding:15px;background:#f3f6f9;border-radius:10px}.stat strong{display:block}small{display:block;font-size:14px;color:#526476}#result{font-weight:bold;color:#064b45;margin-top:14px}#time{font:600 21px monospace;color:white}hr{border:0;border-top:1px solid #d7e0e7;margin:17px 0}[hidden]{display:none!important}@media(max-width:700px){.grid{grid-template-columns:1fr}.map,.card{padding:19px}main{padding:22px 15px}.train{gap:4px}#stats{grid-template-columns:1fr}}
.rates{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,270px),1fr));gap:14px;margin-top:18px}.method{background:#f3f6f9;padding:18px;border-radius:12px}.method h3{margin:0;font-size:18px}.metric{margin-top:14px}.metric div{display:flex;justify-content:space-between;gap:12px}.metric b{white-space:nowrap;font-variant-numeric:tabular-nums}.metric progress{width:100%;height:8px;accent-color:#0b6057;display:block;margin-top:5px}
</style>
</head>
<body>
<header><strong>▣ 레일뷰</strong><span>ITX-새마을 · 모의 열차</span></header>
<main>
  <h1>빈자리, 지금 가도 될까?</h1>
  <p>1·3회차에는 바로 이동하고, 2·4회차에는 5분 뒤 확인합니다. 한 회차가 끝나면 다음 회차가 바로 시작됩니다.</p>

  <div class="grid">
    <section class="map">
      <h2>열차 안 내 위치</h2>
      <strong id="location"></strong>
      <div class="train" id="train"></div>
      <p class="legend">민트색은 현재 위치 · 점선은 안내받은 객차</p>
      <br>
      <h2>5호차 좌석 배치</h2>
      <div class="plan" id="plan" role="group" aria-label="모의 좌석 배치, 안내 좌석 15번"></div>
      <p class="legend">강조된 15번은 안내 대상 좌석입니다.</p>
    </section>

    <section class="card">
      <span class="tag" id="trial"></span>
      <h2 style="font-size:29px;margin:14px 0 2px">5호차 · 15번 좌석</h2>
      <div aria-live="polite">
        <strong id="notice"></strong>
        <p id="stamp"></p>
        <hr>
        <p id="clock"></p>
        <p id="hint"></p>
      </div>
      <button class="action primary" id="go">바로 이동하기</button>
      <button class="action primary" id="refresh" hidden>5분 뒤 새로고침</button>
      <button class="action primary" id="again" hidden>새 실험 시작</button>
      <p id="result" role="status"></p>
    </section>
  </div>

  <section class="card lower" aria-labelledby="trial-results">
    <h2 id="trial-results">4회 시도 결과</h2>
    <div id="stats"></div>
    <p id="summary"></p>
    <small>이동은 모의 시간으로 2분, 새로고침 전 대기는 5분입니다. 다른 승객이 앉는 시점은 회차마다 0~10분 사이에서 새로 뽑습니다.</small>
  </section>

  <section class="card lower" aria-labelledby="rates-title">
    <h2 id="rates-title">방법별 결과 비율</h2>
    <p id="progress"></p>
    <small>각 방법을 완료한 횟수를 기준으로 계산합니다. 착석 실패에는 헛걸음과 점유 확인 후 이동 생략이 포함됩니다.</small>
    <div class="rates" id="rates"></div>
  </section>
</main>

<script>
const $ = id => document.getElementById(id);
const methods = {
  direct: '바로 이동',
  refresh: '5분 뒤 새로고침',
};
const trialMethods = ['direct', 'refresh', 'direct', 'refresh'];
const success = '착석 성공';
const wasted = '착석 실패 · 헛걸음';
const skipped = '착석 실패 · 이동 생략';

let cases, history, round, now, checked, phase, moved;

function clock(t) {
  return '14:' + String(t + 10).padStart(2, '0');
}

function free(t) {
  return t < cases[round];
}

function startTrial() {
  now = 0;
  checked = -10;
  phase = 'choice';
  moved = false;
  render();
}

function startExperiment() {
  cases = trialMethods.map(() => Math.floor(Math.random() * 11));
  history = [];
  round = 0;
  startTrial();
}

function finish(outcome) {
  history.push({ method: trialMethods[round], outcome, time: now, checked });

  if (history.length < trialMethods.length) {
    round += 1;
    startTrial();
  } else {
    phase = 'done';
    render();
  }
}

function move() {
  const direct = phase === 'choice' && trialMethods[round] === 'direct';
  if (!direct && phase !== 'updated') return;

  now += 2;
  moved = true;
  finish(free(now) ? success : wasted);
}

function refresh() {
  if (phase !== 'choice' || trialMethods[round] !== 'refresh') return;

  now += 5;
  checked = now;
  if (!free(now)) {
    finish(skipped);
    return;
  }

  phase = 'updated';
  render();
}

function describeResult(entry) {
  const time = clock(entry.time);
  if (entry.outcome === skipped) {
    return time + '에 다른 승객이 이용 중이어서 이동하지 않았습니다.';
  }
  if (entry.method === 'refresh') {
    const checkedAt = clock(entry.checked);
    return entry.outcome === success
      ? checkedAt + '에 빈자리를 확인하고 ' + time + '에 착석했습니다.'
      : checkedAt + '에는 비어 있었지만 ' + time + '에 도착했을 때는 다른 승객이 이용 중이었습니다.';
  }
  return entry.outcome === success
    ? time + '에 도착해 착석했습니다.'
    : time + '에 도착했을 때 다른 승객이 이용 중이었습니다.';
}

function renderResults() {
  const latest = history.at(-1);
  $('result').textContent = latest
    ? history.length + '회차 · ' + methods[latest.method] + ' · ' + latest.outcome + '. ' + describeResult(latest)
    : '';

  $('stats').innerHTML = trialMethods.map((method, index) => {
    const entry = history[index];
    const status = entry ? entry.outcome : index === round ? '진행 중' : '시도 전';
    const detail = entry ? '<small>' + describeResult(entry) + '</small>' : '';
    return '<div class="stat"><small>' + (index + 1) + '회차 · ' + methods[method]
      + '</small><strong>' + status + '</strong>' + detail + '</div>';
  }).join('');
  $('summary').textContent = phase === 'done' ? '4회 시도를 모두 마쳤습니다.' : '';
}

function renderRates() {
  $('progress').textContent = history.length + '/' + trialMethods.length + '회 완료';

  $('rates').innerHTML = Object.entries(methods).map(([method, title]) => {
    const attempts = history.filter(entry => entry.method === method);
    const total = attempts.length;
    const seated = attempts.filter(entry => entry.outcome === success).length;
    const missed = attempts.filter(entry => entry.outcome === wasted).length;
    const stayed = total - seated - missed;

    function ratio(count) {
      return total ? count + '/' + total + '회 · ' + (Math.round(count / total * 1000) / 10) + '%' : '—';
    }

    const rows = [[success, seated], ['착석 실패', total - seated]].map(([label, count]) =>
      '<div class="metric"><div><span>' + label + '</span><b>' + ratio(count)
      + '</b></div><progress aria-hidden="true" max="' + (total || 1) + '" value="' + count + '"></progress></div>'
    ).join('');
    const skippedDetail = method === 'refresh' ? '<br>점유 확인 후 이동 생략 ' + ratio(stayed) : '';

    return '<div class="method"><h3>' + title + '</h3><small>시도 ' + total
      + '회</small>' + rows + '<hr><small>헛걸음 ' + ratio(missed) + skippedDetail + '</small></div>';
  }).join('');
}

function render() {
  const method = trialMethods[round];
  $('trial').textContent = phase === 'done'
    ? '실험 완료 · 4회'
    : (round + 1) + '/' + trialMethods.length + '회차 · ' + methods[method];
  $('location').textContent = moved ? '현재 위치 · 5호차 15번 좌석 옆' : '현재 위치 · 3호차 뒤쪽 연결통로 부근';
  $('train').innerHTML = Array.from({ length: 6 }, (_, i) =>
    '<div class="car ' + (i === 4 ? 'target ' : '') + (i === (moved ? 4 : 2) ? 'here' : '') + '">' + (i + 1) + '호</div>'
  ).join('');
  $('notice').textContent = free(checked)
    ? '마지막 확인 당시 한 자리가 비어 있었습니다.'
    : '재조회 결과, 다른 승객이 이용 중입니다.';
  $('stamp').textContent = '최초 알림 ' + (now + 10) + '분 전 · 좌석 상태 '
    + (now === checked ? '방금 확인' : (now - checked) + '분 전 확인') + ' (' + clock(checked) + ')';
  $('clock').textContent = '모의 시각 ' + clock(now);
  $('hint').textContent = phase === 'updated'
    ? '현재 빈자리입니다. 지금 이동하면 도착 시점의 상태를 확인합니다.'
    : phase === 'done' ? '' : method === 'direct' ? '좌석까지 이동해 도착 시점의 상태를 확인하세요.'
      : '5분 뒤 좌석이 비어 있는지 확인하세요.';
  $('go').hidden = phase !== 'updated' && !(phase === 'choice' && method === 'direct');
  $('go').textContent = phase === 'updated' ? '확인한 좌석으로 이동' : '바로 이동하기';
  $('refresh').hidden = phase !== 'choice' || method !== 'refresh';
  $('again').hidden = phase !== 'done';

  renderResults();
  renderRates();
}

$('plan').innerHTML = Array.from({ length: 20 }, (_, i) =>
  '<span class="seat ' + (i === 14 ? 'chosen' : '') + '">' + String(i + 1).padStart(2, '0') + '</span>'
).join('');

function runAction(action) {
  const focused = document.activeElement;
  action();
  if (focused?.hidden) {
    [$('go'), $('refresh'), $('again')].find(button => !button.hidden)?.focus({ preventScroll: true });
  }
}

$('go').onclick = () => runAction(move);
$('refresh').onclick = () => runAction(refresh);
$('again').onclick = () => runAction(startExperiment);
startExperiment();
</script>
<script type="module">import { mountAutoSiteWidget } from "/_sites/dispatch-assets/sites-widget.js";mountAutoSiteWidget({"kind":"auto","toolbarOrigin":null,"viewerRemixEnabled":false,"invitationBanner":true,"mobileEnabled":false,"environment":"production","chatgptOrigin":"https://chatgpt.com","locale":"ko-KR","accountId":"personal","projectId":"appgprj_6b02fa0593c88191a3d496940b6e44d2","projectTitle":"레일뷰 · 빈자리 실험실"});</script></body>
</html>
