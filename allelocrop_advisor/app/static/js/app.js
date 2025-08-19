async function postJSON(url, data) {
  const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
  if (!res.ok) throw new Error(await res.text());
  return await res.json();
}

function el(tag, attrs={}, children=[]) {
  const e = document.createElement(tag);
  Object.entries(attrs).forEach(([k,v]) => {
    if (k === 'class') e.className = v; else e.setAttribute(k, v);
  });
  children.forEach(c => { if (typeof c === 'string') e.appendChild(document.createTextNode(c)); else e.appendChild(c); });
  return e;
}

function inputRow(label, id, type='text', value='') {
  return el('div', { class: 'row' }, [
    el('div', { class: 'col' }, [el('label', {}, [label])]),
    el('div', { class: 'col' }, [el('input', { class: 'input', id, type, value }, [])])
  ]);
}

function textareaRow(label, id, value='') {
  return el('div', { class: 'row' }, [
    el('div', { class: 'col' }, [el('label', {}, [label])]),
    el('div', { class: 'col' }, [el('textarea', { class: 'input', id }, [value])])
  ]);
}

function parseList(val) {
  return val.split(',').map(s => s.trim()).filter(Boolean);
}

function render() {
  const app = document.getElementById('app');

  const soilCard = el('div', { class: 'card' }, [
    el('h3', {}, ['Inputs']),
    inputRow('Soil N (kg/acre)', 'soil_N', 'number', '10'),
    inputRow('Soil P', 'soil_P', 'number', '8'),
    inputRow('Soil K', 'soil_K', 'number', '12'),
    inputRow('pH', 'pH', 'number', '6.5'),
    inputRow('OM %', 'OM', 'number', '2.0'),
    inputRow('EC dS/m', 'EC', 'number', '0.2'),
    inputRow('Texture', 'texture', 'text', 'loam'),
    inputRow('Region', 'region', 'text', 'Midwest'),
    inputRow('Season', 'season', 'text', 'Spring'),
    inputRow('Main crop', 'main_crop', 'text', 'corn'),
    inputRow('Weather30d rain', 'w30_rain', 'number', '40'),
    inputRow('Weather30d gdd', 'w30_gdd', 'number', '300'),
    inputRow('Weather60d rain', 'w60_rain', 'number', '80'),
    inputRow('Weather60d gdd', 'w60_gdd', 'number', '600'),
    inputRow('N rate (kg/acre)', 'N_rate', 'number', '90'),
    inputRow('P rate', 'P_rate', 'number', '40'),
    inputRow('K rate', 'K_rate', 'number', '60'),
    inputRow('Observed weeds (comma-separated)', 'weeds', 'text', 'pigweed, foxtail'),
    inputRow('Candidate cover crops (comma-separated)', 'covers', 'text', 'rye, clover, mustard'),
    el('div', {}, [el('button', { class: 'button', id: 'run' }, ['Run'])])
  ]);

  const resultsCard = el('div', { class: 'card' }, [
    el('h3', {}, ['Results']),
    el('div', { id: 'yield' }, []),
    el('div', { id: 'recommend' }, []),
    el('div', { id: 'optimize' }, []),
    el('div', { id: 'explain' }, []),
    el('div', {}, [
      el('button', { class: 'button', id: 'download-pdf' }, ['Download PDF']),
      el('span', {}, [' ']),
      el('button', { class: 'button', id: 'download-csv' }, ['Download CSV'])
    ]),
  ]);

  app.appendChild(soilCard);
  app.appendChild(resultsCard);

  document.getElementById('run').addEventListener('click', async () => {
    const payload = {
      soil_N: parseFloat(document.getElementById('soil_N').value),
      soil_P: parseFloat(document.getElementById('soil_P').value),
      soil_K: parseFloat(document.getElementById('soil_K').value),
      pH: parseFloat(document.getElementById('pH').value),
      OM: parseFloat(document.getElementById('OM').value),
      EC: parseFloat(document.getElementById('EC').value),
      texture: document.getElementById('texture').value,
      region: document.getElementById('region').value,
      season: document.getElementById('season').value,
      main_crop: document.getElementById('main_crop').value,
      weather_30d: { rain: parseFloat(document.getElementById('w30_rain').value), gdd: parseFloat(document.getElementById('w30_gdd').value) },
      weather_60d: { rain: parseFloat(document.getElementById('w60_rain').value), gdd: parseFloat(document.getElementById('w60_gdd').value) },
      N_rate: parseFloat(document.getElementById('N_rate').value),
      P_rate: parseFloat(document.getElementById('P_rate').value),
      K_rate: parseFloat(document.getElementById('K_rate').value),
    };
    const weeds = parseList(document.getElementById('weeds').value);
    const covers = parseList(document.getElementById('covers').value);

    try {
      const y = await postJSON('/predict/yield', payload);
      document.getElementById('yield').innerHTML = `<pre>Yield: ${y.yield_mean.toFixed(1)} (P10=${y.yield_p10.toFixed(1)}, P90=${y.yield_p90.toFixed(1)})</pre>`;

      const recs = await postJSON('/recommend/cover', { main_crop: payload.main_crop, observed_weeds: weeds, region: payload.region, season: payload.season });
      document.getElementById('recommend').innerHTML = `<pre>Recommendations: ${JSON.stringify(recs.recommendations, null, 2)}</pre>`;

      const plans = await postJSON('/optimize', { ...payload, observed_weeds: weeds, candidate_covers: covers });
      window.__lastPlans = plans.pareto;
      document.getElementById('optimize').innerHTML = `<pre>Pareto Plans: ${JSON.stringify(plans.pareto, null, 2)}</pre>`;

      const exp = await postJSON('/explain', { payload: { ...payload, observed_weeds: weeds } });
      document.getElementById('explain').innerHTML = `<pre>Explain: ${JSON.stringify(exp, null, 2)}</pre>`;
    } catch (e) {
      alert(e);
    }
  });
}

render();
