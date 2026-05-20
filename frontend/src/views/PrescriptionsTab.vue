<template>
  <div class="tab">

    <!-- ── HEADER ────────────────────────────────────────────── -->
    <div class="header-row">
      <div>
        <h2 class="section-title">Prescriptions</h2>
        <p class="section-sub">Your doctor-issued prescriptions and medication schedules.</p>
      </div>
      <button class="btn-new" @click="openCreate">+ New Rx</button>
    </div>

    <!-- ── EMPTY ─────────────────────────────────────────────── -->
    <div class="empty-state" v-if="!loading && prescriptions.length === 0">
      <span class="empty-icon">📋</span>
      <p class="empty-title">No prescriptions yet</p>
      <p class="empty-sub">Add a prescription to track your medicines and alarms.</p>
    </div>

    <div class="hint" v-if="loading">
      <span class="hint-icon">⏳</span><p>Loading…</p>
    </div>

    <!-- ── PRESCRIPTION CARDS ─────────────────────────────────── -->
    <div class="rx-list" v-if="!loading && prescriptions.length > 0">
      <div class="rx-card" v-for="rx in prescriptions" :key="rx.prescription_id" @click="openDetail(rx)">
        <div class="rx-card__icon">📋</div>
        <div class="rx-card__body">
          <p class="rx-card__name">{{ rx.name }}</p>
          <p class="rx-card__meta">
            <span v-if="rx.doctor">Dr. {{ rx.doctor }}</span>
            <span v-if="rx.doctor && rx.date"> · </span>
            <span v-if="rx.date">{{ formatDate(rx.date) }}</span>
          </p>
          <p class="rx-card__meta" v-if="rx.detail">{{ rx.detail }}</p>
        </div>
        <span class="rx-card__arrow">›</span>
      </div>
    </div>

    <!-- ── CREATE PRESCRIPTION SHEET ─────────────────────────── -->
    <Teleport to="body">
      <div class="overlay" v-if="showCreate" @click.self="showCreate = false">
        <div class="sheet">
          <div class="sheet-handle"></div>
          <h3 class="sheet-title">New Prescription</h3>
          <p class="err" v-if="createError">{{ createError }}</p>

          <label class="field-label">Prescription Name *</label>
          <input class="field" placeholder="e.g. Monthly checkup" v-model="form.name" />

          <label class="field-label">Doctor</label>
          <input class="field" placeholder="e.g. Dr. Santos" v-model="form.doctor" />

          <label class="field-label">Date</label>
          <input class="field" type="date" v-model="form.date" />

          <label class="field-label">Notes</label>
          <textarea class="field field--ta" rows="2" placeholder="Optional notes…" v-model="form.detail"></textarea>

          <button class="btn-primary" @click="createRx" :disabled="isCreating">
            {{ isCreating ? 'Creating…' : 'Create Prescription' }}
          </button>
          <button class="btn-ghost" @click="showCreate = false">Cancel</button>
        </div>
      </div>
    </Teleport>

    <!-- ── PRESCRIPTION DETAIL SHEET ─────────────────────────── -->
    <Teleport to="body">
      <div class="overlay" v-if="activeRx" @click.self="closeDetail">
        <div class="sheet sheet--tall">
          <div class="sheet-handle"></div>

          <!-- header -->
          <div class="detail-header">
            <div>
              <h3 class="sheet-title">{{ activeRx.name }}</h3>
              <p class="detail-meta" v-if="activeRx.doctor">Dr. {{ activeRx.doctor }}<span v-if="activeRx.date"> · {{ formatDate(activeRx.date) }}</span></p>
              <p class="detail-meta" v-if="activeRx.detail">{{ activeRx.detail }}</p>
            </div>
            <button class="btn-del-rx" @click="deleteRx" title="Delete prescription">🗑</button>
          </div>

          <p class="err" v-if="detailError">{{ detailError }}</p>

          <!-- medicine list -->
          <p class="list-label">Medicines</p>
          <div class="loading-row" v-if="loadingDetails">⏳ Loading medicines…</div>
          <div class="empty-meds" v-else-if="rxDetails.length === 0">No medicines added yet.</div>
          <div class="med-row" v-for="d in rxDetails" :key="d.prescription_detail_id">
            <div class="med-row__info">
              <p class="med-row__name">{{ d.brand_name }}</p>
              <p class="med-row__generic">{{ d.generic_name }} · {{ d.dosage_form }}</p>
              <div class="sched-chips">
                <span class="chip chip--blue">📅 {{ formatDate(d.date_start) }}<template v-if="d.date_end"> → {{ formatDate(d.date_end) }}</template></span>
                <span class="chip chip--green">⏰ {{ d.time_taken }}</span>
                <span class="chip chip--purple">{{ d.days_taken }}</span>
                <span class="chip" :class="d.alarm_active ? 'chip--on' : 'chip--off'">🔔 {{ d.alarm_active ? 'Alarm on' : 'Alarm off' }}</span>
              </div>
            </div>
            <button class="btn-remove" @click="removeDetail(d)" title="Remove">✕</button>
          </div>

          <!-- add medicine -->
          <button class="btn-add-med" @click="openAddMed" style="margin-top:16px">+ Add Medicine</button>
          <button class="btn-ghost" @click="closeDetail" style="margin-top:8px">Close</button>
        </div>
      </div>
    </Teleport>
    <!-- Prescription Picker Sheet -->
    <Teleport to="body">
      <div class="overlay" v-if="showRxPicker" @click.self="showRxPicker = false">
        <div class="sheet">
          <div class="sheet-handle"></div>
          <h3 class="sheet-title">Add to which prescription?</h3>
          <p class="detail-meta" v-if="shelfBridge.pendingMed">
            Adding: <strong>{{ shelfBridge.pendingMed.brand_name }}</strong>
          </p>

          <div class="empty-meds" v-if="prescriptions.length === 0">
            No prescriptions yet. Create one first.
          </div>

          <div
            class="rx-card"
            v-for="rx in prescriptions"
            :key="rx.prescription_id"
            @click="pickRxForMed(rx)"
          >
            <div class="rx-card__icon">📋</div>
            <div class="rx-card__body">
              <p class="rx-card__name">{{ rx.name }}</p>
              <p class="rx-card__meta" v-if="rx.doctor">Dr. {{ rx.doctor }}</p>
            </div>
            <span class="rx-card__arrow">›</span>
          </div>

          <button class="btn-ghost" @click="showRxPicker = false; shelfBridge.pendingMed = null">
            Cancel
          </button>
        </div>
      </div>
    </Teleport>

