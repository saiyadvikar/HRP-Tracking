import sys

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update tab navigation
old_tab = """  <button class="tab" onclick="show('adherence',this)">💊 Treatment Adherence</button>"""
new_tab = """  <button class="tab" onclick="show('adherence',this)">💊 Treatment Adherence</button>
  <button class="tab" onclick="show('cond-actions',this)">🩺 Risk Follow-up & Actions</button>"""

assert old_tab in html, "Tab button pattern not found"
html = html.replace(old_tab, new_tab, 1)

# 2. Insert the new panel before Intrapartum & Delivery
panel_insert_marker = "<!-- ═══════════════════ INTRAPARTUM & DELIVERY ═══════════════════ -->"

new_panel_html = """<!-- ═══════════════════ RISK FOLLOW-UP & ACTIONS ═══════════════════ -->
<div id="p-cond-actions" class="panel">
  <div class="alert a-t" style="margin-bottom:14px">
    🩺 <strong>High-Risk Clinical Follow-up &amp; Actions Taken:</strong> Clinical condition trajectory and field interventions mobilised during Form B follow-up visits. <br>
    <strong>Verification Protocol:</strong> Only visits of mothers enrolled with the corresponding high-risk condition (Form A <code>hrp_categories</code>) are analyzed in each condition denominator and clinical breakdown.
  </div>

  <!-- Condition Filter Navigation Pills -->
  <div class="card" style="margin-bottom:16px; padding:14px 18px; background:#F8FAFC">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px">
      <div style="display:flex; align-items:center; gap:8px">
        <span style="font-size:13px; font-weight:700; color:var(--text-h)">Select High-Risk Factor:</span>
      </div>
      <div style="display:flex; gap:6px; flex-wrap:wrap" id="ca-condition-pills">
        <button class="pill p-t" id="ca-btn-ALL" onclick="setConditionActionsFilter('ALL')" style="cursor:pointer; border:none; font-weight:700">All Risk Factors</button>
        <button class="pill p-gy" id="ca-btn-SCD" onclick="setConditionActionsFilter('SCD')" style="cursor:pointer; border:none">Sickle Cell Disease (SCD)</button>
        <button class="pill p-gy" id="ca-btn-ANEMIA" onclick="setConditionActionsFilter('ANEMIA')" style="cursor:pointer; border:none">Severe Anemia</button>
        <button class="pill p-gy" id="ca-btn-PIH" onclick="setConditionActionsFilter('PIH')" style="cursor:pointer; border:none">PIH / Hypertension</button>
        <button class="pill p-gy" id="ca-btn-GDM" onclick="setConditionActionsFilter('GDM')" style="cursor:pointer; border:none">GDM (Diabetes)</button>
        <button class="pill p-gy" id="ca-btn-LSCS" onclick="setConditionActionsFilter('LSCS')" style="cursor:pointer; border:none">Previous LSCS</button>
        <button class="pill p-gy" id="ca-btn-BOH" onclick="setConditionActionsFilter('BOH')" style="cursor:pointer; border:none">Prev Stillbirth / NND</button>
        <button class="pill p-gy" id="ca-btn-TEEN" onclick="setConditionActionsFilter('TEEN')" style="cursor:pointer; border:none">Teenage Pregnancy</button>
      </div>
    </div>
  </div>

  <!-- Dynamic KPI Summary Cards -->
  <div class="g4" style="margin-bottom:18px">
    <div class="kpi" style="border-top-color:var(--teal)">
      <div class="kl" id="ca-kpi-lbl-enrolled">Verified Mothers</div>
      <div class="kv" id="ca-kpi-enrolled" style="color:var(--teal)">0</div>
      <div class="ks" id="ca-kpi-sub-enrolled">Enrolled with this condition</div>
    </div>
    <div class="kpi" style="border-top-color:var(--blue)">
      <div class="kl" id="ca-kpi-lbl-visits">Verified Visits</div>
      <div class="kv" id="ca-kpi-visits" style="color:var(--blue)">0</div>
      <div class="ks" id="ca-kpi-sub-visits">Form B visits conducted</div>
    </div>
    <div class="kpi" style="border-top-color:var(--green)">
      <div class="kl">Stable / Controlled / On Track</div>
      <div class="kv" id="ca-kpi-controlled" style="color:var(--green)">0 (0%)</div>
      <div class="ks" id="ca-kpi-sub-controlled">Clinically safe status</div>
    </div>
    <div class="kpi" style="border-top-color:var(--red)">
      <div class="kl">Crisis / Uncontrolled / Concerns</div>
      <div class="kv" id="ca-kpi-uncontrolled" style="color:var(--red)">0 (0%)</div>
      <div class="ks" id="ca-kpi-sub-uncontrolled">Active concerns / crisis</div>
    </div>
  </div>

  <!-- Dual Visualizations (Condition Status Donut + Clinical Actions Bar) -->
  <div class="g2" style="margin-bottom:18px; display:grid; grid-template-columns:1fr 1.25fr; gap:16px">
    <!-- Condition Status Donut Chart -->
    <div class="card">
      <div class="ch">
        <span>🩺</span>
        <span class="ct" id="ca-chart-status-title">Condition Status Distribution</span>
      </div>
      <div class="cb" style="position:relative; height:320px; display:flex; flex-direction:column; align-items:center; justify-content:center">
        <canvas id="ca-status-donut-chart" style="max-height:280px; width:100%"></canvas>
      </div>
    </div>

    <!-- Clinical Actions Bar Chart -->
    <div class="card">
      <div class="ch">
        <span>⚡</span>
        <span class="ct" id="ca-chart-actions-title">Clinical Actions Mobilized / Planned</span>
      </div>
      <div class="cb" style="position:relative; height:320px; display:flex; flex-direction:column; align-items:center; justify-content:center">
        <canvas id="ca-actions-bar-chart" style="max-height:280px; width:100%"></canvas>
      </div>
    </div>
  </div>

  <!-- Verified Cases Follow-up Linelist -->
  <div class="card">
    <div class="ch" style="flex-wrap:wrap; gap:12px; justify-content:space-between">
      <div style="display:flex; align-items:center; gap:8px">
        <span>📋</span>
        <span class="ct" id="ca-table-title">Verified Risk Follow-up &amp; Action Register</span>
        <span class="chip" id="ca-record-badge" style="background:var(--teal); color:#fff; font-size:11px; padding:2px 8px; border-radius:12px">0 records</span>
      </div>
      <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap">
        <input type="text" id="ca-search-box" placeholder="🔍 Search Mother, Village, Block..." oninput="onConditionActionsSearch()" style="padding:6px 12px; font-size:12px; border:1px solid #CBD5E1; border-radius:6px; width:220px; outline:none; font-family:inherit">
        <select id="ca-status-filter" onchange="onConditionActionsStatusSelect()" style="padding:6px 10px; font-size:12px; border:1px solid #CBD5E1; border-radius:6px; outline:none; font-family:inherit; background:#fff">
          <option value="ALL">All Statuses</option>
          <option value="CONTROLLED">Controlled / Stable / On Track</option>
          <option value="IMPROVING">Improving / Borderline</option>
          <option value="UNCONTROLLED">Uncontrolled / Crisis / Concerns</option>
        </select>
      </div>
    </div>
    <div class="cb" style="padding:0; overflow-x:auto">
      <table class="tbl" id="ca-linelist-table">
        <thead>
          <tr>
            <th style="width:45px">Sr No.</th>
            <th>Mother Name</th>
            <th>Husband Name</th>
            <th>Block</th>
            <th>Village</th>
            <th>Verified Enrolled Risk</th>
            <th>Visit Date</th>
            <th>GA</th>
            <th>Clinical Value</th>
            <th>Condition Status</th>
            <th>Action Taken / Planned</th>
          </tr>
        </thead>
        <tbody id="ca-linelist-tbody">
          <!-- Populated dynamically -->
        </tbody>
      </table>
    </div>
    <!-- Pagination Footer -->
    <div style="display:flex; justify-content:space-between; align-items:center; padding:12px 18px; border-top:1px solid #E2E8F0; flex-wrap:wrap; gap:10px">
      <div style="font-size:12px; color:var(--text-m)" id="ca-pagination-info">
        Showing 0 to 0 of 0 records
      </div>
      <div style="display:flex; gap:6px">
        <button class="pill p-gy" id="ca-prev-btn" onclick="prevConditionActionsPage()" style="border:none; cursor:pointer; font-family:inherit; font-size:11px; padding:4px 12px">Previous</button>
        <button class="pill p-t" id="ca-next-btn" onclick="nextConditionActionsPage()" style="border:none; cursor:pointer; font-family:inherit; font-size:11px; padding:4px 12px">Next</button>
      </div>
    </div>
  </div>
</div>

"""

