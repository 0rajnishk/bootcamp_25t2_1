<template>
  <div>
    <h2>Signup</h2>
    <form @submit.prevent="signupUser">
      <input type="text" v-model="username" placeholder="Username" required>
      <input type="email" v-model="email" placeholder="Email" required>
      <input type="password" v-model="password" placeholder="Password" required>
      <!-- <select name="role" id="role">
        <option value="employee">Employee</option>
        <option value="manager">Manager</option>
      </select> -->
      <input type="file" accept="application/pdf" @change="handlefile()" required>
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
      file: null, // To hold the file input 
      message: '' // To display success or error messages
    }
  },
  methods: {
    handlefile() {
      const fileInput = document.querySelector('input[type="file"]');
      if (fileInput.files.length > 0) {
        this.file = fileInput.files[0];
      } else {
        this.file = null;
      }
    },

    async signupUser() {
      try {
        const response = await axios.post('http://127.0.0.1:5000/signup', {
          Headers: {
            'Content-Type': 'multipart/form-data'
          },
          file: this.file, 
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