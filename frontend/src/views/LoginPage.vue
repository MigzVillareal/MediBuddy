<template>
  <div class="page">
    <div class="card-wrapper">
      <div class="brand">
        <span class="pill-icon">💊</span>
        <span class="app-name">MediBuddy</span>
      </div>
      <LoginCard />
    </div>
  </div>
</template>

<script setup>
// With script setup, just importing a component registers it automatically.
// No need for a components: {} block.
import LoginCard from '../components/LoginCard.vue'
</script>

<style scoped>
.page {
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(160deg, #0ea5e9 0%, #0369a1 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px 16px;
}
.card-wrapper {
  width: 100%;
  max-width: 440px;
}
.brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 24px;
}
.pill-icon { font-size: 36px; }
.app-name {
  font-size: 28px;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: -0.5px;
  font-family: var(--font-main);
}
@media (max-width: 480px) {
  .app-name { font-size: 24px; }
  .pill-icon { font-size: 30px; }
  :deep(.card) { padding: 24px 18px; }
}
</style>