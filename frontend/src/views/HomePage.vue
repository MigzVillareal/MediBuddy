<template>
  <div class="app-shell">
    <header class="top-bar">
      <span class="top-bar__logo">💊</span>
      <span class="top-bar__name">MediBuddy</span>
    </header>

    <main class="content">
      <HomeTab    v-if="activeTab === 'home'"    />
      <CircleTab  v-if="activeTab === 'circle'"  />
      <AlarmsTab  v-if="activeTab === 'alarms'"  />
      <ProfileTab v-if="activeTab === 'profile'" />
    </main>

    <nav class="bottom-nav">
      <button class="bottom-nav__item" :class="{ 'bottom-nav__item--active': activeTab === 'home' }"    @click="activeTab = 'home'">
        <span class="bottom-nav__icon">🏠</span>
        <span class="bottom-nav__label">Home</span>
      </button>
      <button class="bottom-nav__item" :class="{ 'bottom-nav__item--active': activeTab === 'circle' }"  @click="activeTab = 'circle'">
        <span class="bottom-nav__icon">👨‍👩‍👧</span>
        <span class="bottom-nav__label">Circle</span>
      </button>
      <button class="bottom-nav__item" :class="{ 'bottom-nav__item--active': activeTab === 'alarms' }"  @click="activeTab = 'alarms'">
        <span class="bottom-nav__icon">🔔</span>
        <span class="bottom-nav__label">Alarms</span>
      </button>
      <button class="bottom-nav__item" :class="{ 'bottom-nav__item--active': activeTab === 'profile' }" @click="activeTab = 'profile'">
        <span class="bottom-nav__icon">👤</span>
        <span class="bottom-nav__label">Profile</span>
      </button>
    </nav>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import HomeTab    from './HomeTab.vue'
import CircleTab  from './CircleTab.vue'
import AlarmsTab  from './AlarmsTab.vue'
import ProfileTab from './ProfileTab.vue'

// Tracks which tab is currently visible
const activeTab = ref('home')
</script>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  max-width: (100%, 480px);
  margin: 0 auto;
  background: var(--color-bg);
}
.top-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  background: var(--color-white);
  border-bottom: 1.5px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 10;
}
.top-bar__logo { font-size: 24px; }
.top-bar__name { font-size: 20px; font-weight: 800; color: var(--color-text-dark); font-family: var(--font-main); }
.content { flex: 1; overflow-y: auto; }
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: (100%, 480px);
  background: var(--color-white);
  border-top: 1.5px solid var(--color-border);
  display: flex;
  z-index: 20;
}
.bottom-nav__item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  padding: 10px 0 14px;
  background: none;
  border: none;
  cursor: pointer;
  color: #94a3b8;
  transition: color 0.2s;
}
.bottom-nav__item--active { color: var(--color-primary); }
.bottom-nav__icon  { font-size: 22px; }
.bottom-nav__label { font-size: 11px; font-weight: 700; font-family: var(--font-main); }
</style>