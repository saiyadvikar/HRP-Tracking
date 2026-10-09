import pandas as pd
import numpy as np
import json
import re
from datetime import datetime, timedelta

import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Dynamic Base Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# File paths
path_a = os.path.join(BASE_DIR, "Form A_ Identification Record (Responses).xlsx")
path_b = os.path.join(BASE_DIR, "Form B_ Follow-up Visit Record (Responses).xlsx")
path_c = os.path.join(BASE_DIR, "Form C_ Delivery Outcome Record (Responses).xlsx")

# Read files
df_a = pd.read_excel(path_a)
df_b = pd.read_excel(path_b)
df_c = pd.read_excel(path_c)

# Rename columns if they exist under updated names in the Excel sheets
if 'Column 1' in df_b.columns:
    df_b = df_b.rename(columns={'Column 1': 'MP ID'})

if 'HPLC test - SCD genotype confirmed' in df_a.columns:
    df_a = df_a.rename(columns={'HPLC test - SCD genotype confirmed': 'SCD genotype confirmed'})

if 'Name of facility where delivery occurred- (प्रसव होने वाले स्थान का विशिष्ट नाम)' in df_c.columns:
    df_c = df_c.rename(columns={
        'Name of facility where delivery occurred- (प्रसव होने वाले स्थान का विशिष्ट नाम)':
        'Specific facility name where delivery occurred- (प्रसव होने वाले स्थान का विशिष्ट नाम)'
    })

if 'OGTT blood sugar at Identification (mg/dL)- ( जांच के समय रक्त शर्करा का स्तर (मिलीग्राम/डीएल))' in df_a.columns:
    df_a = df_a.rename(columns={
        'OGTT blood sugar at Identification (mg/dL)- ( जांच के समय रक्त शर्करा का स्तर (मिलीग्राम/डीएल))':
        'Fasting blood sugar at Identification (mg/dL)- ( जांच के समय खाली पेट रक्त शर्करा का स्तर (मिलीग्राम/डीएल))'
    })

# Helper functions
def clean_str(val):
    if pd.isna(val):
        return ""
    return str(val).strip()

def clean_categorical(val):
    if pd.isna(val) or not val:
        return ""
    val_str = str(val).strip()
    # Strip bracketed Hindi translations repeating English information
    for sep in ['- (', '– (', '— (', '-(']:
        idx = val_str.find(sep)
        if idx != -1:
            if re.search(r'[\u0900-\u097F]', val_str[idx:]):
                cleaned = val_str[:idx].strip()
                cleaned = re.sub(r'[-–—\s]+$', '', cleaned).strip()
                if cleaned:
                    return cleaned
    m = re.search(r'\s*\([^\)]*[\u0900-\u097F]', val_str)
    if m:
        cleaned = val_str[:m.start()].strip()
        cleaned = re.sub(r'[-–—\s]+$', '', cleaned).strip()
        if cleaned:
            return cleaned
    return val_str

def clean_name(val):
    if pd.isna(val):
        return ""
    val = str(val).lower().strip()
    val = re.sub(r'\s+', ' ', val)
    return val

def normalize_mp_id(val):
    if pd.isna(val):
        return ""
    try:
        val_str = str(val).strip()
        if 'e' in val_str or 'E' in val_str or '.' in val_str:
            val_float = float(val_str)
            val_int = int(round(val_float))
            return str(val_int)
        if val_str.endswith('.0'):
            val_str = val_str[:-2]
        return val_str
    except Exception:
        return str(val).strip()

def clean_mobile(val):
    if pd.isna(val):
        return ""
    try:
        val_str = str(val).strip()
        if val_str.endswith('.0'):
            val_str = val_str[:-2]
        # Remove any non-digit characters like spaces, hyphens, plus signs
        val_str = re.sub(r'[^\d]', '', val_str)
        return val_str
    except Exception:
        return str(val).strip()

def clean_numeric(val):
    if pd.isna(val):
        return None
    val_str = str(val).strip()
    match = re.search(r'[-+]?\d*\.\d+|\d+', val_str)
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    return None

def clean_int(val):
    num = clean_numeric(val)
    if num is not None:
        return int(round(num))
    return None

# Add normalized columns
df_a['clean_mp_id'] = df_a['MP ID'].apply(normalize_mp_id)
df_b['clean_mp_id'] = df_b['MP ID'].apply(normalize_mp_id)
df_c['clean_mp_id'] = df_c['MP ID'].apply(normalize_mp_id)

df_a['clean_anc_name'] = df_a['ANC Name (गर्भवती महिला का नाम)'].apply(clean_name)
df_a['clean_husband_name'] = df_a['Husband Name (पति का नाम)'].apply(clean_name)

df_b['clean_anc_name'] = df_b['ANC Name (गर्भवती महिला का नाम)'].apply(clean_name)
df_b['clean_husband_name'] = df_b['Husband Name (पति का नाम)'].apply(clean_name)

import os

# Match ANC Linelist (12 Government ANC visits per woman)
anc_linelist_path = os.path.join(BASE_DIR, "ANC linelist", "ANC_Line_list_Report_2026-09-28_13_19_07.xlsx")
anc_visit_map_mp = {}
anc_visit_map_name = {}

if os.path.exists(anc_linelist_path):
    print("Processing ANC Linelist Excel...")
    df_anc = pd.read_excel(anc_linelist_path, header=8)
    mp_col = df_anc.columns[9]
    name_col = df_anc.columns[8]
    husb_col = df_anc.columns[10]
    
    df_anc['clean_mp_id'] = df_anc[mp_col].apply(normalize_mp_id)
    df_anc['clean_anc_name'] = df_anc[name_col].apply(clean_name)
    df_anc['clean_husband_name'] = df_anc[husb_col].apply(clean_name)

    anc_visit_offsets = [
        (20, 21, 24, 25, 26), (31, 32, 35, 36, 37), (42, 43, 46, 47, 48), (53, 54, 57, 58, 59),
        (64, 65, 68, 69, 70), (75, 76, 79, 80, 81), (86, 87, 90, 91, 92), (97, 98, 101, 102, 103),
        (108, 109, 112, 113, 114), (119, 120, 123, 124, 125), (130, 131, 134, 135, 136), (141, 142, 145, 146, 147)
    ]

    for idx, row in df_anc.iterrows():
        mp_id = row['clean_mp_id']
        c_name = row['clean_anc_name']
        c_husb = row['clean_husband_name']

        visits_for_mp = []
        for v_idx, (c_date, c_fac, c_wt, c_bp, c_hb) in enumerate(anc_visit_offsets, 1):
            if c_date >= len(row): continue
            v_date_val = row.iloc[c_date]
            if pd.isna(v_date_val) or not str(v_date_val).strip(): continue
            v_date_str = str(v_date_val)[:10].strip()
            v_fac = clean_str(row.iloc[c_fac]) if c_fac < len(row) else ""
            v_wt = clean_numeric(row.iloc[c_wt]) if c_wt < len(row) else None
            v_bp_str = clean_str(row.iloc[c_bp]) if c_bp < len(row) else ""
            v_hb = clean_numeric(row.iloc[c_hb]) if c_hb < len(row) else None
            visits_for_mp.append({
                "anc_num": v_idx,
                "date": v_date_str,
                "facility": v_fac,
                "weight": v_wt,
                "bp": v_bp_str,
                "hb": v_hb
            })
        if visits_for_mp:
            if mp_id and mp_id not in ['0', 'none', 'nan']:
                anc_visit_map_mp[mp_id] = visits_for_mp
            if c_name:
                key_name = f"{c_name}|{c_husb}"
                anc_visit_map_name[key_name] = visits_for_mp

