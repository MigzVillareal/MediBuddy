import { createRouter, createWebHistory } from 'vue-router'
import LoginPage          from '@/views/LoginPage.vue'
import RegisterPage       from '@/views/RegisterPage.vue'
import HomePage           from '@/views/HomePage.vue'
import MedicineSearchPage from '@/views/MedicineSearchPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [

    { path: '/',                component: HomePage           }, // ← change to LoginPage later
    // { path: '/',             component: LoginPage          }, // ← uncomment this when ready

    { path: '/login',           component: LoginPage          },
    { path: '/register',        component: RegisterPage       },
    { path: '/home',            component: HomePage           },
    { path: '/medicine-search', component: MedicineSearchPage },
  ],
})

export default router