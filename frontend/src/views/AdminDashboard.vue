<template>
    <div>
        <h2>Admin Dashboard</h2>
        <h3>Unapproved Users</h3>
        <p v-if="message">{{ message }}</p>
        <ul v-if="unapprovedUsers.length">
            <li v-for="user in unapprovedUsers" :key="user.user_id">
                {{ user.username }} ({{ user.email }}) - Role: {{ user.role }}
                <button @click="approveUser(user.user_id)">Approve</button>
                <button @click="deleteUser(user.user_id)">Delete</button>
                <select @change="updateUserRole(user.user_id, $event.target.value)">
                    <option value="">Change Role</option>
                    <option value="admin">Admin</option>
                    <option value="manager">Manager</option>
                    <option value="employee">Employee</option>
                </select>
            </li>
        </ul>
        <p v-else>No unapproved users.</p>

        <h3>All Tasks</h3>
        <ul v-if="allTasks.length">
            <li v-for="task in allTasks" :key="task.id">
                <strong>{{ task.title }}</strong> - {{ task.description }} <br>
                Status: {{ task.status }}, Assigned to: {{ task.assigned_user_id }}
                <button @click="deleteTask(task.id)">Delete Task</button>
            </li>
        </ul>
        <p v-else>No tasks available.</p>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            unapprovedUsers: [],
            allTasks: [],
            message: ''
        };
    },
    created() {
        this.fetchUnapprovedUsers();
        this.fetchAllTasks();
    },
    methods: {
        // Set up Axios to include the JWT token in headers for all requests
        getAuthHeaders() {
            const token = localStorage.getItem('token');
            return {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            };
        },
        async fetchUnapprovedUsers() {
            try {
                const response = await axios.get('http://127.0.0.1:5000/admin/users', this.getAuthHeaders());
                this.unapprovedUsers = response.data;
            } catch (error) {
                this.message = error.response?.data?.message || 'Failed to fetch unapproved users.';
                console.error('Error fetching unapproved users:', error);
            }
        },
        async approveUser(userId) {
            try {
                const response = await axios.post('http://127.0.0.1:5000/admin/users', { user_id: userId }, this.getAuthHeaders());
                this.message = response.data.msg;
                this.fetchUnapprovedUsers(); // Refresh the list
            } catch (error) {
                this.message = error.response?.data?.message || 'Failed to approve user.';
                console.error('Error approving user:', error);
            }
        },
        async deleteUser(userId) {
            try {
                const response = await axios.delete('http://127.0.0.1:5000/admin/users', { data: { user_id: userId }, ...this.getAuthHeaders() });
                this.message = response.data.msg;
                this.fetchUnapprovedUsers(); // Refresh the list
            } catch (error) {
                this.message = error.response?.data?.message || 'Failed to delete user.';
                console.error('Error deleting user:', error);
            }
        },
        async updateUserRole(userId, newRole) {
            if (!newRole) return; // Don't do anything if no role is selected
            try {
                const response = await axios.put('http://127.0.0.1:5000/admin/users', { user_id: userId, role: newRole }, this.getAuthHeaders());
                this.message = response.data.msg;
                this.fetchUnapprovedUsers(); // Refresh the list
            } catch (error) {
                this.message = error.response?.data?.message || 'Failed to update user role.';
                console.error('Error updating user role:', error);
            }
        },
        async fetchAllTasks() {
            try {
                const response = await axios.get('http://127.0.0.1:5000/task', this.getAuthHeaders());
                this.allTasks = response.data;
            } catch (error) {
                this.message = error.response?.data?.message || 'Failed to fetch tasks.';
                console.error('Error fetching tasks:', error);
            }
        },
        async deleteTask(taskId) {
            try {
                const response = await axios.delete(`http://127.0.0.1:5000/task/${taskId}`, this.getAuthHeaders());
                this.message = response.data.msg;
                this.fetchAllTasks(); // Refresh the list
            } catch (error) {
                this.message = error.response?.data?.message || 'Failed to delete task.';
                console.error('Error deleting task:', error);
            }
        }
    }
};
</script>