# 1. Compile Patient Cases
cases = []
for idx, row_a in df_a.iterrows():
    hrp_str = clean_str(row_a['HRP categories Idenfied — tick ALL that apply'])
    hrp_list = [c.strip() for c in hrp_str.split(',') if c.strip()]
    if clean_str(row_a['Other HRP category (if not listed above)- (अन्य एचआरपी श्रेणी (यदि ऊपर सूचीबद्ध नहीं है)']):
        hrp_list.append(clean_str(row_a['Other HRP category (if not listed above)- (अन्य एचआरपी श्रेणी (यदि ऊपर सूचीबद्ध नहीं है)']))

    mp_id = row_a['clean_mp_id']
    c_name = clean_name(row_a['ANC Name (गर्भवती महिला का नाम)'])
    c_husb = clean_name(row_a['Husband Name (पति का नाम)'])
    
    anc_v = []
    if mp_id and mp_id in anc_visit_map_mp:
        anc_v = anc_visit_map_mp[mp_id]
    elif f"{c_name}|{c_husb}" in anc_visit_map_name:
        anc_v = anc_visit_map_name[f"{c_name}|{c_husb}"]
    elif c_name in anc_visit_map_name:
        anc_v = anc_visit_map_name[c_name]

    case = {
        "id_a": int(idx),
        "mp_id": row_a['clean_mp_id'],
        "name": clean_str(row_a['ANC Name (गर्भवती महिला का नाम)']),
        "husband_name": clean_str(row_a['Husband Name (पति का नाम)']),
        "age": clean_int(row_a['Age (years)']),
        "block": clean_str(row_a['Block']),
        "village": clean_str(row_a['Village / Gram Panchayat']),
        "mobile": clean_mobile(row_a['Mobile number (own or family contact)- (मोबाइल नंबर (अपना या परिवार का संपर्क नंबर)']),
        "asha": clean_str(row_a['ASHA name']),
        "anm": clean_str(row_a['ANM name']),
        "sub_centre": clean_str(row_a['Sub-centre']),
        "lmp": str(row_a['LMP (Last Menstrual Period)- (अंतिम मासिक धर्म अवधि (एलएमपी)'])[:10] if pd.notna(row_a['LMP (Last Menstrual Period)- (अंतिम मासिक धर्म अवधि (एलएमपी)']) else "",
        "edd": str(row_a['Expected Date of Delivery (EDD)'])[:10] if pd.notna(row_a['Expected Date of Delivery (EDD)']) else "",
        "enrollment_date": str(row_a['Timestamp'])[:10] if ('Timestamp' in row_a and pd.notna(row_a['Timestamp'])) else "",
        "timestamp": str(row_a['Timestamp'])[:19] if ('Timestamp' in row_a and pd.notna(row_a['Timestamp'])) else "",
        "gestational_age_enrollment": clean_str(row_a['Gestational age at Identification (weeks)- (पहचान के समय गर्भकालीन आयु ) (सप्ताह)']),
        "gravida_para": clean_str(row_a['Gravida / Para / Living children']),
        "prev_complications": clean_str(row_a['(प्रसव संबंधी पिछली जटिलताएं ( लागू विकल्पों पर निशान लगाएं)']),
        "planned_facility": clean_str(row_a['Planned facility for delivery- (प्रसव के लिए Plan facility का नाम)']),
        "distance": clean_str(row_a['Distance from home to nearest PHC/CHC (km)- ( घर से निकटतम प्राथमिक स्वास्थ्य केंद्र/ CHC की दूरी (किमी)']),
        "hrp_categories": hrp_list,
        "enrollment_hb": clean_numeric(row_a['Hb at  Identification   (g/dL)']),
        "enrollment_bp_sys": clean_numeric(row_a['Systolic BP at identification (mmHg)']),
        "enrollment_bp_dia": clean_numeric(row_a['Diastolic BP at Identification (mmHg)- (पहचान के समय डायस्टोलिक रक्तचाप)']),
        "enrollment_fbs": clean_numeric(row_a['Fasting blood sugar at Identification (mg/dL)- ( जांच के समय खाली पेट रक्त शर्करा का स्तर (मिलीग्राम/डीएल))']),
        "enrollment_urine_albumin": clean_str(row_a['Urine albumin at  Identification - ( पहचान के समय मूत्र एल्ब्यूमिन)']),
        "scd_genotype": clean_str(row_a['SCD genotype confirmed']),
        "blood_group": clean_str(row_a['Blood group and Rh type']),
        "other_history": clean_str(row_a['Any other relevant history at Identification - (पहचान के समय कोई अन्य संबंधित इतिहास)']),
        "anc_linelist_visits": anc_v,
        "visits": [],
        "delivery": None,
        "matched_via": None
    }
    cases.append(case)