<!-- ADD MEDICINE SHEET ─────────────────────────────────────── -->
<Teleport to="body">
  <div class="overlay" v-if="showAddMed" @click.self="showAddMed = false">
    <div class="sheet sheet--tall">
      <div class="sheet-handle"></div>
      <h3 class="sheet-title">Add Medicine</h3>
      <p class="err" v-if="addError">{{ addError }}</p>

      <!-- STEP 1: Search (always visible) -->
      <label class="field-label">Search Medicine *</label>
      <input
        class="field"
        placeholder="Type brand or generic name…"
        v-model="medSearch"
        @input="searchMed"
      />

      <!-- Results dropdown -->
      <div class="search-results" v-if="medResults.length > 0 && !chosenMed">
        <div
          class="search-result"
          v-for="m in medResults"
          :key="m.lookup_id"
          @click="pickMed(m)"
        >
          <p class="sr__brand">{{ m.brand_name }}</p>
          <p class="sr__generic">{{ m.generic_name }} · {{ m.dosage_form }}</p>
        </div>
      </div>

      <!-- Chosen medicine pill -->
      <div class="chosen-med" v-if="chosenMed">
        <div>
          <p class="chosen-med__name">✅ {{ chosenMed.brand_name }}</p>
          <p class="chosen-med__sub">{{ chosenMed.generic_name }} · {{ chosenMed.dosage_form }}</p>
        </div>
        <button class="btn-clear" @click="clearMed">Change</button>
      </div>

      <!-- STEP 2: Schedule fields — only shown after medicine is chosen -->
      <template v-if="chosenMed">
        <label class="field-label" style="margin-top:12px">Start Date *</label>
        <input class="field" type="date" v-model="detailForm.date_start" />

        <label class="field-label">End Date</label>
        <input class="field" type="date" v-model="detailForm.date_end" />

        <label class="field-label">Times (add each time then press +)</label>
        <div class="time-input-row">
          <input class="field field--sm" type="time" v-model="timeInput" />
          <button class="btn-add-time" @click="addTime">+</button>
        </div>
        <div class="time-chips" v-if="detailForm.times.length > 0">
          <span class="time-chip" v-for="(t, i) in detailForm.times" :key="i">
            {{ t }} <button class="chip-remove" @click="removeTime(i)">×</button>
          </span>
        </div>

        <label class="field-label" style="margin-top:12px">Days Taken *</label>
        <div class="day-grid">
          <button
            class="day-btn"
            v-for="opt in dayOptions"
            :key="opt.value"
            :class="{ 'day-btn--active': detailForm.days_taken === opt.value }"
            @click="detailForm.days_taken = opt.value"
          >{{ opt.label }}</button>
        </div>

        <button class="btn-primary" @click="addDetail" :disabled="isAddingDetail" style="margin-top:16px">
          {{ isAddingDetail ? 'Adding…' : 'Add & Set Alarm' }}
        </button>
      </template>

      <button class="btn-ghost" @click="showAddMed = false">Cancel</button>
    </div>
  </div>
