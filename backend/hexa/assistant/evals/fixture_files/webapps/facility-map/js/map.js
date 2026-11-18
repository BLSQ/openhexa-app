// Facility map: markers, popups, filters and the region summary.

const MAP_CENTER = [16.5, 8.0];
const MAP_ZOOM = 6;

const STATUS_COLORS = {
  open: '#16a34a',
  closed: '#dc2626',
};

const TYPE_LABELS = {
  CSI: 'Centre de santé intégré',
  CS: 'Case de santé',
  HD: 'Hôpital de district',
  PS: 'Poste de santé',
};

const TYPE_RADIUS = {
  CSI: 6,
  CS: 4,
  HD: 9,
  PS: 4,
};

const map = L.map('map').setView(MAP_CENTER, MAP_ZOOM);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors',
}).addTo(map);

const layer = L.layerGroup().addTo(map);
const filters = { region: 'all', type: 'all', status: 'all' };

function buildPopup(facility) {
  return `
    <strong>${facility.name}</strong><br />
    ${TYPE_LABELS[facility.type] || facility.type}<br />
    ${facility.region}<br />
    Status: ${facility.status}`;
}

function markerFor(facility) {
  return L.circleMarker([facility.lat, facility.lon], {
    radius: TYPE_RADIUS[facility.type] || 5,
    color: STATUS_COLORS[facility.status],
    fillColor: STATUS_COLORS[facility.status],
    fillOpacity: 0.8,
    weight: 1,
  }).bindPopup(buildPopup(facility));
}

function matches(facility) {
  return (
    (filters.region === 'all' || facility.region === filters.region) &&
    (filters.type === 'all' || facility.type === filters.type) &&
    (filters.status === 'all' || facility.status === filters.status)
  );
}

function renderMarkers() {
  layer.clearLayers();
  FACILITIES.filter(matches).forEach((facility) => markerFor(facility).addTo(layer));
}

function renderSummary() {
  const tbody = document.querySelector('#summary tbody');
  tbody.innerHTML = '';
  const byRegion = {};
  FACILITIES.filter(matches).forEach((facility) => {
    byRegion[facility.region] = byRegion[facility.region] || { open: 0, closed: 0 };
    byRegion[facility.region][facility.status]++;
  });
  Object.keys(byRegion)
    .sort()
    .forEach((region) => {
      const counts = byRegion[region];
      tbody.insertAdjacentHTML(
        'beforeend',
        `<tr><td>${region}</td><td>${counts.open}</td><td>${counts.closed}</td></tr>`,
      );
    });
}

function populateSelect(id, values, allLabel) {
  const select = document.getElementById(id);
  select.innerHTML = `<option value="all">${allLabel}</option>`;
  values.forEach((value) => select.insertAdjacentHTML('beforeend', `<option>${value}</option>`));
}

function bindFilters() {
  ['region', 'type', 'status'].forEach((key) => {
    document.getElementById(`filter-${key}`).addEventListener('change', (event) => {
      filters[key] = event.target.value;
      renderMarkers();
      renderSummary();
    });
  });
}

// Region outlines, simplified, used to draw the boundaries layer.
const REGION_BOUNDS = {
  Agadez: [
    [11.500, 0.500],
    [11.870, 1.030],
    [12.240, 1.560],
    [12.610, 2.090],
    [12.980, 2.620],
    [13.350, 3.150],
    [13.720, 3.680],
    [14.090, 4.210],
    [14.460, 4.740],
    [14.830, 5.270],
    [15.200, 5.800],
    [15.570, 6.330],
  ],
  Diffa: [
    [12.800, 2.200],
    [13.170, 2.730],
    [13.540, 3.260],
    [13.910, 3.790],
    [14.280, 4.320],
    [14.650, 4.850],
    [15.020, 5.380],
    [15.390, 5.910],
    [15.760, 6.440],
    [16.130, 6.970],
    [16.500, 7.500],
    [16.870, 8.030],
  ],
  Dosso: [
    [14.100, 3.900],
    [14.470, 4.430],
    [14.840, 4.960],
    [15.210, 5.490],
    [15.580, 6.020],
    [15.950, 6.550],
    [16.320, 7.080],
    [16.690, 7.610],
    [17.060, 8.140],
    [17.430, 8.670],
    [17.800, 9.200],
    [18.170, 9.730],
  ],
  Maradi: [
    [15.400, 5.600],
    [15.770, 6.130],
    [16.140, 6.660],
    [16.510, 7.190],
    [16.880, 7.720],
    [17.250, 8.250],
    [17.620, 8.780],
    [17.990, 9.310],
    [18.360, 9.840],
    [18.730, 10.370],
    [19.100, 10.900],
    [19.470, 11.430],
  ],
  Niamey: [
    [16.700, 7.300],
    [17.070, 7.830],
    [17.440, 8.360],
    [17.810, 8.890],
    [18.180, 9.420],
    [18.550, 9.950],
    [18.920, 10.480],
    [19.290, 11.010],
    [19.660, 11.540],
    [20.030, 12.070],
    [20.400, 0.600],
    [20.770, 1.130],
  ],
  Tahoua: [
    [18.000, 9.000],
    [18.370, 9.530],
    [18.740, 10.060],
    [19.110, 10.590],
    [19.480, 11.120],
    [19.850, 11.650],
    [20.220, 12.180],
    [20.590, 0.710],
    [20.960, 1.240],
    [21.330, 1.770],
    [11.700, 2.300],
    [12.070, 2.830],
  ],
  Tillaberi: [
    [19.300, 10.700],
    [19.670, 11.230],
    [20.040, 11.760],
    [20.410, 12.290],
    [20.780, 0.820],
    [21.150, 1.350],
    [11.520, 1.880],
    [11.890, 2.410],
    [12.260, 2.940],
    [12.630, 3.470],
    [13.000, 4.000],
    [13.370, 4.530],
  ],
  Zinder: [
    [20.600, 12.400],
    [20.970, 0.930],
    [21.340, 1.460],
    [11.710, 1.990],
    [12.080, 2.520],
    [12.450, 3.050],
    [12.820, 3.580],
    [13.190, 4.110],
    [13.560, 4.640],
    [13.930, 5.170],
    [14.300, 5.700],
    [14.670, 6.230],
  ],
};

function renderBoundaries() {
  Object.entries(REGION_BOUNDS).forEach(([region, points]) => {
    L.polygon(points, { color: '#475569', weight: 1, fill: false })
      .bindTooltip(region)
      .addTo(map);
  });
}

populateSelect('filter-region', REGIONS_ORDER, 'All regions');
populateSelect('filter-type', Object.keys(TYPE_LABELS), 'All types');
populateSelect('filter-status', Object.keys(STATUS_COLORS), 'All statuses');
bindFilters();
renderBoundaries();
renderMarkers();
renderSummary();
