<template>
  <div class="tab">
    <h2 class="section-title">My Medications</h2>

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
      <div class="med-card" v-for="med in medications" :key="med.id">

        <!-- Name + details -->
        <div class="med-card__info">
          <p class="med-card__brand">{{ med.brand_name }}</p>
          <p class="med-card__generic">{{ med.generic_name }}</p>
          <span class="med-card__form">{{ med.dosage_form }}</span>
        </div>

        <!-- Stock controls -->
        <div class="med-card__controls">
          <!-- Stock badge — turns red when 5 or below -->
          <span class="stock-badge" :class="{ 'stock-badge--low': med.quantity <= 5 }">
            {{ med.quantity }} left
          </span>

          <div class="qty-row">
            <!-- Minus -->
            <button
              class="qty-btn"
              @click="changeStock(med, -1)"
              :disabled="med.quantity <= 0"
            >−</button>

            <!-- Plus -->
            <button class="qty-btn" @click="changeStock(med, +1)">+</button>

            <!-- Delete -->
            <button class="btn-delete" @click="deleteMed(med)">🗑</button>
          </div>
        </div>

      </div>
    </div>

    <!-- + Add Medicine button fixed above bottom nav -->
    <div class="add-btn-wrap">
      <router-link to="/medicine-search" class="btn-add">+ Add Medicine</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const medications = ref([])
const loading     = ref(true)

// ── Fetch medications from backend on component mount ──────────────────────
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

// ── Increment or decrement stock by 1 ──────────────────────────────────────
async function changeStock(med, delta) {
  const newQty = med.quantity + delta
  if (newQty < 0) return

  // Optimistic update — update UI immediately, then sync to backend
  med.quantity = newQty

  try {
    await api.patch(`/meds/drug_stock/${med.id}`, { quantity: newQty })
  } catch (err) {
    // Revert if the request failed
    med.quantity -= delta
    console.error('Failed to update stock:', err)
  }
}

// ── Delete a medication ────────────────────────────────────────────────────
async function deleteMed(med) {
  // Remove from list immediately for snappy UI
  medications.value = medications.value.filter(m => m.id !== med.id)

  try {
    await api.delete(`/meds/drug_stock/${med.id}`)
  } catch (err) {
    // Put it back if delete failed
    medications.value.push(med)
    console.error('Failed to delete medication:', err)
  }
}

// Run on mount
onMounted(fetchMedications)
</script>

<style scoped>
.tab { padding: 20px 20px 140px; } /* extra bottom padding for the fixed button */

.section-title {
  font-size: 20px;
  font-weight: 800;
  color: var(--color-text-dark);
  margin-bottom: 16px;
}

/* ── Empty / loading state ── */
.hint, .empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--color-text-muted);
}
.hint-icon, .empty-icon { font-size: 48px; display: block; margin-bottom: 12px; }
.empty-title { font-size: 17px; font-weight: 700; color: var(--color-text-dark); margin-bottom: 6px; }
.empty-sub   { font-size: 14px; }

/* ── Medication cards ── */
.med-list { display: flex; flex-direction: column; gap: 12px; }

.med-card {
  background: var(--color-white);
  border-radius: 14px;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  box-shadow: var(--shadow-card);
}

.med-card__info { flex: 1; }
.med-card__brand   { font-size: 15px; font-weight: 700; color: var(--color-text-dark); }
.med-card__generic { font-size: 12px; color: var(--color-text-muted); margin-top: 2px; }
.med-card__form {
  display: inline-block;
  margin-top: 6px;
  font-size: 11px;
  font-weight: 700;
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  padding: 2px 8px;
  border-radius: 20px;
}

/* ── Right side controls ── */
.med-card__controls {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.stock-badge {
  font-size: 12px;
  font-weight: 700;
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  padding: 3px 10px;
  border-radius: 20px;
  white-space: nowrap;
}
.stock-badge--low { background: #fee2e2; color: #dc2626; }

.qty-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.qty-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid var(--color-border);
  background: var(--color-white);
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  transition: background 0.15s, border-color 0.15s;
}
.qty-btn:hover  { background: var(--color-primary-light); border-color: var(--color-primary); }
.qty-btn:disabled { opacity: 0.3; cursor: default; }

.btn-delete {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
  opacity: 0.6;
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
  text-align: center;
  width: 100%;
  padding: 15px;
  background: var(--color-primary);
  color: var(--color-white);
  font-size: 16px;
  font-weight: 800;
  font-family: var(--font-main);
  border-radius: var(--radius-btn);
  text-decoration: none;
  box-shadow: 0 4px 16px rgba(14, 165, 233, 0.35);
  transition: background 0.2s, transform 0.1s;
}
.btn-add:hover  { background: var(--color-primary-dark); }
.btn-add:active { transform: scale(0.98); }
</style>