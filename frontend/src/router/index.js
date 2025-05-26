import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Signup from '../views/Signup.vue';
import Login from '../views/Login.vue'; // Combined login for all roles
import AdminDashboard from '../views/AdminDashboard.vue';
import ManagerDashboard from '../views/ManagerDashboard.vue';
import EmployeeDashboard from '../views/EmployeeDashboard.vue';
import AdminLogin from '../views/AdminLogin.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },
    {
      path: '/signup',
      name: 'Signup',
      component: Signup
    },
    {
      path: '/login', // Single login page for all roles
      name: 'Login',
      component: Login
    },
    {
      path: '/adminlogin', // Single login page for all roles
      name: 'adminlogin',
      component: AdminLogin
    },
    {
      path: '/admin/dashboard',
      name: 'AdminDashboard',
      component: AdminDashboard,
      meta: { requiresAuth: true, role: 'admin' } // Requires admin role
    },
    {
      path: '/manager/dashboard',
      name: 'ManagerDashboard',
      component: ManagerDashboard,
      meta: { requiresAuth: true, role: 'manager' } // Requires manager role
    },
    {
      path: '/employee/dashboard',
      name: 'EmployeeDashboard',
      component: EmployeeDashboard,
      meta: { requiresAuth: true, role: 'employee' } // Requires employee role
    }
  ]
});

// Navigation guard to check authentication and roles
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('token');
  const userRole = localStorage.getItem('role'); // Assuming you store role in localStorage

  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      next('/login'); // Redirect to login if not authenticated
    } else {
      if (to.meta.role && to.meta.role !== userRole) {
        // Redirect to home or an unauthorized page if role doesn't match
        alert('Unauthorized access!');
        next('/');
      } else {
        next(); // Allow access
      }
    }
  } else {
    next(); // Allow access to routes that don't require authentication
  }
});

export default router;



// import { createRouter, createWebHistory } from 'vue-router'
// import Home from '../views/Home.vue'
// import Signup from '../views/Signup.vue'
// import AdminLogin from '../views/AdminLogin.vue'
// import AdminDashboard from '../views/AdminDashboard.vue'

// const router = createRouter({
//     history: createWebHistory(import.meta.env.BASE_URL),
//     routes: [
//         {
//             path: '/',
//             name: 'home',
//             component: Home
//       },
//         {
//             path: '/signup',
//             name: 'Signup',
//             component: Signup
//       },
//         {
//             path: '/adminlogin',
//             name: 'AdminLogin',
//             component: AdminLogin
//       },
//         {
//             path: '/admindashboard',
//             name: 'AdminDashboard',
//             component: AdminDashboard
//       }
//     ]
// })

// export default router