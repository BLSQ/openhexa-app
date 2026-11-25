// Malaria surveillance dashboard: data loading, charts, table and filters.

const API_BASE = window.DASHBOARD_CONFIG.apiBase;
const DEFAULT_PERIOD_COUNT = 12;

const CHART_COLORS = {
  suspected: '#94a3b8',
  tested: '#0ea5e9',
  confirmed: '#2563eb',
  treated: '#16a34a',
  severe: '#f59e0b',
  deaths: '#111827',
};

const state = {
  district: 'all',
  indicator: 'confirmed',
  periods: [],
  rows: [],
  sortKey: 'district',
  sortAsc: true,
  lastUpdated: null,
};

// Indicator catalogue: label, unit and how values aggregate across districts.
const INDICATORS = {
  suspected: {
    label: 'Suspected cases',
    unit: 'count',
    aggregate: 'sum',
    decimals: 0,
    i18nKey: 'indicator_suspected',
  },
  tested: {
    label: 'Tested cases',
    unit: 'count',
    aggregate: 'sum',
    decimals: 0,
    i18nKey: 'indicator_tested',
  },
  confirmed: {
    label: 'Confirmed cases',
    unit: 'count',
    aggregate: 'sum',
    decimals: 0,
    i18nKey: 'indicator_confirmed',
  },
  treated: {
    label: 'Treated cases',
    unit: 'count',
    aggregate: 'sum',
    decimals: 0,
    i18nKey: 'indicator_treated',
  },
  severe: {
    label: 'Severe cases',
    unit: 'count',
    aggregate: 'sum',
    decimals: 0,
    i18nKey: 'indicator_severe',
  },
  deaths: {
    label: 'Deaths',
    unit: 'count',
    aggregate: 'sum',
    decimals: 0,
    i18nKey: 'indicator_deaths',
  },
  anc1_ipt: {
    label: 'IPTp first dose',
    unit: 'count',
    aggregate: 'sum',
    decimals: 0,
    i18nKey: 'indicator_anc1_ipt',
  },
  anc3_ipt: {
    label: 'IPTp third dose',
    unit: 'count',
    aggregate: 'sum',
    decimals: 0,
    i18nKey: 'indicator_anc3_ipt',
  },
  llin_distributed: {
    label: 'LLINs distributed',
    unit: 'count',
    aggregate: 'sum',
    decimals: 0,
    i18nKey: 'indicator_llin_distributed',
  },
  rdt_stock: {
    label: 'RDT stock',
    unit: 'count',
    aggregate: 'sum',
    decimals: 0,
    i18nKey: 'indicator_rdt_stock',
  },
  act_stock: {
    label: 'ACT stock',
    unit: 'count',
    aggregate: 'sum',
    decimals: 0,
    i18nKey: 'indicator_act_stock',
  },
  reporting_rate: {
    label: 'Reporting rate',
    unit: 'percent',
    aggregate: 'mean',
    decimals: 1,
    i18nKey: 'indicator_reporting_rate',
  },
  timeliness: {
    label: 'Reporting timeliness',
    unit: 'percent',
    aggregate: 'mean',
    decimals: 1,
    i18nKey: 'indicator_timeliness',
  },
  positivity: {
    label: 'Test positivity rate',
    unit: 'percent',
    aggregate: 'mean',
    decimals: 1,
    i18nKey: 'indicator_positivity',
  },
  incidence: {
    label: 'Incidence per 1000',
    unit: 'rate',
    aggregate: 'mean',
    decimals: 1,
    i18nKey: 'indicator_incidence',
  },
  cfr: {
    label: 'Case fatality rate',
    unit: 'percent',
    aggregate: 'mean',
    decimals: 1,
    i18nKey: 'indicator_cfr',
  },
  testing_rate: {
    label: 'Testing rate',
    unit: 'percent',
    aggregate: 'mean',
    decimals: 1,
    i18nKey: 'indicator_testing_rate',
  },
  treatment_rate: {
    label: 'Treatment rate',
    unit: 'percent',
    aggregate: 'mean',
    decimals: 1,
    i18nKey: 'indicator_treatment_rate',
  },
  smc_round1: {
    label: 'SMC round 1 coverage',
    unit: 'percent',
    aggregate: 'mean',
    decimals: 1,
    i18nKey: 'indicator_smc_round1',
  },
  smc_round2: {
    label: 'SMC round 2 coverage',
    unit: 'percent',
    aggregate: 'mean',
    decimals: 1,
    i18nKey: 'indicator_smc_round2',
  },
  smc_round3: {
    label: 'SMC round 3 coverage',
    unit: 'percent',
    aggregate: 'mean',
    decimals: 1,
    i18nKey: 'indicator_smc_round3',
  },
  smc_round4: {
    label: 'SMC round 4 coverage',
    unit: 'percent',
    aggregate: 'mean',
    decimals: 1,
    i18nKey: 'indicator_smc_round4',
  },
  chw_cases: {
    label: 'Cases treated by CHWs',
    unit: 'count',
    aggregate: 'sum',
    decimals: 0,
    i18nKey: 'indicator_chw_cases',
  },
  referrals: {
    label: 'Referrals',
    unit: 'count',
    aggregate: 'sum',
    decimals: 0,
    i18nKey: 'indicator_referrals',
  },
  stockout_days: {
    label: 'Stock-out days',
    unit: 'count',
    aggregate: 'sum',
    decimals: 0,
    i18nKey: 'indicator_stockout_days',
  },
  under5_confirmed: {
    label: 'Confirmed cases under 5',
    unit: 'count',
    aggregate: 'sum',
    decimals: 0,
    i18nKey: 'indicator_under5_confirmed',
  },
  over5_confirmed: {
    label: 'Confirmed cases 5 and over',
    unit: 'count',
    aggregate: 'sum',
    decimals: 0,
    i18nKey: 'indicator_over5_confirmed',
  },
  pregnant_confirmed: {
    label: 'Confirmed cases in pregnant women',
    unit: 'count',
    aggregate: 'sum',
    decimals: 0,
    i18nKey: 'indicator_pregnant_confirmed',
  },
  hospitalised: {
    label: 'Hospitalisations',
    unit: 'count',
    aggregate: 'sum',
    decimals: 0,
    i18nKey: 'indicator_hospitalised',
  },
  microscopy: {
    label: 'Microscopy tests',
    unit: 'count',
    aggregate: 'sum',
    decimals: 0,
    i18nKey: 'indicator_microscopy',
  },
};

