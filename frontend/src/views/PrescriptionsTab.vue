<template>
  <div class="tab">

    <!-- Circle context switcher -->
    <div class="ctx-bar" v-if="circles.length > 0">
      <button class="ctx-btn" :class="{ 'ctx-btn--active': isOwn }" @click="selectOwn(); loadPrescriptions()">📁 My Rx</button>
      <button
        v-for="c in circles" :key="c.circle_id"
        class="ctx-btn"
        :class="{ 'ctx-btn--active': activeCircle?.circle_id === c.circle_id }"
        @click="selectCircle(c); loadPrescriptions()"
      >👤 {{ c.circle_name }}</button>
    </div>
    <div class="readonly-banner" v-if="!isOwn">👁 Viewing <strong>{{ activeCircle.owner_username }}</strong>'s prescriptions — read only</div>

    <!-- ── HEADER ────────────────────────────────────────────── -->
    <div class="header-row">
      <div>
        <h2 class="section-title">{{ isOwn ? 'Prescriptions' : activeCircle.owner_username + "'s Rx" }}</h2>
        <p class="section-sub">Doctor-issued prescriptions and medication schedules.</p>
      </div>
      <button class="btn-new" v-if="isOwn" @click="openCreate">+ New Rx</button>
    </div>

    <!-- ── EMPTY / LOADING ───────────────────────────────────── -->
    <div class="hint" v-if="loading">
      <span class="hint-icon">⏳</span><p>Loading…</p>
    </div>
    <div class="empty-state" v-else-if="prescriptions.length === 0">
      <span class="empty-icon">📋</span>
      <p class="empty-title">No prescriptions yet</p>
      <p class="empty-sub">Create a prescription, then add medicines from your Shelf.</p>
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
      <Transition name="fade">
        <div class="overlay" v-if="showCreate" @click.self="showCreate = false">
          <Transition name="slide-up">
            <div class="sheet" v-if="showCreate">
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
          </Transition>
        </div>
      </Transition>
    </Teleport>

    <!-- ── PRESCRIPTION DETAIL SHEET ─────────────────────────── -->
    <Teleport to="body">
      <Transition name="fade">
        <div class="overlay" v-if="activeRx" @click.self="closeDetail">
          <Transition name="slide-up">
            <div class="sheet sheet--tall" v-if="activeRx">
              <div class="sheet-handle"></div>

              <!-- Header -->
              <div class="detail-header">
                <div class="detail-header__info">
                  <h3 class="sheet-title">{{ activeRx.name }}</h3>
                  <p class="detail-meta" v-if="activeRx.doctor">
                    Dr. {{ activeRx.doctor }}<span v-if="activeRx.date"> · {{ formatDate(activeRx.date) }}</span>
                  </p>
                  <p class="detail-meta" v-if="activeRx.detail">{{ activeRx.detail }}</p>
                </div>
                <div class="detail-header__actions">
                  <button
                    v-if="isOwn"
                    class="btn-alarm btn-alarm--lg"
                    :class="activeRx.alarm_active ? 'btn-alarm--on' : 'btn-alarm--off'"
                    @click="toggleRxAlarm(activeRx)"
                    :title="activeRx.alarm_active ? 'Disable notifications' : 'Enable notifications'"
                  >{{ activeRx.alarm_active ? '🔔' : '🔕' }}</button>
                  <button class="btn-del-rx" v-if="isOwn" @click="deleteRx" title="Delete prescription">🗑</button>
                </div>
              </div>

              <p class="err" v-if="detailError">{{ detailError }}</p>

              <!-- Medicine list -->
              <p class="list-label">Medicines in this prescription</p>
              <div class="hint-sm" v-if="loadingDetails">⏳ Loading medicines…</div>
              <div class="empty-meds" v-else-if="rxDetails.length === 0">
                <span>💊</span>
                <p>No medicines yet.</p>
                <p class="empty-meds__sub">Go to your Shelf and tap <strong>+ Add to Rx</strong> on a medicine to add it here.</p>
              </div>

              <div class="med-row" v-for="d in rxDetails" :key="d.prescription_detail_id">
                <div class="med-row__info">
                  <div class="med-row__name-row">
                    <span class="med-row__name">{{ d.brand_name }}</span>
                  </div>
                  <p class="med-row__generic" v-if="d.generic_name">{{ d.generic_name }}</p>
                  <div class="sched-chips">
                    <span class="chip chip--blue" v-if="d.days_taken">{{ d.days_taken }}</span>
                    <span
                      class="chip chip--purple"
                      v-for="t in (d.time_taken ? d.time_taken.split(',') : [])"
                      :key="t"
                    >{{ t.trim() }}</span>
                    <span class="chip chip--green" v-if="d.date_start">From {{ formatDate(d.date_start) }}</span>
                    <span class="chip" v-if="d.date_end">Until {{ formatDate(d.date_end) }}</span>
                  </div>
                </div>

                <!-- stock controls (owner only) -->
                <div class="med-row__stock" v-if="isOwn">
                  <button
                    class="stock-badge stock-badge--btn"
                    :class="{ 'stock-badge--low': d.quantity != null && d.quantity <= 5 }"
                    @click="openNumpad(d)"
                  >{{ d.quantity != null ? d.quantity + ' left' : '—' }}</button>
                  <div class="qty-row">
                    <button class="qty-btn" @click="changeStock(d, -1)" :disabled="d.quantity == null || d.quantity <= 0">−</button>
                    <button class="qty-btn" @click="changeStock(d, +1)" :disabled="d.quantity == null">+</button>
                  </div>
                </div>
                <span
                  v-else-if="d.quantity != null"
                  class="stock-badge"
                  :class="{ 'stock-badge--low': d.quantity <= 5 }"
                >{{ d.quantity }} left</span>

                <button
                  class="btn-alarm"
                  :class="d.alarm_active ? 'btn-alarm--on' : 'btn-alarm--off'"
                  @click="toggleDetailAlarm(d)"
                  :title="d.alarm_active ? 'Disable alarm' : 'Enable alarm'"
                >{{ d.alarm_active ? '🔔' : '🔕' }}</button>
                <button class="btn-remove" v-if="isOwn" @click="removeDetail(d)">✕</button>
              </div>

              <div class="shelf-hint" v-if="rxDetails.length > 0">
                <span>💡</span> To add more medicines, go to your Shelf and tap <strong>+ Add to Rx</strong>.
              </div>

              <button class="btn-ghost" @click="closeDetail" style="margin-top:12px">Close</button>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>

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
                <button class="numpad-key" v-for="key in ['1','2','3','4','5','6','7','8','9']" :key="key" @click="pressKey(key)">{{ key }}</button>
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

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/api'
import { circles, activeCircle, isOwn, loadCircles, selectCircle, selectOwn } from '@/composables/useCircleContext'

