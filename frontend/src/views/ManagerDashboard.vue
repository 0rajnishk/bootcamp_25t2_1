<template>
    <div>
        <h2>Manager Dashboard</h2>

        <h3>Create New Task</h3>
        <TaskForm @task-created="handleTaskCreated" />

        <h3>All Tasks</h3>
        <p v-if="message">{{ message }}</p>
        <ul v-if="tasks.length">
            <li v-for="task in tasks" :key="task.id">
                <strong>{{ task.title }}</strong> - {{ task.description }} <br>
                Status: {{ task.status }}, Assigned to: {{ task.assigned_user_id }} <br>
                Deadline: {{ task.deadline }}
                <button @click="editTask(task)">Edit</button>
                <button @click="deleteTask(task.id)">Delete</button>
            </li>
        </ul>
        <p v-else>No tasks available.</p>

        <div v-if="editingTask">
            <h3>Edit Task</h3>
            <form @submit.prevent="updateTask">
                <input type="text" v-model="editingTask.title" placeholder="Title" required>
                <input type="text" v-model="editingTask.description" placeholder="Description" required>
                <select v-model="editingTask.status">
                    <option value="open">Open</option>
                    <option value="in progress">In Progress</option>
                    <option value="closed">Closed</option>
                </select>
                <input type="number" v-model="editingTask.assigned_user_id" placeholder="Assigned User ID" required>
                <input type="datetime-local" v-model="editingTask.deadline" required>
                <button type="submit">Update Task</button>
                <button @click="cancelEdit">Cancel</button>
            </form>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import TaskForm from '../components/TaskForm.vue'; // Import the TaskForm component

export default {
    components: {
        TaskForm // Register the TaskForm component
    },
    data() {
        return {
            tasks: [],
            users: [], // Holds all users for task assignment
            message: '',
            editingTask: null // Holds the task being edited
        };
    },

    created() {
        this.fetchTasks();
        this.fetchAllUsers(); // Fetch all users on component creation
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
        async fetchTasks() {
            try {
                const token = localStorage.getItem('token');
                const response = await axios.get('http://127.0.0.1:5000/task', 
                    {
                        headers: {
                            Authorization: `Bearer ${token}`
                        } 
                    }
                );
                this.tasks = response.data;
            } catch (error) {
                this.message = error.response?.data?.message || 'Failed to fetch tasks.';
                console.error('Error fetching tasks:', error);
            }
        },
        async fetchAllUsers(){
            try {
                const response = await axios.get('http://127.0.0.1:5000/all_users', this.getAuthHeaders());
                this.users = response.data;
                alert(JSON.stringify(this.users));
            } catch (error) {
                this.message = error.response?.data?.message || 'Failed to fetch tasks.';
                console.error('Error fetching tasks:', error);
            }
        },
        handleTaskCreated() {
            this.message = 'Task created successfully!';
            this.fetchTasks(); // Refresh tasks after creation
        },
        editTask(task) {
            // Create a copy to avoid directly modifying the list item before saving
            this.editingTask = { ...task };
            // Format deadline for datetime-local input
            if (this.editingTask.deadline) {
                this.editingTask.deadline = this.editingTask.deadline.slice(0, 16); // "YYYY-MM-DDTHH:MM"
            }
        },
        async updateTask() {
            try {
                const payload = { ...this.editingTask };
                // Ensure deadline is in the correct format for the backend
                payload.deadline = payload.deadline.replace('T', ' ') + ':00'; // "YYYY-MM-DD HH:MM:SS"

                const response = await axios.put(`http://127.0.0.1:5000/task/${this.editingTask.id}`, payload, this.getAuthHeaders());
                this.message = response.data.msg;
                this.editingTask = null; // Clear editing state
                this.fetchTasks(); // Refresh tasks after update
            } catch (error) {
                this.message = error.response?.data?.message || 'Failed to update task.';
                console.error('Error updating task:', error);
            }
        },
        cancelEdit() {
            this.editingTask = null; // Clear editing state
        },
        async deleteTask(taskId) {
            try {
                const response = await axios.delete(`http://127.0.0.1:5000/task/${taskId}`, this.getAuthHeaders());
                this.message = response.data.msg;
                this.fetchTasks(); // Refresh tasks after deletion
            } catch (error) {
                this.message = error.response?.data?.message || 'Failed to delete task.';
                console.error('Error deleting task:', error);
            }
        }
    }
};
</script>

