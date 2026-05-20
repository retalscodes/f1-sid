// Nav burger
const burger = document.getElementById('navBurger');
const navLinks = document.getElementById('navLinks');
if (burger) {
  burger.addEventListener('click', () => navLinks.classList.toggle('open'));
}

// Highlight active nav link
document.querySelectorAll('.nav-links a').forEach(a => {
  if (a.href === location.href) a.classList.add('active');
  else a.classList.remove('active');
});

// ── HOMEPAGE INIT ──
if (document.getElementById('driverStandings')) {
  initHomePage();
}

async function initHomePage() {
  await Promise.all([
    initCountdown(),
    loadWeekend(),
    loadStandings(),
    loadLastRace(),
    loadTicker(),
    loadCalendar(),
  ]);
}

async function loadWeekend() {
  const data = await API.getNextRace();
  if (!data || data.message) return;

  const title = document.getElementById('weekendTitle');
  const flagEl = document.getElementById('weekendFlag');
  const grid = document.getElementById('sessionsGrid');

  const country = data.Circuit?.Location?.country || '';
  const flag = getFlag(country);
  if (title) title.textContent = data.raceName || 'Upcoming Race';
  if (flagEl) flagEl.textContent = flag;

  if (grid) {
    const sessions = data.FirstPractice ? [
      { type: 'FP1',       data: data.FirstPractice },
      { type: 'FP2',       data: data.SecondPractice },
      data.ThirdPractice ? { type: 'FP3', data: data.ThirdPractice } : null,
      data.Sprint        ? { type: 'Sprint', data: data.Sprint } : null,
      { type: 'Qualifying', data: data.Qualifying },
      { type: 'Race',      data: { date: data.date, time: data.time } },
    ].filter(Boolean) : [];

    if (sessions.length) {
      grid.innerHTML = sessions.map(s => {
        const dt = s.data?.date && s.data?.time
          ? new Date(`${s.data.date}T${s.data.time.replace('Z','+00:00')}`)
          : null;
        const dayStr  = dt ? dt.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }) : '—';
        const timeStr = dt ? dt.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) : '—';
        const isRace  = s.type === 'Race';
        return `
          <div class="session-card${isRace ? ' card-accent' : ''}" style="${isRace ? 'border-color:var(--red)' : ''}">
            <div class="session-type">${s.type}</div>
            <div class="session-time">${timeStr}</div>
            <div class="session-date">${dayStr}</div>
          </div>`;
      }).join('');
    } else {
      grid.innerHTML = '<div class="text-dim" style="padding:1rem;">Session times not yet available.</div>';
    }
  }

  // Weather
  if (data.circuit_key && data.weather?.temperature != null) {
    const w = data.weather;
    const ww = document.getElementById('weatherWidget');
    if (ww) {
      ww.style.display = 'block';
      document.getElementById('weatherTemp').textContent = `${Math.round(w.temperature)}°C`;
      document.getElementById('weatherWind').textContent = `${w.windspeed} km/h`;
      const rain = w.hourly?.rain_prob?.[0] ?? '—';
      document.getElementById('weatherRain').textContent = `${rain}%`;
      document.getElementById('weatherDesc').textContent = weatherDesc(w.weathercode);
    }
  }
}

function weatherDesc(code) {
  if (code === 0) return 'Clear sky';
  if (code <= 3)  return 'Partly cloudy';
  if (code <= 9)  return 'Overcast';
  if (code <= 29) return 'Foggy / mist';
  if (code <= 39) return 'Drizzle';
  if (code <= 49) return 'Freezing drizzle';
  if (code <= 59) return 'Rain';
  if (code <= 69) return 'Snow / sleet';
  if (code <= 79) return 'Snow grains';
  if (code <= 89) return 'Rain showers';
  if (code <= 99) return 'Thunderstorm ⚡';
  return 'Unknown';
}

async function loadStandings() {
  const [driverData, constructorData] = await Promise.all([
    API.getDriverChampionship(),
    API.getConstructorChampionship(),
  ]);

  const dEl = document.getElementById('driverStandings');
  const cEl = document.getElementById('constructorStandings');

  if (driverData?.standings && dEl) {
    const top10 = driverData.standings.slice(0, 10);
    const maxPts = parseFloat(top10[0]?.points || 1);
    dEl.innerHTML = `
      <div class="bar-chart">
        ${top10.map((s, i) => {
          const name = `${s.Driver.givenName[0]}. ${s.Driver.familyName}`;
          const pts  = parseFloat(s.points);
          const team = s.Constructors?.[0]?.name || '';
          const color = getTeamColor(team);
          const pct = (pts / maxPts * 100).toFixed(1);
          return `
            <div class="bar-row fade-in" style="animation-delay:${i*0.05}s">
              <div class="bar-label">
                <span class="${posClass(s.position)}" style="margin-right:0.4rem">${s.position}</span>
                ${getFlag(s.Driver.nationality)} ${name}
              </div>
              <div class="bar-track">
                <div class="bar-fill" style="width:${pct}%;background:${color}"></div>
              </div>
              <div class="bar-value">${pts}</div>
            </div>`;
        }).join('')}
      </div>`;
  }

  if (constructorData?.standings && cEl) {
    const top8 = constructorData.standings.slice(0, 8);
    const maxPts = parseFloat(top8[0]?.points || 1);
    cEl.innerHTML = `
      <div class="bar-chart">
        ${top8.map((s, i) => {
          const pts   = parseFloat(s.points);
          const color = getTeamColor(s.Constructor.name);
          const pct   = (pts / maxPts * 100).toFixed(1);
          return `
            <div class="bar-row fade-in" style="animation-delay:${i*0.05}s">
              <div class="bar-label">
                <span class="${posClass(s.position)}" style="margin-right:0.4rem">${s.position}</span>
                ${s.Constructor.name}
              </div>
              <div class="bar-track">
                <div class="bar-fill" style="width:${pct}%;background:${color}"></div>
              </div>
              <div class="bar-value">${pts}</div>
            </div>`;
        }).join('')}
      </div>`;
  }
}