# Match Form B (Follow-ups)
for idx, row_b in df_b.iterrows():
    mp_id_b = row_b['clean_mp_id']
    name_b = row_b['clean_anc_name']
    husband_b = row_b['clean_husband_name']
    
    match_case = None
    
    # Try ID match
    if mp_id_b:
        for case in cases:
            if case['mp_id'] == mp_id_b:
                match_case = case
                break
                
    # Try Name + Husband match
    if not match_case and name_b:
        for case in cases:
            if case['name'].lower().strip() == name_b:
                if not husband_b or not case['husband_name'] or case['husband_name'].lower().strip() == husband_b:
                    match_case = case
                    break
                    
    # Try fuzzy Name match
    if not match_case and name_b:
        if name_b == "nindra" and husband_b == "jaypal":
            for case in cases:
                if case['name'].lower().strip() == "nandra" and case['husband_name'].lower().strip() == "jaypal":
                    match_case = case
                    break
        elif name_b == "fareen":
            for case in cases:
                if case['name'].lower().strip() == "farin":
                    match_case = case
                    break

    if match_case:
        visit_data = {
            "id_b": int(idx),
            "date": str(row_b['Date of this visit'])[:10] if pd.notna(row_b['Date of this visit']) else "",
            "timestamp": str(row_b['Timestamp'])[:19] if ('Timestamp' in row_b and pd.notna(row_b['Timestamp'])) else "",
            "visit_number": clean_int(row_b['Visit number (in this pregnancy)']),
            "gestational_age": clean_int(row_b['Gestational age at this visit (weeks) - (इस जांच के समय गर्भकालीन आयु (सप्ताह में))']),
            "place": clean_str(row_b['Place of contact']),
            "conducted_by": clean_str(row_b['(इस Visit का संचालन करने वाले व्यक्ति का नाम )']),
            "bp_measured": clean_str(row_b['Blood pressure measured this visit - (इस बार मापा गया रक्तचाप)']),
            "weight": clean_numeric(row_b['Weight at this visit (kg) - (इस जांच के समय वजन (किलोग्राम में)']),
            "counselling": clean_str(row_b['Counselling provided — woman can describe her risk factor in own words - (परामर्श प्रदान किया गया — महिला अपने जोखिम कारकों का वर्णन स्वयं के शब्दों में कर सकती है)']),
            "birth_plan": clean_str(row_b['Birth plan discussed / updated this visit - (इस मुलाकात के दौरान जन्म योजना पर चर्चा/ Update किया गया)']),
            "bpcr_calendar": clean_str(row_b['BPCR Calander provided and explained - (बीपीसीआर कैलेंडर उपलब्ध कराया गया और समझाया गया)']),
            "agreed_designated_facility": clean_str(row_b['Women agreed to deliver in a designated facility? (क्या महिला तय की गई जगह पर डिलीवरी करवाने के लिए सहमत हुईं?)']),
            "hb": clean_numeric(row_b['Current Hb (g/dL)']),
            "hb_trend": clean_str(row_b['(पिछली मुलाकात की तुलना में हीमोग्लोबिन का रुझान)']),
            "anemia_status": clean_str(row_b['(इस जांच के दौरान स्थिति — गंभीर एनीमिया)']),
            "bp_systolic": clean_numeric(row_b['(आकलन: इस जांच के दौरान सिस्टोलिक रक्तचाप (mmHg में)']),
            "bp_diastolic": clean_numeric(row_b['(मूल्यांकन: इस जांच के दौरान डायस्टोलिक रक्तचाप (mmHg))']),
            "bp_trend": clean_str(row_b['(आकलन: पिछली जांच की तुलना में रक्तचाप का रुझान)']),
            "pih_status": clean_str(row_b['(इस दौरे के दौरान स्थिति — पीआईएच)']),
            "gdm_fbs": clean_numeric(row_b['(मूल्यांकन: इस मुलाकात के दौरान उपवास रक्त शर्करा का स्तर (मिलीग्राम/डेसीलीटर))']),
            "gdm_rbs": clean_numeric(row_b['(आकलन: यादृच्छिक / भोजन के बाद रक्त शर्करा का स्तर (मिलीग्राम/डेसीलीटर))']),
            "gdm_status": clean_str(row_b['(इस दौरे के दौरान स्थिति — जीडीएम)']),
            "scd_hb": clean_numeric(row_b['(आकलन: वर्तमान हीमोग्लोबिन (ग्राम/डेसीलीटर))']),
            "scd_status": clean_str(row_b['(इस दौरे के समय स्थिति — एससीडी)']),
            "prev_lscs_status": clean_str(row_b['STATUS at this visit — Previous LSCS']),
            "prev_stillbirth_status": clean_str(row_b['(इस मुलाकात के समय की स्थिति — पिछला मृत जन्म / नवजात शिशु मृत्यु)']),
            "teenage_status": clean_str(row_b['(इस मुलाकात के समय की स्थिति — किशोर गर्भावस्था)']),
            "overall_hrp_status": clean_str(row_b['(इस जांच के दौरान समग्र एचआरपी स्थिति (सभी सक्रिय स्थितियों में)']),
            "referral": clean_str(row_b['(क्या इस मुलाकात के दौरान किसी को रेफर किया गया था?)']),
            "next_visit_date": str(row_b['(अगली नियोजित संपर्क तिथि)'])[:10] if pd.notna(row_b['(अगली नियोजित संपर्क तिथि)']) else "",
            "med_adherence_general": clean_str(row_b['(उपचार: पिछले 30 दिनों में दवाओं का नियमित सेवन)']) if '(उपचार: पिछले 30 दिनों में दवाओं का नियमित सेवन)' in df_b.columns else "",
            "med_adherence_pih": clean_str(row_b['(उपचार: पिछले 30 दिनों में उच्च रक्तचाप रोधी दवा का नियमित सेवन)']) if '(उपचार: पिछले 30 दिनों में उच्च रक्तचाप रोधी दवा का नियमित सेवन)' in df_b.columns else "",
            "med_adherence_gdm": clean_str(row_b['(उपचार: पिछले 30 दिनों में दवा का नियमित सेवन)']) if '(उपचार: पिछले 30 दिनों में दवा का नियमित सेवन)' in df_b.columns else "",
            "blood_transfusion": clean_str(row_b['(उपचार: पिछली मुलाकात के बार से रक्त आधान किया गया है?)']) if '(उपचार: पिछली मुलाकात के बार से रक्त आधान किया गया है?)' in df_b.columns else ""
        }
        match_case['visits'].append(visit_data)

# Sort visits by date
for case in cases:
    case['visits'].sort(key=lambda x: x['date'])

from difflib import SequenceMatcher

def similarity(a, b):
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, str(a).lower().strip(), str(b).lower().strip()).ratio()

# Match Form C (Deliveries)
unlinked_deliveries = []
matched_c_count = 0

