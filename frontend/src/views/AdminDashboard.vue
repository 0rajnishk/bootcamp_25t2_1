<template>

    <ul v-for="user in users">
        <li>
            {{ user.username }}
        </li>
        <li> {{ user.email }}</li>
        <button @click="approve_user(user.user_id)">approve</button>
        <br>
        <br>
    </ul>


</template>

<script>
import axios from "axios";


export default {
data(){
    return{
        users:[]
    }
},

    methods: {
        async fetchUsers(){
            alert('mounted worked')
            const resp = await axios.get('http://127.0.0.1:5000/admin')
            this.users = resp.data 
            alert('--')
        },
        async approve_user(user_id){
            const resp = await axios.post('http://127.0.0.1:5000/admin',
            {user_id:user_id},
                {
                    headers:{
                        'Conten-Type': 'application/json'
                    }
                }
            )
            alert('user approved')
        }
    },
    mounted() {
        this.fetchUsers()
    },

}

</script>