</Teleport>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, watch} from 'vue'
import api from '@/api'
import { shelfBridge } from '@/composables/useShelfBridge'

// ── STATE ──────────────────────────────────────────────────────────────
const medSearchInput  = ref(null)
const searchResultsEl = ref(null)
const prescriptions  = ref([])
const loading        = ref(false)
const showCreate     = ref(false)
const isCreating     = ref(false)
const createError    = ref('')

const form = reactive({ name: '', doctor: '', date: '', detail: '' })

const activeRx      = ref(null)
const rxDetails     = ref([])
const loadingDetails = ref(false)
const detailError   = ref('')

const showAddMed    = ref(false)
const medSearch     = ref('')
const medResults    = ref([])
const chosenMed     = ref(null)
const isAddingDetail = ref(false)
const addError      = ref('')
const timeInput     = ref('')
const showRxPicker = ref(false)

const detailForm = reactive({
  date_start: '',
  date_end: '',
  times: [],
  days_taken: 'daily',
})

const dayOptions = [
  { label: 'Daily',     value: 'daily' },
  { label: 'Mon-Wed-Fri', value: 'MWF' },
  { label: 'Tue-Thu-Sat', value: 'TTS' },
  { label: 'Weekdays',  value: 'MTWTHF' },
  { label: 'Weekends',  value: 'SS' },
]

let searchTimeout = null

// ── HELPERS ────────────────────────────────────────────────────
function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('en-PH', { year: 'numeric', month: 'short', day: 'numeric' })
}

// ── INIT ───────────────────────────────────────────────────────
onMounted(async () => {
  await loadPrescriptions()

  if (shelfBridge.pendingMed) {
    openRxPicker()
    shelfBridge.pendingMed = null
  }
})

async function loadPrescriptions() {
  loading.value = true
  try { prescriptions.value = (await api.get('/prescriptions/')).data }
  catch (e) { console.error(e) }
  finally { loading.value = false }
}

// ── CREATE Rx ──────────────────────────────────────────────────
function openCreate() {
  Object.assign(form, { name: '', doctor: '', date: '', detail: '' })
  createError.value = ''
  showCreate.value = true
}

async function createRx() {
  createError.value = ''
  if (!form.name.trim()) { createError.value = 'Prescription name is required.'; return }
  isCreating.value = true
  try {
    await api.post('/prescriptions/', {
      name: form.name.trim(),
      doctor: form.doctor.trim() || null,
      date: form.date || null,
      detail: form.detail.trim() || null,
    })
    showCreate.value = false
    await loadPrescriptions()
  } catch (e) {
    createError.value = e.response?.data?.error || 'Failed to create prescription.'
  } finally { isCreating.value = false }
}

function openRxPicker() {
  showRxPicker.value = true
}

