<template>
    <form @submit.prevent="createTask">
        <div>
            <label for="title">Title:</label>
            <input type="text" id="title" v-model="title" required>
        </div>
        <div>
            <label for="description">Description:</label>
            <textarea id="description" v-model="description" required></textarea>
        </div>
        <div>
            <label for="status">Status:</label>
            <select id="status" v-model="status">
                <option value="open">Open</option>
                <option value="in progress">In Progress</option>
                <option value="closed">Closed</option>
            </select>
        </div>
        <div>
            <label for="assigned_user_id">Assigned User ID:</label>
            <input type="number" id="assigned_user_id" v-model="assigned_user_id" required>
        </div>
        <div>
            <label for="deadline">Deadline:</label>
            <input type="datetime-local" id="deadline" v-model="deadline" required>
        </div>
        <button type="submit">Add Task</button>
        <p v-if="message">{{ message }}</p>
    </form>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            title: '',
            description: '',
            status: 'open',
            assigned_user_id: null,
            deadline: '',
            message: ''
        };
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
        async createTask() {
            try {
                const formattedDeadline = this.deadline.replace('T', ' ') + ':00'; // "YYYY-MM-DD HH:MM:SS"
                const response = await axios.post('http://127.0.0.1:5000/task', {
                    title: this.title,
                    description: this.description,
                    status: this.status,
                    assigned_user_id: this.assigned_user_id,
                    deadline: formattedDeadline
                }, this.getAuthHeaders());
                this.message = response.data.msg;
                // Clear form fields
                this.title = '';
                this.description = '';
                this.status = 'open';
                this.assigned_user_id = null;
                this.deadline = '';
                this.$emit('task-created'); // Emit event to parent to refresh tasks
            } catch (error) {
                this.message = error.response?.data?.message || 'Failed to create task.';
                console.error('Error creating task:', error);
            }
        }
    }
};
</script>

<style scoped>
form div {
    margin-bottom: 10px;
}

label {
    display: block;
    margin-bottom: 5px;
}

input[type="text"],
input[type="number"],
input[type="datetime-local"],
select,
textarea {
    width: 100%;
    padding: 8px;
    box-sizing: border-box;
}

button {
    padding: 10px 15px;
    background-color: #007bff;
    color: white;
    border: none;
    cursor: pointer;
}
</style>