for idx, row_c in df_c.iterrows():
    mp_id_c = row_c['clean_mp_id']
    name_c = clean_name(row_c['ANC Name (गर्भवती महिला का नाम)']) if 'ANC Name (गर्भवती महिला का नाम)' in df_c.columns else ""
    husb_c = clean_name(row_c['Husband Name (पति का नाम)']) if 'Husband Name (पति का नाम)' in df_c.columns else ""
    
    match_case = None
    
    # Stage 1: Clean MP ID match
    if mp_id_c and mp_id_c not in ['0', 'no', 'none']:
        for case in cases:
            if case['mp_id'] == mp_id_c:
                match_case = case
                break
                
    # Stage 2: Exact Name & Husband Name match
    if not match_case and name_c:
        for case in cases:
            a_anc = clean_name(case['name'])
            a_husb = clean_name(case['husband_name'])
            if a_anc == name_c:
                if not husb_c or not a_husb or a_husb == husb_c or similarity(husb_c, a_husb) >= 0.65:
                    match_case = case
                    break
                    
    # Stage 3: Fuzzy Name & Husband Name similarity match
    if not match_case and name_c:
        best_score = 0
        best_case = None
        for case in cases:
            a_anc = clean_name(case['name'])
            a_husb = clean_name(case['husband_name'])
            name_sim = similarity(name_c, a_anc)
            husb_sim = similarity(husb_c, a_husb) if (husb_c and a_husb) else 0.8
            is_sub = (name_c in a_anc or a_anc in name_c) and len(name_c) >= 3
            husb_sub = (husb_c in a_husb or a_husb in husb_c) and len(husb_c) >= 3 if (husb_c and a_husb) else False
            
            if (name_sim >= 0.75 or is_sub) and (husb_sim >= 0.60 or husb_sub):
                comb_score = name_sim + husb_sim
                if comb_score > best_score:
                    best_score = comb_score
                    best_case = case
        if best_case:
            match_case = best_case

    # Helper for robust Form C column lookup
    def get_c_val(keywords, default=None):
        for col_name in row_c.index:
            col_str = str(col_name).lower()
            if all(k.lower() in col_str for k in keywords):
                return row_c.get(col_name)
        return default

    # Direct column extraction for Form C accounting for rearranged columns
    timestamp_c = str(row_c['Timestamp'])[:19] if ('Timestamp' in row_c and pd.notna(row_c['Timestamp'])) else ""
    del_date = str(row_c.get('Date of delivery', ''))[:10] if pd.notna(row_c.get('Date of delivery')) else ""
    gest_age = clean_int(get_c_val(['gestational age at delivery']))
    del_place = clean_categorical(clean_str(get_c_val(['place of delivery'])))
    del_type = clean_categorical(clean_str(get_c_val(['type of delivery'])))

    fac_name = clean_str(get_c_val(['name of facility where delivery occurred']) or get_c_val(['specific facility name']) or '')

    was_planned = clean_categorical(clean_str(get_c_val(['planned in form b']) or get_c_val(['was delivery at the facility planned']) or ''))
    unplanned_reason = clean_str(get_c_val(['if not at planned facility']) or get_c_val(['if not delivered at planned facility']) or '')

    total_anc = clean_int(get_c_val(['total anc visits']))

    # General clinical values recorded on admission
    hb_adm = clean_numeric(get_c_val(['hb on admission']))
    bp_measured_adm = clean_categorical(clean_str(get_c_val(['bp measured and recorded'])))
    bp_adm = clean_str(get_c_val(['bp on admission']))
    rbs_adm = clean_numeric(get_c_val(['rbs on admission']))

    # Condition-specific fields
    anemia_hb = clean_numeric(get_c_val(['hb at admission', 'anemia']))
    anemia_status = clean_categorical(clean_str(get_c_val(['status', 'anemia'])))

    pih_bp = clean_str(get_c_val(['bp at delivery', 'pih']))
    pih_status = clean_categorical(clean_str(get_c_val(['status', 'pih'])))
    mgso4_given = clean_categorical(clean_str(get_c_val(['mgso4'])))

    gdm_sugar = clean_numeric(get_c_val(['blood sugar at delivery', 'gdm']))
    gdm_status = clean_categorical(clean_str(get_c_val(['status', 'gdm'])))

    scd_hb = clean_numeric(get_c_val(['hb at delivery', 'scd']))
    scd_status = clean_categorical(clean_str(get_c_val(['status', 'scd'])))

    overall_hrp_status = clean_categorical(clean_str(get_c_val(['overall hrp status'])))

    partograph = clean_categorical(clean_str(get_c_val(['partograph'])))
    oxytocin = clean_categorical(clean_str(get_c_val(['oxytocin'])))
    companion = clean_categorical(clean_str(get_c_val(['companion'])))
    abuse_reported = clean_categorical(clean_str(get_c_val(['abuse']) or get_c_val(['disrespectful'])))

    baby_alive = clean_categorical(clean_str(get_c_val(['baby born alive'])))
    birth_weight = clean_numeric(get_c_val(['birth weight (grams)']))
    birth_weight_cat = clean_categorical(clean_str(get_c_val(['birth weight category'])))
    baby_cried = clean_categorical(clean_str(get_c_val(['baby cried'])))
    resuscitation = clean_categorical(clean_str(get_c_val(['resuscitation'])))
    baby_transferred = clean_categorical(clean_str(get_c_val(['transferred to sncu']) or get_c_val(['baby transferred'])))
    transfer_reason = clean_str(get_c_val(['reason for sncu']))
    sts_initiated = clean_categorical(clean_str(get_c_val(['skin-to-skin']) or get_c_val(['sts'])))
    breastfeeding = clean_categorical(clean_str(get_c_val(['breastfeeding'])))
    vit_k = clean_categorical(clean_str(get_c_val(['vitamin k'])))
    baby_glucose_checked = clean_categorical(clean_str(get_c_val(['blood glucose checked'])))

    # Qualitative explanation fields - preserve as clean_str (keeps Hindi notes intact!)
    gaps_concerns = clean_str(get_c_val(['gaps or concerns']))
    remarks = clean_str(get_c_val(['general remarks']))
    completed_by = clean_str(get_c_val(['person completing this form']))

    # Effective clinical parameters (seamless fallback to admission values)
    eff_hb = anemia_hb if anemia_hb is not None else (scd_hb if scd_hb is not None else hb_adm)
    eff_bp = pih_bp if (pih_bp and ('/' in pih_bp or any(ch.isdigit() for ch in pih_bp))) else bp_adm
    eff_sugar = gdm_sugar if gdm_sugar is not None else rbs_adm

    delivery_data = {
        "id_c": int(idx),
        "mp_id": mp_id_c,
        "delivery_date": del_date,
        "timestamp": timestamp_c,
        "gestational_age": gest_age,
        "place": del_place,
        "type": del_type,
        "facility_name": fac_name,
        "was_planned": was_planned,
        "unplanned_reason": unplanned_reason,
        "total_anc": total_anc,
        "hb": eff_hb,
        "hb_admission": hb_adm,
        "anemia_status": anemia_status,
        "bp": eff_bp,
        "bp_admission": bp_adm,
        "bp_measured_admission": bp_measured_adm,
        "pih_status": pih_status,
        "mgso4_given": mgso4_given,
        "blood_sugar": eff_sugar,
        "rbs_admission": rbs_adm,
        "gdm_status": gdm_status,
        "scd_hb": scd_hb,
        "scd_status": scd_status,
        "overall_hrp_status": overall_hrp_status,
        "partograph_plotted": partograph,
        "oxytocin_given": oxytocin,
        "birth_companion": companion,
        "respectful_care": abuse_reported,
        "baby_alive": baby_alive,
        "birth_weight": birth_weight,
        "birth_weight_category": birth_weight_cat,
        "baby_cried": baby_cried,
        "resuscitation_required": resuscitation,
        "baby_transferred": baby_transferred,
        "baby_transfer_reason": transfer_reason,
        "sts_initiated": sts_initiated,
        "breastfeeding_initiated": breastfeeding,
        "vit_k_given": vit_k,
        "baby_glucose_checked": baby_glucose_checked,
        "gaps_concerns": gaps_concerns,
        "remarks": remarks,
        "completed_by": completed_by
    }

    if match_case:
        match_case['delivery'] = delivery_data
        matched_c_count += 1
    else:
        unlinked_delivery = {
            "id_c": int(idx),
            "mp_id": mp_id_c,
            "name": clean_str(row_c['ANC Name (गर्भवती महिला का नाम)']) if 'ANC Name (गर्भवती महिला का नाम)' in df_c.columns else "",
            "husband_name": clean_str(row_c['Husband Name (पति का नाम)']) if 'Husband Name (पति का नाम)' in df_c.columns else "",
            "data": delivery_data
        }
        unlinked_deliveries.append(unlinked_delivery)