async function loadTicker() {
  const data = await API.getDriverChampionship();
  const track = document.getElementById('tickerTrack');
  if (!track || !data?.standings) return;
  const items = data.standings.slice(0, 10).map(s => {
    const name = `${s.Driver.givenName[0]}. ${s.Driver.familyName}`;
    const flag = getFlag(s.Driver.nationality);
    return `${flag} ${s.position}. ${name} — ${parseFloat(s.points)}pts`;
  }).join('  ·  ');
  // Duplicate for seamless loop
  track.innerHTML = `<span>${items}</span><span>${items}</span>`;
  track.classList.add('scrolling');
}

async function loadCalendar() {
  const year = new Date().getFullYear();
  const schedule = await API.getSchedule(year);
  const strip = document.getElementById('calendarStrip');
  if (!strip || !schedule?.length) return;

  const now = new Date().toISOString().slice(0, 10);
  const nextIdx = schedule.findIndex(r => r.date >= now);

  strip.innerHTML = schedule.map((r, i) => {
    const isPast = r.date < now;
    const isNext = i === nextIdx;
    const flag = getFlag(r.Circuit?.Location?.country || r.Circuit?.Location?.locality || '');
    const shortName = (r.raceName || '').replace(' Grand Prix', '').replace(' GP', '');
    const dateStr = new Date(r.date + 'T12:00:00').toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    return `
      <div class="race-card-mini${isNext ? ' next-race' : ''}${isPast ? ' past-race' : ''}">
        ${isNext ? '<div class="rcm-badge">NEXT</div>' : ''}
        <div class="rcm-round">R${r.round}</div>
        <div class="rcm-flag">${flag || '🏁'}</div>
        <div class="rcm-name">${shortName}</div>
        <div class="rcm-date">${dateStr}</div>
        ${isPast ? '<div class="rcm-done">✓</div>' : ''}
      </div>`;
  }).join('');

  // Scroll next race into view
  const nextCard = strip.querySelector('.next-race');
  if (nextCard) {
    setTimeout(() => nextCard.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' }), 600);
  }
}

async function loadLastRace() {
  const year = new Date().getFullYear();
  const schedule = await API.getSchedule(year);
  if (!schedule) return;

  const now = new Date().toISOString().slice(0, 10);
  const past = schedule.filter(r => r.date <= now);
  if (!past.length) return;

  const last = past[past.length - 1];
  const weekend = await API.getRaceWeekend(year, last.round);
  if (!weekend?.result?.Results) return;

  const results = weekend.result.Results;
  const el = document.getElementById('lastRaceResults');
  const titleEl = document.getElementById('lastRaceTitle');

  if (titleEl) {
    const flag = getFlag(last.Circuit?.Location?.country || '');
    titleEl.textContent = `${flag} ${last.raceName}`;
  }

  if (el) {
    el.innerHTML = `
      <table class="standings-table">
        <thead>
          <tr>
            <th>Pos</th><th>Driver</th><th>Team</th><th>Grid</th><th>Points</th><th>Status</th>
          </tr>
        </thead>
        <tbody>
          ${results.slice(0, 10).map(r => {
            const team  = r.Constructor?.name || '';
            const color = getTeamColor(team);
            const drv   = r.Driver;
            const nat   = getFlag(drv.nationality);
            return `
              <tr class="fade-in">
                <td><span class="${posClass(r.position)}">${r.position}</span></td>
                <td>
                  <div style="display:flex;align-items:center;gap:0.5rem;">
                    <div style="width:4px;height:24px;border-radius:2px;background:${color};flex-shrink:0;"></div>
                    ${nat} ${drv.givenName} <strong>${drv.familyName}</strong>
                    ${r.FastestLap?.rank === '1' ? '<span class="badge badge-green" style="margin-left:0.5rem;">FL</span>' : ''}
                  </div>
                </td>
                <td style="color:var(--text-dim);font-size:0.85rem;">${team}</td>
                <td class="font-mono text-dim">${r.grid}</td>
                <td class="font-mono text-red fw-700">${r.points}</td>
                <td style="font-size:0.8rem;color:${r.status==='Finished'?'var(--text-dim)':'var(--red)'};">${r.status}</td>
              </tr>`;
          }).join('')}
        </tbody>
      </table>`;
  }

  // Sid reaction
  if (results.length >= 3) {
    const reaction = await API.getSidReaction({
      winner: `${results[0].Driver.givenName} ${results[0].Driver.familyName}`,
      p2: `${results[1].Driver.givenName} ${results[1].Driver.familyName}`,
      p3: `${results[2].Driver.givenName} ${results[2].Driver.familyName}`,
      race_name: last.raceName,
    });
    if (reaction?.reaction) {
      const sidBox = document.getElementById('sidReaction');
      const sidText = document.getElementById('sidReactionText');
      if (sidBox && sidText) {
        sidText.textContent = reaction.reaction;
        sidBox.style.display = 'block';
      }
    }
  }
}
