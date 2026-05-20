<template>
  <div class="tab">
    <h2 class="section-title">My Shelf</h2>

    <div class="hint" v-if="loading">
      <span class="hint-icon">⏳</span><p>Loading your medications...</p>
    </div>
    <div class="empty-state" v-else-if="medications.length === 0">
      <span class="empty-icon">💊</span>
      <p class="empty-title">No medications yet</p>
      <p class="empty-sub">Tap <strong>+ Add Medicine</strong> below to get started.</p>
    </div>

    <div class="med-list" v-else>
      <div class="med-card" v-for="med in medications" :key="med.supply_id">
        <div class="med-card__info">
          <p class="med-card__brand">{{ med.brand_name }}</p>
          <p class="med-card__generic">{{ med.generic_name }}</p>
          <span class="med-card__form">{{ med.dosage_strength }}</span>
          <span class="med-card__form">{{ truncateAtBracket(med.dosage_form) }}</span>
          <span class="med-card__form">{{ truncateAtBracket(med.category) }}</span>
          <span class="med-card__exp" v-if="med.expiration_date">Expiry: {{ med.expiration_date }}</span>
        </div>
        <div class="med-card__controls">
          <button class="stock-button" :class="{ 'stock-button--low': med.supply_stock <= 5 }" @click="openNumpad(med)">
            {{ med.supply_stock }} left
          </button>
          <div class="qty-row">
            <button class="qty-btn" @click="changeStock(med, -1)" :disabled="med.supply_stock <= 0">−</button>
            <button class="qty-btn" @click="changeStock(med, +1)">+</button>
            <button class="btn-delete" @click="deleteMed(med)">🗑</button>
            <button class="btn-add-to-rx" @click="openRxPicker(med)">+ Add to Rx</button>
          </div>
        </div>
      </div>
    </div>

    <div class="add-btn-wrap">
      <router-link to="/medicine-search" class="btn-add">+ Add Medicine</router-link>
    </div>

    <!-- ── NUMPAD SHEET ── -->
    <Teleport to="body">
      <Transition name="fade">
        <div class="overlay" v-if="numpadTarget" @click.self="closeNumpad">
          <Transition name="slide-up">
            <div class="numpad-sheet" v-if="numpadTarget">
              <div class="sheet-handle"></div>
              <p class="numpad-label">{{ numpadTarget.brand_name }}</p>
              <p class="numpad-sub">Set stock quantity</p>
              <div class="numpad-display" :class="{ 'numpad-display--low': numpadDisplay !== '0' && +numpadDisplay <= 5 }">
                <span class="numpad-value">{{ numpadDisplay }}</span>
                <span class="numpad-unit">pcs</span>
              </div>
              <div class="numpad-grid">
                <button class="numpad-key" v-for="key in numKeys" :key="key" @click="pressKey(key)">{{ key }}</button>
                <button class="numpad-key numpad-key--action" @click="pressKey('C')">C</button>
                <button class="numpad-key" @click="pressKey('0')">0</button>
                <button class="numpad-key numpad-key--action" @click="pressKey('⌫')">⌫</button>
              </div>
              <button class="numpad-confirm" @click="confirmNumpad">✓ &nbsp; Set to {{ numpadDisplay }} pcs</button>
              <button class="numpad-cancel" @click="closeNumpad">Cancel</button>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>

    <!-- ── RX PICKER SHEET ── -->
    <Teleport to="body">
      <Transition name="fade">
        <div class="overlay" v-if="showRxPicker" @click.self="cancelAddToRx">
          <Transition name="slide-up">
            <div class="sheet" v-if="showRxPicker">
              <div class="sheet-handle"></div>
              <h3 class="sheet-title">Add to Prescription</h3>
              <div class="chosen-med" v-if="pendingMed">
                <p class="chosen-med__name">💊 {{ pendingMed.brand_name }}</p>
                <p class="chosen-med__sub">{{ pendingMed.generic_name }} · {{ pendingMed.dosage_strength }}</p>
              </div>
              <p class="list-label">Select a prescription</p>
              <div class="hint-sm" v-if="loadingRx">⏳ Loading prescriptions…</div>
              <div class="empty-meds" v-else-if="rxList.length === 0">
                No prescriptions yet. Create one in the Rx tab first.
              </div>
              <div class="rx-pick-card" v-for="rx in rxList" :key="rx.prescription_id" @click="pickRx(rx)">
                <span class="rx-pick-icon">📋</span>
                <div class="rx-pick-body">
                  <p class="rx-pick-name">{{ rx.name }}</p>
                  <p class="rx-pick-meta" v-if="rx.doctor">Dr. {{ rx.doctor }}</p>
                </div>
                <span class="rx-pick-arrow">›</span>
              </div>
              <button class="btn-ghost" @click="cancelAddToRx">Cancel</button>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>

    <!-- ── SCHEDULE FORM SHEET ── -->
    <Teleport to="body">
      <Transition name="fade">
        <div class="overlay" v-if="showSchedForm" @click.self="showSchedForm = false">
          <Transition name="slide-up">
            <div class="sheet sheet--tall" v-if="showSchedForm">
              <div class="sheet-handle"></div>
              <h3 class="sheet-title">Set Schedule</h3>

              <!-- Context -->
              <div class="sched-context">
                <div class="sched-context__row">
                  <span>💊</span>
                  <div>
                    <p class="sched-context__name">{{ pendingMed?.brand_name }}</p>
                    <p class="sched-context__sub">{{ pendingMed?.generic_name }}</p>
                  </div>
                </div>
                <div class="sched-context__row sched-context__row--rx">
                  <span>📋</span>
                  <p class="sched-context__name">{{ selectedRx?.name }}</p>
                </div>
              </div>

              <p class="err" v-if="schedError">{{ schedError }}</p>

              <label class="field-label">Start Date *</label>
              <input class="field" type="date" v-model="schedForm.date_start" />

              <label class="field-label">End Date</label>
              <input class="field" type="date" v-model="schedForm.date_end" />

              <label class="field-label">Times (add each, then press +)</label>
              <div class="time-input-row">
                <input class="field field--sm" type="time" v-model="schedForm.timeInput" />
                <button class="btn-add-time" @click="addTime">+</button>
              </div>
              <div class="time-chips" v-if="schedForm.times.length > 0">
                <span class="time-chip" v-for="(t, i) in schedForm.times" :key="i">
                  {{ t }} <button class="chip-remove" @click="removeTime(i)">×</button>
                </span>
              </div>

              <label class="field-label" style="margin-top:12px">Days Taken *</label>
              <div class="day-grid">
                <button
                  class="day-btn"
                  v-for="opt in dayOptions" :key="opt.value"
                  :class="{ 'day-btn--active': schedForm.days_taken === opt.value }"
                  @click="schedForm.days_taken = opt.value"
                >{{ opt.label }}</button>
              </div>

              <button class="btn-primary" @click="submitAddToRx" :disabled="addingDetail" style="margin-top:16px">
                {{ addingDetail ? 'Adding…' : 'Add to Prescription' }}
              </button>
              <button class="btn-ghost" @click="showSchedForm = false">Cancel</button>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import api from '@/api'

