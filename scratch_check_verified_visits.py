import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

data = json.load(open('dashboard_data.json', encoding='utf-8'))
cases = data['cases']

cond_visits = {
    'Severe Anemia': {'patients': set(), 'visits': []},
    'PIH': {'patients': set(), 'visits': []},
    'GDM': {'patients': set(), 'visits': []},
    'SCD': {'patients': set(), 'visits': []},
    'Previous LSCS': {'patients': set(), 'visits': []},
    'BOH': {'patients': set(), 'visits': []},
    'Teenage': {'patients': set(), 'visits': []}
}

for c in cases:
    cats = [cat.lower() for cat in c.get('hrp_categories', [])]
    has_anemia = any('anemia' in cat or 'anaemia' in cat for cat in cats)
    has_pih = any('pih' in cat or 'hypertension' in cat for cat in cats)
    has_gdm = any('gdm' in cat or 'diabetes' in cat for cat in cats)
    has_scd = any('scd' in cat or 'sickle' in cat for cat in cats)
    has_lscs = any('lscs' in cat or 'cesarean' in cat for cat in cats)
    has_boh = any('stillbirth' in cat or 'neonatal' in cat or 'death' in cat or 'boh' in cat for cat in cats)
    has_teen = any('teen' in cat for cat in cats) or (c.get('age') and c['age'] < 20)

    for v in c.get('visits', []):
        if has_anemia and v.get('anemia_status'):
            cond_visits['Severe Anemia']['patients'].add(c['id_a'])
            cond_visits['Severe Anemia']['visits'].append((c['name'], v.get('visit_number'), v.get('anemia_status'), v.get('hb')))
        if has_pih and v.get('pih_status'):
            cond_visits['PIH']['patients'].add(c['id_a'])
            cond_visits['PIH']['visits'].append((c['name'], v.get('visit_number'), v.get('pih_status'), f"{v.get('bp_systolic')}/{v.get('bp_diastolic')}"))
        if has_gdm and v.get('gdm_status'):
            cond_visits['GDM']['patients'].add(c['id_a'])
            cond_visits['GDM']['visits'].append((c['name'], v.get('visit_number'), v.get('gdm_status'), f"FBS:{v.get('gdm_fbs')}/RBS:{v.get('gdm_rbs')}"))
        if has_scd and v.get('scd_status'):
            cond_visits['SCD']['patients'].add(c['id_a'])
            cond_visits['SCD']['visits'].append((c['name'], v.get('visit_number'), v.get('scd_status'), v.get('scd_hb') or v.get('hb')))
        if has_lscs and v.get('prev_lscs_status'):
            cond_visits['Previous LSCS']['patients'].add(c['id_a'])
            cond_visits['Previous LSCS']['visits'].append((c['name'], v.get('visit_number'), v.get('prev_lscs_status')))
        if has_boh and v.get('prev_stillbirth_status'):
            cond_visits['BOH']['patients'].add(c['id_a'])
            cond_visits['BOH']['visits'].append((c['name'], v.get('visit_number'), v.get('prev_stillbirth_status')))
        if has_teen and v.get('teenage_status'):
            cond_visits['Teenage']['patients'].add(c['id_a'])
            cond_visits['Teenage']['visits'].append((c['name'], v.get('visit_number'), v.get('teenage_status')))

for k, d in cond_visits.items():
    print(f"\nCondition: {k} | Unique Verified Patients: {len(d['patients'])} | Total Follow-up Visits: {len(d['visits'])}")
    status_summary = {}
    for item in d['visits']:
        st = item[2]
        status_summary[st] = status_summary.get(st, 0) + 1
    for st, cnt in sorted(status_summary.items(), key=lambda x: -x[1]):
        print(f"  {cnt:2d} | {st[:60]}")
