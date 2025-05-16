import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Signup from '../views/Signup.vue'
import AdminLogin from '../views/AdminLogin.vue'
import AdminDashboard from '../views/AdminDashboard.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/home',
            name: 'home',
            component: Home
      },
        {
            path: '/signup',
            name: 'Signup',
            component: Signup
      },
        {
            path: '/adminlogin',
            name: 'AdminLogin',
            component: AdminLogin
      },
        {
            path: '/admindashboard',
            name: 'AdminDashboard',
            component: AdminDashboard
      }
    ]
})

export default router