function formatDate(isoString) {
  const date = new Date(isoString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function formatValue(value, indicator) {
  if (value === null || value === undefined) {
    return '–';
  }
  const meta = INDICATORS[indicator];
  const fixed = Number(value).toFixed(meta.decimals);
  return meta.unit === 'percent' ? `${fixed}%` : Number(fixed).toLocaleString();
}

function periodLabel(period) {
  const year = period.slice(0, 4);
  const month = Number(period.slice(4, 6));
  return `${t('month_' + month)} ${year}`;
}

async function fetchJson(path, params = {}) {
  const url = new URL(path, API_BASE);
  Object.entries(params).forEach(([key, value]) => url.searchParams.set(key, value));
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

async function loadData() {
  showSpinner(true);
  try {
    const payload = await fetchJson('indicators.json', { periods: DEFAULT_PERIOD_COUNT });
    state.rows = payload.rows;
    state.periods = payload.periods;
    state.lastUpdated = payload.generated_at;
    render();
  } catch (error) {
    showError(t('error_loading'));
    console.error(error);
  } finally {
    showSpinner(false);
  }
}

function showSpinner(visible) {
  document.getElementById('spinner').hidden = !visible;
}

function showError(message) {
  const banner = document.getElementById('error-banner');
  banner.textContent = message;
  banner.hidden = false;
}

function filteredRows() {
  if (state.district === 'all') {
    return state.rows;
  }
  return state.rows.filter((row) => row.district === state.district);
}

function aggregate(rows, indicator, period) {
  const values = rows
    .filter((row) => row.period === period)
    .map((row) => row[indicator])
    .filter((value) => value !== null && value !== undefined);
  if (!values.length) {
    return null;
  }
  const total = values.reduce((sum, value) => sum + value, 0);
  return INDICATORS[indicator].aggregate === 'mean' ? total / values.length : total;
}

function renderHeader() {
  const updated = document.getElementById('last-updated');
  updated.textContent = state.lastUpdated
    ? `${t('last_updated')}: ${formatDate(state.lastUpdated)}`
    : '';
  const range = document.getElementById('period-range');
  if (state.periods.length) {
    const first = state.periods[0];
    const last = state.periods[state.periods.length - 1];
    range.textContent = `${periodLabel(first)} – ${periodLabel(last)}`;
  }
}

function renderKpis() {
  const container = document.getElementById('kpis');
  container.innerHTML = '';
  const lastPeriod = state.periods[state.periods.length - 1];
  const previousPeriod = state.periods[state.periods.length - 2];
  ['suspected', 'tested', 'confirmed', 'deaths'].forEach((indicator) => {
    const current = aggregate(filteredRows(), indicator, lastPeriod);
    const previous = aggregate(filteredRows(), indicator, previousPeriod);
    const card = document.createElement('div');
    card.className = 'kpi-card';
    const delta = previous ? ((current - previous) / previous) * 100 : null;
    card.innerHTML = `
      <span class="kpi-label">${t(INDICATORS[indicator].i18nKey)}</span>
      <span class="kpi-value">${formatValue(current, indicator)}</span>
      <span class="kpi-delta ${delta > 0 ? 'up' : 'down'}">
        ${delta === null ? '' : `${delta.toFixed(1)}%`}
      </span>`;
    container.appendChild(card);
  });
}

let trendChart = null;

function renderTrendChart() {
  const canvas = document.getElementById('trend-chart');
  const series = ['suspected', 'tested', 'confirmed', 'treated'];
  const datasets = series.map((indicator) => ({
    label: t(INDICATORS[indicator].i18nKey),
    data: state.periods.map((period) => aggregate(filteredRows(), indicator, period)),
    borderColor: CHART_COLORS[indicator],
    backgroundColor: CHART_COLORS[indicator],
    tension: 0.25,
    pointRadius: 2,
  }));
  if (trendChart) {
    trendChart.destroy();
  }
  trendChart = new Chart(canvas, {
    type: 'line',
    data: { labels: state.periods.map(periodLabel), datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: { y: { beginAtZero: true } },
    },
  });
}

let districtChart = null;

function renderDistrictChart() {
  const canvas = document.getElementById('district-chart');
  const lastPeriod = state.periods[state.periods.length - 1];
  const byDistrict = {};
  state.rows
    .filter((row) => row.period === lastPeriod)
    .forEach((row) => {
      byDistrict[row.district] = row[state.indicator];
    });
  const labels = Object.keys(byDistrict).sort();
  if (districtChart) {
    districtChart.destroy();
  }
  districtChart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: t(INDICATORS[state.indicator].i18nKey),
          data: labels.map((label) => byDistrict[label]),
          backgroundColor: CHART_COLORS[state.indicator] || '#64748b',
        },
      ],
    },
    options: { indexAxis: 'y', plugins: { legend: { display: false } } },
  });
}

