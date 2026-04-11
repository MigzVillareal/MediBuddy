<template>
  <div class="page">
    <header class="top-bar">
      <button class="btn-back" @click="router.back()">← Back</button>
      <span class="top-bar__title">Add Medicine</span>
    </header>

    <div class="search-wrap">
      <input class="search-input" type="text" placeholder="Search medicine name..." v-model="searchQuery" @input="handleSearch" />
    </div>

    <div class="hint" v-if="!searchQuery">
      <span class="hint-icon">🔍</span>
      <p>Start typing to search for a medicine.</p>
    </div>

    <div class="results" v-if="searchQuery">
      <p class="results-label" v-if="filteredMeds.length > 0">{{ filteredMeds.length }} result(s) found</p>
      <div class="hint" v-if="filteredMeds.length === 0">
        <span class="hint-icon">😕</span>
        <p>No medicine found for "<strong>{{ searchQuery }}</strong>"</p>
      </div>
      <div class="result-list">
        <div class="result-card" v-for="med in filteredMeds" :key="med.id" @click="selectMedicine(med)">
          <div>
            <p class="result-card__name">{{ med.genericName }}</p>
            <p class="result-card__brand">{{ med.brandName }}</p>
            <span class="result-card__form">{{ med.dosageForm }}</span>
          </div>
          <span class="result-card__arrow">›</span>
        </div>
      </div>
    </div>

    <div class="modal-overlay" v-if="selectedMed" @click.self="selectedMed = null">
      <div class="modal">
        <h3 class="modal-title">{{ selectedMed.genericName }}</h3>
        <p class="modal-sub">{{ selectedMed.brandName }} · {{ selectedMed.dosageForm }}</p>
        <div class="field">
          <label class="label">Dose</label>
          <input class="input" type="text" placeholder="e.g. 500mg" v-model="form.dose" />
        </div>
        <div class="field">
          <label class="label">Schedule</label>
          <input class="input" type="text" placeholder="e.g. Every 8 hours" v-model="form.schedule" />
        </div>
        <div class="field">
          <label class="label">Stock (number of pills)</label>
          <input class="input" type="number" placeholder="e.g. 30" v-model="form.stock" min="1" />
        </div>
        <p class="error" v-if="formError">{{ formError }}</p>
        <button class="btn-primary" @click="confirmAdd">Add to My Medications</button>
        <button class="btn-cancel" @click="selectedMed = null">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const searchQuery = ref('')
const selectedMed = ref(null)
const formError   = ref('')
const filteredMeds = ref([])

// reactive() works like ref() but is better for objects with multiple fields
const form = reactive({ dose: '', schedule: '', stock: '' })

// Placeholder list — later replace with FDA Philippines API call
const allMedicines = [
  { id: 1,  genericName: 'Amlodipine',  brandName: 'Norvasc',    dosageForm: 'Tablet'  },
  { id: 2,  genericName: 'Metformin',   brandName: 'Glucophage', dosageForm: 'Tablet'  },
  { id: 3,  genericName: 'Atorvastatin',brandName: 'Lipitor',    dosageForm: 'Tablet'  },
  { id: 4,  genericName: 'Losartan',    brandName: 'Cozaar',     dosageForm: 'Tablet'  },
  { id: 5,  genericName: 'Omeprazole',  brandName: 'Prilosec',   dosageForm: 'Capsule' },
  { id: 6,  genericName: 'Paracetamol', brandName: 'Biogesic',   dosageForm: 'Tablet'  },
  { id: 7,  genericName: 'Amoxicillin', brandName: 'Amoxil',     dosageForm: 'Capsule' },
  { id: 8,  genericName: 'Cetirizine',  brandName: 'Zyrtec',     dosageForm: 'Tablet'  },
  { id: 9,  genericName: 'Furosemide',  brandName: 'Lasix',      dosageForm: 'Tablet'  },
  { id: 10, genericName: 'Aspirin',     brandName: 'Bayer',      dosageForm: 'Tablet'  },
]

function handleSearch() {
  const q = searchQuery.value.toLowerCase().trim()
  if (!q) { filteredMeds.value = []; return }
  filteredMeds.value = allMedicines.filter(med =>
    med.genericName.toLowerCase().includes(q) ||
    med.brandName.toLowerCase().includes(q)
  )
}

