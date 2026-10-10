import urllib.request
import json
import csv
import os
import sys
from collections import Counter, defaultdict

API_URL = "https://data.gov.il/api/3/action/datastore_search"
RESOURCE_ID = "bb68386a-a331-4bbc-b668-bba2766d517d"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print("Starting scan of all garages in Israel from official data.gov.il repository...")

all_records = []
offset = 0
limit = 5000

while True:
    url = f"{API_URL}?resource_id={RESOURCE_ID}&limit={limit}&offset={offset}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            records = data.get('result', {}).get('records', [])
            total = data.get('result', {}).get('total', 0)
            all_records.extend(records)
            print(f"Fetched {len(all_records)} / {total} records...")
            if len(records) < limit or len(all_records) >= total:
                break
            offset += limit
    except Exception as e:
        print(f"Error fetching offset {offset}: {e}")
        break

print(f"\nTotal raw specialization records fetched: {len(all_records)}")

# Group by unique garage (mispar_mosah)
garages_dict = {}
for r in all_records:
    g_id = r.get('mispar_mosah')
    if not g_id:
        continue
    
    if g_id not in garages_dict:
        garages_dict[g_id] = {
            'garage_id': g_id,
            'name': (r.get('shem_mosah') or '').strip(),
            'type': (r.get('sug_mosah') or '').strip(),
            'type_code': r.get('cod_sug_mosah'),
            'address': (r.get('ktovet') or '').strip(),
            'city': (r.get('yishuv') or '').strip(),
            'phone': (r.get('telephone') or '').strip(),
            'postal_code': r.get('mikud'),
            'company_id': r.get('rasham_havarot'),
            'professions': [],
            'managers': []
        }
    
    prof = (r.get('miktzoa') or '').strip()
    if prof and prof not in garages_dict[g_id]['professions']:
        garages_dict[g_id]['professions'].append(prof)
        
    mgr = (r.get('menahel_miktzoa') or '').strip()
    if mgr and mgr not in garages_dict[g_id]['managers']:
        garages_dict[g_id]['managers'].append(mgr)

garages_list = list(garages_dict.values())
print(f"Total UNIQUE garages identified: {len(garages_list)}")

# Compute analytics and statistics
city_counter = Counter(g['city'] for g in garages_list if g['city'])
type_counter = Counter(g['type'] for g in garages_list if g['type'])

profession_counter = Counter()
for g in garages_list:
    for p in g['professions']:
        profession_counter[p] += 1

manager_counter = Counter()
for g in garages_list:
    for m in g['managers']:
        manager_counter[m] += 1

multi_branch_counter = Counter(g['company_id'] for g in garages_list if g['company_id'])
top_chains = multi_branch_counter.most_common(20)

analytics = {
    'total_unique_garages': len(garages_list),
    'total_specializations_recorded': len(all_records),
    'top_cities': city_counter.most_common(30),
    'garage_types': type_counter.most_common(),
    'top_professions_specializations': profession_counter.most_common(30),
    'top_frequent_managers': [item for item in manager_counter.most_common(30) if item[0]],
    'top_company_chains': [
        {
            'company_id': cid,
            'branches_count': count,
            'sample_names': list(set(g['name'] for g in garages_list if g['company_id'] == cid))[:3]
        }
        for cid, count in top_chains if count > 1
    ]
}

# 1. Export Full JSON Dataset
json_path = os.path.join(BASE_DIR, 'garages_israel_dataset.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(garages_list, f, ensure_ascii=False, indent=2)
print(f"Saved: {json_path}")

# 2. Export Analytics Summary JSON
analytics_path = os.path.join(BASE_DIR, 'garages_analytics_summary.json')
with open(analytics_path, 'w', encoding='utf-8') as f:
    json.dump(analytics, f, ensure_ascii=False, indent=2)
print(f"Saved: {analytics_path}")

# 3. Export Clean Flat CSV for Excel
csv_path = os.path.join(BASE_DIR, 'garages_israel_dataset.csv')
with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        'מזהה מוסך', 'שם מוסך', 'סוג מוסך', 'עיר / יישוב', 'כתובת', 
        'טלפון', 'מיקוד', 'מספר ח.פ / רשם חברות', 'כמות מקצועות', 
        'מקצועות והתמחויות', 'מנהלים מקצועיים'
    ])
    for g in garages_list:
        writer.writerow([
            g['garage_id'],
            g['name'],
            g['type'],
            g['city'],
            g['address'],
            g['phone'],
            g['postal_code'] or '',
            g['company_id'] or '',
            len(g['professions']),
            " | ".join(g['professions']),
            " | ".join(g['managers'])
        ])
print(f"Saved: {csv_path}")

print("\n--- Summary Highlights ---")
print(f"Total Unique Garages: {len(garages_list)}")
print(f"Top 5 Cities: {city_counter.most_common(5)}")
print(f"Top 5 Professions: {profession_counter.most_common(5)}")
