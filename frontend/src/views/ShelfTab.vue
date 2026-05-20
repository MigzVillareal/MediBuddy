<template>
  <div class="tab">
    <h2 class="section-title">My Shelf</h2>

    <!-- Loading state -->
    <div class="hint" v-if="loading">
      <span class="hint-icon">⏳</span>
      <p>Loading your medications...</p>
    </div>

    <!-- Empty state -->
    <div class="empty-state" v-else-if="medications.length === 0">
      <span class="empty-icon">💊</span>
      <p class="empty-title">No medications yet</p>
      <p class="empty-sub">Tap <strong>+ Add Medicine</strong> below to get started.</p>
    </div>

    <!-- Medication cards -->
    <div class="med-list" v-else>
      <div class="med-card" v-for="med in medications" :key="med.supply_id">

        <!-- Name + details -->
        <div class="med-card__info">
          <p class="med-card__brand">{{ med.brand_name }}</p>
          <p class="med-card__generic">{{ med.generic_name }}</p>
          <span class="med-card__form">{{ med.dosage_strength }}</span>
          <span class="med-card__form">{{ truncateAtBracket(med.dosage_form) }}</span>
          <span class="med-card__form">{{ truncateAtBracket(med.category) }}</span>
          <span class="med-card__exp" v-if="med.expiration_date">Expiry: {{ med.expiration_date }}</span>
        </div>

        <!-- Stock controls -->
        <div class="med-card__controls">
          <button
            class="stock-button"
            :class="{ 'stock-button--low': med.supply_stock <= 5 }"
            @click="openNumpad(med)"
            title="Tap to set quantity"
          >
            {{ med.supply_stock }} left
          </button>

          <div class="qty-row">
            <button class="qty-btn" @click="changeStock(med, -1)" :disabled="med.supply_stock <= 0">−</button>
            <button class="qty-btn" @click="changeStock(med, +1)">+</button>

            <!-- Delete -->
            <button class="btn-delete" @click="deleteMed(med)">🗑</button>
            <button class="btn-add-to-rx" @click="addToPrescription(med)">+ Add to Rx</button>
          </div>
        </div>

      </div>
    </div>

    <!-- + Add Medicine button fixed above bottom nav -->
    <div class="add-btn-wrap">
      <router-link to="/medicine-search" class="btn-add">+ Add Medicine</router-link>
    </div>

    <!-- ── NUMPAD SHEET ───────────────────────────────────────── -->
    <Teleport to="body">
      <Transition name="fade">
        <div class="overlay" v-if="numpadTarget" @click.self="closeNumpad">
          <Transition name="slide-up">
            <div class="numpad-sheet" v-if="numpadTarget">
              <div class="sheet-handle"></div>

              <!-- Medicine name + current stock -->
              <p class="numpad-label">{{ numpadTarget.brand_name }}</p>
              <p class="numpad-sub">Set stock quantity</p>

              <!-- Display -->
              <div class="numpad-display" :class="{ 'numpad-display--low': numpadDisplay !== '0' && +numpadDisplay <= 5 }">
                <span class="numpad-value">{{ numpadDisplay }}</span>
                <span class="numpad-unit">pcs</span>
              </div>

              <!-- Keys -->
              <div class="numpad-grid">
                <button
                  class="numpad-key"
                  v-for="key in numKeys"
                  :key="key"
                  @click="pressKey(key)"
                >{{ key }}</button>

                <!-- bottom row: Clear | 0 | ⌫ -->
                <button class="numpad-key numpad-key--action" @click="pressKey('C')">C</button>
                <button class="numpad-key" @click="pressKey('0')">0</button>
                <button class="numpad-key numpad-key--action" @click="pressKey('⌫')">⌫</button>
              </div>

              <!-- Confirm -->
              <button class="numpad-confirm" @click="confirmNumpad">
                ✓ &nbsp; Set to {{ numpadDisplay }} pcs
              </button>
              <button class="numpad-cancel" @click="closeNumpad">Cancel</button>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api'
import { shelfBridge } from '@/composables/useShelfBridge'

const medications  = ref([])
const loading      = ref(true)

// ── Numpad state ───────────────────────────────────────────────
const numpadTarget  = ref(null)   // the med being edited
const numpadRaw     = ref('')     // raw digit string e.g. "125"

const numKeys = ['1','2','3','4','5','6','7','8','9']

const numpadDisplay = computed(() => numpadRaw.value === '' ? '0' : numpadRaw.value)

function openNumpad(med) {
  numpadTarget.value = med
  numpadRaw.value    = med.supply_stock > 0 ? String(med.supply_stock) : ''
}

