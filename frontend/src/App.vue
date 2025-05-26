<template>
  <div id="app">
    <nav>
      <router-link to="/">Home</router-link> |
      <router-link to="/signup">Signup</router-link> |
      <router-link to="/login">Login</router-link> |
      <router-link to="/admin/dashboard">Admin Dashboard</router-link> |
      <router-link to="/manager/dashboard">Manager Dashboard</router-link> |
      <router-link to="/employee/dashboard">Employee Dashboard</router-link>
      <button v-if="isLoggedIn" @click="logout">Logout</button>
    </nav>
    <hr>
    <router-view />
  </div>
</template>

<script>
export default {
  computed: {
    // Check if the user is logged in by looking for a token in local storage
    isLoggedIn() {
      return !!localStorage.getItem('token');
    }
  },
  methods: {
    // Log out the user by removing token and role from local storage and redirecting to home
    logout() {
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      this.$router.push('/');
      alert('Logged out successfully!');
    }
  }
}
</script>

<style>
/* Basic styling for the nav bar */
nav {
  padding: 10px;
  background-color: #f0f0f0;
}

nav a {
  margin-right: 10px;
  text-decoration: none;
  color: #333;
}

nav a.router-link-exact-active {
  font-weight: bold;
  color: #007bff;
}

button {
  margin-left: 10px;
  padding: 5px 10px;
  cursor: pointer;
}
</style>