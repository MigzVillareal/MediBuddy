<template>
  <div class="tab">
    <h2 class="section-title">Alarms</h2>

    <!-- Empty state -->
    <div class="empty-state" v-if="alarms.length === 0 && !showForm">
      <span class="empty-icon">🔔</span>
      <p class="empty-title">No alarms set</p>
      <p class="empty-sub">Tap <strong>+ Add Alarm</strong> below to set a medication reminder.</p>
    </div>

    <!-- Alarm list -->
    <div class="alarm-list" v-if="alarms.length > 0">
      <transition-group name="alarm-fade" tag="div" class="alarm-list-inner">
        <div
          class="alarm-card"
          v-for="alarm in sortedAlarms"
          :key="alarm.id"
          :class="{ 'alarm-card--off': !alarm.enabled }"
        >
          <!-- Left: icon + info -->
          <div class="alarm-card__left">
            <div class="alarm-icon">💊</div>
            <div class="alarm-info">
              <p class="alarm-time">{{ formatTime(alarm.time) }}</p>
              <p class="alarm-label">{{ alarm.label || 'Medication Reminder' }}</p>
              <div class="alarm-days">
                <span
                  class="day-pill"
                  v-for="d in DAYS"
                  :key="d.short"
                  :class="{ 'day-pill--active': alarm.days.includes(d.short) }"
                >{{ d.short }}</span>
              </div>
            </div>
          </div>

          <!-- Right: toggle + delete -->
          <div class="alarm-card__right">
            <label class="toggle" :for="`toggle-${alarm.id}`">
              <input
                type="checkbox"
                :id="`toggle-${alarm.id}`"
                v-model="alarm.enabled"
                @change="saveAlarms"
              />
              <span class="toggle__track"></span>
            </label>
            <button class="btn-delete" @click="deleteAlarm(alarm.id)" title="Delete alarm">🗑</button>
          </div>
        </div>
      </transition-group>
    </div>

    <!-- Add Alarm Form Modal -->
    <transition name="modal-slide">
      <div class="modal-backdrop" v-if="showForm" @click.self="cancelForm">
        <div class="modal">
          <h3 class="modal-title">New Alarm</h3>

          <!-- Time picker -->
          <div class="form-group">
            <label class="form-label" for="alarm-time">Time</label>
            <input
              id="alarm-time"
              type="time"
              class="form-input"
              v-model="newAlarm.time"
            />
          </div>

          <!-- Label -->
          <div class="form-group">
            <label class="form-label" for="alarm-label">Label</label>
            <input
              id="alarm-label"
              type="text"
              class="form-input"
              v-model="newAlarm.label"
              placeholder="e.g. Morning pills"
              maxlength="40"
            />
          </div>

          <!-- Day selector -->
          <div class="form-group">
            <label class="form-label">Repeat</label>
            <div class="day-selector">
              <button
                class="day-btn"
                v-for="d in DAYS"
                :key="d.short"
                :class="{ 'day-btn--active': newAlarm.days.includes(d.short) }"
                @click="toggleDay(d.short)"
                type="button"
              >{{ d.short }}</button>
            </div>
            <p class="repeat-hint">{{ repeatSummary }}</p>
          </div>

          <!-- Actions -->
          <div class="modal-actions">
            <button class="btn-cancel" @click="cancelForm">Cancel</button>
            <button class="btn-save" @click="addAlarm" :disabled="!newAlarm.time">Save</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Add Alarm FAB -->
    <div class="add-btn-wrap">
      <button class="btn-add" @click="openForm">+ Add Alarm</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const DAYS = [
  { short: 'Su' }, { short: 'Mo' }, { short: 'Tu' },
  { short: 'We' }, { short: 'Th' }, { short: 'Fr' }, { short: 'Sa' }
]

// ── Persistent alarm storage via localStorage ──────────────────────────────
const STORAGE_KEY = 'medibuddy_alarms'

function loadAlarms() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || []
  } catch {
    return []
  }
}

function saveAlarms() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(alarms.value))
}

