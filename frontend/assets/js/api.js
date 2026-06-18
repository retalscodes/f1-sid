const BASE = '/api';

// Maps human-readable names → Ergast driver IDs
const DRIVER_NAME_MAP = {
  // === CURRENT GRID ===
  'max': 'max_verstappen', 'verstappen': 'max_verstappen', 'max verstappen': 'max_verstappen', 'super max': 'max_verstappen',
  'hamilton': 'hamilton', 'lewis': 'hamilton', 'lewis hamilton': 'hamilton', 'sir lewis': 'hamilton',
  'leclerc': 'leclerc', 'charles': 'leclerc', 'charles leclerc': 'leclerc', 'sharl': 'leclerc',
  'norris': 'norris', 'lando': 'norris', 'lando norris': 'norris',
  'piastri': 'piastri', 'oscar': 'piastri', 'oscar piastri': 'piastri',
  'russell': 'russell', 'george': 'russell', 'george russell': 'russell',
  'antonelli': 'antonelli', 'kimi antonelli': 'antonelli', 'andrea antonelli': 'antonelli',
  'alonso': 'alonso', 'fernando': 'alonso', 'fernando alonso': 'alonso', 'nando': 'alonso',
  'stroll': 'stroll', 'lance': 'stroll', 'lance stroll': 'stroll',
  'sainz': 'sainz', 'carlos': 'sainz', 'carlos sainz': 'sainz',
  'perez': 'perez', 'checo': 'perez', 'sergio': 'perez', 'sergio perez': 'perez',
  'hadjar': 'hadjar', 'isack': 'hadjar', 'isack hadjar': 'hadjar',
  'bearman': 'bearman', 'ollie': 'bearman', 'oliver bearman': 'bearman',
  'doohan': 'doohan', 'jack': 'doohan', 'jack doohan': 'doohan',
  'gasly': 'gasly', 'pierre': 'gasly', 'pierre gasly': 'gasly',
  'ocon': 'ocon', 'esteban': 'ocon', 'esteban ocon': 'ocon',
  'hulkenberg': 'hulkenberg', 'hulk': 'hulkenberg', 'nico hulkenberg': 'hulkenberg',
  'tsunoda': 'tsunoda', 'yuki': 'tsunoda', 'yuki tsunoda': 'tsunoda',
  'lawson': 'lawson', 'liam': 'lawson', 'liam lawson': 'lawson',
  'bottas': 'bottas', 'valtteri': 'bottas', 'valtteri bottas': 'bottas',
  'albon': 'albon', 'alex': 'albon', 'alex albon': 'albon',
  'magnussen': 'kevin_magnussen', 'kevin magnussen': 'kevin_magnussen',
  'zhou': 'zhou', 'guanyu': 'zhou', 'guanyu zhou': 'zhou',
  // === RECENT RETIREES ===
  'vettel': 'vettel', 'sebastian': 'vettel', 'seb': 'vettel', 'sebastian vettel': 'vettel',
  'ricciardo': 'ricciardo', 'daniel': 'ricciardo', 'danny ric': 'ricciardo', 'daniel ricciardo': 'ricciardo',
  'rosberg': 'rosberg', 'nico rosberg': 'rosberg', 'nico': 'rosberg',
  'webber': 'webber', 'mark': 'webber', 'mark webber': 'webber',
  'button': 'button', 'jenson': 'button', 'jenson button': 'button',
  'massa': 'massa', 'felipe': 'massa', 'felipe massa': 'massa',
  'barrichello': 'barrichello', 'rubens': 'barrichello', 'rubens barrichello': 'barrichello',
  'coulthard': 'coulthard', 'dc': 'coulthard', 'david coulthard': 'coulthard',
  'irvine': 'irvine', 'eddie irvine': 'irvine',
  // === ALL-TIME LEGENDS ===
  'raikkonen': 'raikkonen', 'kimi raikkonen': 'raikkonen', 'kimi': 'raikkonen', 'iceman': 'raikkonen',
  'schumacher': 'michael_schumacher', 'michael schumacher': 'michael_schumacher', 'schumi': 'michael_schumacher', 'michael': 'michael_schumacher', 'msc': 'michael_schumacher',
  'mick schumacher': 'mick_schumacher', 'mick': 'mick_schumacher',
  'senna': 'senna', 'ayrton': 'senna', 'ayrton senna': 'senna', 'magic senna': 'senna',
  'prost': 'prost', 'alain': 'prost', 'alain prost': 'prost', 'professor': 'prost', 'the professor': 'prost',
  'lauda': 'lauda', 'niki': 'lauda', 'niki lauda': 'lauda',
  'mansell': 'mansell', 'nigel': 'mansell', 'nigel mansell': 'mansell',
  'hill': 'damon_hill', 'damon': 'damon_hill', 'damon hill': 'damon_hill',
  'graham hill': 'graham_hill',
  'villeneuve': 'villeneuve', 'jacques': 'villeneuve', 'jacques villeneuve': 'villeneuve',
  'gilles': 'gilles_villeneuve', 'gilles villeneuve': 'gilles_villeneuve',
  'hakkinen': 'hakkinen', 'mika': 'hakkinen', 'mika hakkinen': 'hakkinen', 'flying finn': 'hakkinen',
  'stewart': 'stewart', 'jackie': 'stewart', 'jackie stewart': 'stewart',
  'clark': 'clark', 'jim clark': 'clark', 'jim': 'clark',
  'fangio': 'fangio', 'juan fangio': 'fangio',
  'ascari': 'ascari', 'alberto ascari': 'ascari',
  'moss': 'moss', 'stirling moss': 'moss', 'stirling': 'moss',
  'fittipaldi': 'emerson_fittipaldi', 'emerson': 'emerson_fittipaldi', 'emerson fittipaldi': 'emerson_fittipaldi',
  'piquet': 'piquet', 'nelson piquet': 'piquet', 'nelson': 'piquet',
  'hunt': 'hunt', 'james hunt': 'hunt', 'james': 'hunt',
  'andretti': 'mario_andretti', 'mario andretti': 'mario_andretti',
  'rindt': 'rindt', 'jochen rindt': 'rindt', 'jochen': 'rindt',
  'gurney': 'gurney', 'dan gurney': 'gurney',
};

