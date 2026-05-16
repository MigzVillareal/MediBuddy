import { createRouter, createWebHistory } from 'vue-router'
import LoginPage          from '@/views/LoginPage.vue'
import RegisterPage       from '@/views/RegisterPage.vue'
import HomePage           from '@/views/HomePage.vue'
import MedicineSearchPage from '@/views/MedicineSearchPage.vue'
import api                from '@/api'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/',                component: HomePage,           meta: {public: true} },
    { path: '/login',           component: LoginPage,          meta: {public: true} },
    { path: '/register',        component: RegisterPage,       meta: {public: true} },
    { path: '/home',            component: HomePage,           meta: {public: false} },
    { path: '/medicine-search', component: MedicineSearchPage, meta: {public: false} },
  ],
})

router.beforeEach(async (to) => {

  let isAuthenticated = false
  try {
    await api.get('/auth/me')
    isAuthenticated = true
  } catch {
    isAuthenticated = false
  }

  if (to.path === '/') {
    return isAuthenticated ? '/home' : '/login'
  }

  
  // if (to.meta.public) {
  //   if (isAuthenticated && (to.path === '/login' || to.path === '/register')) {
  //     return '/home'
  //   }
  //   return true
  // }

  if (!isAuthenticated) {
    return '/login'
  }
  return true
})
export default router