<template>
  <div>
    <h2>Signup</h2>
    <form @submit.prevent="signupUser">
      <input type="text" v-model="username" placeholder="Username" required>
      <input type="email" v-model="email" placeholder="Email" required>
      <input type="password" v-model="password" placeholder="Password" required>
      <select name="role" id="role">
        <!-- <option value="admin">Admin</option> -->
        <option value="employee">Employee</option>
        <option value="manager">Manager</option>
      </select>
      <button type="submit">Signup</button>
    </form>
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      username: '',
      email: '',
      password: '',
      role: 'employee', 
      message: '' // To display success or error messages
    }
  },
  methods: {
    async signupUser() {
      try {
        const response = await axios.post('http://127.0.0.1:5000/signup', {
          username: this.username,
          email: this.email,
          password: this.password,
          role: this.role 
        });
        this.message = response.data.message || 'Signup successful! Awaiting admin approval.';
        this.username = '';
        this.email = '';
        this.password = '';
        this.role = 'employee'; // Reset role to default
      } catch (error) {
        this.message = error.response?.data?.message || 'Signup failed. Please try again.';
        console.error('Signup error:', error);
      }
    }
  }
}
</script>