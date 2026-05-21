<template>
  <div class="app-shell">
    <header class="top-bar">
      <span class="top-bar__logo">💊</span>
      <span class="top-bar__name">MediBuddy</span>
      <div class="top-bar__right">
        <!-- Due-today trigger -->
        <button
          v-if="dueMeds.length > 0"
          class="due-pill"
          @click="showDueSheet = true"
          title="Medicines due today"
        >
          <span class="due-pill__icon">🔔</span>
          <span class="due-pill__count">{{ pendingCount }}</span>
        </button>
        <span class="top-bar__user">{{ user.username }}</span>
      </div>
    </header>

    <main class="content">
      <ShelfTab          v-if="activeTab === 'home'"          />
      <PrescriptionsTab  v-if="activeTab === 'prescriptions'" />
      <CircleTab         v-if="activeTab === 'circle'"        />
      <ProfileTab        v-if="activeTab === 'profile'"       />
    </main>

    <nav class="bottom-nav">
      <button class="bottom-nav__item" :class="{ 'bottom-nav__item--active': activeTab === 'home' }"    @click="activeTab = 'home'">
        <span class="bottom-nav__icon">🗂</span>
        <span class="bottom-nav__label">Shelf</span>
      </button>
      <button class="bottom-nav__item" :class="{ 'bottom-nav__item--active': activeTab === 'prescriptions' }" @click="activeTab = 'prescriptions'">
        <span class="bottom-nav__icon">📋</span>
        <span class="bottom-nav__label">Rx</span>
      </button>
      <button class="bottom-nav__item" :class="{ 'bottom-nav__item--active': activeTab === 'circle' }"  @click="activeTab = 'circle'">
        <span class="bottom-nav__icon">👨‍👩‍👧</span>
        <span class="bottom-nav__label">Circle</span>
      </button>
      <button class="bottom-nav__item" :class="{ 'bottom-nav__item--active': activeTab === 'profile' }" @click="activeTab = 'profile'">
        <span class="bottom-nav__icon">👤</span>
        <span class="bottom-nav__label">Profile</span>
      </button>
    </nav>

    <!-- ── DUE TODAY BOTTOM SHEET ── -->
    <Teleport to="body">
      <Transition name="fade">
        <div class="overlay" v-if="showDueSheet" @click.self="showDueSheet = false">
          <Transition name="slide-up">
            <div class="due-sheet" v-if="showDueSheet">
              <div class="sheet-handle"></div>

              <div class="due-sheet__header">
                <div>
                  <h3 class="due-sheet__title">Today's Medicines</h3>
                  <p class="due-sheet__sub">{{ pendingCount }} remaining · {{ takenCount }} taken</p>
                </div>
                <button class="btn-close" @click="showDueSheet = false">✕</button>
              </div>

              <!-- Loading -->
              <div class="due-loading" v-if="loadingDue">⏳ Loading…</div>

              <!-- All done -->
              <div class="due-done" v-else-if="pendingCount === 0">
                <span class="due-done__icon">🎉</span>
                <p class="due-done__title">All done for today!</p>
                <p class="due-done__sub">You've taken or skipped all your medicines.</p>
              </div>

              <!-- List -->
              <div class="due-list" v-else>
                <TransitionGroup name="due-row">
                  <div
                    v-for="med in visibleMeds"
                    :key="med.prescription_detail_id"
                    class="due-row"
                    :class="{
                      'due-row--taken':   med._status === 'taken',
                      'due-row--skipped': med._status === 'skipped',
                      'due-row--low':     med.supply_stock != null && med.supply_stock <= 5,
                    }"
                  >
                    <div class="due-row__info">
                      <p class="due-row__name">{{ med.brand_name }}</p>
                      <p class="due-row__generic" v-if="med.generic_name">{{ med.generic_name }}</p>
                      <div class="due-row__chips">
                        <span class="chip chip--purple"
                          v-for="t in (med.time_taken ? med.time_taken.split(',') : [])"
                          :key="t"
                        >{{ t.trim() }}</span>
                        <span
                          class="chip"
                          :class="med.supply_stock != null && med.supply_stock <= 5 ? 'chip--red' : 'chip--blue'"
                          v-if="med.supply_stock != null"
                        >{{ med.supply_stock }} left</span>
                      </div>
                    </div>

                    <!-- Status: pending -->
                    <div class="due-row__actions" v-if="!med._status">
                      <button
                        class="btn-take"
                        :disabled="med.supply_stock != null && med.supply_stock <= 0"
                        @click="takeMed(med)"
                      >
                        <span v-if="med._loading">⏳</span>
                        <span v-else>✓ Take</span>
                      </button>
                      <button class="btn-skip" @click="skipMed(med)">✗ Skip</button>
                    </div>

                    <!-- Status: taken -->
                    <div class="due-row__done due-row__done--taken" v-else-if="med._status === 'taken'">
                      ✓ Taken
                    </div>

                    <!-- Status: skipped -->
                    <div class="due-row__done due-row__done--skipped" v-else-if="med._status === 'skipped'">
                      ✗ Skipped
                    </div>
                  </div>
                </TransitionGroup>
              </div>

              <button class="btn-ghost" @click="showDueSheet = false" style="margin-top:12px">Close</button>
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
import ShelfTab          from './ShelfTab.vue'
import PrescriptionsTab  from './PrescriptionsTab.vue'
import CircleTab         from './CircleTab.vue'
import ProfileTab        from './ProfileTab.vue'