const medications = ref([])
const loading     = ref(true)

// ── Numpad ──────────────────────────────────────────────────────
const numpadTarget  = ref(null)
const numpadRaw     = ref('')
const numKeys = ['1','2','3','4','5','6','7','8','9']
const numpadDisplay = computed(() => numpadRaw.value === '' ? '0' : numpadRaw.value)

function openNumpad(med) { numpadTarget.value = med; numpadRaw.value = med.supply_stock > 0 ? String(med.supply_stock) : '' }
function closeNumpad()   { numpadTarget.value = null; numpadRaw.value = '' }
function pressKey(key) {
  if (key === 'C')  { numpadRaw.value = ''; return }
  if (key === '⌫')  { numpadRaw.value = numpadRaw.value.slice(0, -1); return }
  if (numpadRaw.value.length >= 4) return
  if (numpadRaw.value === '' && key === '0') return
  numpadRaw.value += key
}
async function confirmNumpad() {
  const med = numpadTarget.value
  const newQty = Math.max(0, parseInt(numpadDisplay.value, 10) || 0)
  const prev = med.supply_stock
  med.supply_stock = newQty
  closeNumpad()
  try { await api.patch(`/meds/drug_stock/${med.supply_id}`, { supply_stock: newQty }) }
  catch (err) { med.supply_stock = prev; console.error(err) }
}
function truncateAtBracket(str) {
  if (!str) return ''
  const i = Math.min(
    str.includes('(') ? str.indexOf('(') : Infinity,
    str.includes('[') ? str.indexOf('[') : Infinity
  )
  return i === Infinity ? str.trim() : str.slice(0, i).trim()
}