# 2. Detailed Trajectory Analysis (Enrollment -> Follow-up -> Delivery)
# We want to know:
# - How many improved from enrollment to follow-up?
# - How many improved from follow-up to delivery?
# - How many improved from enrollment to delivery?

linkage_improvements = {
    "enr_to_fup": { "improved": 0, "stable": 0, "worsened": 0, "total": 0, "details": [] },
    "fup_to_del": { "improved": 0, "stable": 0, "worsened": 0, "total": 0, "details": [] },
    "enr_to_del": { "improved": 0, "stable": 0, "worsened": 0, "total": 0, "details": [] }
}

for case in cases:
    # Trajectory 1: Enrollment to Follow-up
    # Require baseline clinical values and at least one follow-up visit with values
    if len(case['visits']) > 0:
        base_hb = case['enrollment_hb']
        # Find the last follow-up visit with an Hb value
        fup_hb = None
        for v in reversed(case['visits']):
            if v['hb'] is not None:
                fup_hb = v['hb']
                break
        
        if base_hb and fup_hb:
            diff = fup_hb - base_hb
            linkage_improvements["enr_to_fup"]["total"] += 1
            if diff >= 1.0:
                linkage_improvements["enr_to_fup"]["improved"] += 1
                status = "Improved"
            elif diff <= -1.0:
                linkage_improvements["enr_to_fup"]["worsened"] += 1
                status = "Worsened"
            else:
                linkage_improvements["enr_to_fup"]["stable"] += 1
                status = "Stable"
            
            linkage_improvements["enr_to_fup"]["details"].append({
                "name": case['name'],
                "base_hb": base_hb,
                "fup_hb": fup_hb,
                "diff": round(diff, 2),
                "status": status
            })

    # Trajectory 2: Follow-up to Delivery
    # Require at least one follow-up visit and a delivery record
    if len(case['visits']) > 0 and case['delivery']:
        del_data = case['delivery']
        del_hb = del_data['hb']
        
        # Get the last follow-up Hb
        fup_hb = None
        for v in reversed(case['visits']):
            if v['hb'] is not None:
                fup_hb = v['hb']
                break
                
        if fup_hb and del_hb:
            diff = del_hb - fup_hb
            linkage_improvements["fup_to_del"]["total"] += 1
            if diff >= 1.0:
                linkage_improvements["fup_to_del"]["improved"] += 1
                status = "Improved"
            elif diff <= -1.0:
                linkage_improvements["fup_to_del"]["worsened"] += 1
                status = "Worsened"
            else:
                linkage_improvements["fup_to_del"]["stable"] += 1
                status = "Stable"
                
            linkage_improvements["fup_to_del"]["details"].append({
                "name": case['name'],
                "fup_hb": fup_hb,
                "del_hb": del_hb,
                "diff": round(diff, 2),
                "status": status
            })

    # Trajectory 3: Enrollment to Delivery
    # Require baseline Hb and delivery Hb
    if case['delivery']:
        del_data = case['delivery']
        base_hb = case['enrollment_hb']
        del_hb = del_data['hb']
        
        if base_hb and del_hb:
            diff = del_hb - base_hb
            linkage_improvements["enr_to_del"]["total"] += 1
            if diff >= 1.0:
                linkage_improvements["enr_to_del"]["improved"] += 1
                status = "Improved"
            elif diff <= -1.0:
                linkage_improvements["enr_to_del"]["worsened"] += 1
                status = "Worsened"
            else:
                linkage_improvements["enr_to_del"]["stable"] += 1
                status = "Stable"
                
            linkage_improvements["enr_to_del"]["details"].append({
                "name": case['name'],
                "base_hb": base_hb,
                "del_hb": del_hb,
                "diff": round(diff, 2),
                "status": status
            })

