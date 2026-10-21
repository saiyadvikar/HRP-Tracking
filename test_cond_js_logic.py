import json

data = json.load(open('dashboard_data.json', encoding='utf-8'))
cases = data['cases']

def get_status_cat(s):
    if not s: return 'UNKNOWN'
    s = s.lower()
    if any(k in s for k in ['controlled', 'नियंत्रित', 'stable', 'स्थिर', 'on track', 'योजना के अनुसार']): return 'CONTROLLED'
    if any(k in s for k in ['improving', 'सुधार', 'borderline', 'सीमा रेखा']): return 'IMPROVING'
    if any(k in s for k in ['not controlled', 'अनियंत्रित', 'crisis', 'संकट', 'worsen', 'बिगड़', 'concern', 'दर्द', 'pain', 'कम', 'reduced']): return 'UNCONTROLLED'
    return 'OTHER'

cond_list = [
    ('ALL', ''),
    ('SCD', 'scd'),
    ('ANEMIA', 'anemia'),
    ('PIH', 'pih'),
    ('GDM', 'gdm'),
    ('LSCS', 'lscs'),
    ('BOH', 'stillbirth'),
    ('TEEN', 'teen')
]

for cond_key, query in cond_list:
    v_cases = set()
    records = []
    for c in cases:
        hrp = ' '.join(c.get('hrp_categories', [])).lower()
        if query and query not in hrp: continue
        for v in c.get('visits', []):
            st = ''
            act = ''
            if cond_key == 'SCD' or (cond_key == 'ALL' and ('scd' in hrp or 'sickle' in hrp)):
                if v.get('scd_status') or v.get('scd_action'):
                    st = v.get('scd_status'); act = v.get('scd_action')
                    v_cases.add(c['id_a']); records.append((st, act, 'SCD'))
            if cond_key == 'ANEMIA' or (cond_key == 'ALL' and ('anemia' in hrp or 'anaemia' in hrp)):
                if v.get('anemia_status') or v.get('anemia_action'):
                    st = v.get('anemia_status'); act = v.get('anemia_action')
                    v_cases.add(c['id_a']); records.append((st, act, 'ANEMIA'))
            if cond_key == 'PIH' or (cond_key == 'ALL' and ('pih' in hrp or 'hypertension' in hrp)):
                if v.get('pih_status') or v.get('pih_action'):
                    st = v.get('pih_status'); act = v.get('pih_action')
                    v_cases.add(c['id_a']); records.append((st, act, 'PIH'))
            if cond_key == 'GDM' or (cond_key == 'ALL' and ('gdm' in hrp or 'diabetes' in hrp)):
                if v.get('gdm_status') or v.get('gdm_action'):
                    st = v.get('gdm_status'); act = v.get('gdm_action')
                    v_cases.add(c['id_a']); records.append((st, act, 'GDM'))
            if cond_key == 'LSCS' or (cond_key == 'ALL' and ('lscs' in hrp or 'cesarean' in hrp)):
                if v.get('prev_lscs_status') or v.get('prev_lscs_remarks'):
                    st = v.get('prev_lscs_status'); act = v.get('prev_lscs_remarks')
                    v_cases.add(c['id_a']); records.append((st, act, 'LSCS'))
            if cond_key == 'BOH' or (cond_key == 'ALL' and any(x in hrp for x in ['stillbirth', 'neonatal', 'death', 'boh'])):
                if v.get('prev_stillbirth_status') or v.get('prev_stillbirth_remarks'):
                    st = v.get('prev_stillbirth_status'); act = v.get('prev_stillbirth_remarks')
                    v_cases.add(c['id_a']); records.append((st, act, 'BOH'))
            if cond_key == 'TEEN' or (cond_key == 'ALL' and ('teen' in hrp or 'किशोर' in hrp)):
                if v.get('teenage_status') or v.get('teenage_remarks'):
                    st = v.get('teenage_status'); act = v.get('teenage_remarks')
                    v_cases.add(c['id_a']); records.append((st, act, 'TEEN'))
                
    st_cats = {'CONTROLLED': 0, 'IMPROVING': 0, 'UNCONTROLLED': 0, 'OTHER': 0}
    for st, act, ck in records:
        cat = get_status_cat(st)
        st_cats[cat] = st_cats.get(cat, 0) + 1
        
    c_cnt = st_cats['CONTROLLED']
    i_cnt = st_cats['IMPROVING']
    u_cnt = st_cats['UNCONTROLLED']
    print(f"{cond_key:7s}: {len(v_cases):2d} mothers | {len(records):2d} verified assessments | Controlled: {c_cnt:2d} | Improving: {i_cnt:2d} | Uncontrolled/Crisis: {u_cnt:2d}")
