import re

filepath = "generate_analysis_data.py"

with open(filepath, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Add is_valid_mp and similarity after normalize_mp_id
p1_old = """def normalize_mp_id(val):
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
        return str(val).strip()"""

p1_new = """def normalize_mp_id(val):
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

def is_valid_mp(mp):
    if not mp or pd.isna(mp):
        return False
    v = str(mp).strip().replace('.0', '').lower()
    if v in ['', '0', 'nan', 'none', 'no', 'null']:
        return False
    if v.replace('0', '') == '':
        return False  # all zeroes like 00000000000
    if len(v) < 6:
        return False
    return True

from difflib import SequenceMatcher

def similarity(a, b):
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, str(a).lower().strip(), str(b).lower().strip()).ratio()"""

# Normalize CRLF for replacement matching
code_norm = code.replace('\r\n', '\n')
p1_old_norm = p1_old.replace('\r\n', '\n')
assert p1_old_norm in code_norm, "Pattern 1 not found"
code_norm = code_norm.replace(p1_old_norm, p1_new.replace('\r\n', '\n'), 1)

# 2. Form B matching & visit_data columns
p2_old = """# Match Form B (Follow-ups)
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
        match_case['visits'].append(visit_data)"""

p2_new = """# Match Form B (Follow-ups)
for idx, row_b in df_b.iterrows():
    mp_id_b = row_b['clean_mp_id']
    name_b = row_b['clean_anc_name']
    husband_b = row_b['clean_husband_name']
    
    match_case = None
    
    # Try ID match (valid MP ID only)
    if is_valid_mp(mp_id_b):
        for case in cases:
            if is_valid_mp(case['mp_id']) and case['mp_id'] == mp_id_b:
                match_case = case
                break
                
    # Try Name + Husband match
    if not match_case and name_b:
        for case in cases:
            a_anc = clean_name(case['name'])
            a_husb = clean_name(case['husband_name'])
            if a_anc == name_b:
                if not husband_b or not a_husb or a_husb == husband_b or similarity(husband_b, a_husb) >= 0.65:
                    match_case = case
                    break
                    
    # Try fuzzy Name match
    if not match_case and name_b:
        best_score = 0
        best_case = None
        for case in cases:
            a_anc = clean_name(case['name'])
            a_husb = clean_name(case['husband_name'])
            ns = similarity(name_b, a_anc)
            hs = similarity(husband_b, a_husb) if (husband_b and a_husb) else 0.5
            is_sub = (name_b in a_anc or a_anc in name_b) and len(name_b) >= 4
            husb_sub = (husband_b in a_husb or a_husb in husband_b) and len(husband_b) >= 3 if (husband_b and a_husb) else False
            if (ns >= 0.75 or is_sub) and (hs >= 0.65 or husb_sub):
                if ns + hs > best_score:
                    best_score = ns + hs
                    best_case = case
        if best_case and best_score >= 1.4:
            match_case = best_case

    # Specific known spelling variations
    if not match_case and name_b:
        if name_b in ["nindra", "nandra"] and husband_b == "jaypal":
            for case in cases:
                if case['name'].lower().strip() in ["nandra", "nindra"] and case['husband_name'].lower().strip() == "jaypal":
                    match_case = case
                    break
        elif name_b in ["fareen", "farin"]:
            for case in cases:
                if case['name'].lower().strip() in ["fareen", "farin"]:
                    match_case = case
                    break
        elif "anjali" in name_b and "ganesh" in husband_b:
            for case in cases:
                if "anjali" in case['name'].lower() and "ganesh" in case['husband_name'].lower():
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
            "anemia_status": clean_str(row_b.iloc[26]) if len(row_b) > 26 else "",
            "anemia_action": clean_str(row_b.iloc[27]) if len(row_b) > 27 else "",
            "bp_systolic": clean_numeric(row_b['(आकलन: इस जांच के दौरान सिस्टोलिक रक्तचाप (mmHg में)']),
            "bp_diastolic": clean_numeric(row_b['(मूल्यांकन: इस जांच के दौरान डायस्टोलिक रक्तचाप (mmHg))']),
            "bp_trend": clean_str(row_b['(आकलन: पिछली जांच की तुलना में रक्तचाप का रुझान)']),
            "pih_status": clean_str(row_b.iloc[40]) if len(row_b) > 40 else "",
            "pih_action": clean_str(row_b.iloc[41]) if len(row_b) > 41 else "",
            "gdm_fbs": clean_numeric(row_b['(मूल्यांकन: इस मुलाकात के दौरान उपवास रक्त शर्करा का स्तर (मिलीग्राम/डेसीलीटर))']),
            "gdm_rbs": clean_numeric(row_b['(आकलन: यादृच्छिक / भोजन के बाद रक्त शर्करा का स्तर (मिलीग्राम/डेसीलीटर))']),
            "gdm_status": clean_str(row_b.iloc[51]) if len(row_b) > 51 else "",
            "gdm_action": clean_str(row_b.iloc[52]) if len(row_b) > 52 else "",
            "scd_hb": clean_numeric(row_b['(आकलन: वर्तमान हीमोग्लोबिन (ग्राम/डेसीलीटर))']),
            "scd_status": clean_str(row_b.iloc[61]) if len(row_b) > 61 else "",
            "scd_action": clean_str(row_b.iloc[62]) if len(row_b) > 62 else "",
            "prev_lscs_status": clean_str(row_b.iloc[71]) if len(row_b) > 71 else "",
            "prev_lscs_remarks": clean_str(row_b.iloc[72]) if len(row_b) > 72 else "",
            "prev_stillbirth_status": clean_str(row_b.iloc[81]) if len(row_b) > 81 else "",
            "prev_stillbirth_remarks": clean_str(row_b.iloc[82]) if len(row_b) > 82 else "",
            "teenage_status": clean_str(row_b.iloc[93]) if len(row_b) > 93 else "",
            "teenage_remarks": clean_str(row_b.iloc[94]) if len(row_b) > 94 else "",
            "overall_hrp_status": clean_str(row_b['(इस जांच के दौरान समग्र एचआरपी स्थिति (सभी सक्रिय स्थितियों में)']),
            "referral": clean_str(row_b['(क्या इस मुलाकात के दौरान किसी को रेफर किया गया था?)']),
            "next_visit_date": str(row_b['(अगली नियोजित संपर्क तिथि)'])[:10] if pd.notna(row_b['(अगली नियोजित संपर्क तिथि)']) else "",
            "med_adherence_general": clean_str(row_b['(उपचार: पिछले 30 दिनों में दवाओं का नियमित सेवन)']) if '(उपचार: पिछले 30 दिनों में दवाओं का नियमित सेवन)' in df_b.columns else "",
            "med_adherence_pih": clean_str(row_b['(उपचार: पिछले 30 दिनों में उच्च रक्तचाप रोधी दवा का नियमित सेवन)']) if '(उपचार: पिछले 30 दिनों में उच्च रक्तचाप रोधी दवा का नियमित सेवन)' in df_b.columns else "",
            "med_adherence_gdm": clean_str(row_b['(उपचार: पिछले 30 दिनों में दवा का नियमित सेवन)']) if '(उपचार: पिछले 30 दिनों में दवा का नियमित सेवन)' in df_b.columns else "",
            "blood_transfusion": clean_str(row_b['(उपचार: पिछली मुलाकात के बार से रक्त आधान किया गया है?)']) if '(उपचार: पिछली मुलाकात के बार से रक्त आधान किया गया है?)' in df_b.columns else ""
        }
        match_case['visits'].append(visit_data)"""

p2_old_norm = p2_old.replace('\r\n', '\n')
assert p2_old_norm in code_norm, "Pattern 2 not found"
code_norm = code_norm.replace(p2_old_norm, p2_new.replace('\r\n', '\n'), 1)

# 3. Form C matching and unlinked delivery handling
p3_old = """# Match Form C (Deliveries)
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
            match_case = best_case"""

p3_new = """# Match Form C (Deliveries)
unlinked_deliveries = []
matched_c_count = 0

for idx, row_c in df_c.iterrows():
    mp_id_c = row_c['clean_mp_id']
    name_c = clean_name(row_c['ANC Name (गर्भवती महिला का नाम)']) if 'ANC Name (गर्भवती महिला का नाम)' in df_c.columns else ""
    husb_c = clean_name(row_c['Husband Name (पति का नाम)']) if 'Husband Name (पति का नाम)' in df_c.columns else ""
    
    match_case = None
    
    # Stage 1: Valid MP ID match (reject dummy zeroes and only match cases without a delivery already)
    if is_valid_mp(mp_id_c):
        for case in cases:
            if is_valid_mp(case['mp_id']) and case['mp_id'] == mp_id_c and case['delivery'] is None:
                match_case = case
                break
                
    # Stage 2: Exact Name & Husband Name match
    if not match_case and name_c:
        for case in cases:
            if case['delivery'] is not None:
                continue
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
            if case['delivery'] is not None:
                continue
            a_anc = clean_name(case['name'])
            a_husb = clean_name(case['husband_name'])
            name_sim = similarity(name_c, a_anc)
            husb_sim = similarity(husb_c, a_husb) if (husb_c and a_husb) else (0.8 if name_sim >= 0.9 else 0.0)
            is_sub = (name_c in a_anc or a_anc in name_c) and len(name_c) >= 4
            husb_sub = (husb_c in a_husb or a_husb in husb_c) and len(husb_c) >= 3 if (husb_c and a_husb) else False
            
            if (name_sim >= 0.80 or is_sub) and (husb_sim >= 0.60 or husb_sub):
                comb_score = name_sim + husb_sim
                if comb_score > best_score:
                    best_score = comb_score
                    best_case = case
        if best_case and best_score >= 1.4:
            match_case = best_case"""

p3_old_norm = p3_old.replace('\r\n', '\n')
assert p3_old_norm in code_norm, "Pattern 3 not found"
code_norm = code_norm.replace(p3_old_norm, p3_new.replace('\r\n', '\n'), 1)

# 4. Handle unlinked delivery insertion so all 77 deliveries are in cases
p4_old = """    if match_case:
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
        unlinked_deliveries.append(unlinked_delivery)"""

p4_new = """    if match_case:
        match_case['delivery'] = delivery_data
        matched_c_count += 1
    else:
        # Create unlinked delivery case in cases array so all 77 deliveries are included in cases
        inferred_cats = []
        if anemia_status or (eff_hb is not None and eff_hb < 7.0):
            inferred_cats.append("Severe Anemia")
        if pih_status or mgso4_given == 'Yes' or (eff_bp and any(x in str(eff_bp) for x in ['140', '150', '160', '170'])):
            inferred_cats.append("PIH / Gestational Hypertension")
        if gdm_status:
            inferred_cats.append("GDM")
        if scd_status or scd_hb is not None:
            inferred_cats.append("Sickle Cell Disease")
        if del_type and 'cesarean' in str(del_type).lower():
            inferred_cats.append("Previous LSCS")
        if not inferred_cats:
            inferred_cats.append("High Risk Pregnancy (Delivery)")
            
        unlinked_case = {
            "id_a": 1000 + int(idx),
            "mp_id": mp_id_c if is_valid_mp(mp_id_c) else f"C-{idx+1:02d}",
            "name": clean_str(row_c.get('ANC Name (गर्भवती महिला का नाम)')) or f"Delivery Record #{idx+1}",
            "husband_name": clean_str(row_c.get('Husband Name (पति का नाम)')) or "-",
            "age": clean_int(get_c_val(['age'])),
            "block": clean_str(row_c.get('Block')) or clean_str(get_c_val(['block'])) or "Unknown",
            "village": clean_str(row_c.get('Village / Gram Panchayat')) or clean_str(get_c_val(['village'])) or "Unknown",
            "mobile": clean_mobile(row_c.get('Mobile number')) if 'Mobile number' in row_c else "",
            "asha": clean_str(row_c.get('ASHA name')) or "",
            "anm": clean_str(row_c.get('ANM name')) or "",
            "sub_centre": clean_str(row_c.get('Sub-centre')) or "",
            "lmp": "",
            "edd": "",
            "enrollment_date": del_date,
            "timestamp": timestamp_c,
            "gestational_age_enrollment": gest_age,
            "gravida_para": "",
            "prev_complications": "",
            "planned_facility": fac_name,
            "distance": "",
            "hrp_categories": inferred_cats,
            "enrollment_hb": hb_adm,
            "enrollment_bp_sys": None,
            "enrollment_bp_dia": None,
            "enrollment_fbs": rbs_adm,
            "enrollment_urine_albumin": "",
            "scd_genotype": "",
            "blood_group": "",
            "other_history": "",
            "anc_linelist_visits": [],
            "visits": [],
            "delivery": delivery_data,
            "matched_via": "Unlinked / Direct Delivery Record",
            "is_unlinked_delivery": True
        }
        cases.append(unlinked_case)
        unlinked_deliveries.append({
            "id_c": int(idx),
            "mp_id": mp_id_c,
            "name": clean_str(row_c.get('ANC Name (गर्भवती महिला का नाम)')) or f"Delivery Record #{idx+1}",
            "husband_name": clean_str(row_c.get('Husband Name (पति का नाम)')) or "-",
            "data": delivery_data
        })"""

p4_old_norm = p4_old.replace('\r\n', '\n')
assert p4_old_norm in code_norm, "Pattern 4 not found"
code_norm = code_norm.replace(p4_old_norm, p4_new.replace('\r\n', '\n'), 1)

# Write back
with open(filepath, "w", encoding="utf-8") as f:
    f.write(code_norm)

print("Successfully updated generate_analysis_data.py!")