# 3. Overall Case-by-Case trajectory compiling
# Add trajectory details to each case
for case in cases:
    # Add trajectory metrics
    if case['delivery']:
        del_data = case['delivery']
        improvement_status = "Unknown"
        improvement_details = []
        
        # Anemia Trajectory
        if any("anemia" in cat.lower() for cat in case['hrp_categories']):
            hb_start = case['enrollment_hb']
            hb_end = del_data.get('hb')
            if hb_start is not None and hb_end is not None:
                diff = hb_end - hb_start
                if diff >= 1.0:
                    improvement_details.append(f"Anemia improved: Hb increased by {diff:.1f} g/dL (from {hb_start} to {hb_end})")
                elif diff > 0:
                    improvement_details.append(f"Anemia stable: Hb increased by {diff:.1f} g/dL (from {hb_start} to {hb_end})")
                elif diff == 0:
                    improvement_details.append(f"Anemia stable: Hb unchanged at {hb_end} g/dL")
                else:
                    improvement_details.append(f"Anemia worsened: Hb decreased by {abs(diff):.1f} g/dL (from {hb_start} to {hb_end})")
            if del_data.get('anemia_status'):
                improvement_details.append(f"Anemia Status: {del_data['anemia_status']}")
        
        # PIH Trajectory
        if any("pih" in cat.lower() or "hypertension" in cat.lower() for cat in case['hrp_categories']):
            bp_start_sys = case['enrollment_bp_sys']
            bp_start_dia = case['enrollment_bp_dia']
            bp_end_str = del_data.get('bp')
            bp_end_sys, bp_end_dia = None, None
            if bp_end_str and '/' in bp_end_str:
                try:
                    parts = bp_end_str.split('/')
                    bp_end_sys = float(parts[0])
                    bp_end_dia = float(parts[1])
                except:
                    pass
            
            if bp_start_sys is not None and bp_end_sys is not None and bp_end_dia is not None:
                if bp_end_sys < 140 and bp_end_dia < 90:
                    improvement_details.append(f"PIH Controlled: BP normalized to {bp_end_str} (from {bp_start_sys}/{bp_start_dia})")
                else:
                    improvement_details.append(f"PIH High: BP remained high at {bp_end_str} (from {bp_start_sys}/{bp_start_dia})")
            if del_data.get('pih_status'):
                improvement_details.append(f"PIH Status: {del_data['pih_status']}")

        # SCD Trajectory
        if any("scd" in cat.lower() or "sickle" in cat.lower() for cat in case['hrp_categories']):
            scd_end = del_data.get('scd_hb') or del_data.get('hb')
            hb_start = case['enrollment_hb']
            if hb_start is not None and scd_end is not None:
                diff = scd_end - hb_start
                if diff >= 1.0:
                    improvement_details.append(f"SCD improved: Hb increased by {diff:.1f} g/dL (from {hb_start} to {scd_end})")
                elif diff > 0:
                    improvement_details.append(f"SCD stable: Hb increased by {diff:.1f} g/dL (from {hb_start} to {scd_end})")
                elif diff == 0:
                    improvement_details.append(f"SCD stable: Hb unchanged at {scd_end} g/dL")
                else:
                    improvement_details.append(f"SCD worsened: Hb decreased by {abs(diff):.1f} g/dL (from {hb_start} to {scd_end})")
            if del_data.get('scd_status'):
                improvement_details.append(f"SCD Status: {del_data['scd_status']}")

        # GDM Trajectory
        if any("gdm" in cat.lower() or "diabetes" in cat.lower() for cat in case['hrp_categories']):
            sugar_end = del_data.get('blood_sugar')
            sugar_start = case.get('enrollment_fbs')
            if sugar_start is not None and sugar_end is not None:
                if sugar_end < 140:
                    improvement_details.append(f"GDM Controlled: Blood sugar {sugar_end} mg/dL at delivery (from {sugar_start} mg/dL)")
                else:
                    improvement_details.append(f"GDM High: Blood sugar {sugar_end} mg/dL at delivery (from {sugar_start} mg/dL)")
            if del_data.get('gdm_status'):
                improvement_details.append(f"GDM Status: {del_data['gdm_status']}")

        # Other Risks (LSCS, Stillbirth, Teen, etc.)
        has_bio_risk = (
            any("anemia" in cat.lower() for cat in case['hrp_categories']) or
            any("scd" in cat.lower() or "sickle" in cat.lower() for cat in case['hrp_categories']) or
            any("pih" in cat.lower() or "hypertension" in cat.lower() for cat in case['hrp_categories']) or
            any("gdm" in cat.lower() or "diabetes" in cat.lower() for cat in case['hrp_categories'])
        )
        if not has_bio_risk:
            del_place = (del_data.get('place') or '').lower()
            del_fac = (del_data.get('facility_name') or '').lower()
            is_home = 'home' in del_place or 'home' in del_fac
            if is_home:
                improvement_details.append("Home Delivery (Unsafe)")
            else:
                fac_disp = del_data.get('facility_name') or del_data.get('place') or 'Facility'
                was_plan = 'yes' in (del_data.get('was_planned') or '').lower()
                improvement_details.append(f"Safe Institutional Delivery ({fac_disp}) - {'Planned Adherent' if was_plan else 'Facility Delivery'}")

        # Overall improvement classification
        is_worsened = False
        worsened_reasons = []
        anemia_st = (del_data['anemia_status'] or '').lower()
        pih_st = (del_data['pih_status'] or '').lower()
        scd_st = (del_data['scd_status'] or '').lower()
        overall_status_del = (del_data['overall_hrp_status'] or '').lower()
        del_hb = del_data['hb'] or del_data['scd_hb']
        base_hb = case['enrollment_hb']

        has_anemia_cat = any("anemia" in cat.lower() or "anaemia" in cat.lower() for cat in case['hrp_categories'])
        if has_anemia_cat:
            del_hb_val = del_data.get('hb')
            if del_hb_val is not None:
                if del_hb_val > 7.0:
                    improvement_details.append(f"Severe Anemia Resolved (Hb {del_hb_val} > 7.0 g/dL)")
                else:
                    is_worsened = True
                    worsened_reasons.append(f"Severe Anemia Unresolved (Hb {del_hb_val} < 7.0 g/dL)")
            elif 'not controlled' in anemia_st or 'no improvement' in anemia_st:
                is_worsened = True
                worsened_reasons.append("Severe Anemia Unresolved (Hb < 7.0 g/dL)")
            elif 'controlled' in anemia_st:
                improvement_details.append("Severe Anemia Resolved (Hb > 7.0 g/dL)")

        if 'not controlled' in pih_st:
            is_worsened = True
            worsened_reasons.append("PIH not controlled at delivery")
        if 'anaemic' in scd_st and (del_hb is not None and del_hb < 7.0):
            is_worsened = True
            worsened_reasons.append(f"SCD Anaemic at delivery (Hb {del_hb} g/dL)")
        if 'worsen' in overall_status_del or 'not controlled' in overall_status_del:
            is_worsened = True
            worsened_reasons.append("Overall condition worsened/uncontrolled")

        # Previous LSCS criteria: Emergency LSCS is unfavourable, Elective LSCS is favourable
        has_lscs = any("lscs" in cat.lower() or "cesarean" in cat.lower() for cat in case['hrp_categories'])
        del_type_str = (del_data.get('type') or '').lower()
        if has_lscs:
            if 'emergency' in del_type_str:
                is_worsened = True
                worsened_reasons.append("Emergency LSCS (unfavourable outcome)")
            elif 'elective' in del_type_str or 'planned' in del_type_str or 'normal' in del_type_str:
                improvement_details.append("Elective LSCS / Safe Delivery (favourable outcome)")

        # Teenage & Previous Stillbirth / Neonatal Death criteria: Planned FRU is favourable, other is unfavourable
        has_boh_or_teen = any("stillbirth" in cat.lower() or "neonatal" in cat.lower() or "death" in cat.lower() or "boh" in cat.lower() or "teen" in cat.lower() for cat in case['hrp_categories']) or (case.get('age') and case['age'] < 20)
        if has_boh_or_teen:
            del_p = (del_data.get('place') or '').lower()
            del_f = (del_data.get('facility_name') or '').lower()
            is_fru_fac = any(k in (del_p + ' ' + del_f) for k in ['dh', 'sdh', 'district', 'medical', 'private', 'hospital', 'gurjar', 'indore', 'khandwa'])
            was_pl = 'yes' in (del_data.get('was_planned') or '').lower()
            if is_fru_fac and was_pl:
                improvement_details.append(f"Planned FRU Delivery ({del_data.get('facility_name') or del_data.get('place')}) (favourable outcome)")
            else:
                is_worsened = True
                worsened_reasons.append(f"High-risk BOH/Teen delivered at non-FRU / unplanned facility ({del_data.get('facility_name') or del_data.get('place')}) (unfavourable outcome)")

        if is_worsened:
            improvement_status = "Worsened / Uncontrolled"
        elif "all conditions controlled" in overall_status_del or (
            ("controlled" in anemia_st or "stable" in scd_st or "controlled" in pih_st) and
            not ("some" in overall_status_del)
        ):
            improvement_status = "Controlled / Resolved"
        elif "some conditions controlled" in overall_status_del or any("improved" in det.lower() for det in improvement_details):
            improvement_status = "Partially Improved"
        else:
            improvement_status = "Controlled / Resolved"
            
        improvement_details.extend(worsened_reasons)
        case['improvement_status'] = improvement_status
        case['improvement_details'] = improvement_details

