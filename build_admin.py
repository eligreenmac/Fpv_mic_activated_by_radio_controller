import json
import os

BASE_DIR = r"c:\Users\USER\Desktop\ramah\shema"
json_path = os.path.join(BASE_DIR, 'garages_israel_dataset.json')
analytics_path = os.path.join(BASE_DIR, 'garages_analytics_summary.json')

with open(json_path, 'r', encoding='utf-8') as f:
    garages = json.load(f)

with open(analytics_path, 'r', encoding='utf-8') as f:
    analytics = json.load(f)

html_code = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>פורטל ניהול ואדמין | Admin Control Center</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700;800&family=Rubik:wght@400;500;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {{
      --bg-main: #0b0f19;
      --bg-card: #151d2e;
      --bg-card-hover: #1c263d;
      --border: #23304a;
      --primary: #38bdf8;
      --primary-hover: #0ea5e9;
      --accent: #f59e0b;
      --success: #10b981;
      --danger: #ef4444;
      --purple: #a855f7;
      --text: #f8fafc;
      --text-muted: #94a3b8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Assistant', sans-serif;
      background: var(--bg-main);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}
    /* Top Navbar */
    .navbar {{
      background: #101726;
      border-bottom: 1px solid var(--border);
      padding: 12px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
      font-family: 'Rubik', sans-serif;
      font-size: 20px;
      font-weight: 800;
      color: var(--primary);
    }}
    .brand i {{ font-size: 24px; color: var(--accent); }}
    .badge-admin {{
      background: linear-gradient(135deg, #f59e0b, #d97706);
      color: #000;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 900;
      letter-spacing: 0.5px;
    }}
    
    /* Navigation Tabs */
    .nav-tabs {{
      display: flex;
      gap: 8px;
      background: #0b0f19;
      padding: 6px;
      border-radius: 10px;
      border: 1px solid var(--border);
    }}
    .tab-btn {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 8px 16px;
      border-radius: 8px;
      font-family: 'Rubik', sans-serif;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s;
    }}
    .tab-btn:hover {{
      color: var(--text);
      background: rgba(56, 189, 248, 0.1);
    }}
    .tab-btn.active {{
      background: var(--primary);
      color: #0b0f19;
      box-shadow: 0 2px 10px rgba(56, 189, 248, 0.4);
    }}
    
    /* Content Layout */
    .main-container {{
      flex: 1;
      padding: 24px;
      max-width: 1600px;
      margin: 0 auto;
      width: 100%;
    }}
    .tab-content {{
      display: none;
      animation: fadeIn 0.3s ease;
    }}
    .tab-content.active {{
      display: block;
    }}
    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(6px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Global Cards & Stats */
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}
    .stat-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 20px;
      text-align: center;
      box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}
    .stat-num {{
      font-family: 'Rubik', sans-serif;
      font-size: 34px;
      font-weight: 800;
      color: var(--primary);
      margin-bottom: 4px;
    }}
    .stat-num.accent {{ color: var(--accent); }}
    .stat-num.success {{ color: var(--success); }}
    .stat-num.purple {{ color: var(--purple); }}
    .stat-label {{
      color: var(--text-muted);
      font-size: 13px;
      font-weight: 600;
    }}

    /* Charts Grid */
    .charts-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(460px, 1fr));
      gap: 20px;
      margin-bottom: 25px;
    }}
    .chart-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 20px;
    }}
    .chart-card h3 {{
      font-family: 'Rubik', sans-serif;
      font-size: 17px;
      color: var(--primary);
      margin-bottom: 15px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 10px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    /* Controls Bar */
    .controls {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 18px;
      margin-bottom: 20px;
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }}
    .search-box {{
      flex: 2;
      min-width: 260px;
    }}
    input, select {{
      width: 100%;
      padding: 12px 16px;
      background: #0c1220;
      border: 1px solid var(--border);
      border-radius: 8px;
      color: #fff;
      font-size: 14px;
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
    .btn {{
      padding: 10px 18px;
      background: var(--primary);
      color: #0b0f19;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 700;
      font-family: inherit;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s;
      text-decoration: none;
    }}
    .btn:hover {{ background: var(--primary-hover); transform: translateY(-1px); }}
    .btn-export {{ background: var(--success); color: #fff; }}
    .btn-export:hover {{ background: #059669; }}
    .btn-action {{ background: #2563eb; color: #fff; }}

    /* Tables */
    .table-container {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 14px;
      overflow: hidden;
      box-shadow: 0 10px 25px rgba(0,0,0,0.4);
    }}
    .table-header-bar {{
      padding: 15px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #111827;
      border-bottom: 1px solid var(--border);
    }}
    .count-badge {{
      background: var(--primary);
      color: #0b0f19;
      padding: 4px 12px;
      border-radius: 20px;
      font-weight: 800;
      font-size: 13px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: right;
    }}
    th, td {{
      padding: 12px 16px;
      border-bottom: 1px solid var(--border);
      font-size: 13.5px;
    }}
    th {{
      background: #0d1424;
      color: var(--text-muted);
      font-weight: 700;
      user-select: none;
    }}
    tr:hover td {{
      background: rgba(56, 189, 248, 0.04);
    }}
    .tag {{
      display: inline-block;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 11.5px;
      margin: 2px;
      background: #1e293b;
      color: #cbd5e1;
      border: 1px solid #334155;
    }}
    .tag-electric {{ background: rgba(16, 185, 129, 0.15); color: #6ee7b7; border-color: #059669; }}
    .tag-diesel {{ background: rgba(245, 158, 11, 0.15); color: #fde68a; border-color: #d97706; }}
    .tag-bodywork {{ background: rgba(168, 85, 247, 0.15); color: #e9d5ff; border-color: #9333ea; }}
    
    .pagination {{
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 12px;
      padding: 16px;
      background: #111827;
    }}
    .pagination button:disabled {{
      background: #1e293b;
      color: #475569;
      cursor: not-allowed;
    }}

    /* Embed Frame Tab */
    .frame-container {{
      width: 100%;
      height: 820px;
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 14px;
      overflow: hidden;
    }}
    iframe {{
      width: 100%;
      height: 100%;
      border: none;
    }}

    /* Quick Cards */
    .quick-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 20px;
      margin-bottom: 24px;
    }}
    .action-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 16px;
    }}
    .action-card h3 {{
      font-family: 'Rubik', sans-serif;
      font-size: 18px;
      color: var(--primary);
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .action-card p {{
      color: var(--text-muted);
      font-size: 14px;
      line-height: 1.5;
    }}
  </style>
</head>
<body>

  <!-- Top Navbar with Navigation Tabs -->
  <nav class="navbar">
    <div class="brand">
      <i class="fa-solid fa-layer-group"></i>
      <span>מרכז הבקרה והאדמין</span>
      <span class="badge-admin">ADMIN PORTAL</span>
    </div>
    <div class="nav-tabs">
      <button class="tab-btn active" onclick="switchTab('tab-garages')">
        <i class="fa-solid fa-warehouse"></i> מאגר מוסכים ודאטה
      </button>
      <button class="tab-btn" onclick="switchTab('tab-analytics')">
        <i class="fa-solid fa-chart-pie"></i> סטטיסטיקה ופילוח
      </button>
      <button class="tab-btn" onclick="switchTab('tab-fpv')">
        <i class="fa-solid fa-microphone-lines"></i> מקליט קול FPV
      </button>
      <button class="tab-btn" onclick="switchTab('tab-propeller')">
        <i class="fa-solid fa-fan"></i> מחולל פרופלורים
      </button>
      <button class="tab-btn" onclick="switchTab('tab-downloads')">
        <i class="fa-solid fa-download"></i> הורדת מאגרים
      </button>
    </div>
  </nav>

  <main class="main-container">

    <!-- TAB 1: GARAGES DATABASE -->
    <section id="tab-garages" class="tab-content active">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-num">{analytics['total_unique_garages']:,}</div>
          <div class="stat-label">סך מוסכים ייחודיים בישראל</div>
        </div>
        <div class="stat-card">
          <div class="stat-num accent">{analytics['total_specializations_recorded']:,}</div>
          <div class="stat-label">סך הסמכות והתמחויות מורשות</div>
        </div>
        <div class="stat-card">
          <div class="stat-num success">{len(analytics['top_cities'])}</div>
          <div class="stat-label">ערים ויישובים פעילים</div>
        </div>
        <div class="stat-card">
          <div class="stat-num purple">{len(analytics['top_professions_specializations'])}</div>
          <div class="stat-label">מקצועות ותחומי שירות</div>
        </div>
      </div>

      <div class="controls">
        <div class="search-box">
          <input type="text" id="searchInput" placeholder="🔍 חיפוש חופשי: שם מוסך, כתובת, טלפון, עיר, מנהל מקצועי, התמחות...">
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
        <button class="btn btn-export" onclick="exportFilteredCSV()">
          <i class="fa-solid fa-file-csv"></i> ייצוא ל-CSV
        </button>
      </div>

      <div class="table-container">
        <div class="table-header-bar">
          <div><strong style="font-size:16px;">רשימת מוסכים ומכוני רישוי מורשים</strong></div>
          <div id="resultsCount" class="count-badge">0 מוסכים</div>
        </div>
        <table>
          <thead>
            <tr>
              <th>מס' מוסך</th>
              <th>שם המוסך</th>
              <th>סוג</th>
              <th>עיר / יישוב</th>
              <th>כתובת</th>
              <th>טלפון</th>
              <th>התמחויות מורשות</th>
              <th>מנהל מקצועי</th>
            </tr>
          </thead>
          <tbody id="garagesTableBody"></tbody>
        </table>
        <div class="pagination">
          <button class="btn" id="prevBtn" onclick="changePage(-1)">◀ הקודם</button>
          <span id="pageInfo" style="font-weight:600;">עמוד 1 מתוך 1</span>
          <button class="btn" id="nextBtn" onclick="changePage(1)">הבא ▶</button>
        </div>
      </div>
    </section>

    <!-- TAB 2: ANALYTICS & PATTERNS -->
    <section id="tab-analytics" class="tab-content">
      <div class="charts-grid">
        <div class="chart-card">
          <h3><i class="fa-solid fa-city"></i> 10 הערים עם ריכוז המוסכים הגבוה ביותר</h3>
          <canvas id="cityChart" height="220"></canvas>
        </div>
        <div class="chart-card">
          <h3><i class="fa-solid fa-wrench"></i> התפלגות מקצועות והתמחויות ראשיות</h3>
          <canvas id="profChart" height="220"></canvas>
        </div>
      </div>

      <div class="quick-grid">
        <div class="action-card">
          <h3><i class="fa-solid fa-network-wired"></i> רשתות וחברות מובילות (ח.פ מרובה סניפים)</h3>
          <p>רשימת גופים וחברות המחזיקים במספר סניפים ומוסכים מורשים ברחבי הארץ.</p>
          <div style="max-height: 250px; overflow-y:auto;">
            <table style="font-size: 13px;">
              <thead>
                <tr>
                  <th>ח.פ חברה</th>
                  <th>כמות סניפים</th>
                  <th>שמות לדוגמה</th>
                </tr>
              </thead>
              <tbody>
                {''.join([f"<tr><td><strong>{c['company_id']}</strong></td><td><span class='count-badge'>{c['branches_count']} סניפים</span></td><td>{', '.join(c['sample_names'])}</td></tr>" for c in analytics['top_company_chains'][:10]])}
              </tbody>
            </table>
          </div>
        </div>

        <div class="action-card">
          <h3><i class="fa-solid fa-user-tie"></i> מנהלים מקצועיים מובילים</h3>
          <p>מנהלים מקצועיים הרשומים על מספר מוסכים והסמכות מורשות במקביל.</p>
          <div style="max-height: 250px; overflow-y:auto;">
            <table style="font-size: 13px;">
              <thead>
                <tr>
                  <th>שם מנהל מקצועי</th>
                  <th>מספר הסמכות</th>
                </tr>
              </thead>
              <tbody>
                {''.join([f"<tr><td><strong>{m[0]}</strong></td><td><span class='tag'>{m[1]} רישומים</span></td></tr>" for m in analytics['top_frequent_managers'][:10]])}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>

    <!-- TAB 3: FPV AUDIO RECORDER HUB -->
    <section id="tab-fpv" class="tab-content">
      <div class="quick-grid">
        <div class="action-card">
          <h3><i class="fa-solid fa-wifi"></i> חיבור אלחוטי ישיר לרחפן (Wi-Fi Web Server)</h3>
          <p>התחבר ל-Wi-Fi של הרחפן ישירות מהטלפון או המחשב להורדת קבצי אודיו 16kHz ללא הוצאת כרטיס SD.</p>
          <div style="background:#0c1220; padding:12px; border-radius:8px; border:1px solid var(--border); font-size:14px;">
            <div><strong>שם רשת (SSID):</strong> <code>FPV-Audio-Recorder</code></div>
            <div><strong>אבטחה:</strong> <code>רשת פתוחה (Open Network)</code></div>
            <div><strong>כתובת גישה:</strong> <a href="http://192.168.4.1" target="_blank" style="color:var(--primary); font-weight:bold;">http://192.168.4.1</a></div>
          </div>
          <a class="btn btn-action" href="http://192.168.4.1" target="_blank">
            <i class="fa-solid fa-arrow-up-right-from-square"></i> פתח דף ניהול מקליט (192.168.4.1)
          </a>
        </div>

        <div class="action-card">
          <h3><i class="fa-solid fa-microchip"></i> הגדרות חומרה ו-Betaflight PINIO</h3>
          <p>מיפוי רגל 10 כטריגר הקלטה באמצעות מתג AUX בשלט הרדיו.</p>
          <pre style="background:#0c1220; padding:12px; border-radius:8px; font-size:12px; color:#a7f3d0; overflow-x:auto;">
resource SERIAL_TX 3 NONE
resource PINIO 1 B10
set pinio_config = 1,129,129,129
set pinio_box = 40,255,255,255
save</pre>
        </div>
      </div>
    </section>

    <!-- TAB 4: PROPELLER GENERATOR -->
    <section id="tab-propeller" class="tab-content">
      <div class="frame-container">
        <iframe src="propeller_generator.html"></iframe>
      </div>
    </section>

    <!-- TAB 5: DOWNLOADS & EXPORTS -->
    <section id="tab-downloads" class="tab-content">
      <div class="quick-grid">
        <div class="action-card">
          <h3><i class="fa-solid fa-file-csv"></i> מאגר המוסכים המלא (CSV לאקסל)</h3>
          <p>קובץ CSV מלא עם 5,475 מוסכים, כולל כתובות, טלפונים, התמחויות ומנהלים.</p>
          <a class="btn btn-export" href="garages_israel_dataset.csv" download>
            <i class="fa-solid fa-download"></i> הורד קובץ CSV
          </a>
        </div>

        <div class="action-card">
          <h3><i class="fa-solid fa-file-code"></i> מאגר מובנה לפיתוח (JSON)</h3>
          <p>קובץ JSON מובנה עם כל הרשומות המקובצות לפי מזהה מוסך ייחודי.</p>
          <a class="btn btn-action" href="garages_israel_dataset.json" download>
            <i class="fa-solid fa-download"></i> הורד קובץ JSON
          </a>
        </div>

        <div class="action-card">
          <h3><i class="fa-solid fa-chart-line"></i> דוח סטטיסטיקות ואנליטיקה (JSON)</h3>
          <p>ריכוז נתונים ופילוחים סטטיסטיים לתקיפה ואנליזת שוק.</p>
          <a class="btn btn-action" href="garages_analytics_summary.json" download>
            <i class="fa-solid fa-download"></i> הורד דוח אנליטיקה
          </a>
        </div>
      </div>
    </section>

  </main>

  <script>
    const allGarages = {json.dumps(garages, ensure_ascii=False)};
    const analytics = {json.dumps(analytics, ensure_ascii=False)};

    let filteredGarages = [...allGarages];
    let currentPage = 1;
    const pageSize = 50;

    // Tab Switching
    function switchTab(tabId) {{
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
      
      const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
      if (activeBtn) activeBtn.classList.add('active');
      
      const activeContent = document.getElementById(tabId);
      if (activeContent) activeContent.classList.add('active');
    }}

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
          x: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#23304a' }} }},
          y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#23304a' }} }}
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
          backgroundColor: ['#38bdf8', '#f59e0b', '#10b981', '#ec4899', '#a855f7', '#14b8a6', '#f43f5e', '#64748b']
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

admin_path = os.path.join(BASE_DIR, 'admin.html')
with open(admin_path, 'w', encoding='utf-8') as f:
    f.write(html_code)

print(f"Admin Portal created successfully at: {admin_path}")