function sortRows(rows) {
  const direction = state.sortAsc ? 1 : -1;
  return [...rows].sort((a, b) => {
    const left = a[state.sortKey];
    const right = b[state.sortKey];
    if (left === right) return 0;
    return left > right ? direction : -direction;
  });
}

function renderTable() {
  const tbody = document.querySelector('#data-table tbody');
  tbody.innerHTML = '';
  const lastPeriod = state.periods[state.periods.length - 1];
  const rows = sortRows(filteredRows().filter((row) => row.period === lastPeriod));
  rows.forEach((row) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${row.district}</td>
      <td>${formatValue(row.suspected, 'suspected')}</td>
      <td>${formatValue(row.tested, 'tested')}</td>
      <td>${formatValue(row.confirmed, 'confirmed')}</td>
      <td>${formatValue(row.positivity, 'positivity')}</td>
      <td>${formatValue(row.reporting_rate, 'reporting_rate')}</td>`;
    tbody.appendChild(tr);
  });
}

function exportCsv() {
  const header = ['district', 'period', ...Object.keys(INDICATORS)];
  const lines = [header.join(',')];
  filteredRows().forEach((row) => {
    lines.push(header.map((key) => row[key] ?? '').join(','));
  });
  const blob = new Blob([lines.join('\n')], { type: 'text/csv' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `malaria_${state.district}.csv`;
  link.click();
}

function populateFilters() {
  const districtSelect = document.getElementById('district-filter');
  const districts = [...new Set(state.rows.map((row) => row.district))].sort();
  districtSelect.innerHTML = `<option value="all">${t('all_districts')}</option>`;
  districts.forEach((district) => {
    districtSelect.insertAdjacentHTML('beforeend', `<option>${district}</option>`);
  });
  const indicatorSelect = document.getElementById('indicator-filter');
  indicatorSelect.innerHTML = '';
  Object.entries(INDICATORS).forEach(([code, meta]) => {
    indicatorSelect.insertAdjacentHTML(
      'beforeend',
      `<option value="${code}">${t(meta.i18nKey)}</option>`,
    );
  });
  indicatorSelect.value = state.indicator;
}

function bindEvents() {
  document.getElementById('district-filter').addEventListener('change', (event) => {
    state.district = event.target.value;
    render();
  });
  document.getElementById('indicator-filter').addEventListener('change', (event) => {
    state.indicator = event.target.value;
    renderDistrictChart();
  });
  document.querySelectorAll('#data-table th[data-key]').forEach((th) => {
    th.addEventListener('click', () => {
      const key = th.dataset.key;
      state.sortAsc = state.sortKey === key ? !state.sortAsc : true;
      state.sortKey = key;
      renderTable();
    });
  });
  const exportButton = document.getElementById('export-csv');
  exportButton.textContent = t('export_csv');
  exportButton.addEventListener('click', exportCsv);
  document.getElementById('language-toggle').addEventListener('click', () => {
    setLanguage(currentLanguage() === 'en' ? 'fr' : 'en');
    populateFilters();
    render();
  });
}

function render() {
  renderHeader();
  renderKpis();
  renderTrendChart();
  renderDistrictChart();
  renderTable();
}

// Per-district thresholds used to flag epidemic weeks in the alerts panel.
const EPIDEMIC_THRESHOLDS = {
  'Agadez': {
    confirmed: 120,
    severe: 12,
    deaths: 1,
    positivity: 30,
  },
  'Arlit': {
    confirmed: 157,
    severe: 15,
    deaths: 1,
    positivity: 37,
  },
  'Bilma': {
    confirmed: 194,
    severe: 19,
    deaths: 1,
    positivity: 44,
  },
  'Dosso': {
    confirmed: 231,
    severe: 23,
    deaths: 2,
    positivity: 51,
  },
  'Boboye': {
    confirmed: 268,
    severe: 26,
    deaths: 2,
    positivity: 58,
  },
  'Gaya': {
    confirmed: 305,
    severe: 30,
    deaths: 3,
    positivity: 65,
  },
  'Maradi': {
    confirmed: 342,
    severe: 34,
    deaths: 3,
    positivity: 32,
  },
  'Dakoro': {
    confirmed: 379,
    severe: 37,
    deaths: 3,
    positivity: 39,
  },
  'Tessaoua': {
    confirmed: 416,
    severe: 41,
    deaths: 4,
    positivity: 46,
  },
  'Tahoua': {
    confirmed: 453,
    severe: 45,
    deaths: 4,
    positivity: 53,
  },
  'Birni N'Konni': {
    confirmed: 490,
    severe: 49,
    deaths: 4,
    positivity: 60,
  },
  'Illela': {
    confirmed: 127,
    severe: 12,
    deaths: 1,
    positivity: 67,
  },
  'Tillaberi': {
    confirmed: 164,
    severe: 16,
    deaths: 1,
    positivity: 34,
  },
  'Filingue': {
    confirmed: 201,
    severe: 20,
    deaths: 2,
    positivity: 41,
  },
  'Ouallam': {
    confirmed: 238,
    severe: 23,
    deaths: 2,
    positivity: 48,
  },
  'Zinder': {
    confirmed: 275,
    severe: 27,
    deaths: 2,
    positivity: 55,
  },
  'Magaria': {
    confirmed: 312,
    severe: 31,
    deaths: 3,
    positivity: 62,
  },
  'Mirriah': {
    confirmed: 349,
    severe: 34,
    deaths: 3,
    positivity: 69,
  },
  'Diffa': {
    confirmed: 386,
    severe: 38,
    deaths: 3,
    positivity: 36,
  },
  'Maine-Soroa': {
    confirmed: 423,
    severe: 42,
    deaths: 4,
    positivity: 43,
  },
  'Niamey I': {
    confirmed: 460,
    severe: 46,
    deaths: 4,
    positivity: 50,
  },
  'Niamey II': {
    confirmed: 497,
    severe: 49,
    deaths: 4,
    positivity: 57,
  },
  'Niamey III': {
    confirmed: 134,
    severe: 13,
    deaths: 1,
    positivity: 64,
  },
  'Niamey IV': {
    confirmed: 171,
    severe: 17,
    deaths: 1,
    positivity: 31,
  },
  'Niamey V': {
    confirmed: 208,
    severe: 20,
    deaths: 2,
    positivity: 38,
  },
};

function alertsFor(row) {
  const thresholds = EPIDEMIC_THRESHOLDS[row.district];
  if (!thresholds) {
    return [];
  }
  return Object.entries(thresholds)
    .filter(([indicator, limit]) => row[indicator] !== undefined && row[indicator] > limit)
    .map(([indicator, limit]) => ({ indicator, limit, value: row[indicator] }));
}

function renderAlerts() {
  const list = document.getElementById('alerts');
  if (!list) return;
  list.innerHTML = '';
  const lastPeriod = state.periods[state.periods.length - 1];
  state.rows
    .filter((row) => row.period === lastPeriod)
    .flatMap((row) => alertsFor(row).map((alert) => ({ ...alert, district: row.district })))
    .forEach((alert) => {
      const item = document.createElement('li');
      item.textContent = `${alert.district}: ${t(INDICATORS[alert.indicator].i18nKey)} ${alert.value} > ${alert.limit}`;
      list.appendChild(item);
    });
}

document.addEventListener('DOMContentLoaded', () => {
  bindEvents();
  loadData().then(() => {
    populateFilters();
    renderAlerts();
  });
});
