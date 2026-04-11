import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '@/views/LoginPage.vue'
import RegisterPage from '@/views/RegisterPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/',         component: LoginPage    },  // default page
    { path: '/login',    component: LoginPage    },  // same page, two paths
    { path: '/register', component: RegisterPage },  // now connected!
  ],
})

export default router