function resolveDriverId(raw) {
  const s = (raw || '').toLowerCase().trim();
  if (DRIVER_NAME_MAP[s]) return DRIVER_NAME_MAP[s];
  // Fallback: replace spaces with underscores (Ergast style)
  return s.replace(/\s+/g, '_');
}

const TEAM_COLORS = {
  'Red Bull Racing': '#3671C6', 'Oracle Red Bull Racing': '#3671C6',
  'Scuderia Ferrari': '#E8002D', 'Ferrari': '#E8002D',
  'Mercedes': '#27F4D2', 'Mercedes-AMG Petronas': '#27F4D2',
  'McLaren': '#FF8000', 'McLaren F1 Team': '#FF8000',
  'Aston Martin': '#229971', 'Aston Martin Aramco': '#229971',
  'Alpine': '#0093CC', 'Alpine F1 Team': '#0093CC',
  'Williams': '#64C4FF', 'Williams Racing': '#64C4FF',
  'Haas': '#B6BABD', 'Haas F1 Team': '#B6BABD', 'MoneyGram Haas': '#B6BABD',
  'RB': '#6692FF', 'Visa Cash App RB': '#6692FF', 'AlphaTauri': '#6692FF',
  'Kick Sauber': '#52E252', 'Alfa Romeo': '#900000', 'Sauber': '#52E252',
};

const COUNTRY_FLAGS = {
  'Bahrain': '🇧🇭', 'Saudi Arabia': '🇸🇦', 'Australia': '🇦🇺', 'Japan': '🇯🇵',
  'China': '🇨🇳', 'United States': '🇺🇸', 'USA': '🇺🇸', 'Italy': '🇮🇹',
  'Monaco': '🇲🇨', 'Canada': '🇨🇦', 'Spain': '🇪🇸', 'Austria': '🇦🇹',
  'Great Britain': '🇬🇧', 'UK': '🇬🇧', 'Belgium': '🇧🇪', 'Hungary': '🇭🇺',
  'Netherlands': '🇳🇱', 'Singapore': '🇸🇬', 'Mexico': '🇲🇽', 'Brazil': '🇧🇷',
  'Qatar': '🇶🇦', 'UAE': '🇦🇪', 'Abu Dhabi': '🇦🇪', 'Azerbaijan': '🇦🇿',
  'British': '🇬🇧', 'German': '🇩🇪', 'Dutch': '🇳🇱', 'Finnish': '🇫🇮',
  'French': '🇫🇷', 'Spanish': '🇪🇸', 'Mexican': '🇲🇽', 'Australian': '🇦🇺',
  'Canadian': '🇨🇦', 'Brazilian': '🇧🇷', 'Monegasque': '🇲🇨', 'Thai': '🇹🇭',
  'Danish': '🇩🇰', 'Chinese': '🇨🇳', 'American': '🇺🇸', 'New Zealander': '🇳🇿',
  'Japanese': '🇯🇵', 'Argentine': '🇦🇷', 'Italian': '🇮🇹', 'Austrian': '🇦🇹',
  'Swiss': '🇨🇭', 'Belgian': '🇧🇪', 'Polish': '🇵🇱', 'Russian': '🇷🇺',
};