# 4. Statistical Aggregations for Deep Analysis
# Demographic details
age_bins = [0, 19, 24, 29, 34, 100]
age_labels = ["Under 20 (Teenage)", "20-24", "25-29", "30-34", "35+"]
df_a['age_group'] = pd.cut(df_a['Age (years)'], bins=age_bins, labels=age_labels)
age_dist = df_a['age_group'].value_counts().to_dict()

# Gestational age at identification
ga_dist = df_a['Gestational age at Identification (weeks)- (पहचान के समय गर्भकालीन आयु ) (सप्ताह)'].value_counts().to_dict()

# Distance to facility
dist_dist = df_a['Distance from home to nearest PHC/CHC (km)- ( घर से निकटतम प्राथमिक स्वास्थ्य केंद्र/ CHC की दूरी (किमी)'].value_counts().to_dict()

# Baseline Hb distribution
hb_bins = [0, 6.9, 9.9, 10.9, 100]
hb_labels = ["Severe Anemia (<7.0)", "Moderate Anemia (7.0-9.9)", "Mild Anemia (10.0-10.9)", "Normal (>=11.0)"]
df_a['hb_num'] = df_a['Hb at  Identification   (g/dL)'].apply(clean_numeric)
df_a['hb_group'] = pd.cut(df_a['hb_num'], bins=hb_bins, labels=hb_labels)
hb_dist = df_a['hb_group'].value_counts().to_dict()

# Baseline BP distribution
def classify_bp(row):
    sys = clean_numeric(row['Systolic BP at identification (mmHg)'])
    dia = clean_numeric(row['Diastolic BP at Identification (mmHg)- (पहचान के समय डायस्टोलिक रक्तचाप)'])
    if pd.isna(sys) or pd.isna(dia):
        return None
    if sys < 120 and dia < 80:
        return "Normal (<120/80)"
    elif sys < 130 and dia < 80:
        return "Elevated (120-129/<80)"
    elif sys < 140 or dia < 90:
        return "Stage 1 Hypertension (130-139/80-89)"
    elif sys < 160 or dia < 110:
        return "Stage 2 Hypertension (140-159/90-109)"
    else:
        return "Severe Hypertensive Crisis (>=160/110)"

df_a['bp_group'] = df_a.apply(classify_bp, axis=1)
bp_dist = df_a['bp_group'].value_counts().to_dict()

# 5. Dynamic Python Thematic Analysis on Qualitative Remarks
qualitative_themes = {
    "refusal_social": {
        "title": "Refusal, Health Beliefs & Social Barriers",
        "icon": "🗣️",
        "color": "amber",
        "keywords": ["refuse", "unwilling", "home", "mother-in-law", "fear", "husband", "manaa", "samjha", "parivar", "family", "tradition"],
        "quotes": []
    },
    "transport_delays": {
        "title": "Decision & Transport Delays (Delay 1 & 2)",
        "icon": "🚨",
        "color": "rose",
        "keywords": ["vehicle", "auto", "transport", "late", "delay", "night", "janani", "gadi", "rasta", "far", "wait", "morning", "distance", "km"],
        "quotes": []
    },
    "supply_gaps": {
        "title": "Facility Infrastructure & Medical Supply Gaps",
        "icon": "📦",
        "color": "blue",
        "keywords": ["supply", "stock", "blood", "transfusion", "unit", "kit", "calendar", "bpcr", "ifa", "calcium", "medicine", "tablet", "lack", "not available", "shortage"],
        "quotes": []
    },
    "complications_referrals": {
        "title": "Severe Clinical Complication & Facility Referrals",
        "icon": "🏥",
        "color": "teal",
        "keywords": ["refer", "dh", "chc", "sncu", "icu", "nrc", "fits", "bp", "hb", "crisis", "pain", "bleed", "lscs", "c-section", "weight", "asphyxia", "cried", "stillbirth", "death", "transferred"],
        "quotes": []
    }
}

text_cols_a = [c for c in df_a.columns if any(k in c.lower() for k in ['history', 'other', 'complication'])]
text_cols_b = [c for c in df_b.columns if any(k in c.lower() for k in ['remark', 'refer', 'gap', 'observation', 'concern'])]
text_cols_c = [c for c in df_c.columns if any(k in c.lower() for k in ['gap', 'concern', 'reason', 'remark'])]