function closeNumpad() {
  numpadTarget.value = null
  numpadRaw.value    = ''
}

function pressKey(key) {
  if (key === 'C')  { numpadRaw.value = ''; return }
  if (key === '⌫')  { numpadRaw.value = numpadRaw.value.slice(0, -1); return }
  if (numpadRaw.value.length >= 4) return   // cap at 9999
  // Prevent leading zeros
  if (numpadRaw.value === '' && key === '0') return
  numpadRaw.value += key
}

async function confirmNumpad() {
  const med    = numpadTarget.value
  const newQty = Math.max(0, parseInt(numpadDisplay.value, 10) || 0)
  const prev   = med.supply_stock
  med.supply_stock = newQty
  closeNumpad()
  try {
    await api.patch(`/meds/drug_stock/${med.supply_id}`, { supply_stock: newQty })
  } catch (err) {
    med.supply_stock = prev
    console.error('Failed to update stock:', err)
  }
}

function truncateAtBracket(str) {
  if (!str) return ''
  const i = Math.min(
    str.includes('(') ? str.indexOf('(') : Infinity,
    str.includes('[') ? str.indexOf('[') : Infinity
  )
  return i === Infinity ? str.trim() : str.slice(0, i).trim()
}

function addToPrescription(med) {
  shelfBridge.pendingMed = {
    lookup_id:    med.lookup_id,   // adjust to whatever field your med object has
    brand_name:   med.brand_name,
    generic_name: med.generic_name,
    dosage_form:  med.dosage_form,
  }
  // switch to prescriptions tab — adjust to however your tab routing works
  shelfBridge.targetTab = 'prescriptions'
}


// ── Stock ±1 ───────────────────────────────────────────────────
async function changeStock(med, delta) {
  const newQty = med.supply_stock + delta
  if (newQty < 0) return
  med.supply_stock = newQty
  try {
    await api.patch(`/meds/drug_stock/${med.supply_id}`, { supply_stock: newQty })
  } catch (err) {
    med.supply_stock -= delta
    console.error('Failed to update stock:', err)
  }
}

// ── Delete ─────────────────────────────────────────────────────
async function deleteMed(med) {
  medications.value = medications.value.filter(m => m.supply_id !== med.supply_id)
  try {
    await api.delete(`/meds/drug_stock/${med.supply_id}`)
  } catch (err) {
    medications.value.push(med)
    console.error('Failed to delete medication:', err)
  }
}

