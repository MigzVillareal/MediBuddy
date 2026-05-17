import { createRouter, createWebHistory } from 'vue-router'
import LoginPage          from '@/views/LoginPage.vue'
import RegisterPage       from '@/views/RegisterPage.vue'
import HomePage           from '@/views/HomePage.vue'
import MedicineSearchPage from '@/views/MedicineSearchPage.vue'
import api                from '@/api'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/',                component: LoginPage,           meta: {public: true} },
    { path: '/login',           component: LoginPage,          meta: {public: true} },
    { path: '/register',        component: RegisterPage,       meta: {public: true} },
    { path: '/home',            component: HomePage,           meta: {public: false} },
    { path: '/medicine-search', component: MedicineSearchPage, meta: {public: false} },
  ],
})

router.beforeEach(async (to) => {
  // Don't check auth for public routes
  if (to.meta.public) {
    return true
  }

  let isAuthenticated = false
  try {
    await api.get('/auth/me')
    isAuthenticated = true
  } catch {
    isAuthenticated = false
  }

  if (!isAuthenticated) {
    return '/login'
  }
  return true
})
export default router