const user       = ref({ username: '' })
const activeTab  = ref('home')

// ── DUE TODAY ────────────────────────────────────────────────────────────────
const dueMeds     = ref([])
const loadingDue  = ref(false)
const showDueSheet = ref(false)

const pendingCount = computed(() => dueMeds.value.filter(m => !m._status).length)
const takenCount   = computed(() => dueMeds.value.filter(m => m._status === 'taken').length)
const visibleMeds  = computed(() => dueMeds.value) // show all rows, taken/skipped greyed

async function loadDueMeds() {
  loadingDue.value = true
  try {
    const data = (await api.get('/prescriptions/due-today')).data
    // Attach reactive UI state to each item
    dueMeds.value = data.map(m => ({ ...m, _status: null, _loading: false }))
  } catch (e) {
    console.error('loadDueMeds', e)
    dueMeds.value = []
  } finally {
    loadingDue.value = false
  }
}

async function takeMed(med) {
  if (med._loading) return
  med._loading = true

  const previousStock = med.supply_stock
  if (med.supply_stock != null) {
    med.supply_stock -= 1  // optimistic update
  }

  try {
    const res = await api.post(
      `/prescriptions/${med.prescription_id}/details/${med.prescription_detail_id}/take`
    )
    med._status = 'taken'
    // Sync with server's actual value
    if (res.data.supply_stock != null) {
      med.supply_stock = res.data.supply_stock
    }
  } catch (e) {
    med.supply_stock = previousStock  // revert on failure
    const msg = e.response?.data?.error || 'Failed to record.'
    alert(msg)
  } finally {
    med._loading = false
  }
}

function skipMed(med) {
  med._status = 'skipped'
}

// ── INIT ─────────────────────────────────────────────────────────────────────
onMounted(async () => {
  const res = await fetch('/api/auth/me')
  const data = await res.json()
  user.value.username = data.username
  await loadDueMeds()
})
</script>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  max-width: 480px;
  margin: 0 auto;
  background: var(--color-bg);
}

/* Top bar */
.top-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 20px;
  background: var(--color-white);
  border-bottom: 1.5px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 10;
}
.top-bar__logo { font-size: 24px; }
.top-bar__name { font-size: 20px; font-weight: 800; color: var(--color-text-dark); font-family: var(--font-main); }
.top-bar__right { margin-left: auto; display: flex; align-items: center; gap: 10px; }
.top-bar__user  { font-size: 14px; font-weight: 600; color: var(--color-text-muted); }

/* Due-today pill button */
.due-pill {
  display: flex; align-items: center; gap: 5px;
  padding: 6px 12px; border-radius: 20px;
  background: var(--color-primary); color: #fff;
  border: none; cursor: pointer; font-family: var(--font-main);
  font-size: 13px; font-weight: 700;
  box-shadow: 0 2px 10px rgba(14,165,233,.35);
  transition: background .2s, transform .1s;
  animation: pulse-pill 2.5s ease-in-out infinite;
}
.due-pill:hover  { background: var(--color-primary-dark); }
.due-pill:active { transform: scale(.94); }
.due-pill__icon  { font-size: 15px; }
.due-pill__count { font-size: 14px; font-weight: 800; }
@keyframes pulse-pill {
  0%, 100% { box-shadow: 0 2px 10px rgba(14,165,233,.35); }
  50%       { box-shadow: 0 2px 18px rgba(14,165,233,.65); }
}

/* Main content + nav */
.content { flex: 1; overflow-y: auto; }
.bottom-nav {
  position: fixed; bottom: 0; left: 50%; transform: translateX(-50%);
  width: 100%; max-width: 480px;
  background: var(--color-white); border-top: 1.5px solid var(--color-border);
  display: flex; z-index: 20;
}
.bottom-nav__item {
  flex: 1; display: flex; flex-direction: column; align-items: center;
  justify-content: center; gap: 3px; padding: 10px 0 14px;
  background: none; border: none; cursor: pointer; color: #94a3b8;
  transition: color 0.2s;
}
.bottom-nav__item--active { color: var(--color-primary); }
.bottom-nav__icon  { font-size: 22px; }
.bottom-nav__label { font-size: 11px; font-weight: 700; font-family: var(--font-main); }