async function fetchMedications() {
  loading.value = true
  try {
    const res = await api.get('/meds/drug_stock')
    medications.value = res.data
  } catch (err) {
    console.error('Failed to load medications:', err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchMedications)
</script>

<style scoped>
.tab { padding: 20px 20px 140px; }

.section-title { font-size: 20px; font-weight: 800; color: var(--color-text-dark); margin-bottom: 16px; }

.hint, .empty-state { text-align: center; padding: 60px 20px; color: var(--color-text-muted); }
.hint-icon, .empty-icon { font-size: 48px; display: block; margin-bottom: 12px; }
.empty-title { font-size: 17px; font-weight: 700; color: var(--color-text-dark); margin-bottom: 6px; }
.empty-sub   { font-size: 14px; }

.med-list { display: flex; flex-direction: column; gap: 12px; }
.med-card {
  background: var(--color-white); border-radius: 14px; padding: 14px 16px;
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px; box-shadow: var(--shadow-card);
}
.med-card__info { flex: 1; }
.med-card__brand   { font-size: 15px; font-weight: 700; color: var(--color-text-dark); }
.med-card__generic { font-size: 12px; color: var(--color-text-muted); margin-top: 2px; }
.med-card__form {
  display: inline-block; margin-top: 6px; margin-right: 6px;
  font-size: 11px; font-weight: 700; background: var(--color-primary-light);
  color: var(--color-primary-dark); padding: 2px 8px; border-radius: 20px;
}
.med-card__exp {
  display: inline-block; margin-top: 6px; margin-right: 6px;
  font-size: 11px; font-weight: 700; background: var(--color-primary-muted);
  color: var(--color-primary-muted); padding: 2px 8px; border-radius: 20px;
}

.med-card__controls { display: flex; flex-direction: column; align-items: flex-end; gap: 8px; }

.stock-button {
  font-size: 12px; font-weight: 700; border: none; cursor: pointer;
  background: var(--color-primary-light); color: var(--color-primary-dark);
  padding: 5px 12px; border-radius: 20px; white-space: nowrap;
  transition: transform .1s, box-shadow .1s;
}
.stock-button:active { transform: scale(.93); }
.stock-button--low { background: #fee2e2; color: #dc2626; }

.qty-row { display: flex; align-items: center; gap: 6px; }
.qty-btn {
  width: 32px; height: 32px; border-radius: 50%; border: 2px solid var(--color-border);
  background: var(--color-white); font-size: 18px; font-weight: 700; cursor: pointer;
  display: flex; align-items: center; justify-content: center; color: var(--color-primary);
  transition: background .15s, border-color .15s;
}
.qty-btn:hover    { background: var(--color-primary-light); border-color: var(--color-primary); }
.qty-btn:disabled { opacity: .3; cursor: default; }
.btn-delete { background: none; border: none; font-size: 18px; cursor: pointer; padding: 4px; opacity: .6; transition: opacity .15s; }
.btn-delete:hover { opacity: 1; }

.btn-add-to-rx{
  
}

.add-btn-wrap {
  position: fixed; bottom: 100px; left: 50%; transform: translateX(-50%);
  width: calc(100% - 40px); max-width: 440px; z-index: 9;
}
.btn-add {
  display: block; text-align: center; width: 100%; padding: 15px;
  background: var(--color-primary); color: var(--color-white);
  font-size: 16px; font-weight: 800; font-family: var(--font-main);
  border-radius: var(--radius-btn); text-decoration: none;
  box-shadow: 0 4px 16px rgba(14,165,233,.35); transition: background .2s, transform .1s;
}
.btn-add:hover  { background: var(--color-primary-dark); }
.btn-add:active { transform: scale(.98); }

/* ── Overlay ── */
.overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,.45);
  display: flex; align-items: flex-end; justify-content: center; z-index: 400;
}

/* ── Numpad sheet ── */
.numpad-sheet {
  background: var(--color-white); border-radius: 24px 24px 0 0;
  padding: 12px 24px 44px; width: 100%; max-width: 420px;
  display: flex; flex-direction: column; align-items: center; gap: 0;
}
.sheet-handle { width: 40px; height: 4px; background: #cbd5e1; border-radius: 2px; margin-bottom: 16px; }

.numpad-label { font-size: 16px; font-weight: 800; color: var(--color-text-dark); text-align: center; }
.numpad-sub   { font-size: 12px; color: var(--color-text-muted); margin-top: 2px; margin-bottom: 16px; }

/* Display */
.numpad-display {
  width: 100%; background: var(--color-primary-light);
  border-radius: 16px; padding: 14px 20px;
  display: flex; align-items: baseline; justify-content: center;
  gap: 8px; margin-bottom: 20px; transition: background .2s;
}
.numpad-display--low { background: #fee2e2; }
.numpad-value { font-size: 42px; font-weight: 900; color: var(--color-primary-dark); line-height: 1; }
.numpad-display--low .numpad-value { color: #dc2626; }
.numpad-unit  { font-size: 16px; font-weight: 600; color: var(--color-text-muted); }

/* Key grid — 3 cols for 1-9, then bottom row */
.numpad-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  width: 100%;
  margin-bottom: 16px;
}
.numpad-key {
  height: 60px; border-radius: 14px; border: none;
  background: #f1f5f9; color: var(--color-text-dark);
  font-size: 22px; font-weight: 700; font-family: var(--font-main);
  cursor: pointer; transition: background .1s, transform .08s;
  display: flex; align-items: center; justify-content: center;
  -webkit-tap-highlight-color: transparent;
}
.numpad-key:active { background: var(--color-primary-light); transform: scale(.92); }
.numpad-key--action { background: #e2e8f0; color: var(--color-text-muted); font-size: 18px; }
.numpad-key--action:active { background: #cbd5e1; }

/* Confirm / cancel */
.numpad-confirm {
  width: 100%; padding: 15px; border: none; border-radius: var(--radius-btn);
  background: var(--color-primary); color: #fff;
  font-size: 16px; font-weight: 800; font-family: var(--font-main);
  cursor: pointer; transition: background .2s; margin-bottom: 10px;
}
.numpad-confirm:hover { background: var(--color-primary-dark); }
.numpad-cancel {
  width: 100%; padding: 12px; border: 2px solid var(--color-border); border-radius: var(--radius-btn);
  background: none; color: var(--color-text-muted);
  font-size: 14px; font-weight: 600; font-family: var(--font-main); cursor: pointer;
}

/* ── Transitions ── */
.fade-enter-active, .fade-leave-active { transition: opacity .22s; }
.fade-enter-from,  .fade-leave-to      { opacity: 0; }

.slide-up-enter-active, .slide-up-leave-active { transition: transform .25s cubic-bezier(.32,1,.32,1); }
.slide-up-enter-from,   .slide-up-leave-to     { transform: translateY(100%); }
</style>