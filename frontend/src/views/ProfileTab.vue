<template>
  <div class="tab">
    <div class="profile-header">
      <div class="profile-avatar">
        {{ user.firstName.charAt(0) }}{{ user.lastName.charAt(0) }}
      </div>
      <p class="profile-name">{{ user.firstName }} {{ user.lastName }}</p>
      <p class="profile-username">@{{ user.username }}</p>
    </div>

    <div class="profile-card">
      <div class="profile-row">
        <span class="profile-row__label">First Name</span>
        <span class="profile-row__value">{{ user.firstName }}</span>
      </div>
      <div class="profile-row">
        <span class="profile-row__label">Last Name</span>
        <span class="profile-row__value">{{ user.lastName }}</span>
      </div>
      <div class="profile-row">
        <span class="profile-row__label">Username</span>
        <span class="profile-row__value">@{{ user.username }}</span>
      </div>
    </div>

    <button class="btn-logout" @click="handleLogout">Sign Out</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Placeholder — later this will come from your backend after login
const user = ref({
  firstName: 'Juan',
  lastName: 'Dela Cruz',
  username: 'juandc',
})

async function handleLogout() {
  try {
    await fetch('/api/auth/logout', { method: 'POST' })
  } catch (err) {
    // Even if logout fails on the server, clear the frontend anyway
    console.error('Logout error:', err)
  }
  router.push('/login')
}
</script>

<style scoped>
.tab { padding: 20px 20px 100px; }
.profile-header { text-align: center; padding: 28px 0 24px; }
.profile-avatar {
  width: 72px; height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, #38bdf8, #0369a1);
  color: white;
  font-size: 24px; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 12px;
}
.profile-name     { font-size: 20px; font-weight: 800; color: var(--color-text-dark); }
.profile-username { font-size: 14px; color: var(--color-text-muted); margin-top: 2px; }
.profile-card { background: var(--color-white); border-radius: 16px; box-shadow: var(--shadow-card); overflow: hidden; margin-bottom: 20px; }
.profile-row { display: flex; justify-content: space-between; align-items: center; padding: 14px 18px; border-bottom: 1px solid var(--color-border); }
.profile-row:last-child { border-bottom: none; }
.profile-row__label { font-size: 13px; color: var(--color-text-muted); font-weight: 600; }
.profile-row__value { font-size: 14px; color: var(--color-text-dark); font-weight: 700; }
.btn-logout { width: 100%; padding: 14px; background: none; border: 2px solid var(--color-border); border-radius: var(--radius-btn); color: var(--color-text-body); font-size: 15px; font-weight: 700; font-family: var(--font-main); cursor: pointer; transition: border-color 0.2s, color 0.2s; }
.btn-logout:hover { border-color: #ef4444; color: #ef4444; }
</style>