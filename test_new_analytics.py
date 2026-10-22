import pandas as pd
import json

data = json.load(open('dashboard_data.json', encoding='utf-8'))
cases = data['cases']
df_c = pd.read_excel('Form C_ Delivery Outcome Record (Responses).xlsx')
df_b = pd.read_excel('Form B_ Follow-up Visit Record (Responses).xlsx')
df_a = pd.read_excel('Form A_ Identification Record (Responses).xlsx')

print(f"Total cases: {len(cases)}")
delivered_cases = [c for c in cases if c.get('delivery')]
print(f"Total delivered cases: {len(delivered_cases)}")

# 1. Test Clinical Delta Tracking by Treatment Type
anemia_tx_stats = {
    'Blood Transfusion': {'count': 0, 'hbs_init': [], 'hbs_final': [], 'deltas': []},
    'IV Iron (Sucrose)': {'count': 0, 'hbs_init': [], 'hbs_final': [], 'deltas': []},
    'Oral IFA / Routine': {'count': 0, 'hbs_init': [], 'hbs_final': [], 'deltas': []}
}

for c in delivered_cases:
    hrp = ' '.join(c.get('hrp_categories', [])).lower()
    if 'anemia' in hrp or 'anaemia' in hrp:
        init_hb = c.get('enrollment_hb')
        del_data = c.get('delivery') or {}
        final_hb = del_data.get('hb')
        
        # Check Form B visits for treatment mentions
        tx_type = 'Oral IFA / Routine'
        has_bt = False
        has_iv = False
        for v in c.get('visits', []):
            act = (v.get('anemia_action') or '').lower()
            bt_note = (v.get('blood_transfusion') or '').lower()
            if 'transfusion' in act or 'transfusion' in bt_note or 'रक्त आधान' in act:
                has_bt = True
            if 'iv iron' in act or 'iron sucrose' in act:
                has_iv = True
        if has_bt:
            tx_type = 'Blood Transfusion'
        elif has_iv:
            tx_type = 'IV Iron (Sucrose)'
            
        anemia_tx_stats[tx_type]['count'] += 1
        if init_hb is not None and final_hb is not None:
            anemia_tx_stats[tx_type]['hbs_init'].append(init_hb)
            anemia_tx_stats[tx_type]['hbs_final'].append(final_hb)
            anemia_tx_stats[tx_type]['deltas'].append(round(final_hb - init_hb, 2))

print("\n--- Anemia Treatment Trajectory ---")
for tx, s in anemia_tx_stats.items():
    avg_init = round(sum(s['hbs_init'])/len(s['hbs_init']), 2) if s['hbs_init'] else 0
    avg_final = round(sum(s['hbs_final'])/len(s['hbs_final']), 2) if s['hbs_final'] else 0
    avg_delta = round(sum(s['deltas'])/len(s['deltas']), 2) if s['deltas'] else 0
    print(f"{tx}: count={s['count']}, paired={len(s['deltas'])}, avg_init={avg_init}, avg_final={avg_final}, avg_gain={avg_delta}")

# 2. Multi-Risk Co-occurrence
categories = [
    'Severe Anemia', 'PIH / Hypertension', 'Sickle Cell Disease (SCD)',
    'Previous LSCS', 'Prev Stillbirth / NND', 'Teenage Pregnancy', 'GDM'
]
def get_norm_cats(hrp_list):
    res = []
    txt = ' '.join(hrp_list).lower()
    if 'anemia' in txt or 'anaemia' in txt: res.append('Severe Anemia')
    if 'pih' in txt or 'hypertension' in txt: res.append('PIH / Hypertension')
    if 'scd' in txt or 'sickle' in txt: res.append('Sickle Cell Disease (SCD)')
    if 'lscs' in txt: res.append('Previous LSCS')
    if 'stillbirth' in txt or 'neonatal' in txt or 'death' in txt or 'boh' in txt: res.append('Prev Stillbirth / NND')
    if 'teen' in txt: res.append('Teenage Pregnancy')
    if 'gdm' in txt or 'diabetes' in txt: res.append('GDM')
    return res