function selectMedicine(med) {
  selectedMed.value = med
  form.dose = ''; form.schedule = ''; form.stock = ''
  formError.value = ''
}

function confirmAdd() {
  formError.value = ''
  if (!form.dose || !form.schedule || !form.stock) {
    formError.value = 'Please fill in all fields.'
    return
  }
  // Later: save to backend / shared store
  alert(`${selectedMed.value.genericName} added!`)
  selectedMed.value = null
  router.back()
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--color-bg); max-width: 480px; margin: 0 auto; }
.top-bar { display: flex; align-items: center; gap: 12px; padding: 16px 20px; background: var(--color-white); border-bottom: 1.5px solid var(--color-border); position: sticky; top: 0; z-index: 10; }
.btn-back { background: none; border: none; font-size: 16px; font-weight: 700; color: var(--color-primary); cursor: pointer; font-family: var(--font-main); padding: 0; }
.top-bar__title { font-size: 18px; font-weight: 800; color: var(--color-text-dark); }
.search-wrap { padding: 16px 20px; background: var(--color-white); border-bottom: 1px solid var(--color-border); }
.search-input { width: 100%; padding: 13px 16px; border: 2px solid var(--color-border); border-radius: var(--radius-input); font-size: 16px; font-family: var(--font-main); color: #1e293b; background: var(--color-input-bg); outline: none; transition: border-color 0.2s; }
.search-input:focus { border-color: var(--color-primary); }
.hint { text-align: center; padding: 50px 20px; color: var(--color-text-muted); font-size: 14px; }
.hint-icon { font-size: 40px; display: block; margin-bottom: 10px; }
.results { padding: 16px 20px; }
.results-label { font-size: 12px; font-weight: 700; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; }
.result-list { display: flex; flex-direction: column; gap: 10px; }
.result-card { background: var(--color-white); border-radius: 14px; padding: 14px 16px; display: flex; align-items: center; justify-content: space-between; box-shadow: var(--shadow-card); cursor: pointer; transition: transform 0.1s; }
.result-card:active { transform: scale(0.98); }
.result-card__name  { font-size: 15px; font-weight: 700; color: var(--color-text-dark); }
.result-card__brand { font-size: 12px; color: var(--color-text-muted); margin-top: 2px; }
.result-card__form  { display: inline-block; margin-top: 6px; font-size: 11px; font-weight: 700; background: var(--color-primary-light); color: var(--color-primary-dark); padding: 2px 8px; border-radius: 20px; }
.result-card__arrow { font-size: 22px; color: var(--color-primary); }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.35); display: flex; align-items: flex-end; z-index: 100; }
.modal { background: var(--color-white); border-radius: 24px 24px 0 0; padding: 28px 24px 40px; width: 100%; }
.modal-title { font-size: 18px; font-weight: 800; color: var(--color-text-dark); }
.modal-sub   { font-size: 13px; color: var(--color-text-muted); margin-bottom: 20px; }
.field { margin-bottom: 16px; }
.label { display: block; font-size: 12px; font-weight: 700; color: var(--color-text-body); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
.input { width: 100%; padding: 13px 16px; border: 2px solid var(--color-border); border-radius: var(--radius-input); font-size: 16px; font-family: var(--font-main); color: #1e293b; background: var(--color-input-bg); outline: none; transition: border-color 0.2s; }
.input:focus { border-color: var(--color-primary); }
.error { color: #ef4444; font-size: 13px; font-weight: 600; margin-bottom: 10px; }
.btn-primary { width: 100%; padding: 14px; background: var(--color-primary); border: none; border-radius: var(--radius-btn); color: var(--color-white); font-size: 15px; font-weight: 800; font-family: var(--font-main); cursor: pointer; transition: background 0.2s; margin-bottom: 10px; }
.btn-primary:hover { background: var(--color-primary-dark); }
.btn-cancel { width: 100%; padding: 12px; background: none; border: 2px solid var(--color-border); border-radius: var(--radius-btn); color: var(--color-text-body); font-size: 15px; font-weight: 700; font-family: var(--font-main); cursor: pointer; }
</style>