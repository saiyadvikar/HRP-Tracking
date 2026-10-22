import re

with open("generate_analysis_data.py", "r", encoding="utf-8") as f:
    code = f.read()

target_marker = """# Compiling all analysis statistics
analysis_stats = {
    "age_distribution": age_dist,
    "gestational_age_identification": ga_dist,
    "distance_distribution": dist_dist,
    "baseline_hb_distribution": hb_dist,
    "baseline_bp_distribution": bp_dist,
    "linkage_improvements": linkage_improvements
}"""

new_analytics_code = """# 6. Advanced Clinical Trajectories, Multi-Risk Clustering, Facility Leakage & WHO QoC
delivered_cases = [c for c in cases if c.get('delivery')]

# 6.1 Anemia & PIH Clinical Trajectory Response
anemia_tx = {
    'Blood Transfusion': {'count': 0, 'paired': 0, 'init_sum': 0.0, 'final_sum': 0.0, 'gain_sum': 0.0, 'resolved': 0},
    'IV Iron (Sucrose)': {'count': 0, 'paired': 0, 'init_sum': 0.0, 'final_sum': 0.0, 'gain_sum': 0.0, 'resolved': 0},
    'Oral IFA / Routine': {'count': 0, 'paired': 0, 'init_sum': 0.0, 'final_sum': 0.0, 'gain_sum': 0.0, 'resolved': 0}
}

for c in delivered_cases:
    hrp = ' '.join(c.get('hrp_categories', [])).lower()
    if 'anemia' in hrp or 'anaemia' in hrp:
        init_hb = c.get('enrollment_hb')
        d = c.get('delivery') or {}
        final_hb = d.get('hb')
        
        tx_type = 'Oral IFA / Routine'
        for v in c.get('visits', []):
            act = (v.get('anemia_action') or '').lower()
            bt = (v.get('blood_transfusion') or '').lower()
            if 'transfusion' in act or 'transfusion' in bt or 'रक्त आधान' in act:
                tx_type = 'Blood Transfusion'
                break
            elif 'iv iron' in act or 'iron sucrose' in act:
                tx_type = 'IV Iron (Sucrose)'
                
        anemia_tx[tx_type]['count'] += 1
        if init_hb is not None and final_hb is not None:
            anemia_tx[tx_type]['paired'] += 1
            anemia_tx[tx_type]['init_sum'] += init_hb
            anemia_tx[tx_type]['final_sum'] += final_hb
            gain = final_hb - init_hb
            anemia_tx[tx_type]['gain_sum'] += gain
            if final_hb >= 7.0:
                anemia_tx[tx_type]['resolved'] += 1

anemia_trajectory_data = {}
for k, v in anemia_tx.items():
    p = v['paired']
    anemia_trajectory_data[k] = {
        'total_cases': v['count'],
        'paired_cases': p,
        'avg_init_hb': round(v['init_sum'] / p, 2) if p > 0 else 0,
        'avg_final_hb': round(v['final_sum'] / p, 2) if p > 0 else 0,
        'avg_gain_hb': round(v['gain_sum'] / p, 2) if p > 0 else 0,
        'resolution_rate': round((v['resolved'] / p) * 100, 1) if p > 0 else 0
    }

pih_paired = 0
pih_controlled_del = 0
pih_mild_del = 0
pih_severe_del = 0
pih_sys_init = 0.0
pih_dia_init = 0.0
pih_sys_del = 0.0
pih_dia_del = 0.0

for c in delivered_cases:
    hrp = ' '.join(c.get('hrp_categories', [])).lower()
    if 'pih' in hrp or 'hypertension' in hrp:
        init_s = c.get('enrollment_bp_sys')
        init_d = c.get('enrollment_bp_dia')
        del_bp_str = str((c.get('delivery') or {}).get('bp') or '')
        
        del_s, del_d = None, None
        if '/' in del_bp_str:
            parts = del_bp_str.split('/')
            try:
                del_s = float(''.join(ch for ch in parts[0] if ch.isdigit() or ch=='.'))
                del_d = float(''.join(ch for ch in parts[1] if ch.isdigit() or ch=='.'))
            except: pass
            
        if del_s and del_d:
            if del_s < 140 and del_d < 90:
                pih_controlled_del += 1
            elif del_s < 160 and del_d < 110:
                pih_mild_del += 1
            else:
                pih_severe_del += 1
                
            if init_s and init_d:
                pih_paired += 1
                pih_sys_init += init_s
                pih_dia_init += init_d
                pih_sys_del += del_s
                pih_dia_del += del_d

pih_trajectory_data = {
    'total_pih_deliveries': len([c for c in delivered_cases if 'pih' in ' '.join(c.get('hrp_categories',[])).lower()]),
    'bp_recorded_at_delivery': (pih_controlled_del + pih_mild_del + pih_severe_del),
    'controlled_under_140_90': pih_controlled_del,
    'mild_140_159_90_109': pih_mild_del,
    'severe_160_110_plus': pih_severe_del,
    'control_rate': round((pih_controlled_del / max(1, (pih_controlled_del + pih_mild_del + pih_severe_del))) * 100, 1),
    'paired_cases': pih_paired,
    'avg_init_bp': f"{round(pih_sys_init/pih_paired)}/{round(pih_dia_init/pih_paired)}" if pih_paired else "-",
    'avg_del_bp': f"{round(pih_sys_del/pih_paired)}/{round(pih_dia_del/pih_paired)}" if pih_paired else "-"
}

clinical_trajectories = {
    'anemia': anemia_trajectory_data,
    'pih': pih_trajectory_data
}

# 6.2 Multi-Risk Co-occurrence Matrix & Compounding Morbidity
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

multi_risk_cases_count = sum(1 for c in cases if len(get_norm_cats(c.get('hrp_categories', []))) >= 2)
co_matrix = {c1: {c2: 0 for c2 in categories} for c1 in categories}

for c in cases:
    cats = get_norm_cats(c.get('hrp_categories', []))
    for c1 in cats:
        for c2 in cats:
            co_matrix[c1][c2] += 1

pair_stats = []
for i, c1 in enumerate(categories):
    for j, c2 in enumerate(categories):
        if j > i:
            cnt = co_matrix[c1][c2]
            if cnt > 0:
                pair_del = [c for c in delivered_cases if c1 in get_norm_cats(c.get('hrp_categories',[])) and c2 in get_norm_cats(c.get('hrp_categories',[]))]
                lscs_cnt = sum(1 for c in pair_del if 'lscs' in str((c.get('delivery') or {}).get('type')).lower() or 'cesarean' in str((c.get('delivery') or {}).get('type')).lower())
                lbw_cnt = sum(1 for c in pair_del if 'lbw' in str((c.get('delivery') or {}).get('birth_weight_category')).lower() or 'vlbw' in str((c.get('delivery') or {}).get('birth_weight_category')).lower())
                sncu_cnt = sum(1 for c in pair_del if (c.get('delivery') or {}).get('baby_transferred') and not str((c.get('delivery') or {}).get('baby_transferred')).lower().startswith('no'))
                
                pair_stats.append({
                    'pair': f"{c1} + {c2}",
                    'c1': c1,
                    'c2': c2,
                    'total_enrolled': cnt,
                    'delivered_count': len(pair_del),
                    'lscs_count': lscs_cnt,
                    'lbw_count': lbw_cnt,
                    'sncu_count': sncu_cnt
                })

pair_stats.sort(key=lambda x: x['total_enrolled'], reverse=True)

multi_risk_matrix = {
    'total_multi_risk_cases': multi_risk_cases_count,
    'categories': categories,
    'co_occurrence_matrix': co_matrix,
    'top_pairs': pair_stats
}

# 6.3 Facility Referral Adherence & Leakage Analytics
leakage_summary = {
    'Planned Facility Met': 0,
    'Diverted to Other Facility': 0,
    'Out of District': 0,
    'Home Delivery': 0
}
tier_counts = {'DH': 0, 'CHC': 0, 'SDH': 0, 'PHC': 0, 'Private': 0, 'Home': 0, 'Out of District': 0}
cleaned_reasons = {}

for c in delivered_cases:
    d = c.get('delivery') or {}
    place = str(d.get('place') or '').strip()
    planned = str(d.get('was_planned') or '').lower()
    reason = str(d.get('unplanned_reason') or '').strip()
    
    if 'home' in place.lower():
        leakage_summary['Home Delivery'] += 1
        tier_counts['Home'] += 1
    elif 'out of district' in place.lower():
        leakage_summary['Out of District'] += 1
        tier_counts['Out of District'] += 1
    elif 'dh' in place.lower():
        tier_counts['DH'] += 1
    elif 'sdh' in place.lower():
        tier_counts['SDH'] += 1
    elif 'chc' in place.lower():
        tier_counts['CHC'] += 1
    elif 'phc' in place.lower():
        tier_counts['PHC'] += 1
    elif 'private' in place.lower():
        tier_counts['Private'] += 1

    if 'home' not in place.lower() and 'out of district' not in place.lower():
        if 'yes' in planned:
            leakage_summary['Planned Facility Met'] += 1
        else:
            leakage_summary['Diverted to Other Facility'] += 1
            
    if reason and reason.lower() not in ['nan', 'none', 'no', '-', '']:
        cleaned_reasons[reason] = cleaned_reasons.get(reason, 0) + 1

facility_leakage = {
    'adherence_summary': leakage_summary,
    'delivery_tiers': tier_counts,
    'diversion_reasons': cleaned_reasons
}

# 6.4 WHO Quality of Care (QoC) Composite Metrics
tier_qoc = {}
all_qoc = {'total': 0, 'oxytocin': 0, 'partograph': 0, 'companion': 0, 'respectful': 0, 'sts': 0, 'bf': 0, 'vit_k': 0}

for c in delivered_cases:
    d = c.get('delivery') or {}
    place = str(d.get('place') or 'Unknown').strip()
    if place not in tier_qoc:
        tier_qoc[place] = {'total': 0, 'oxytocin': 0, 'partograph': 0, 'companion': 0, 'respectful': 0, 'sts': 0, 'bf': 0, 'vit_k': 0}
        
    tier_qoc[place]['total'] += 1
    all_qoc['total'] += 1
    
    if (d.get('oxytocin_given') or '').lower() == 'yes':
        tier_qoc[place]['oxytocin'] += 1; all_qoc['oxytocin'] += 1
    if (d.get('partograph_plotted') or '').lower() == 'yes':
        tier_qoc[place]['partograph'] += 1; all_qoc['partograph'] += 1
    if (d.get('birth_companion') or '').lower() == 'yes':
        tier_qoc[place]['companion'] += 1; all_qoc['companion'] += 1
    if 'no' in (d.get('respectful_care') or '').lower():
        tier_qoc[place]['respectful'] += 1; all_qoc['respectful'] += 1
    if (d.get('sts_initiated') or '').lower() == 'yes':
        tier_qoc[place]['sts'] += 1; all_qoc['sts'] += 1
    if (d.get('breastfeeding_initiated') or '').lower() == 'yes':
        tier_qoc[place]['bf'] += 1; all_qoc['bf'] += 1
    if (d.get('vit_k_given') or '').lower() == 'yes':
        tier_qoc[place]['vit_k'] += 1; all_qoc['vit_k'] += 1

qoc_summary = {}
for place, s in tier_qoc.items():
    tot = max(1, s['total'])
    scores = [
        round((s['oxytocin']/tot)*100),
        round((s['partograph']/tot)*100),
        round((s['companion']/tot)*100),
        round((s['respectful']/tot)*100),
        round((s['sts']/tot)*100),
        round((s['bf']/tot)*100),
        round((s['vit_k']/tot)*100)
    ]
    qoc_summary[place] = {
        'total': s['total'],
        'oxytocin_pct': scores[0],
        'partograph_pct': scores[1],
        'companion_pct': scores[2],
        'respectful_pct': scores[3],
        'sts_pct': scores[4],
        'bf_pct': scores[5],
        'vit_k_pct': scores[6],
        'composite_score': round(sum(scores)/len(scores), 1)
    }

# Overall composite
tot_all = max(1, all_qoc['total'])
all_scores = [
    round((all_qoc['oxytocin']/tot_all)*100),
    round((all_qoc['partograph']/tot_all)*100),
    round((all_qoc['companion']/tot_all)*100),
    round((all_qoc['respectful']/tot_all)*100),
    round((all_qoc['sts']/tot_all)*100),
    round((all_qoc['bf']/tot_all)*100),
    round((all_qoc['vit_k']/tot_all)*100)
]
qoc_summary['OVERALL'] = {
    'total': all_qoc['total'],
    'oxytocin_pct': all_scores[0],
    'partograph_pct': all_scores[1],
    'companion_pct': all_scores[2],
    'respectful_pct': all_scores[3],
    'sts_pct': all_scores[4],
    'bf_pct': all_scores[5],
    'vit_k_pct': all_scores[6],
    'composite_score': round(sum(all_scores)/len(all_scores), 1)
}

who_qoc_metrics = qoc_summary

# Compiling all analysis statistics
analysis_stats = {
    "age_distribution": age_dist,
    "gestational_age_identification": ga_dist,
    "distance_distribution": dist_dist,
    "baseline_hb_distribution": hb_dist,
    "baseline_bp_distribution": bp_dist,
    "linkage_improvements": linkage_improvements,
    "clinical_trajectories": clinical_trajectories,
    "multi_risk_matrix": multi_risk_matrix,
    "facility_leakage": facility_leakage,
    "who_qoc_metrics": who_qoc_metrics
}"""

code_norm = code.replace('\r\n', '\n')
target_marker_norm = target_marker.replace('\r\n', '\n')
assert target_marker_norm in code_norm, "Target marker for analysis_stats not found"
code_norm = code_norm.replace(target_marker_norm, new_analytics_code.replace('\r\n', '\n'), 1)

with open("generate_analysis_data.py", "w", encoding="utf-8") as f:
    f.write(code_norm)

print("Successfully injected 4 advanced analytics modules into generate_analysis_data.py!")