async function pickRxForMed(rx) {
  showRxPicker.value = false
  await openDetail(rx)        // sets activeRx and loads its details
  openAddMed()                // opens the Add Medicine sheet
  pickMed(shelfBridge.pendingMed)   // pre-fills the medicine
  shelfBridge.pendingMed = null
}

// ── DETAIL ─────────────────────────────────────────────────────
async function openDetail(rx) {
  activeRx.value = rx
  detailError.value = ''
  await loadDetails()
}

function closeDetail() {
  activeRx.value = null
  rxDetails.value = []
  showAddMed.value = false
}

async function loadDetails() {
  if (!activeRx.value) return
  loadingDetails.value = true
  try {
    rxDetails.value = (await api.get(`/prescriptions/${activeRx.value.prescription_id}/details`)).data
  } catch (e) { console.error(e) }
  finally { loadingDetails.value = false }
}

async function deleteRx() {
  if (!confirm(`Delete "${activeRx.value.name}"? This will also remove its medicines and alarms.`)) return
  try {
    await api.delete(`/prescriptions/${activeRx.value.prescription_id}`)
    closeDetail()
    await loadPrescriptions()
  } catch (e) { detailError.value = e.response?.data?.error || 'Delete failed.' }
}

async function removeDetail(d) {
  if (!confirm(`Remove ${d.brand_name} from this prescription?`)) return
  try {
    await api.delete(`/prescriptions/${activeRx.value.prescription_id}/details/${d.prescription_detail_id}`)
    await loadDetails()
  } catch (e) { detailError.value = e.response?.data?.error || 'Remove failed.' }
}

// ── ADD MEDICINE ───────────────────────────────────────────────
function openAddMed() {
  resetAddForm()
  showAddMed.value = true
}

function searchMed() {
  clearTimeout(searchTimeout)
  chosenMed.value = null
  if (!medSearch.value.trim()) { medResults.value = []; return }
  searchTimeout = setTimeout(async () => {
    try {
      medResults.value = (await api.get('/autocomplete/', { params: { q: medSearch.value.trim() } })).data
      // scroll results into view on mobile
      await nextTick()
      searchResultsEl.value?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    } catch (e) { medResults.value = [] }
  }, 200)
}

function pickMed(m) {
  chosenMed.value = m
  medResults.value = []
}

function clearMed() {
  chosenMed.value = null
  medSearch.value = ''
  medResults.value = []
}

function addTime() {
  const t = timeInput.value.trim()
  if (t && !detailForm.times.includes(t)) detailForm.times.push(t)
  timeInput.value = ''
}

function removeTime(i) {
  detailForm.times.splice(i, 1)
}

function resetAddForm() {
  medSearch.value = ''
  medResults.value = []
  chosenMed.value = null
  timeInput.value = ''
  Object.assign(detailForm, { date_start: '', date_end: '', times: [], days_taken: 'daily' })
  addError.value = ''
}

async function addDetail() {
  addError.value = ''
  if (!chosenMed.value)              { addError.value = 'Please select a medicine.'; return }
  if (!detailForm.date_start)        { addError.value = 'Start date is required.'; return }
  if (detailForm.times.length === 0) { addError.value = 'Add at least one time.'; return }

  // Get OneSignal subscription ID
  let onesignal_id = null
  try {
    await window.OneSignal.Notifications.requestPermission()
    onesignal_id = await window.OneSignal.User.PushSubscription.id
  } catch (e) {
    console.warn('OneSignal not available:', e)
  }

  isAddingDetail.value = true
  try {
    await api.post(`/prescriptions/${activeRx.value.prescription_id}/details`, {
      lookup_id:    chosenMed.value.lookup_id,
      date_start:   detailForm.date_start,
      date_end:     detailForm.date_end || null,
      time_taken:   detailForm.times.join(','),
      days_taken:   detailForm.days_taken,
      onesignal_id: onesignal_id,   // new
    })
    showAddMed.value = false
    resetAddForm()
    await loadDetails()
    await loadPrescriptions()
  } catch (e) {
    addError.value = e.response?.data?.error || 'Failed to add medicine.'
  } finally { isAddingDetail.value = false }
}
</script>

<style scoped>
.tab { padding: 20px 20px 100px; }