// ── Stock ±1 ────────────────────────────────────────────────────
async function changeStock(med, delta) {
  const newQty = med.supply_stock + delta
  if (newQty < 0) return
  med.supply_stock = newQty
  try { await api.patch(`/meds/drug_stock/${med.supply_id}`, { supply_stock: newQty }) }
  catch (err) { med.supply_stock -= delta; console.error(err) }
}

// ── Delete ──────────────────────────────────────────────────────
async function deleteMed(med) {
  medications.value = medications.value.filter(m => m.supply_id !== med.supply_id)
  try { await api.delete(`/meds/drug_stock/${med.supply_id}`) }
  catch (err) { medications.value.push(med); console.error(err) }
}

// ── Fetch ───────────────────────────────────────────────────────
async function fetchMedications() {
  loading.value = true
  try { medications.value = (await api.get('/meds/drug_stock')).data }
  catch (err) { console.error(err) }
  finally { loading.value = false }
}
onMounted(fetchMedications)

// ── Add to Rx flow ──────────────────────────────────────────────
const showRxPicker  = ref(false)
const showSchedForm = ref(false)
const rxList        = ref([])
const loadingRx     = ref(false)
const pendingMed    = ref(null)
const selectedRx    = ref(null)
const addingDetail  = ref(false)
const schedError    = ref('')

const schedForm = reactive({
  date_start: '', date_end: '', times: [], days_taken: 'daily', timeInput: '',
})

const dayOptions = [
  { label: 'Daily',       value: 'daily'  },
  { label: 'Mon-Wed-Fri', value: 'MWF'    },
  { label: 'Tue-Thu-Sat', value: 'TTS'    },
  { label: 'Weekdays',    value: 'MTWTHF' },
  { label: 'Weekends',    value: 'SS'     },
]

async function openRxPicker(med) {
  pendingMed.value = med
  loadingRx.value  = true
  showRxPicker.value = true
  try { rxList.value = (await api.get('/prescriptions/')).data }
  catch (e) { rxList.value = [] }
  finally { loadingRx.value = false }
}

function cancelAddToRx() {
  showRxPicker.value = false
  pendingMed.value   = null
  selectedRx.value   = null
}

function pickRx(rx) {
  selectedRx.value    = rx
  showRxPicker.value  = false
  Object.assign(schedForm, { date_start: '', date_end: '', times: [], days_taken: 'daily', timeInput: '' })
  schedError.value    = ''
  showSchedForm.value = true
}

function addTime() {
  const t = schedForm.timeInput.trim()
  if (t && !schedForm.times.includes(t)) schedForm.times.push(t)
  schedForm.timeInput = ''
}
function removeTime(i) { schedForm.times.splice(i, 1) }