assert panel_insert_marker in html, "Panel insert marker not found"
html = html.replace(panel_insert_marker, new_panel_html + panel_insert_marker, 1)

# 3. Update show() function to trigger renderConditionActionsSection
old_show = """  if (name === 'linelist' && typeof renderLineList === 'function') {
    renderLineList();
  }"""
new_show = """  if (name === 'linelist' && typeof renderLineList === 'function') {
    renderLineList();
  }
  if (name === 'cond-actions' && typeof renderConditionActionsSection === 'function') {
    renderConditionActionsSection();
  }"""

assert old_show in html, "old_show pattern not found"
html = html.replace(old_show, new_show, 1)

# 4. Insert call in renderDashboard
old_rd = """  if (typeof renderUnmatchedDeliveries === 'function') {
    renderUnmatchedDeliveries();
  }"""
new_rd = """  if (typeof renderUnmatchedDeliveries === 'function') {
    renderUnmatchedDeliveries();
  }
  if (typeof renderConditionActionsSection === 'function') {
    renderConditionActionsSection();
  }"""

assert old_rd in html, "old_rd pattern not found"
html = html.replace(old_rd, new_rd, 1)

# 5. Append JavaScript functions at the end of the script tag
ca_js_code = """
// ═══════════════════════════════════════════════════════════════════
// HIGH-RISK CLINICAL CONDITION STATUS & ACTION SECTION
// ═══════════════════════════════════════════════════════════════════
window.currentCaConditionFilter = 'ALL';
window.currentCaStatusFilter = 'ALL';
window.currentCaSearchQuery = '';
window.currentCaPage = 1;
const CA_PAGE_SIZE = 15;
window.caStatusDonutChartInstance = null;
window.caActionsBarChartInstance = null;

function setConditionActionsFilter(condKey) {
  window.currentCaConditionFilter = condKey;
  window.currentCaPage = 1;
  
  const btnIds = ['ALL', 'SCD', 'ANEMIA', 'PIH', 'GDM', 'LSCS', 'BOH', 'TEEN'];
  btnIds.forEach(id => {
    const btn = document.getElementById('ca-btn-' + id);
    if (!btn) return;
    if (id === condKey) {
      btn.className = 'pill p-t';
      btn.style.fontWeight = '700';
    } else {
      btn.className = 'pill p-gy';
      btn.style.fontWeight = '500';
    }
  });

  renderConditionActionsSection();
}

function onConditionActionsStatusSelect() {
  const sel = document.getElementById('ca-status-filter');
  if (sel) {
    window.currentCaStatusFilter = sel.value;
    window.currentCaPage = 1;
    renderConditionActionsLinelist();
  }
}

function onConditionActionsSearch() {
  const inp = document.getElementById('ca-search-box');
  if (inp) {
    window.currentCaSearchQuery = inp.value.trim().toLowerCase();
    window.currentCaPage = 1;
    renderConditionActionsLinelist();
  }
}

function prevConditionActionsPage() {
  if (window.currentCaPage > 1) {
    window.currentCaPage--;
    renderConditionActionsLinelist();
  }
}

function nextConditionActionsPage() {
  window.currentCaPage++;
  renderConditionActionsLinelist();
}

function getConditionStatusCategory(condKey, statusStr) {
  if (!statusStr || statusStr === 'nan') return 'UNKNOWN';
  const s = statusStr.toLowerCase();
  if (s.includes('controlled') || s.includes('नियंत्रित') || s.includes('stable') || s.includes('स्थिर') || s.includes('on track') || s.includes('योजना के अनुसार')) {
    return 'CONTROLLED';
  }
  if (s.includes('improving') || s.includes('सुधार') || s.includes('borderline') || s.includes('सीमा रेखा')) {
    return 'IMPROVING';
  }
  if (s.includes('not controlled') || s.includes('अनियंत्रित') || s.includes('crisis') || s.includes('संकट') || s.includes('worsen') || s.includes('बिगड़') || s.includes('concern') || s.includes('दर्द') || s.includes('pain') || s.includes('कम') || s.includes('reduced')) {
    return 'UNCONTROLLED';
  }
  return 'OTHER';
}

function cleanActionLabel(raw) {
  if (!raw || raw === 'nan') return 'Routine Care (Stable)';
  const s = raw.toLowerCase();
  if (s.includes('no action') || s.includes('आवश्यकता नही') || s.includes('stable') || s.includes('controlled')) {
    return 'No action needed (Stable/Controlled)';
  }
  if (s.includes('blood transfusion') || s.includes('रक्त आधान')) {
    return 'Blood Transfusion Arranged';
  }
  if (s.includes('referral to chc / dh') || s.includes('सीएचसी/डीएच')) {
    return 'Referral to CHC / DH';
  }
  if (s.includes('referral to phc') || s.includes('प्राथमिक स्वास्थ्य केंद्र')) {
    return 'Referral to PHC';
  }
  if (s.includes('iv iron') || s.includes('iron sucrose')) {
    return 'IV Iron Arranged (PHC/CHC)';
  }
  if (s.includes('oral ifa') || s.includes('आईएफए')) {
    return 'Oral IFA Adherence Counselling';
  }
  if (s.includes('mo review') || s.includes('escalated to mo') || s.includes('एमओ')) {
    return 'Escalated to MO Review';
  }
  if (s.includes('increased monitoring') || s.includes('निगरानी की आवृत्ति')) {
    return 'Frequent Monitoring Planned';
  }
  if (s.includes('counselling') || s.includes('परामर्श')) {
    return 'Birth Plan & Facility Counselling';
  }
  if (s.includes('sanawad') || s.includes('chc') || s.includes('dh') || s.includes('refer')) {
    return 'Hospital Referral Arranged';
  }
  if (raw.length > 32) return raw.substring(0, 32) + '...';
  return raw;
}

function getConditionDisplayMeta(condKey) {
  const meta = {
    'ALL': { title: 'All High-Risk Conditions', desc: 'All Enrolled Conditions' },
    'SCD': { title: 'Sickle Cell Disease (SCD)', desc: 'SCD Verified Cohort' },
    'ANEMIA': { title: 'Severe Anemia (Hb < 7)', desc: 'Severe Anemia Verified Cohort' },
    'PIH': { title: 'PIH / Gestational Hypertension', desc: 'PIH Verified Cohort' },
    'GDM': { title: 'Gestational Diabetes Mellitus (GDM)', desc: 'GDM Verified Cohort' },
    'LSCS': { title: 'Previous LSCS (C-Section)', desc: 'Previous LSCS Cohort' },
    'BOH': { title: 'Prev Stillbirth / Neonatal Death (BOH)', desc: 'BOH Verified Cohort' },
    'TEEN': { title: 'Teenage Pregnancy (<20y)', desc: 'Teenage Pregnancy Cohort' }
  };
  return meta[condKey] || meta['ALL'];
}

function collectVerifiedRiskRecords(filterCondKey) {
  const allVerified = [];
  const verifiedMothers = new Set();
  
  if (!dashboardData || !dashboardData.cases) return { records: [], motherCount: 0 };
  
  dashboardData.cases.forEach(c => {
    if (!c.visits || c.visits.length === 0) return;
    const hrp = (c.hrp_categories || []).join(' ').toLowerCase();
    
    const isAnemia = hrp.includes('anemia') || hrp.includes('anaemia');
    const isPih = hrp.includes('pih') || hrp.includes('hypertension');
    const isScd = hrp.includes('scd') || hrp.includes('sickle');
    const isGdm = hrp.includes('gdm') || hrp.includes('diabetes');
    const isLscs = hrp.includes('lscs') || hrp.includes('cesarean');
    const isBoh = hrp.includes('stillbirth') || hrp.includes('neonatal') || hrp.includes('death') || hrp.includes('boh');
    const isTeen = hrp.includes('teen') || hrp.includes('किशोर');
    
    c.visits.forEach(v => {
      // SCD
      if ((filterCondKey === 'ALL' || filterCondKey === 'SCD') && isScd && (v.scd_status || v.scd_action)) {
        verifiedMothers.add(c.id_a);
        allVerified.push({
          caseId: c.id_a,
          name: c.name,
          age: c.age,
          husband: c.husband_name,
          block: c.block,
          village: c.village,
          conditionName: 'Sickle Cell Disease (SCD)',
          conditionKey: 'SCD',
          date: v.date,
          ga: v.gestational_age,
          clinicalVal: v.scd_hb ? `Hb: ${v.scd_hb} g/dL` : (v.hb ? `Hb: ${v.hb} g/dL` : '-'),
          statusRaw: v.scd_status || 'Not Recorded',
          statusCat: getConditionStatusCategory('SCD', v.scd_status),
          actionRaw: v.scd_action || 'Routine care',
          actionClean: cleanActionLabel(v.scd_action)
        });
      }
      
      // Severe Anemia
      if ((filterCondKey === 'ALL' || filterCondKey === 'ANEMIA') && isAnemia && (v.anemia_status || v.anemia_action)) {
        verifiedMothers.add(c.id_a);
        allVerified.push({
          caseId: c.id_a,
          name: c.name,
          age: c.age,
          husband: c.husband_name,
          block: c.block,
          village: c.village,
          conditionName: 'Severe Anemia',
          conditionKey: 'ANEMIA',
          date: v.date,
          ga: v.gestational_age,
          clinicalVal: v.hb ? `Hb: ${v.hb} g/dL` : '-',
          statusRaw: v.anemia_status || 'Not Recorded',
          statusCat: getConditionStatusCategory('ANEMIA', v.anemia_status),
          actionRaw: v.anemia_action || 'Routine care',
          actionClean: cleanActionLabel(v.anemia_action)
        });
      }
      
      // PIH
      if ((filterCondKey === 'ALL' || filterCondKey === 'PIH') && isPih && (v.pih_status || v.pih_action)) {
        verifiedMothers.add(c.id_a);
        const bpStr = (v.bp_systolic && v.bp_diastolic) ? `${v.bp_systolic}/${v.bp_diastolic} mmHg` : '-';
        allVerified.push({
          caseId: c.id_a,
          name: c.name,
          age: c.age,
          husband: c.husband_name,
          block: c.block,
          village: c.village,
          conditionName: 'PIH / Hypertension',
          conditionKey: 'PIH',
          date: v.date,
          ga: v.gestational_age,
          clinicalVal: `BP: ${bpStr}`,
          statusRaw: v.pih_status || 'Not Recorded',
          statusCat: getConditionStatusCategory('PIH', v.pih_status),
          actionRaw: v.pih_action || 'Routine care',
          actionClean: cleanActionLabel(v.pih_action)
        });
      }
      
      // GDM
      if ((filterCondKey === 'ALL' || filterCondKey === 'GDM') && isGdm && (v.gdm_status || v.gdm_action)) {
        verifiedMothers.add(c.id_a);
        const sugarStr = v.gdm_rbs ? `RBS: ${v.gdm_rbs} mg/dL` : (v.gdm_fbs ? `FBS: ${v.gdm_fbs} mg/dL` : '-');
        allVerified.push({
          caseId: c.id_a,
          name: c.name,
          age: c.age,
          husband: c.husband_name,
          block: c.block,
          village: c.village,
          conditionName: 'Gestational Diabetes (GDM)',
          conditionKey: 'GDM',
          date: v.date,
          ga: v.gestational_age,
          clinicalVal: sugarStr,
          statusRaw: v.gdm_status || 'Not Recorded',
          statusCat: getConditionStatusCategory('GDM', v.gdm_status),
          actionRaw: v.gdm_action || 'Routine care',
          actionClean: cleanActionLabel(v.gdm_action)
        });
      }
      
      // Previous LSCS
      if ((filterCondKey === 'ALL' || filterCondKey === 'LSCS') && isLscs && (v.prev_lscs_status || v.prev_lscs_remarks)) {
        verifiedMothers.add(c.id_a);
        allVerified.push({
          caseId: c.id_a,
          name: c.name,
          age: c.age,
          husband: c.husband_name,
          block: c.block,
          village: c.village,
          conditionName: 'Previous LSCS',
          conditionKey: 'LSCS',
          date: v.date,
          ga: v.gestational_age,
          clinicalVal: 'Prior C-Section',
          statusRaw: v.prev_lscs_status || 'Not Recorded',
          statusCat: getConditionStatusCategory('LSCS', v.prev_lscs_status),
          actionRaw: v.prev_lscs_remarks || 'On Track',
          actionClean: cleanActionLabel(v.prev_lscs_remarks)
        });
      }
      
      // BOH
      if ((filterCondKey === 'ALL' || filterCondKey === 'BOH') && isBoh && (v.prev_stillbirth_status || v.prev_stillbirth_remarks)) {
        verifiedMothers.add(c.id_a);
        allVerified.push({
          caseId: c.id_a,
          name: c.name,
          age: c.age,
          husband: c.husband_name,
          block: c.block,
          village: c.village,
          conditionName: 'Prev Stillbirth / NND',
          conditionKey: 'BOH',
          date: v.date,
          ga: v.gestational_age,
          clinicalVal: 'Bad Obstetric History',
          statusRaw: v.prev_stillbirth_status || 'Not Recorded',
          statusCat: getConditionStatusCategory('BOH', v.prev_stillbirth_status),
          actionRaw: v.prev_stillbirth_remarks || 'On Track',
          actionClean: cleanActionLabel(v.prev_stillbirth_remarks)
        });
      }
      
      // Teenage
      if ((filterCondKey === 'ALL' || filterCondKey === 'TEEN') && isTeen && (v.teenage_status || v.teenage_remarks)) {
        verifiedMothers.add(c.id_a);
        allVerified.push({
          caseId: c.id_a,
          name: c.name,
          age: c.age,
          husband: c.husband_name,
          block: c.block,
          village: c.village,
          conditionName: 'Teenage Pregnancy',
          conditionKey: 'TEEN',
          date: v.date,
          ga: v.gestational_age,
          clinicalVal: c.age ? `Age: ${c.age}y` : '<20y',
          statusRaw: v.teenage_status || 'Not Recorded',
          statusCat: getConditionStatusCategory('TEEN', v.teenage_status),
          actionRaw: v.teenage_remarks || 'On Track',
          actionClean: cleanActionLabel(v.teenage_remarks)
        });
      }
    });
  });
  
  allVerified.sort((a, b) => (b.date || '').localeCompare(a.date || ''));
  return { records: allVerified, motherCount: verifiedMothers.size };
}

function renderConditionActionsSection() {
  const condKey = window.currentCaConditionFilter || 'ALL';
  const { records, motherCount } = collectVerifiedRiskRecords(condKey);
  const meta = getConditionDisplayMeta(condKey);
  
  const chartStatusTitle = document.getElementById('ca-chart-status-title');
  if (chartStatusTitle) chartStatusTitle.textContent = `${meta.title} — Condition Status Breakdown (n=${records.length})`;
  
  const chartActionsTitle = document.getElementById('ca-chart-actions-title');
  if (chartActionsTitle) chartActionsTitle.textContent = `${meta.title} — Clinical Actions Mobilized (n=${records.length})`;

  const tableTitle = document.getElementById('ca-table-title');
  if (tableTitle) tableTitle.textContent = `Verified Risk Follow-up & Action Register (${meta.desc})`;

  let controlledCount = 0;
  let improvingCount = 0;
  let uncontrolledCount = 0;
  
  records.forEach(r => {
    if (r.statusCat === 'CONTROLLED') controlledCount++;
    else if (r.statusCat === 'IMPROVING') improvingCount++;
    else if (r.statusCat === 'UNCONTROLLED') uncontrolledCount++;
  });
  
  const total = records.length;
  const pct = (cnt) => total > 0 ? Math.round((cnt / total) * 100) : 0;
  
  const elEnrolled = document.getElementById('ca-kpi-enrolled');
  if (elEnrolled) elEnrolled.textContent = motherCount;
  
  const elVisits = document.getElementById('ca-kpi-visits');
  if (elVisits) elVisits.textContent = total;
  
  const elControlled = document.getElementById('ca-kpi-controlled');
  if (elControlled) elControlled.textContent = `${controlledCount} (${pct(controlledCount)}%)`;
  
  const elUncontrolled = document.getElementById('ca-kpi-uncontrolled');
  if (elUncontrolled) elUncontrolled.textContent = `${uncontrolledCount} (${pct(uncontrolledCount)}%)`;
  
  const elSubControlled = document.getElementById('ca-kpi-sub-controlled');
  if (elSubControlled) elSubControlled.textContent = `${improvingCount} (${pct(improvingCount)}%) improving / borderline`;

  renderConditionActionsCharts(records);
  renderConditionActionsLinelist();
}

function renderConditionActionsCharts(records) {
  let controlled = 0, improving = 0, uncontrolled = 0;
  records.forEach(r => {
    if (r.statusCat === 'CONTROLLED') controlled++;
    else if (r.statusCat === 'IMPROVING') improving++;
    else if (r.statusCat === 'UNCONTROLLED') uncontrolled++;
  });
  
  const statusCanvas = document.getElementById('ca-status-donut-chart');
  if (statusCanvas) {
    if (window.caStatusDonutChartInstance) {
      window.caStatusDonutChartInstance.destroy();
    }
    const ctx = statusCanvas.getContext('2d');
    window.caStatusDonutChartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Controlled / Stable / On Track', 'Improving / Borderline', 'Crisis / Uncontrolled / Concern'],
        datasets: [{
          data: [controlled, improving, uncontrolled],
          backgroundColor: ['#2E7D32', '#00838F', '#C62828'],
          borderWidth: 2,
          borderColor: '#FFFFFF'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11, weight: '600' } } },
          tooltip: {
            callbacks: {
              label: function(context) {
                const total = controlled + improving + uncontrolled;
                const val = context.raw || 0;
                const p = total > 0 ? Math.round((val / total) * 100) : 0;
                return ` ${context.label}: ${val} (${p}%)`;
              }
            }
          }
        },
        cutout: '62%'
      }
    });
  }

  const actionCounts = {};
  records.forEach(r => {
    const act = r.actionClean;
    actionCounts[act] = (actionCounts[act] || 0) + 1;
  });
  
  const sortedActions = Object.entries(actionCounts).sort((a, b) => b[1] - a[1]);
  const actionLabels = sortedActions.map(e => e[0]);
  const actionValues = sortedActions.map(e => e[1]);
  
  const actionColors = actionLabels.map(l => {
    if (l.includes('No action') || l.includes('Routine')) return '#2E7D32';
    if (l.includes('Transfusion')) return '#C62828';
    if (l.includes('Referral') || l.includes('Hospital')) return '#E65100';
    if (l.includes('Iron')) return '#1565C0';
    if (l.includes('MO')) return '#6A1B9A';
    if (l.includes('Monitoring')) return '#00838F';
    return '#455A64';
  });

  const actionsCanvas = document.getElementById('ca-actions-bar-chart');
  if (actionsCanvas) {
    if (window.caActionsBarChartInstance) {
      window.caActionsBarChartInstance.destroy();
    }
    const ctx = actionsCanvas.getContext('2d');
    window.caActionsBarChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: actionLabels,
        datasets: [{
          data: actionValues,
          backgroundColor: actionColors,
          borderRadius: 4
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` Actions Mobilized: ${ctx.raw}`
            }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: { precision: 0, font: { size: 11 } },
            grid: { color: '#F1F5F9' }
          },
          y: {
            ticks: { font: { size: 10, weight: '600' } },
            grid: { display: false }
          }
        }
      }
    });
  }
}

function renderConditionActionsLinelist() {
  const condKey = window.currentCaConditionFilter || 'ALL';
  const statusFilter = window.currentCaStatusFilter || 'ALL';
  const query = window.currentCaSearchQuery || '';
  
  const { records } = collectVerifiedRiskRecords(condKey);
  
  const filtered = records.filter(r => {
    if (statusFilter !== 'ALL' && r.statusCat !== statusFilter) return false;
    if (query) {
      const matchName = (r.name || '').toLowerCase().includes(query);
      const matchHusb = (r.husband || '').toLowerCase().includes(query);
      const matchVillage = (r.village || '').toLowerCase().includes(query);
      const matchBlock = (r.block || '').toLowerCase().includes(query);
      const matchCond = (r.conditionName || '').toLowerCase().includes(query);
      if (!matchName && !matchHusb && !matchVillage && !matchBlock && !matchCond) return false;
    }
    return true;
  });
  
  const total = filtered.length;
  const badgeEl = document.getElementById('ca-record-badge');
  if (badgeEl) badgeEl.textContent = `${total} records`;

  const totalPages = Math.ceil(total / CA_PAGE_SIZE) || 1;
  if (window.currentCaPage > totalPages) window.currentCaPage = totalPages;
  if (window.currentCaPage < 1) window.currentCaPage = 1;

  const startIdx = (window.currentCaPage - 1) * CA_PAGE_SIZE;
  const endIdx = Math.min(startIdx + CA_PAGE_SIZE, total);
  const pageItems = filtered.slice(startIdx, endIdx);

  const infoEl = document.getElementById('ca-pagination-info');
  if (infoEl) {
    infoEl.textContent = total > 0 ? `Showing ${startIdx + 1} to ${endIdx} of ${total} verified follow-up records` : 'Showing 0 records';
  }

  const prevBtn = document.getElementById('ca-prev-btn');
  const nextBtn = document.getElementById('ca-next-btn');
  if (prevBtn) prevBtn.disabled = window.currentCaPage <= 1;
  if (nextBtn) nextBtn.disabled = window.currentCaPage >= totalPages;

  const tbody = document.getElementById('ca-linelist-tbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  if (pageItems.length === 0) {
    tbody.innerHTML = '<tr><td colspan="11" style="text-align:center; padding:24px; color:var(--text-m)">No verified follow-up records match the selected criteria.</td></tr>';
    return;
  }

  pageItems.forEach((r, idx) => {
    const tr = document.createElement('tr');
    
    let stBadge = '';
    if (r.statusCat === 'CONTROLLED') {
      stBadge = `<span class="pill p-g" title="${r.statusRaw}">🟢 Stable / Controlled</span>`;
    } else if (r.statusCat === 'IMPROVING') {
      stBadge = `<span class="pill p-b" title="${r.statusRaw}">🔵 Improving / Borderline</span>`;
    } else if (r.statusCat === 'UNCONTROLLED') {
      stBadge = `<span class="pill p-r" title="${r.statusRaw}">🔴 Crisis / Uncontrolled</span>`;
    } else {
      stBadge = `<span class="pill p-gy" title="${r.statusRaw}">⚪ ${r.statusRaw}</span>`;
    }

    let actBadge = '';
    const actClean = r.actionClean;
    if (actClean.includes('No action') || actClean.includes('Routine') || actClean.includes('On Track')) {
      actBadge = `<span style="color:#2E7D32; font-weight:600; font-size:11px">✓ Routine Care (Stable)</span>`;
    } else if (actClean.includes('Transfusion')) {
      actBadge = `<span style="background:#FFEBEE; color:#C62828; padding:3px 7px; border-radius:4px; font-weight:700; font-size:11px; display:inline-block">🩸 ${actClean}</span>`;
    } else if (actClean.includes('Referral') || actClean.includes('Hospital')) {
      actBadge = `<span style="background:#FFF3E0; color:#E65100; padding:3px 7px; border-radius:4px; font-weight:700; font-size:11px; display:inline-block">🏥 ${actClean}</span>`;
    } else if (actClean.includes('Iron')) {
      actBadge = `<span style="background:#E3F2FD; color:#1565C0; padding:3px 7px; border-radius:4px; font-weight:700; font-size:11px; display:inline-block">💉 ${actClean}</span>`;
    } else if (actClean.includes('MO')) {
      actBadge = `<span style="background:#F3E5F5; color:#6A1B9A; padding:3px 7px; border-radius:4px; font-weight:700; font-size:11px; display:inline-block">👩‍⚕️ ${actClean}</span>`;
    } else {
      actBadge = `<span style="background:#ECEFF1; color:#37474F; padding:3px 7px; border-radius:4px; font-weight:600; font-size:11px; display:inline-block">⚡ ${actClean}</span>`;
    }

    const nameHtml = `<div><strong style="color:var(--teal); cursor:pointer;" onclick="openPatientModal(${r.caseId})">${r.name}</strong><br><small style="color:var(--text-m)">Age: ${r.age || '-'}y</small></div>`;

    tr.innerHTML = `
      <td>${startIdx + idx + 1}</td>
      <td>${nameHtml}</td>
      <td>${r.husband || '-'}</td>
      <td><strong>${r.block || '-'}</strong></td>
      <td>${r.village || '-'}</td>
      <td><span class="pill p-t" style="font-size:10.5px">${r.conditionName}</span></td>
      <td>${formatDate(r.date)}</td>
      <td>${r.ga ? r.ga + 'w' : '-'}</td>
      <td><strong>${r.clinicalVal}</strong></td>
      <td>${stBadge}<br><small style="color:var(--text-m); font-size:9.5px; display:block; max-width:180px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap" title="${r.statusRaw}">${r.statusRaw}</small></td>
      <td>${actBadge}<br><small style="color:var(--text-m); font-size:9.5px; display:block; max-width:200px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap" title="${r.actionRaw}">${r.actionRaw}</small></td>
    `;
    tbody.appendChild(tr);
  });
}
"""

script_end_marker = "</script>\n</body>\n</html>"
if script_end_marker not in html:
    script_end_marker = "</script>\r\n</body>\r\n</html>"

assert script_end_marker in html, "Script end marker not found"
html = html.replace(script_end_marker, ca_js_code + "\n" + script_end_marker, 1)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Successfully updated index.html with Risk Follow-up & Actions section!")
