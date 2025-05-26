<template>
    <div>
        <h2>Login</h2>
        <form @submit.prevent="loginUser">
            <input type="email" v-model="email" placeholder="Email" required>
            <input type="password" v-model="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <p v-if="message">{{ message }}</p>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            email: '',
            password: '',
            message: ''
        }
    },
    methods: {
        async loginUser() {
            try {
                const response = await axios.post('http://127.0.0.1:5000/login', {
                    email: this.email,
                    password: this.password
                });
                const token = response.data.token;
                const role = response.data.role; // Assuming backend sends back the role

                localStorage.setItem('token', token);
                localStorage.setItem('role', role); // Store the user's role

                this.message = response.data.message || 'Login successful!';

                // Redirect based on role
                if (role === 'admin') {
                    this.$router.push('/admin/dashboard');
                } else if (role === 'manager') {
                    this.$router.push('/manager/dashboard');
                } else if (role === 'employee') {
                    this.$router.push('/employee/dashboard');
                } else {
                    // Fallback if role is not recognized
                    this.$router.push('/');
                }

            } catch (error) {
                this.message = error.response?.data?.message || 'Login failed. Invalid credentials or account not approved.';
                console.error('Login error:', error);
            }
        }
    }
}
</script>