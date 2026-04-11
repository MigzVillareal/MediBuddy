<template>
  <div class="tab">
    <h2 class="section-title">My Medications</h2>

    <div class="empty-state" v-if="medications.length === 0">
      <span class="empty-icon">💊</span>
      <p class="empty-title">No medications yet</p>
      <p class="empty-sub">Tap <strong>+ Add Medicine</strong> below to get started.</p>
    </div>

    <div class="med-list" v-else>
      <div class="med-card" v-for="med in medications" :key="med.id">
        <div class="med-card__left">
          <span class="med-card__icon">💊</span>
          <div>
            <p class="med-card__name">{{ med.name }}</p>
            <p class="med-card__detail">{{ med.dose }} · {{ med.schedule }}</p>
          </div>
        </div>
        <span class="med-card__stock" :class="{ 'med-card__stock--low': med.stock <= 5 }">
          {{ med.stock }} left
        </span>
      </div>
    </div>

    <div class="add-btn-wrap">
      <router-link to="/medicine-search" class="btn-add">+ Add Medicine</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// ref([]) makes an empty array that Vue can track for changes
const medications = ref([])
</script>

<style scoped>
.tab { padding: 20px 20px 100px; }
.section-title {
  font-size: 20px;
  font-weight: 800;
  color: var(--color-text-dark);
  margin-bottom: 16px;
}
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--color-text-muted);
}
.empty-icon  { font-size: 52px; display: block; margin-bottom: 12px; }
.empty-title { font-size: 17px; font-weight: 700; color: var(--color-text-dark); margin-bottom: 6px; }
.empty-sub   { font-size: 14px; }
.med-list { display: flex; flex-direction: column; gap: 12px; }
.med-card {
  background: var(--color-white);
  border-radius: 14px;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: var(--shadow-card);
}
.med-card__left   { display: flex; align-items: center; gap: 12px; }
.med-card__icon   { font-size: 28px; }
.med-card__name   { font-size: 15px; font-weight: 700; color: var(--color-text-dark); }
.med-card__detail { font-size: 12px; color: var(--color-text-muted); margin-top: 2px; }
.med-card__stock {
  font-size: 12px;
  font-weight: 700;
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  padding: 4px 10px;
  border-radius: 20px;
}
.med-card__stock--low { background: #fee2e2; color: #dc2626; }
.add-btn-wrap {
  position: fixed;
  bottom: 72px;
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