const alarms = ref(loadAlarms())

// Sort alarms by time ascending
const sortedAlarms = computed(() =>
  [...alarms.value].sort((a, b) => a.time.localeCompare(b.time))
)

// ── New alarm form state ───────────────────────────────────────────────────
const showForm = ref(false)

function freshAlarm() {
  return { time: '', label: '', days: ['Mo', 'Tu', 'We', 'Th', 'Fr'] }
}

const newAlarm = ref(freshAlarm())

function openForm() {
  newAlarm.value = freshAlarm()
  showForm.value = true
}

function cancelForm() {
  showForm.value = false
}

function toggleDay(day) {
  const idx = newAlarm.value.days.indexOf(day)
  if (idx === -1) newAlarm.value.days.push(day)
  else newAlarm.value.days.splice(idx, 1)
}

const repeatSummary = computed(() => {
  const d = newAlarm.value.days
  if (d.length === 0) return 'Once (no repeat)'
  if (d.length === 7) return 'Every day'
  const weekdays = ['Mo', 'Tu', 'We', 'Th', 'Fr']
  const weekend  = ['Sa', 'Su']
  if (weekdays.every(x => d.includes(x)) && d.length === 5) return 'Weekdays'
  if (weekend.every(x => d.includes(x)) && d.length === 2) return 'Weekends'
  return d.join(', ')
})

function addAlarm() {
  if (!newAlarm.value.time) return
  alarms.value.push({
    id:      Date.now(),
    time:    newAlarm.value.time,
    label:   newAlarm.value.label.trim() || 'Medication Reminder',
    days:    [...newAlarm.value.days],
    enabled: true
  })
  saveAlarms()
  showForm.value = false
}

function deleteAlarm(id) {
  alarms.value = alarms.value.filter(a => a.id !== id)
  saveAlarms()
}

// ── Display helpers ────────────────────────────────────────────────────────
function formatTime(time24) {
  if (!time24) return ''
  const [h, m] = time24.split(':').map(Number)
  const suffix = h >= 12 ? 'PM' : 'AM'
  const h12    = h % 12 || 12
  return `${h12}:${String(m).padStart(2, '0')} ${suffix}`
}
</script>

<style scoped>
.tab { padding: 20px 20px 140px; }

.section-title {
  font-size: 20px;
  font-weight: 800;
  color: var(--color-text-dark);
  margin-bottom: 16px;
}

/* ── Empty state ── */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--color-text-muted);
}
.empty-icon  { font-size: 52px; display: block; margin-bottom: 12px; }
.empty-title { font-size: 17px; font-weight: 700; color: var(--color-text-dark); margin-bottom: 6px; }
.empty-sub   { font-size: 14px; }

/* ── Alarm list ── */
.alarm-list-inner { display: flex; flex-direction: column; gap: 12px; }

.alarm-card {
  background: var(--color-white);
  border-radius: 16px;
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  box-shadow: var(--shadow-card);
  transition: opacity 0.25s;
}
.alarm-card--off { opacity: 0.45; }

.alarm-card__left { display: flex; align-items: center; gap: 14px; flex: 1; min-width: 0; }
.alarm-icon { font-size: 28px; flex-shrink: 0; }

