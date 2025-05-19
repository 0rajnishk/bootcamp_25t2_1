<template>
    <h2>
        Admin Login
    </h2>
    <form @submit.prevent="adminLogin">
        <input type="email" v-model="email" placeholder="Email" required>
        <input type="password" v-model="password" placeholder="Password" required>
        <button type="submit">login</button>

    </form>



</template>

<script>
import axios from "axios";

export default {
    data() {
        return {
            email: '',
            password: ''
        }
    },
    methods: {
        async adminLogin() {
            const response = await axios.post('http://127.0.0.1:5000/login',
                {
                    email: this.email,
                    password: this.password
                }
            );
            const token = response.data.token
            localStorage.setItem("token", token)
            alert(JSON.stringify(response.data.message))
            this.$router.push('/admindashboard')
        }

    }
}

</script>