let _raceDateTime = null;
let _countdownInterval = null;

function pad(n) { return String(n).padStart(2, '0'); }

function startCountdown(raceDatetime) {
  _raceDateTime = new Date(raceDatetime);
  if (_countdownInterval) clearInterval(_countdownInterval);
  tick();
  _countdownInterval = setInterval(tick, 1000);
}

function tick() {
  if (!_raceDateTime) return;
  const now = new Date();
  const diff = _raceDateTime - now;
  if (diff <= 0) {
    document.getElementById('cdDays').textContent = '00';
    document.getElementById('cdHours').textContent = '00';
    document.getElementById('cdMins').textContent = '00';
    document.getElementById('cdSecs').textContent = '00';
    clearInterval(_countdownInterval);
    return;
  }
  const days  = Math.floor(diff / 86400000);
  const hours = Math.floor((diff % 86400000) / 3600000);
  const mins  = Math.floor((diff % 3600000) / 60000);
  const secs  = Math.floor((diff % 60000) / 1000);
  document.getElementById('cdDays').textContent  = pad(days);
  document.getElementById('cdHours').textContent = pad(hours);
  document.getElementById('cdMins').textContent  = pad(mins);
  document.getElementById('cdSecs').textContent  = pad(secs);
}

async function initCountdown() {
  const data = await API.getCountdown();
  if (!data || data.message) return;

  const label = document.getElementById('countdownLabel');
  const flag = getFlag(data.country || '');
  if (label) label.innerHTML = `${flag} ${data.race_name} — Round ${data.round}`;

  if (data.race_datetime) startCountdown(data.race_datetime);

  // Start lights animation
  runStartLights();
}

function runStartLights() {
  const lights = [1,2,3,4,5].map(i => document.getElementById('l' + i));
  if (!lights[0]) return;
  let i = 0;
  const on = setInterval(() => {
    if (i < lights.length) { lights[i].classList.add('on'); i++; }
    else {
      clearInterval(on);
      setTimeout(() => {
        lights.forEach(l => l && l.classList.remove('on'));
        setTimeout(runStartLights, 8000);
      }, 1200);
    }
  }, 400);
}
