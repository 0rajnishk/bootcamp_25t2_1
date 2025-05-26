<template>
    <div>
        <h2>Employee Dashboard</h2>
        <h3>My Tasks</h3>
        <p v-if="message">{{ message }}</p>
        <ul v-if="myTasks.length">
            <li v-for="task in myTasks" :key="task.id">
                <strong>{{ task.title }}</strong> - {{ task.description }} <br>
                Current Status: {{ task.status }}
                <select @change="updateTaskStatus(task.id, $event.target.value)">
                    <option :value="task.status" selected disabled>Change Status</option>
                    <option value="open">Open</option>
                    <option value="in progress">In Progress</option>
                    <option value="closed">Closed</option>
                </select>
            </li>
        </ul>
        <p v-else>No tasks assigned to you.</p>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            myTasks: [],
            message: ''
        };
    },
    created() {
        this.fetchMyTasks();
    },
    methods: {
        getAuthHeaders() {
            const token = localStorage.getItem('token');
            return {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            };
        },
        async fetchMyTasks() {
            try {
                // Assuming your backend /task endpoint handles employee role by filtering tasks
                const response = await axios.get('http://127.0.0.1:5000/task', this.getAuthHeaders());
                this.myTasks = response.data;
            } catch (error) {
                this.message = error.response?.data?.message || 'Failed to fetch your tasks.';
                console.error('Error fetching employee tasks:', error);
            }
        },
        async updateTaskStatus(taskId, newStatus) {
            try {
                const response = await axios.put(`http://127.0.0.1:5000/task/${taskId}`, { status: newStatus }, this.getAuthHeaders());
                this.message = response.data.msg;
                this.fetchMyTasks(); // Refresh tasks after update
            } catch (error) {
                this.message = error.response?.data?.message || 'Failed to update task status.';
                console.error('Error updating task status:', error);
            }
        }
    }
};
</script>