function getTeamColor(team) {
  return TEAM_COLORS[team] || '#888888';
}

function getFlag(country) {
  return COUNTRY_FLAGS[country] || '🏴';
}

function posClass(pos) {
  if (pos == 1) return 'pos-1';
  if (pos == 2) return 'pos-2';
  if (pos == 3) return 'pos-3';
  return 'pos-n';
}

async function apiFetch(path, opts = {}) {
  try {
    const res = await fetch(BASE + path, opts);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    console.error('API error:', path, e);
    return null;
  }
}

const API = {
  // Races
  getSchedule: (year) => apiFetch(`/races/schedule${year ? '?year=' + year : ''}`),
  getNextRace: () => apiFetch('/races/next'),
  getCountdown: () => apiFetch('/races/countdown'),
  getRaceWeekend: (year, round) => apiFetch(`/races/weekend/${year}/${round}`),
  getCircuitWeather: (key) => apiFetch(`/races/weather/${key}`),

  // Live
  getLiveStatus: () => apiFetch('/live/status'),
  getLivePositions: (sk) => apiFetch(`/live/positions/${sk}`),
  getLiveIntervals: (sk) => apiFetch(`/live/intervals/${sk}`),
  getLiveStints: (sk) => apiFetch(`/live/stints/${sk}`),
  getLiveWeather: (sk) => apiFetch(`/live/weather/${sk}`),
  getRaceControl: (sk) => apiFetch(`/live/race-control/${sk}`),
  getTeamRadio: (sk) => apiFetch(`/live/radio/${sk}`),
  getLivePitStops: (sk) => apiFetch(`/live/pit-stops/${sk}`),
  getLatestSession: () => apiFetch('/live/latest-session'),

  // History
  getSeasons: () => apiFetch('/history/seasons'),
  getConstructors: () => apiFetch('/history/constructors'),
  getConstructorHistory: (id) => apiFetch(`/history/constructor/${id}`),
  getConstructorSeasonDrivers: (id, year) => apiFetch(`/history/constructor/${id}/${year}/drivers`),
  getDriverProfile: (id) => apiFetch(`/history/driver/${id}`),
  getDriverYearResults: (id, year) => apiFetch(`/history/driver/${id}/results/${year}`),
  getSeasonOverview: (year) => apiFetch(`/history/season/${year}`),
  getSeasonDrivers: (year) => apiFetch(`/history/season/${year}/drivers`),
  getH2H: (year, d1, d2) => apiFetch(`/history/h2h/${year}/${d1}/${d2}`),
  getCareerStats: (id) => apiFetch(`/history/career/${id}`),

  // Championship
  getDriverChampionship: (year) => apiFetch(`/championship/drivers${year ? '?year=' + year : ''}`),
  getConstructorChampionship: (year) => apiFetch(`/championship/constructors${year ? '?year=' + year : ''}`),
  getChampionshipBattle: (year) => apiFetch(`/championship/battle${year ? '?year=' + year : ''}`),

  // Circuits
  listCircuits: () => apiFetch('/circuits/'),
  getCircuitDNA: (key) => apiFetch(`/circuits/${key}`),

  // Chat
  askSid: (message) => apiFetch('/chat/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  }),
  getSidReaction: (data) => apiFetch('/chat/reaction', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  getGlossaryExplain: (term, definition) => apiFetch('/chat/glossary', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ term, definition }),
  }),

  // Analytics (FastF1-backed)
  getAnalyticsRounds: (year) => apiFetch(`/analytics/rounds/${year}`),
  getLapComparison: (year, round, d1, d2) => apiFetch(`/analytics/lap-comparison/${year}/${round}?d1=${d1}&d2=${d2}`),
  getTireStrategy: (year, round) => apiFetch(`/analytics/tire-strategy/${year}/${round}`),
  getQualiComparison: (year, round, d1, d2) => apiFetch(`/analytics/quali-comparison/${year}/${round}?d1=${d1}&d2=${d2}`),
  getSeasonDuel: (year, d1, d2) => apiFetch(`/analytics/season-duel/${year}/${d1}/${d2}`),
  getDriverForm: (id) => apiFetch(`/analytics/driver-form/${id}`),
  getRacePredictor: (year, round) => apiFetch(`/analytics/predict/${year}/${round}`),

  // Predictions
  createRoom: (data) => apiFetch('/predictions/room', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  getRoom: (code) => apiFetch(`/predictions/room/${code}`),
  submitPrediction: (code, data) => apiFetch(`/predictions/room/${code}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  scoreRoom: (code, data) => apiFetch(`/predictions/room/${code}/score`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  resetRoom: (code) => apiFetch(`/predictions/room/${code}/reset`, { method: 'DELETE' }),
};