co_matrix = {c1: {c2: 0 for c2 in categories} for c1 in categories}
multi_count = 0
for c in cases:
    cats = get_norm_cats(c.get('hrp_categories', []))
    if len(cats) > 1:
        multi_count += 1
    for c1 in cats:
        for c2 in cats:
            co_matrix[c1][c2] += 1

print(f"\n--- Multi-Risk Cases: {multi_count} / {len(cases)} ---")
print("Top co-occurring pairs:")
pairs = []
for i, c1 in enumerate(categories):
    for j, c2 in enumerate(categories):
        if j > i:
            cnt = co_matrix[c1][c2]
            if cnt > 0:
                pairs.append((f"{c1} + {c2}", cnt))
pairs.sort(key=lambda x: x[1], reverse=True)
for p, cnt in pairs[:8]:
    print(f"  {cnt:2d} cases: {p}")

# 3. Facility Referral Adherence & Leakage
leakage_summary = {
    'Planned Facility Met': 0,
    'Diverted to Other Facility': 0,
    'Home Delivery': 0,
    'Out of District': 0
}
tier_matrix = {} # planned_tier -> actual_tier -> count
unplanned_reasons = {}

for c in delivered_cases:
    d = c.get('delivery') or {}
    planned = (d.get('was_planned') or '').lower()
    place = (d.get('place') or '').strip()
    reason = (d.get('unplanned_reason') or '').strip()
    
    if 'home' in place.lower():
        leakage_summary['Home Delivery'] += 1
    elif 'out of district' in place.lower():
        leakage_summary['Out of District'] += 1
    elif 'yes' in planned:
        leakage_summary['Planned Facility Met'] += 1
    else:
        leakage_summary['Diverted to Other Facility'] += 1
        
    if reason and reason.lower() not in ['nan', 'none', 'no', '-']:
        unplanned_reasons[reason] = unplanned_reasons.get(reason, 0) + 1

print(f"\n--- Delivery Facility Adherence ---")
print(leakage_summary)
print("Unplanned reasons:", list(unplanned_reasons.items())[:5])

# 4. WHO QoC Composite by Facility Tier
qoc_by_tier = {}
for c in delivered_cases:
    d = c.get('delivery') or {}
    place = d.get('place') or 'Unknown'
    if place not in qoc_by_tier:
        qoc_by_tier[place] = {
            'total': 0, 'oxytocin': 0, 'partograph': 0, 'companion': 0,
            'respectful': 0, 'sts': 0, 'bf': 0, 'vit_k': 0
        }
    qoc_by_tier[place]['total'] += 1
    
    if (d.get('oxytocin_given') or '').lower() == 'yes': qoc_by_tier[place]['oxytocin'] += 1
    if (d.get('partograph_plotted') or '').lower() == 'yes': qoc_by_tier[place]['partograph'] += 1
    if (d.get('birth_companion') or '').lower() == 'yes': qoc_by_tier[place]['companion'] += 1
    if 'no' in (d.get('respectful_care') or '').lower(): qoc_by_tier[place]['respectful'] += 1 # 'No abuse reported'
    if (d.get('sts_initiated') or '').lower() == 'yes': qoc_by_tier[place]['sts'] += 1
    if (d.get('breastfeeding_initiated') or '').lower() == 'yes': qoc_by_tier[place]['bf'] += 1
    if (d.get('vit_k_given') or '').lower() == 'yes': qoc_by_tier[place]['vit_k'] += 1

print(f"\n--- Quality of Care by Facility Tier ---")
for tier, stats in qoc_by_tier.items():
    tot = stats['total']
    if tot >= 3:
        oxy_p = round((stats['oxytocin']/tot)*100)
        parto_p = round((stats['partograph']/tot)*100)
        sts_p = round((stats['sts']/tot)*100)
        bf_p = round((stats['bf']/tot)*100)
        vk_p = round((stats['vit_k']/tot)*100)
        print(f"{tier:15s} (n={tot:2d}): Oxytocin={oxy_p}%, Parto={parto_p}%, STS={sts_p}%, BF={bf_p}%, VitK={vk_p}%")