async function submitAddToRx() {
  schedError.value = ''
  if (!schedForm.date_start)          { schedError.value = 'Start date is required.'; return }
  if (schedForm.times.length === 0)   { schedError.value = 'Add at least one time.'; return }
  addingDetail.value = true
  try {
    await api.post(`/prescriptions/${selectedRx.value.prescription_id}/details`, {
      supply_id:  pendingMed.value.supply_id,
      date_start: schedForm.date_start,
      date_end:   schedForm.date_end || null,
      time_taken: schedForm.times.join(','),
      days_taken: schedForm.days_taken,
    })
    showSchedForm.value = false
    pendingMed.value    = null
    selectedRx.value    = null
  } catch (e) {
    schedError.value = e.response?.data?.error || 'Failed to add to prescription.'
  } finally { addingDetail.value = false }
}
</script>

<style scoped>
.tab { padding: 20px 20px 140px; }
.section-title { font-size:20px; font-weight:800; color:var(--color-text-dark); margin-bottom:16px; }
.hint,.empty-state { text-align:center; padding:60px 20px; color:var(--color-text-muted); }
.hint-icon,.empty-icon { font-size:48px; display:block; margin-bottom:12px; }
.empty-title { font-size:17px; font-weight:700; color:var(--color-text-dark); margin-bottom:6px; }
.empty-sub   { font-size:14px; }
.hint-sm { font-size:13px; color:var(--color-text-muted); padding:8px 0; }

.med-list { display:flex; flex-direction:column; gap:12px; }
.med-card { background:var(--color-white); border-radius:14px; padding:14px 16px; display:flex; align-items:center; justify-content:space-between; gap:12px; box-shadow:var(--shadow-card); }
.med-card__info { flex:1; }
.med-card__brand   { font-size:15px; font-weight:700; color:var(--color-text-dark); }
.med-card__generic { font-size:12px; color:var(--color-text-muted); margin-top:2px; }
.med-card__form { display:inline-block; margin-top:6px; margin-right:6px; font-size:11px; font-weight:700; background:var(--color-primary-light); color:var(--color-primary-dark); padding:2px 8px; border-radius:20px; }
.med-card__exp  { display:inline-block; margin-top:6px; font-size:11px; font-weight:600; color:var(--color-text-muted); padding:2px 8px; }
.med-card__controls { display:flex; flex-direction:column; align-items:flex-end; gap:8px; }