/* Overlay + sheet */
.overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,.45);
  display: flex; align-items: flex-end; justify-content: center; z-index: 400;
}
.due-sheet {
  background: var(--color-white); border-radius: 24px 24px 0 0;
  padding: 12px 24px 48px; width: 100%; max-width: 500px;
  max-height: 88vh; overflow-y: auto;
  display: flex; flex-direction: column; gap: 10px;
}
.sheet-handle { width: 40px; height: 4px; background: #cbd5e1; border-radius: 2px; margin: 0 auto 6px; flex-shrink: 0; }

/* Sheet header */
.due-sheet__header { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; }
.due-sheet__title  { font-size: 19px; font-weight: 800; color: var(--color-text-dark); }
.due-sheet__sub    { font-size: 12px; color: var(--color-text-muted); margin-top: 3px; }
.btn-close { background: none; border: none; font-size: 18px; cursor: pointer; color: var(--color-text-muted); padding: 4px; line-height: 1; }

/* Loading / done */
.due-loading { font-size: 14px; color: var(--color-text-muted); text-align: center; padding: 24px 0; }
.due-done { text-align: center; padding: 32px 16px; }
.due-done__icon  { font-size: 52px; display: block; margin-bottom: 12px; }
.due-done__title { font-size: 18px; font-weight: 800; color: var(--color-text-dark); margin-bottom: 6px; }
.due-done__sub   { font-size: 13px; color: var(--color-text-muted); }

/* Due list rows */
.due-list { display: flex; flex-direction: column; gap: 0; }
.due-row {
  display: flex; align-items: center; gap: 12px;
  padding: 14px 0; border-bottom: 1px solid var(--color-border);
  transition: opacity .3s;
}
.due-row--taken   { opacity: .5; }
.due-row--skipped { opacity: .4; }
.due-row__info    { flex: 1; min-width: 0; }
.due-row__name    { font-size: 15px; font-weight: 700; color: var(--color-text-dark); }
.due-row__generic { font-size: 12px; color: var(--color-text-muted); margin-top: 1px; }
.due-row__chips   { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 6px; }
.chip { font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 20px; background: #e2e8f0; color: #64748b; }
.chip--blue   { background: #e0f2fe; color: #0369a1; }
.chip--purple { background: #ede9fe; color: #7c3aed; }
.chip--red    { background: #fee2e2; color: #dc2626; }

/* Action buttons */
.due-row__actions { display: flex; flex-direction: column; gap: 6px; flex-shrink: 0; }
.btn-take {
  padding: 8px 14px; border: none; border-radius: 10px;
  background: var(--color-primary); color: #fff;
  font-size: 13px; font-weight: 700; font-family: var(--font-main);
  cursor: pointer; white-space: nowrap;
  transition: background .2s, transform .1s;
}
.btn-take:hover:not(:disabled) { background: var(--color-primary-dark); }
.btn-take:active { transform: scale(.93); }
.btn-take:disabled { opacity: .4; cursor: not-allowed; }
.btn-skip {
  padding: 7px 14px; border-radius: 10px;
  border: 2px solid var(--color-border); background: none;
  font-size: 13px; font-weight: 600; font-family: var(--font-main);
  color: var(--color-text-muted); cursor: pointer;
  transition: border-color .15s, color .15s;
}
.btn-skip:hover { border-color: #ef4444; color: #ef4444; }

/* Done labels */
.due-row__done { font-size: 13px; font-weight: 700; flex-shrink: 0; padding: 6px 10px; border-radius: 10px; }
.due-row__done--taken   { background: #dcfce7; color: #15803d; }
.due-row__done--skipped { background: #f1f5f9; color: #94a3b8; }

/* Ghost button */
.btn-ghost {
  width: 100%; padding: 12px; background: none;
  border: 2px solid var(--color-border); border-radius: var(--radius-btn);
  color: var(--color-text-muted); font-size: 14px; font-weight: 600;
  font-family: var(--font-main); cursor: pointer;
}

/* Row transition */
.due-row-enter-active, .due-row-leave-active { transition: opacity .3s, transform .3s; }
.due-row-enter-from, .due-row-leave-to { opacity: 0; transform: translateX(20px); }

/* Sheet transitions */
.fade-enter-active, .fade-leave-active { transition: opacity .22s; }
.fade-enter-from,   .fade-leave-to     { opacity: 0; }
.slide-up-enter-active, .slide-up-leave-active { transition: transform .28s cubic-bezier(.32,1,.32,1); }
.slide-up-enter-from,   .slide-up-leave-to     { transform: translateY(100%); }
</style>