// ── STATE ──────────────────────────────────────────────────────────────────────
const prescriptions   = ref([])
const loading         = ref(false)
const showCreate      = ref(false)
const isCreating      = ref(false)
const createError     = ref('')

const form = reactive({ name: '', doctor: '', date: '', detail: '' })

const activeRx       = ref(null)
const rxDetails      = ref([])
const loadingDetails = ref(false)
const detailError    = ref('')

// ── NUMPAD (stock editor) ─────────────────────────────────────────────────────
const numpadTarget  = ref(null)
const numpadRaw     = ref('')
const numpadDisplay = computed(() => numpadRaw.value === '' ? '0' : numpadRaw.value)

function openNumpad(d) {
  numpadTarget.value = d
  numpadRaw.value    = d.quantity != null && d.quantity > 0 ? String(d.quantity) : ''
}
function closeNumpad() { numpadTarget.value = null; numpadRaw.value = '' }
function pressKey(key) {
  if (key === 'C')  { numpadRaw.value = ''; return }
  if (key === '⌫')  { numpadRaw.value = numpadRaw.value.slice(0, -1); return }
  if (numpadRaw.value.length >= 4) return
  if (numpadRaw.value === '' && key === '0') return
  numpadRaw.value += key
}
async function confirmNumpad() {
  const d = numpadTarget.value
  if (d.supply_id == null) { closeNumpad(); return }
  const newQty = Math.max(0, parseInt(numpadDisplay.value, 10) || 0)
  const prev = d.quantity
  d.quantity = newQty
  closeNumpad()
  try { await api.patch(`/meds/drug_stock/${d.supply_id}`, { supply_stock: newQty }) }
  catch (err) { d.quantity = prev; console.error(err) }
}
async function changeStock(d, delta) {
  if (d.supply_id == null) return
  const newQty = (d.quantity ?? 0) + delta
  if (newQty < 0) return
  d.quantity = newQty
  try { await api.patch(`/meds/drug_stock/${d.supply_id}`, { supply_stock: newQty }) }
  catch (err) { d.quantity -= delta; console.error(err) }
}