.stock-button { font-size:12px; font-weight:700; border:none; cursor:pointer; background:var(--color-primary-light); color:var(--color-primary-dark); padding:5px 12px; border-radius:20px; white-space:nowrap; transition:transform .1s; }
.stock-button:active { transform:scale(.93); }
.stock-button--low { background:#fee2e2; color:#dc2626; }

.qty-row { display:flex; align-items:center; gap:6px; }
.qty-btn { width:32px; height:32px; border-radius:50%; border:2px solid var(--color-border); background:var(--color-white); font-size:18px; font-weight:700; cursor:pointer; display:flex; align-items:center; justify-content:center; color:var(--color-primary); transition:background .15s; }
.qty-btn:hover    { background:var(--color-primary-light); border-color:var(--color-primary); }
.qty-btn:disabled { opacity:.3; cursor:default; }
.btn-delete { background:none; border:none; font-size:18px; cursor:pointer; padding:4px; opacity:.6; transition:opacity .15s; }
.btn-delete:hover { opacity:1; }

.btn-add-to-rx {
  padding:6px 12px; background:var(--color-primary); color:#fff;
  border:none; border-radius:20px; font-size:12px; font-weight:700;
  font-family:var(--font-main); cursor:pointer; white-space:nowrap;
  transition:background .2s, transform .1s;
}
.btn-add-to-rx:hover  { background:var(--color-primary-dark); }
.btn-add-to-rx:active { transform:scale(.93); }

.add-btn-wrap { position:fixed; bottom:100px; left:50%; transform:translateX(-50%); width:calc(100% - 40px); max-width:440px; z-index:9; }
.btn-add { display:block; text-align:center; width:100%; padding:15px; background:var(--color-primary); color:var(--color-white); font-size:16px; font-weight:800; font-family:var(--font-main); border-radius:var(--radius-btn); text-decoration:none; box-shadow:0 4px 16px rgba(14,165,233,.35); transition:background .2s, transform .1s; }
.btn-add:hover  { background:var(--color-primary-dark); }
.btn-add:active { transform:scale(.98); }

/* Overlay + sheets */
.overlay { position:fixed; inset:0; background:rgba(0,0,0,.45); display:flex; align-items:flex-end; justify-content:center; z-index:400; }
.sheet { background:var(--color-white); border-radius:24px 24px 0 0; padding:12px 24px 40px; width:100%; max-width:500px; max-height:85vh; overflow-y:auto; display:flex; flex-direction:column; gap:10px; }
.sheet--tall { max-height:93vh; }
.sheet-handle { width:40px; height:4px; background:#cbd5e1; border-radius:2px; margin:0 auto 8px; flex-shrink:0; }
.sheet-title { font-size:19px; font-weight:800; color:var(--color-text-dark); }

/* Chosen med + list label */
.chosen-med { background:var(--color-primary-light); border-radius:12px; padding:12px 14px; }
.chosen-med__name { font-size:14px; font-weight:700; color:var(--color-primary-dark); }
.chosen-med__sub  { font-size:12px; color:var(--color-text-muted); margin-top:2px; }
.list-label { font-size:11px; font-weight:700; color:var(--color-text-muted); text-transform:uppercase; letter-spacing:.06em; }
.empty-meds { font-size:13px; color:var(--color-text-muted); padding:8px 0; }

/* Rx picker cards */
.rx-pick-card { display:flex; align-items:center; gap:12px; padding:14px 12px; background:var(--color-white); border:2px solid var(--color-border); border-radius:14px; cursor:pointer; transition:border-color .15s, background .15s; }
.rx-pick-card:hover { border-color:var(--color-primary); background:var(--color-primary-light); }
.rx-pick-icon { font-size:24px; flex-shrink:0; }
.rx-pick-body { flex:1; }
.rx-pick-name { font-size:15px; font-weight:700; color:var(--color-text-dark); }
.rx-pick-meta { font-size:12px; color:var(--color-text-muted); margin-top:2px; }
.rx-pick-arrow { font-size:20px; color:var(--color-text-muted); }

/* Schedule context */
.sched-context { background:#f8fafc; border-radius:14px; padding:14px; display:flex; flex-direction:column; gap:8px; }
.sched-context__row { display:flex; align-items:center; gap:10px; font-size:14px; }
.sched-context__row--rx { padding-top:8px; border-top:1px solid var(--color-border); }
.sched-context__name { font-size:14px; font-weight:700; color:var(--color-text-dark); }
.sched-context__sub  { font-size:12px; color:var(--color-text-muted); }

/* Time input */
.time-input-row { display:flex; gap:8px; }
.field--sm { flex:1; }
.btn-add-time { padding:0 16px; background:var(--color-primary); color:#fff; border:none; border-radius:var(--radius-input); font-size:20px; font-weight:700; cursor:pointer; }
.time-chips { display:flex; flex-wrap:wrap; gap:6px; }
.time-chip { background:var(--color-primary-light); color:var(--color-primary-dark); font-size:12px; font-weight:700; padding:4px 10px; border-radius:20px; display:flex; align-items:center; gap:4px; }
.chip-remove { background:none; border:none; color:var(--color-primary-dark); font-size:14px; cursor:pointer; padding:0; line-height:1; }

/* Day grid */
.day-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }
.day-btn { padding:10px 6px; border-radius:10px; border:2px solid var(--color-border); background:var(--color-white); font-size:13px; font-weight:600; font-family:var(--font-main); color:var(--color-text-muted); cursor:pointer; transition:all .15s; }
.day-btn--active { background:var(--color-primary); border-color:var(--color-primary); color:#fff; }

/* Shared fields/buttons */
.field-label { font-size:11px; font-weight:700; color:var(--color-text-muted); text-transform:uppercase; letter-spacing:.05em; margin-bottom:4px; margin-top:4px; }
.field { width:100%; padding:12px 14px; border:2px solid var(--color-border); border-radius:var(--radius-input); font-size:15px; font-family:var(--font-main); color:#1e293b; background:var(--color-input-bg); outline:none; box-sizing:border-box; transition:border-color .2s; }
.field:focus { border-color:var(--color-primary); }
.btn-primary { width:100%; padding:14px; background:var(--color-primary); border:none; border-radius:var(--radius-btn); color:#fff; font-size:15px; font-weight:800; font-family:var(--font-main); cursor:pointer; transition:background .2s; }
.btn-primary:hover:not(:disabled) { background:var(--color-primary-dark); }
.btn-primary:disabled { opacity:.6; cursor:not-allowed; }
.btn-ghost { width:100%; padding:12px; background:none; border:2px solid var(--color-border); border-radius:var(--radius-btn); color:var(--color-text-muted); font-size:14px; font-weight:600; font-family:var(--font-main); cursor:pointer; }
.err { font-size:13px; color:#ef4444; font-weight:600; }

/* Numpad */
.numpad-sheet { background:var(--color-white); border-radius:24px 24px 0 0; padding:12px 24px 44px; width:100%; max-width:420px; display:flex; flex-direction:column; align-items:center; gap:0; }
.numpad-label { font-size:16px; font-weight:800; color:var(--color-text-dark); text-align:center; }
.numpad-sub   { font-size:12px; color:var(--color-text-muted); margin-top:2px; margin-bottom:16px; }
.numpad-display { width:100%; background:var(--color-primary-light); border-radius:16px; padding:14px 20px; display:flex; align-items:baseline; justify-content:center; gap:8px; margin-bottom:20px; transition:background .2s; }
.numpad-display--low { background:#fee2e2; }
.numpad-value { font-size:42px; font-weight:900; color:var(--color-primary-dark); line-height:1; }
.numpad-display--low .numpad-value { color:#dc2626; }
.numpad-unit  { font-size:16px; font-weight:600; color:var(--color-text-muted); }
.numpad-grid  { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; width:100%; margin-bottom:16px; }
.numpad-key   { height:60px; border-radius:14px; border:none; background:#f1f5f9; color:var(--color-text-dark); font-size:22px; font-weight:700; font-family:var(--font-main); cursor:pointer; transition:background .1s,transform .08s; display:flex; align-items:center; justify-content:center; }
.numpad-key:active { background:var(--color-primary-light); transform:scale(.92); }
.numpad-key--action { background:#e2e8f0; color:var(--color-text-muted); font-size:18px; }
.numpad-confirm { width:100%; padding:15px; border:none; border-radius:var(--radius-btn); background:var(--color-primary); color:#fff; font-size:16px; font-weight:800; font-family:var(--font-main); cursor:pointer; transition:background .2s; margin-bottom:10px; }
.numpad-confirm:hover { background:var(--color-primary-dark); }
.numpad-cancel  { width:100%; padding:12px; border:2px solid var(--color-border); border-radius:var(--radius-btn); background:none; color:var(--color-text-muted); font-size:14px; font-weight:600; font-family:var(--font-main); cursor:pointer; }

/* Transitions */
.fade-enter-active,.fade-leave-active { transition:opacity .22s; }
.fade-enter-from,.fade-leave-to       { opacity:0; }
.slide-up-enter-active,.slide-up-leave-active { transition:transform .25s cubic-bezier(.32,1,.32,1); }
.slide-up-enter-from,.slide-up-leave-to       { transform:translateY(100%); }
</style>