.alarm-info { flex: 1; min-width: 0; }
.alarm-time  { font-size: 26px; font-weight: 800; color: var(--color-text-dark); line-height: 1; }
.alarm-label { font-size: 13px; color: var(--color-text-muted); margin: 4px 0 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.alarm-days { display: flex; gap: 4px; flex-wrap: wrap; }
.day-pill {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 20px;
  background: var(--color-border);
  color: var(--color-text-muted);
}
.day-pill--active {
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
}

.alarm-card__right { display: flex; flex-direction: column; align-items: center; gap: 10px; flex-shrink: 0; }

/* ── Toggle switch ── */
.toggle { position: relative; display: inline-block; width: 46px; height: 26px; cursor: pointer; }
.toggle input { opacity: 0; width: 0; height: 0; }
.toggle__track {
  position: absolute;
  inset: 0;
  background: #cbd5e1;
  border-radius: 26px;
  transition: background 0.25s;
}
.toggle__track::after {
  content: '';
  position: absolute;
  width: 20px; height: 20px;
  border-radius: 50%;
  background: white;
  top: 3px; left: 3px;
  transition: transform 0.25s;
  box-shadow: 0 1px 4px rgba(0,0,0,.18);
}
.toggle input:checked ~ .toggle__track { background: var(--color-primary); }
.toggle input:checked ~ .toggle__track::after { transform: translateX(20px); }

.btn-delete {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
  opacity: 0.55;
  transition: opacity 0.15s;
}
.btn-delete:hover { opacity: 1; }

/* ── Add button ── */
.add-btn-wrap {
  position: fixed;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  width: calc(100% - 40px);
  max-width: 440px;
  z-index: 9;
}
.btn-add {
  display: block;
  width: 100%;
  padding: 15px;
  background: var(--color-primary);
  color: white;
  font-size: 16px;
  font-weight: 800;
  font-family: var(--font-main);
  border: none;
  border-radius: var(--radius-btn);
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(14, 165, 233, 0.35);
  transition: background 0.2s, transform 0.1s;
}
.btn-add:hover  { background: var(--color-primary-dark); }
.btn-add:active { transform: scale(0.98); }

/* ── Modal ── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: flex-end;
  z-index: 100;
}
.modal {
  width: 100%;
  max-width: 480px;
  margin: 0 auto;
  background: var(--color-white);
  border-radius: 24px 24px 0 0;
  padding: 28px 24px 40px;
}
.modal-title {
  font-size: 18px;
  font-weight: 800;
  color: var(--color-text-dark);
  margin-bottom: 20px;
}

.form-group { margin-bottom: 20px; }
.form-label {
  display: block;
  font-size: 12px;
  font-weight: 700;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}
.form-input {
  width: 100%;
  padding: 12px 14px;
  border: 2px solid var(--color-border);
  border-radius: 12px;
  background: var(--color-input-bg);
  color: var(--color-text-dark);
  font-size: 16px;
  font-family: var(--font-main);
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.form-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15);
}

/* ── Day selector ── */
.day-selector { display: flex; gap: 6px; flex-wrap: wrap; }
.day-btn {
  width: 38px; height: 38px;
  border-radius: 50%;
  border: 2px solid var(--color-border);
  background: var(--color-white);
  font-size: 11px;
  font-weight: 700;
  font-family: var(--font-main);
  cursor: pointer;
  color: var(--color-text-muted);
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}
.day-btn--active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}
.repeat-hint {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-top: 8px;
}

.modal-actions { display: flex; gap: 12px; margin-top: 8px; }
.btn-cancel {
  flex: 1;
  padding: 13px;
  background: none;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-btn);
  font-size: 15px;
  font-weight: 700;
  font-family: var(--font-main);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: border-color 0.15s;
}
.btn-cancel:hover { border-color: #94a3b8; }
.btn-save {
  flex: 1;
  padding: 13px;
  background: var(--color-primary);
  border: none;
  border-radius: var(--radius-btn);
  font-size: 15px;
  font-weight: 800;
  font-family: var(--font-main);
  color: white;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-save:hover    { background: var(--color-primary-dark); }
.btn-save:disabled { opacity: 0.4; cursor: default; }

/* ── Transitions ── */
.modal-slide-enter-active,
.modal-slide-leave-active { transition: opacity 0.25s; }
.modal-slide-enter-active .modal,
.modal-slide-leave-active .modal { transition: transform 0.3s cubic-bezier(.4,0,.2,1); }
.modal-slide-enter-from,
.modal-slide-leave-to { opacity: 0; }
.modal-slide-enter-from .modal,
.modal-slide-leave-to  .modal { transform: translateY(100%); }

.alarm-fade-enter-active,
.alarm-fade-leave-active { transition: all 0.25s ease; }
.alarm-fade-enter-from,
.alarm-fade-leave-to { opacity: 0; transform: translateY(8px); }
</style>