// ── HELPERS ────────────────────────────────────────────────────────────────────
function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('en-PH', { year: 'numeric', month: 'short', day: 'numeric' })
}

// ── INIT ───────────────────────────────────────────────────────────────────────
onMounted(async () => { await loadCircles(); await loadPrescriptions() })

async function loadPrescriptions() {
  loading.value = true
  try {
    const url = activeCircle.value
      ? `/circle/${activeCircle.value.circle_id}/prescriptions`
      : '/prescriptions/'
    prescriptions.value = (await api.get(url)).data
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

// ── CREATE Rx ──────────────────────────────────────────────────────────────────
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
      name:   form.name.trim(),
      doctor: form.doctor.trim() || null,
      date:   form.date || null,
      detail: form.detail.trim() || null,
    })
    showCreate.value = false
    await loadPrescriptions()
  } catch (e) {
    createError.value = e.response?.data?.error || 'Failed to create prescription.'
  } finally { isCreating.value = false }
}

// ── ALARM TOGGLES ──────────────────────────────────────────────────────────────

// Toggle alarm on the prescription itself (header bell)
async function toggleRxAlarm(rx) {
  const prev = rx.alarm_active
  rx.alarm_active = !prev
  try {
    let onesignal_id = null
    if (!prev) {
      try {
        await window.OneSignal.Notifications.requestPermission()
        onesignal_id = window.OneSignal.User.PushSubscription.id
      } catch (e) { console.warn('OneSignal not available:', e) }
    }
    const res = await api.patch(`/prescriptions/${rx.prescription_id}/alarm`, { onesignal_id })
    rx.alarm_active = res.data.alarm_active
  } catch (e) {
    rx.alarm_active = prev
    console.error('Failed to toggle prescription alarm:', e)
  }
}

// Toggle alarm on a prescription detail (individual medicine row)
async function toggleDetailAlarm(d) {
  const prev = d.alarm_active
  d.alarm_active = !prev
  try {
    let onesignal_id = null
    if (!prev) {
      try {
        await window.OneSignal.Notifications.requestPermission()
        onesignal_id = window.OneSignal.User.PushSubscription.id
      } catch (e) { console.warn('OneSignal not available:', e) }
    }
    const res = await api.patch(
      `/prescriptions/${activeRx.value.prescription_id}/details/${d.prescription_detail_id}/alarm`,
      { onesignal_id }
    )
    d.alarm_active = res.data.alarm_active
  } catch (e) {
    d.alarm_active = prev
    console.error('Failed to toggle detail alarm:', e)
  }
}

// ── DETAIL ─────────────────────────────────────────────────────────────────────
async function openDetail(rx) {
  activeRx.value    = rx
  detailError.value = ''
  await loadDetails()
}

function closeDetail() {
  activeRx.value  = null
  rxDetails.value = []
}

async function loadDetails() {
  if (!activeRx.value) return
  loadingDetails.value = true
  try {
    const url = activeCircle.value
      ? `/circle/${activeCircle.value.circle_id}/prescriptions/${activeRx.value.prescription_id}/details`
      : `/prescriptions/${activeRx.value.prescription_id}/details`
    rxDetails.value = (await api.get(url)).data
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
    const url = activeCircle.value
      ? `/circle/${activeCircle.value.circle_id}/prescriptions/${activeRx.value.prescription_id}/details/${d.prescription_detail_id}`
      : `/prescriptions/${activeRx.value.prescription_id}/details/${d.prescription_detail_id}`
    await api.delete(url)
    await loadDetails()
  } catch (e) { detailError.value = e.response?.data?.error || 'Remove failed.' }
}
</script>

