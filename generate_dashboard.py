import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, 'garages_israel_dataset.json')
analytics_path = os.path.join(BASE_DIR, 'garages_analytics_summary.json')

with open(json_path, 'r', encoding='utf-8') as f:
    garages = json.load(f)

with open(analytics_path, 'r', encoding='utf-8') as f:
    analytics = json.load(f)

html_content = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>דאשבורד מוסכים מורשים בישראל | ניתוח ומרכז נתונים</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700;800&family=Rubik:wght@400;500;700;800&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {{
      --bg: #0f172a;
      --card-bg: #1e293b;
      --border: #334155;
      --primary: #38bdf8;
      --accent: #f59e0b;
      --success: #10b981;
      --danger: #ef4444;
      --text: #f8fafc;
      --text-muted: #94a3b8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Assistant', sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding: 20px;
    }}
    header {{
      text-align: center;
      margin-bottom: 25px;
      padding: 20px;
      background: linear-gradient(135deg, #1e293b, #0f172a);
      border: 1px solid var(--border);
      border-radius: 16px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }}
    h1 {{
      font-family: 'Rubik', sans-serif;
      font-size: 32px;
      color: var(--primary);
      margin-bottom: 8px;
    }}
    .subtitle {{
      color: var(--text-muted);
      font-size: 16px;
    }}
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 25px;
    }}
    .stat-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      text-align: center;
      transition: transform 0.2s;
    }}
    .stat-card:hover {{ transform: translateY(-4px); }}
    .stat-num {{
      font-family: 'Rubik', sans-serif;
      font-size: 36px;
      font-weight: 800;
      color: var(--accent);
      margin-bottom: 4px;
    }}
    .stat-label {{
      font-size: 14px;
      color: var(--text-muted);
      font-weight: 600;
    }}
    .charts-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }}
    .chart-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 20px;
    }}
    .chart-card h3 {{
      font-family: 'Rubik', sans-serif;
      font-size: 18px;
      margin-bottom: 15px;
      color: var(--primary);
      border-bottom: 1px solid var(--border);
      padding-bottom: 8px;
    }}
    .controls {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 20px;
      margin-bottom: 20px;
      display: flex;
      flex-wrap: wrap;
      gap: 15px;
      align-items: center;
    }}
    .search-box {{
      flex: 2;
      min-width: 250px;
      position: relative;
    }}
    input, select {{
      width: 100%;
      padding: 12px 16px;
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 8px;
      color: #fff;
      font-size: 15px;
      font-family: inherit;
    }}
    input:focus, select:focus {{
      outline: none;
      border-color: var(--primary);
    }}
    .filter-item {{
      flex: 1;
      min-width: 180px;
    }}
    .table-container {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 14px;
      overflow: hidden;
      box-shadow: 0 10px 20px rgba(0,0,0,0.4);
    }}
    .table-header-bar {{
      padding: 15px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #151f30;
      border-bottom: 1px solid var(--border);
    }}
    .count-badge {{
      background: var(--primary);
      color: #0f172a;
      padding: 4px 12px;
      border-radius: 20px;
      font-weight: 700;
      font-size: 14px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: right;
    }}
    th, td {{
      padding: 12px 16px;
      border-bottom: 1px solid var(--border);
      font-size: 14px;
    }}
    th {{
      background: #111827;
      color: var(--text-muted);
      font-weight: 700;
      cursor: pointer;
      user-select: none;
    }}
    th:hover {{ color: var(--primary); }}
    tr:hover td {{
      background: rgba(56, 189, 248, 0.05);
    }}
    .tag {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 12px;
      margin: 2px;
      background: #334155;
      color: #e2e8f0;
    }}
    .tag-electric {{ background: #065f46; color: #a7f3d0; }}
    .tag-diesel {{ background: #854d0e; color: #fef08a; }}
    .tag-bodywork {{ background: #701a75; color: #f5d0fe; }}
    .pagination {{
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 10px;
      padding: 15px;
      background: #151f30;
    }}
    .btn {{
      padding: 8px 16px;
      background: var(--primary);
      color: #0f172a;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 700;
      font-family: inherit;
    }}
    .btn:disabled {{
      background: var(--border);
      color: var(--text-muted);
      cursor: not-allowed;
    }}
    .btn-export {{
      background: var(--success);
      color: white;
    }}
  </style>
</head>
<body>

  <header>
    <h1>🚗 מאגר המוסכים המורשים בישראל</h1>
    <p class="subtitle">ניתוח נתונים מקיף, פילוח גאוגרפי והתמחויות לתקיפה אסטרטגית של הפרויקט</p>
  </header>

  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-num">{analytics['total_unique_garages']:,}</div>
      <div class="stat-label">סך מוסכים ייחודיים</div>
    </div>
    <div class="stat-card">
      <div class="stat-num">{analytics['total_specializations_recorded']:,}</div>
      <div class="stat-label">רישומי התמחויות מורשות</div>
    </div>
    <div class="stat-card">
      <div class="stat-num">{len(analytics['top_cities'])}</div>
      <div class="stat-label">ערים ויישובים פעילים</div>
    </div>
    <div class="stat-card">
      <div class="stat-num">{len(analytics['top_professions_specializations'])}</div>
      <div class="stat-label">סוגי מקצועות והסמכות</div>
    </div>
  </div>

  <div class="charts-grid">
    <div class="chart-card">
      <h3>🏙️ 10 הערים המובילות בכמות מוסכים</h3>
      <canvas id="cityChart" height="200"></canvas>
    </div>
    <div class="chart-card">
      <h3>🔧 התמחויות ומקצועות נפוצים ביותר</h3>
      <canvas id="profChart" height="200"></canvas>
    </div>
  </div>

  <div class="controls">
    <div class="search-box">
      <input type="text" id="searchInput" placeholder="🔍 חיפוש חופשי לפי שם מוסך, כתובת, טלפון, מנהל מקצועי...">
    </div>
    <div class="filter-item">
      <select id="cityFilter">
        <option value="">כל הערים והיישובים</option>
      </select>
    </div>
    <div class="filter-item">
      <select id="profFilter">
        <option value="">כל ההתמחויות</option>
      </select>
    </div>
    <div class="filter-item">
      <select id="typeFilter">
        <option value="">כל סוגי המוסכים</option>
      </select>
    </div>
    <button class="btn btn-export" onclick="exportFilteredCSV()">📥 ייצוא תוצאות ל-CSV</button>
  </div>

  <div class="table-container">
    <div class="table-header-bar">
      <div><strong>תוצאות מסוננות</strong></div>
      <div id="resultsCount" class="count-badge">0 מוסכים</div>
    </div>
    <table>
      <thead>
        <tr>
          <th>מס' מוסך</th>
          <th>שם המוסך</th>
          <th>סוג</th>
          <th>יישוב / עיר</th>
          <th>כתובת</th>
          <th>טלפון</th>
          <th>התמחויות ומקצועות</th>
          <th>מנהל מקצועי</th>
        </tr>
      </thead>
      <tbody id="garagesTableBody">
      </tbody>
    </table>
    <div class="pagination">
      <button class="btn" id="prevBtn" onclick="changePage(-1)">◀ הקודם</button>
      <span id="pageInfo">עמוד 1 מתוך 1</span>
      <button class="btn" id="nextBtn" onclick="changePage(1)">הבא ▶</button>
    </div>
  </div>

  <script>
    const allGarages = {json.dumps(garages, ensure_ascii=False)};
    const analytics = {json.dumps(analytics, ensure_ascii=False)};

    let filteredGarages = [...allGarages];
    let currentPage = 1;
    const pageSize = 50;

    // Populate Filters
    const cityFilter = document.getElementById('cityFilter');
    const cities = [...new Set(allGarages.map(g => g.city).filter(Boolean))].sort();
    cities.forEach(c => {{
      const opt = document.createElement('option');
      opt.value = c;
      opt.textContent = c;
      cityFilter.appendChild(opt);
    }});

    const profFilter = document.getElementById('profFilter');
    const professions = analytics.top_professions_specializations.map(p => p[0]);
    professions.forEach(p => {{
      const opt = document.createElement('option');
      opt.value = p;
      opt.textContent = p;
      profFilter.appendChild(opt);
    }});

    const typeFilter = document.getElementById('typeFilter');
    const types = [...new Set(allGarages.map(g => g.type).filter(Boolean))].sort();
    types.forEach(t => {{
      const opt = document.createElement('option');
      opt.value = t;
      opt.textContent = t;
      typeFilter.appendChild(opt);
    }});

    function filterData() {{
      const query = document.getElementById('searchInput').value.trim().toLowerCase();
      const selCity = cityFilter.value;
      const selProf = profFilter.value;
      const selType = typeFilter.value;

      filteredGarages = allGarages.filter(g => {{
        if (selCity && g.city !== selCity) return false;
        if (selType && g.type !== selType) return false;
        if (selProf && !g.professions.includes(selProf)) return false;
        if (query) {{
          const str = (g.name + ' ' + g.address + ' ' + g.phone + ' ' + g.city + ' ' + g.managers.join(' ') + ' ' + g.professions.join(' ')).toLowerCase();
          if (!str.includes(query)) return false;
        }}
        return true;
      }});

      currentPage = 1;
      renderTable();
    }}

    function renderTable() {{
      const tbody = document.getElementById('garagesTableBody');
      tbody.innerHTML = '';

      const total = filteredGarages.length;
      document.getElementById('resultsCount').textContent = total.toLocaleString() + ' מוסכים';

      const totalPages = Math.ceil(total / pageSize) || 1;
      document.getElementById('pageInfo').textContent = `עמוד ${{currentPage}} מתוך ${{totalPages}}`;
      document.getElementById('prevBtn').disabled = (currentPage === 1);
      document.getElementById('nextBtn').disabled = (currentPage === totalPages);

      const start = (currentPage - 1) * pageSize;
      const pageItems = filteredGarages.slice(start, start + pageSize);

      pageItems.forEach(g => {{
        const tr = document.createElement('tr');
        
        let profTags = g.professions.map(p => {{
          let cls = 'tag';
          if (p.includes('חשמלי') || p.includes('היברידי')) cls += ' tag-electric';
          else if (p.includes('דיזל') || p.includes('בנזין')) cls += ' tag-diesel';
          else if (p.includes('מרכבי') || p.includes('צבעות')) cls += ' tag-bodywork';
          return `<span class="${{cls}}">${{p}}</span>`;
        }}).join('');

        tr.innerHTML = `
          <td><strong>${{g.garage_id}}</strong></td>
          <td><strong style="color: var(--primary);">${{g.name}}</strong></td>
          <td><span class="tag">${{g.type || '-'}}</span></td>
          <td>${{g.city || '-'}}</td>
          <td>${{g.address || '-'}}</td>
          <td><a href="tel:${{g.phone}}" style="color:var(--accent); text-decoration:none;">${{g.phone || '-'}}</a></td>
          <td>${{profTags}}</td>
          <td>${{g.managers.join(', ') || '-'}}</td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function changePage(delta) {{
      currentPage += delta;
      renderTable();
      window.scrollTo({{ top: document.querySelector('.controls').offsetTop, behavior: 'smooth' }});
    }}

    document.getElementById('searchInput').addEventListener('input', filterData);
    cityFilter.addEventListener('change', filterData);
    profFilter.addEventListener('change', filterData);
    typeFilter.addEventListener('change', filterData);

    // Render Charts
    const topCities = analytics.top_cities.slice(0, 10);
    new Chart(document.getElementById('cityChart'), {{
      type: 'bar',
      data: {{
        labels: topCities.map(c => c[0]),
        datasets: [{{
          label: 'כמות מוסכים',
          data: topCities.map(c => c[1]),
          backgroundColor: '#38bdf8'
        }}]
      }},
      options: {{
        responsive: true,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
          x: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }},
          y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }}
        }}
      }}
    }});

    const topProfs = analytics.top_professions_specializations.slice(0, 8);
    new Chart(document.getElementById('profChart'), {{
      type: 'doughnut',
      data: {{
        labels: topProfs.map(p => p[0]),
        datasets: [{{
          data: topProfs.map(p => p[1]),
          backgroundColor: ['#38bdf8', '#f59e0b', '#10b981', '#ec4899', '#8b5cf6', '#14b8a6', '#f43f5e', '#64748b']
        }}]
      }},
      options: {{
        responsive: true,
        plugins: {{
          legend: {{ position: 'right', labels: {{ color: '#f8fafc', font: {{ family: 'Assistant' }} }} }}
        }}
      }}
    }});

    function exportFilteredCSV() {{
      let csvContent = "data:text/csv;charset=utf-8,\uFEFF";
      csvContent += "מזהה מוסך,שם מוסך,סוג,יישוב,כתובת,טלפון,התמחויות,מנהלים מקצועיים\n";
      filteredGarages.forEach(g => {{
        let row = [
          g.garage_id,
          `"${{(g.name||'').replace(/"/g, '""')}}"`,
          `"${{(g.type||'').replace(/"/g, '""')}}"`,
          `"${{(g.city||'').replace(/"/g, '""')}}"`,
          `"${{(g.address||'').replace(/"/g, '""')}}"`,
          `"${{(g.phone||'').replace(/"/g, '""')}}"`,
          `"${{(g.professions.join(' | ')).replace(/"/g, '""')}}"`,
          `"${{(g.managers.join(' | ')).replace(/"/g, '""')}}"`
        ];
        csvContent += row.join(",") + "\\n";
      }});
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", "garages_filtered_export.csv");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }}

    // Initial render
    filterData();
  </script>
</body>
</html>
"""

dashboard_path = os.path.join(BASE_DIR, 'garages_dashboard.html')
with open(dashboard_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Interactive Dashboard Generated at: {dashboard_path}")
