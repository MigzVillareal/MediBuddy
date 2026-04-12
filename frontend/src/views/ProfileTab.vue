<template>
  <div class="tab">
    <div class="profile-header">
      <div class="profile-avatar">
        {{ user.firstName?.charAt(0) || '' }}{{ user.lastName?.charAt(0) || '' }}
      </div>
      <p class="profile-name">{{ user.firstName }} {{ user.lastName }}</p>
      <p class="profile-username">@{{ user.username }}</p>
    </div>

    <div class="profile-card">
      <div class="profile-row">
        <span class="profile-row__label">First Name</span>
        <input class="profile-row__value input-inline" v-model="user.firstName" />
      </div>

      <div class="profile-row">
        <span class="profile-row__label">Last Name</span>
        <input class="profile-row__value input-inline" v-model="user.lastName" />
      </div>

      <div class="profile-row">
        <span class="profile-row__label">Username</span>
        <span class="profile-row__value">@{{ user.username }}</span>
      </div>
    </div>

    <div class="button-group">
      <button v-if="hasChanges" class="btn-save" @click="saveProfile">
        Save Changes
      </button>

      <button class="btn-logout" @click="handleLogout">
        Sign Out
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api.js'

const router = useRouter()

const user = ref({
  firstName: '',
  lastName: '',
  username: ''
})

const originalUser = ref(null)

// 🔍 detect changes
const hasChanges = computed(() => {
  if (!originalUser.value) return false

  return (
    user.value.firstName !== originalUser.value.firstName ||
    user.value.lastName !== originalUser.value.lastName
  )
})

onMounted(async () => {
  try {
    const res = await api.get('/auth/me')

    const fetchedUser = {
      firstName: res.data.first_name || '',
      lastName: res.data.last_name || '',
      username: res.data.username || ''
    }

    user.value = { ...fetchedUser }
    originalUser.value = { ...fetchedUser }

  } catch (err) {
    console.error('Failed to load user:', err)
  }
})

async function saveProfile() {
  try {
    await api.post('/auth/profile', {
      first_name: user.value.firstName,
      last_name: user.value.lastName
    })

    originalUser.value = { ...user.value }

    alert('Profile updated!')
  } catch (err) {
    console.error('Update failed:', err)
  }
}

async function handleLogout() {
  try {
    await api.post('/auth/logout')
  } catch (err) {
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
.input-inline { width: 60%; padding: 10px 12px; border: 2px solid var(--color-border); border-radius: 10px; background: var(--color-input-bg); color: var(--color-text-dark); font-size: 14px; font-family: var(--font-main); outline: none; margin-left: auto; transition: border-color 0.2s, box-shadow 0.2s; }
.input-inline:hover { border-color: #94a3b8; }
.input-inline:focus { border-color: var(--color-primary); box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15); }
.profile-row:last-child { border-bottom: none; }
.profile-row__label { font-size: 13px; color: var(--color-text-muted); font-weight: 600; }
.profile-row__value { font-size: 14px; color: var(--color-text-dark); font-weight: 700; }
.button-group { display: flex; flex-direction: column;gap: 12px; }
.button-group button { width: 100%; padding: 14px; background: none; border: 2px solid var(--color-border); border-radius: var(--radius-btn); color: var(--color-text-body); font-size: 15px; font-weight: 700; font-family: var(--font-main); cursor: pointer; transition: border-color 0.2s, color 0.2s; }
.btn-save:hover { border-color: #ef4444; color: #ef4444; }
.btn-logout:hover { border-color: #ef4444; color: #ef4444; }
</style>