<style scoped>
.tab { padding: 20px 20px 100px; }

/* Circle context bar */
.ctx-bar { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:14px; }
.ctx-btn { flex-shrink:0; padding:7px 14px; border-radius:20px; border:2px solid var(--color-border); background:var(--color-white); font-size:13px; font-weight:600; font-family:var(--font-main); color:var(--color-text-muted); cursor:pointer; white-space:nowrap; transition:all .15s; }
.ctx-btn--active { background:var(--color-primary); border-color:var(--color-primary); color:#fff; }
.ctx-btn:hover:not(.ctx-btn--active) { border-color:var(--color-primary); color:var(--color-primary); }
.readonly-banner { background:#fef9c3; border:1.5px solid #fde68a; border-radius:10px; padding:9px 14px; font-size:13px; color:#92400e; margin-bottom:12px; }

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
.hint-sm { font-size:13px; color:var(--color-text-muted); padding:8px 0; }

/* rx cards */
.rx-list { display:flex; flex-direction:column; gap:12px; }
.rx-card {
  background:var(--color-white); border-radius:16px; padding:16px;
  display:flex; align-items:center; gap:14px;
  box-shadow:var(--shadow-card); cursor:pointer;
  transition:transform .15s, box-shadow .15s;
}
.rx-card:hover { transform:translateY(-2px); box-shadow:0 6px 24px rgba(0,0,0,.1); }
.rx-card__icon { font-size:28px; flex-shrink:0; }
.rx-card__body { flex:1; }
.rx-card__name { font-size:16px; font-weight:700; color:var(--color-text-dark); }
.rx-card__meta { font-size:12px; color:var(--color-text-muted); margin-top:3px; }
.rx-card__arrow { font-size:22px; color:var(--color-text-muted); }

/* alarm toggle */
.btn-alarm {
  flex-shrink:0; width:36px; height:36px; border-radius:50%; border:none;
  font-size:18px; cursor:pointer; display:flex; align-items:center; justify-content:center;
  transition:background .2s, transform .1s;
}
.btn-alarm:active { transform:scale(.88); }
.btn-alarm--on  { background:#dcfce7; }
.btn-alarm--off { background:#f1f5f9; }
.btn-alarm--lg  { width:40px; height:40px; font-size:20px; }

/* overlay + sheet */
.overlay { position:fixed; inset:0; background:rgba(0,0,0,.45); display:flex; align-items:flex-end; justify-content:center; z-index:300; }
.sheet {
  background:var(--color-white); border-radius:24px 24px 0 0;
  padding:12px 24px 40px; width:100%; max-width:500px;
  max-height:85vh; overflow-y:auto;
  display:flex; flex-direction:column; gap:10px;
}
.sheet--tall { max-height:93vh; }
.sheet-handle { width:40px; height:4px; background:#cbd5e1; border-radius:2px; margin:0 auto 8px; flex-shrink:0; }
.sheet-title { font-size:19px; font-weight:800; color:var(--color-text-dark); }

/* detail header */
.detail-header { display:flex; align-items:flex-start; justify-content:space-between; gap:8px; }
.detail-header__info { flex:1; }
.detail-header__actions { display:flex; align-items:center; gap:6px; flex-shrink:0; }
.detail-meta { font-size:13px; color:var(--color-text-muted); margin-top:3px; }
.btn-del-rx { background:none; border:none; font-size:20px; cursor:pointer; padding:4px; }

/* list-label */
.list-label { font-size:11px; font-weight:700; color:var(--color-text-muted); text-transform:uppercase; letter-spacing:.06em; margin-top:4px; }

/* empty meds */
.empty-meds { text-align:center; padding:24px 16px; color:var(--color-text-muted); font-size:14px; }
.empty-meds span { font-size:36px; display:block; margin-bottom:8px; }
.empty-meds p { margin-bottom:4px; }
.empty-meds__sub { font-size:12px; }

/* shelf hint */
.shelf-hint { background:var(--color-primary-light); border-radius:10px; padding:10px 14px; font-size:12px; color:var(--color-primary-dark); margin-top:8px; }

/* med rows */
.med-row { display:flex; align-items:center; gap:10px; padding:12px 0; border-bottom:1px solid var(--color-border); }
.med-row__info { flex:1; min-width:0; }
.med-row__name-row { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
.med-row__name { font-size:14px; font-weight:700; color:var(--color-text-dark); }
.med-row__generic { font-size:12px; color:var(--color-text-muted); margin-top:2px; }
.med-row__stock { display:flex; flex-direction:column; align-items:flex-end; gap:5px; flex-shrink:0; }
.stock-badge--btn { cursor:pointer; border:none; font-family:var(--font-main); transition:transform .1s; }
.stock-badge--btn:active { transform:scale(.93); }
.qty-row { display:flex; align-items:center; gap:5px; }
.qty-btn { width:28px; height:28px; border-radius:50%; border:2px solid var(--color-border); background:var(--color-white); font-size:15px; font-weight:700; cursor:pointer; display:flex; align-items:center; justify-content:center; color:var(--color-primary); transition:background .15s; }
.qty-btn:hover { background:var(--color-primary-light); border-color:var(--color-primary); }
.qty-btn:disabled { opacity:.3; cursor:default; }
.sched-chips { display:flex; flex-wrap:wrap; gap:5px; margin-top:7px; }

/* stock badge */
.stock-badge {
  font-size:11px; font-weight:700; padding:2px 8px; border-radius:20px;
  background:var(--color-primary-light); color:var(--color-primary-dark);
}
.stock-badge--low { background:#fee2e2; color:#dc2626; }

/* chips */
.chip { font-size:11px; font-weight:600; padding:3px 8px; border-radius:20px; background:#e2e8f0; color:#64748b; }
.chip--blue   { background:#e0f2fe; color:#0369a1; }
.chip--green  { background:#dcfce7; color:#15803d; }
.chip--purple { background:#ede9fe; color:#7c3aed; }

/* remove button */
.btn-remove { width:28px; height:28px; border-radius:50%; border:none; background:#fee2e2; color:#ef4444; font-size:13px; cursor:pointer; display:flex; align-items:center; justify-content:center; transition:background .2s; flex-shrink:0; margin-top:2px; }
.btn-remove:hover { background:#ef4444; color:#fff; }

/* shared fields / buttons */
.field-label { font-size:11px; font-weight:700; color:var(--color-text-muted); text-transform:uppercase; letter-spacing:.05em; margin-bottom:4px; margin-top:4px; }
.field { width:100%; padding:12px 14px; border:2px solid var(--color-border); border-radius:var(--radius-input); font-size:15px; font-family:var(--font-main); color:#1e293b; background:var(--color-input-bg); outline:none; box-sizing:border-box; transition:border-color .2s; resize:none; }
.field:focus { border-color:var(--color-primary); }
.field--ta { resize:vertical; }
.btn-primary { width:100%; padding:14px; background:var(--color-primary); border:none; border-radius:var(--radius-btn); color:#fff; font-size:15px; font-weight:800; font-family:var(--font-main); cursor:pointer; transition:background .2s; }
.btn-primary:hover:not(:disabled) { background:var(--color-primary-dark); }
.btn-primary:disabled { opacity:.6; cursor:not-allowed; }
.btn-ghost { width:100%; padding:12px; background:none; border:2px solid var(--color-border); border-radius:var(--radius-btn); color:var(--color-text-muted); font-size:14px; font-weight:600; font-family:var(--font-main); cursor:pointer; }
.err { font-size:13px; color:#ef4444; font-weight:600; }

/* numpad */
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
.fade-enter-active, .fade-leave-active { transition:opacity .22s; }
.fade-enter-from, .fade-leave-to       { opacity:0; }
.slide-up-enter-active, .slide-up-leave-active { transition:transform .25s cubic-bezier(.32,1,.32,1); }
.slide-up-enter-from, .slide-up-leave-to       { transform:translateY(100%); }
</style>