seen_quotes = set()
for df, cols in [(df_a, text_cols_a), (df_b, text_cols_b), (df_c, text_cols_c)]:
    for col in cols:
        for val in df[col].dropna():
            text = str(val).strip()
            if text and text.lower() not in ['no', 'nil', 'n/a', 'none', 'nan', '0', '-'] and text not in seen_quotes:
                seen_quotes.add(text)
                text_lower = text.lower()
                matched = False
                for theme_key, theme_info in qualitative_themes.items():
                    if any(kw in text_lower for kw in theme_info["keywords"]):
                        theme_info["quotes"].append(text)
                        matched = True
                        break
                if not matched:
                    qualitative_themes["complications_referrals"]["quotes"].append(text)

# Compiling all analysis statistics
analysis_stats = {
    "age_distribution": age_dist,
    "gestational_age_identification": ga_dist,
    "distance_distribution": dist_dist,
    "baseline_hb_distribution": hb_dist,
    "baseline_bp_distribution": bp_dist,
    "linkage_improvements": linkage_improvements
}

# Compile final output
output_data = {
    "evaluation_date": datetime.today().strftime('%Y-%m-%d'),
    "generated_date": datetime.today().strftime('%d-%m-%Y'),
    "stats": {
        "total_enrolled": len([c for c in cases if c['id_a'] != 9999]),
        "total_follow_ups": len(df_b),
        "total_deliveries": len(df_c),
        "matched_follow_ups": len([c for c in cases if len(c['visits']) > 0]),
        "matched_deliveries": matched_c_count,
        "block_distribution": df_a['Block'].value_counts().to_dict(),
        "hrp_distribution": {},
        "delivery_places": df_c['Place of delivery-(डिलिवरी का स्थान)'].value_counts().to_dict(),
        "delivery_types": df_c['Type of delivery- (डिलिवरी का स्थान)'].value_counts().to_dict(),
        "baby_outcomes": df_c['Baby born alive?- (बच्चा जीवित पैदा हुआ?)'].value_counts().to_dict(),
        "birth_weight_categories": df_c['Birth weight category- (जन्म भार वर्ग)'].value_counts().to_dict()
    },
    "cases": cases,
    "unlinked_deliveries": unlinked_deliveries,
    "analysis_stats": analysis_stats,
    "qualitative_themes": qualitative_themes
}

# HRP Category distribution
for case in cases:
    for cat in case['hrp_categories']:
        output_data['stats']['hrp_distribution'][cat] = output_data['stats']['hrp_distribution'].get(cat, 0) + 1

# Write JS to file
js_output_path = os.path.join(BASE_DIR, "dashboard_data.js")
with open(js_output_path, 'w', encoding='utf-8') as f:
    f.write("const dashboardData = ")
    json.dump(output_data, f, indent=2, ensure_ascii=False)
    f.write(";")

# Write JSON to file
json_output_path = os.path.join(BASE_DIR, "dashboard_data.json")
with open(json_output_path, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"Successfully generated analysis data! Saved to {js_output_path} and {json_output_path}")

# Generate self-contained shareable HTML dashboards
dashboards_to_update = [
    {
        "name": "index.html",
        "local_path": os.path.join(BASE_DIR, "index.html"),
        "artifact_path": "c:/Users/User/.gemini/antigravity/brain/a880b367-e099-452a-abcc-3d5ab1953c67/index.html"
    },
    {
        "name": "artifact UHRP Tracking Dashboard.html",
        "local_path": os.path.join(BASE_DIR, "index.html"),
        "artifact_path": "c:/Users/User/.gemini/antigravity/brain/a880b367-e099-452a-abcc-3d5ab1953c67/UHRP Tracking Dashboard.html"
    }
]

js_data = "const dashboardData = " + json.dumps(output_data, indent=2, ensure_ascii=False) + ";"
inlined_script = f"<script>\n{js_data}\n</script>"

for db in dashboards_to_update:
    try:
        if not os.path.exists(db["local_path"]):
            print(f"Warning: Dashboard file {db['local_path']} not found!")
            continue
            
        with open(db["local_path"], 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Replace either external script reference or existing inlined script block
        if '<script src="dashboard_data.js"></script>' in html_content:
            shareable_html = html_content.replace('<script src="dashboard_data.js"></script>', inlined_script)
        else:
            shareable_html = re.sub(
                r'<script>\s*const dashboardData\s*=\s*.*?</script>',
                lambda m: inlined_script,
                html_content,
                flags=re.DOTALL
            )
        
        with open(db["local_path"], 'w', encoding='utf-8') as f:
            f.write(shareable_html)
            
        if os.path.exists(os.path.dirname(db["artifact_path"])):
            with open(db["artifact_path"], 'w', encoding='utf-8') as f:
                f.write(shareable_html)
                
        print(f"Successfully generated shareable single-file dashboard! Saved to {db['local_path']}")
    except Exception as e:
        print(f"Error generating dashboard {db['name']}: {e}")

# -------------------------------------------------------------
# Automatic Git Stage, Commit & Push to GitHub
# -------------------------------------------------------------
import subprocess

def auto_push_to_github():
    print("\n---------------------------------------------------")
    print("  Syncing updated project files with GitHub...")
    print("---------------------------------------------------")
    try:
        # Stage all changes in project directory
        add_res = subprocess.run(
            ["git", "add", "-A"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )
        if add_res.returncode != 0 and add_res.stderr:
            print(f"Git add note: {add_res.stderr.strip()}")
            
        # Check if there are staged changes
        staged_check = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )
        
        if not staged_check.stdout.strip():
            print("Git working tree is already up-to-date; no new changes to commit.")
            return

        timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        commit_msg = f"Auto-update UHRP dashboard data [{timestamp_str}]"
        
        commit_res = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )
        if commit_res.returncode == 0:
            print(f"Committed changes: \"{commit_msg}\"")
        else:
            print(f"Git commit output: {commit_res.stdout.strip() or commit_res.stderr.strip()}")

        # Push to remote repository (origin main)
        print("Pushing commits to GitHub (origin main)...")
        push_res = subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )
        if push_res.returncode == 0:
            print("SUCCESS: Successfully pushed updated project files to GitHub!")
        else:
            # Fallback plain git push if origin main had a tracking variation
            push_fallback = subprocess.run(
                ["git", "push"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True
            )
            if push_fallback.returncode == 0:
                print("SUCCESS: Successfully pushed updated project files to GitHub!")
            else:
                err_msg = push_res.stderr.strip() or push_fallback.stderr.strip()
                print(f"Git push notice: {err_msg}")

    except Exception as e:
        print(f"Notice: Automatic GitHub sync encountered an issue: {e}")

auto_push_to_github()