/* header */
.header-row { display:flex; align-items:flex-start; justify-content:space-between; gap:12px; margin-bottom:18px; }
.section-title { font-size:20px; font-weight:800; color:var(--color-text-dark); margin-bottom:2px; }
.section-sub   { font-size:13px; color:var(--color-text-muted); }
.btn-new { flex-shrink:0; padding:10px 16px; background:var(--color-primary); color:#fff; border:none; border-radius:12px; font-size:14px; font-weight:700; font-family:var(--font-main); cursor:pointer; transition:background .2s; }
.btn-new:hover { background:var(--color-primary-dark); }

/* empty / loading */
.empty-state,.hint { text-align:center; padding:40px 20px; color:var(--color-text-muted); }
.empty-icon,.hint-icon { font-size:48px; display:block; margin-bottom:12px; }
.empty-title { font-size:17px; font-weight:700; color:var(--color-text-dark); margin-bottom:6px; }
.empty-sub   { font-size:14px; }

/* rx cards */
.rx-list { display:flex; flex-direction:column; gap:12px; }
.rx-card { background:var(--color-white); border-radius:16px; padding:16px; display:flex; align-items:center; gap:14px; box-shadow:var(--shadow-card); cursor:pointer; transition:transform .15s,box-shadow .15s; }
.rx-card:hover { transform:translateY(-2px); box-shadow:0 6px 24px rgba(0,0,0,.1); }
.rx-card__icon { font-size:28px; flex-shrink:0; }
.rx-card__body { flex:1; }
.rx-card__name { font-size:16px; font-weight:700; color:var(--color-text-dark); }
.rx-card__meta { font-size:12px; color:var(--color-text-muted); margin-top:3px; }
.rx-card__arrow { font-size:22px; color:var(--color-text-muted); }

/* overlay + sheet */
.overlay { position:fixed; inset:0; background:rgba(0,0,0,.45); display:flex; align-items:flex-end; justify-content:center; z-index:300; }
.sheet { background:var(--color-white); border-radius:24px 24px 0 0; padding:12px 24px 40px; width:100%; max-width:500px; max-height:85vh; overflow-y:auto; display:flex; flex-direction:column; gap:10px; animation:slideUp .22s ease; }
.sheet--tall { max-height:93vh; }
.sheet-handle { width:40px; height:4px; background:#cbd5e1; border-radius:2px; margin:0 auto 8px; flex-shrink:0; }
@keyframes slideUp { from{transform:translateY(36px);opacity:0} to{transform:translateY(0);opacity:1} }
.sheet-title { font-size:19px; font-weight:800; color:var(--color-text-dark); }

/* detail header */
.detail-header { display:flex; align-items:flex-start; justify-content:space-between; gap:8px; }
.detail-meta { font-size:13px; color:var(--color-text-muted); margin-top:3px; }
.btn-del-rx { background:none; border:none; font-size:20px; cursor:pointer; padding:4px; flex-shrink:0; }

/* list-label */
.list-label { font-size:11px; font-weight:700; color:var(--color-text-muted); text-transform:uppercase; letter-spacing:.06em; margin-top:4px; }
.loading-row,.empty-meds { font-size:13px; color:var(--color-text-muted); }

/* med rows */
.med-row { display:flex; align-items:flex-start; gap:12px; padding:12px 0; border-bottom:1px solid var(--color-border); }
.med-row__info { flex:1; }
.med-row__name { font-size:14px; font-weight:700; color:var(--color-text-dark); }
.med-row__generic { font-size:12px; color:var(--color-text-muted); margin-top:2px; }
.sched-chips { display:flex; flex-wrap:wrap; gap:5px; margin-top:7px; }
.chip { font-size:11px; font-weight:600; padding:3px 8px; border-radius:20px; background:#e2e8f0; color:#64748b; }
.chip--blue   { background:#e0f2fe; color:#0369a1; }
.chip--green  { background:#dcfce7; color:#15803d; }
.chip--purple { background:#ede9fe; color:#7c3aed; }
.chip--on  { background:#dcfce7; color:#15803d; }
.chip--off { background:#fee2e2; color:#b91c1c; }

/* add med button */
.btn-add-med { width:100%; padding:13px; background:var(--color-primary-light); border:2px dashed var(--color-primary); border-radius:var(--radius-btn); color:var(--color-primary-dark); font-size:14px; font-weight:700; font-family:var(--font-main); cursor:pointer; transition:background .2s; }
.btn-add-med:hover { background:var(--color-primary); color:#fff; }

/* search */
.search-results { background: var(--color-white); border: 2px solid var(--color-border); border-radius: 12px; overflow: hidden; max-height: 220px; overflow-y: auto;
}
.search-result { padding:12px 14px; cursor:pointer; border-bottom:1px solid var(--color-border); transition:background .15s; }
.search-result:last-child { border-bottom:none; }
.search-result:hover { background:var(--color-primary-light); }
.sr__brand { font-size:14px; font-weight:700; color:var(--color-text-dark); }
.sr__generic { font-size:12px; color:var(--color-text-muted); margin-top:2px; }
.chosen-med { background:var(--color-primary-light); border-radius:12px; padding:12px 14px; display:flex; align-items:center; justify-content:space-between; gap:8px; }
.chosen-med__name { font-size:14px; font-weight:700; color:var(--color-primary-dark); }
.chosen-med__sub  { font-size:12px; color:var(--color-text-muted); margin-top:2px; }
.btn-clear { background:none; border:none; color:var(--color-primary); font-size:13px; font-weight:700; cursor:pointer; flex-shrink:0; }

/* time input */
.time-input-row { display:flex; gap:8px; }
.field--sm { flex:1; }
.btn-add-time { padding:0 16px; background:var(--color-primary); color:#fff; border:none; border-radius:var(--radius-input); font-size:20px; font-weight:700; cursor:pointer; }
.time-chips { display:flex; flex-wrap:wrap; gap:6px; }
.time-chip { background:var(--color-primary-light); color:var(--color-primary-dark); font-size:12px; font-weight:700; padding:4px 10px; border-radius:20px; display:flex; align-items:center; gap:4px; }
.chip-remove { background:none; border:none; color:var(--color-primary-dark); font-size:14px; cursor:pointer; padding:0; line-height:1; }

/* day grid */
.day-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }
.day-btn { padding:10px 6px; border-radius:10px; border:2px solid var(--color-border); background:var(--color-white); font-size:13px; font-weight:600; font-family:var(--font-main); color:var(--color-text-muted); cursor:pointer; transition:all .15s; }
.day-btn--active { background:var(--color-primary); border-color:var(--color-primary); color:#fff; }

/* shared fields / buttons */
.field-label { font-size:11px; font-weight:700; color:var(--color-text-muted); text-transform:uppercase; letter-spacing:.05em; margin-bottom:4px; margin-top:4px; }
.field { width:100%; padding:12px 14px; border:2px solid var(--color-border); border-radius:var(--radius-input); font-size:15px; font-family:var(--font-main); color:#1e293b; background:var(--color-input-bg); outline:none; box-sizing:border-box; transition:border-color .2s; resize:none; }
.field:focus { border-color:var(--color-primary); }
.field--ta { resize:vertical; }
.btn-primary { width:100%; padding:14px; background:var(--color-primary); border:none; border-radius:var(--radius-btn); color:#fff; font-size:15px; font-weight:800; font-family:var(--font-main); cursor:pointer; transition:background .2s; }
.btn-primary:hover:not(:disabled) { background:var(--color-primary-dark); }
.btn-primary:disabled { opacity:.6; cursor:not-allowed; }
.btn-ghost { width:100%; padding:12px; background:none; border:2px solid var(--color-border); border-radius:var(--radius-btn); color:var(--color-text-muted); font-size:14px; font-weight:600; font-family:var(--font-main); cursor:pointer; }
.btn-remove { width:28px; height:28px; border-radius:50%; border:none; background:#fee2e2; color:#ef4444; font-size:13px; cursor:pointer; display:flex; align-items:center; justify-content:center; transition:background .2s; flex-shrink:0; margin-top:2px; }
.btn-remove:hover { background:#ef4444; color:#fff; }
.err { font-size:13px; color:#ef4444; font-weight:600; }
</style>
