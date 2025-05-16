<template>
<h2>Signup</h2>
<form @submit.prevent="signupUser">
<input type="text" v-model="username" placeholder="Username" required>
<input type="email" v-model="email" placeholder="Email" required>
<input type="password" v-model="password" placeholder="Password" required>
<button type="submit">Signup</button>

</form>

<button @click="click()">click me</button>

</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      username: '',
      email: '',
      password: ''
    }
  },
  methods: {
    click() {
        alert(this.username)
    },

      async signupUser(){
          const response = await axios.post('http://127.0.0.1:5000/signup',
            {   username:this.username,
                email: this.email,
                password: this.password
            }
          );
        alert("signup api call");
        console.log(response.data)
        alert(JSON.stringify(response.data))

      }

  }
}

</script>