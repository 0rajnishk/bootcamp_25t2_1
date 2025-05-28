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
<div>
    <h3>Upload Document</h3>
    <form @submit.prevent="uploadDocument" enctype="multipart/form-data">
        <input type="file" @change="handleFileChange" required>
        <button type="submit">Upload</button>
    </form>
</div>
<p v-if="uploadMessage">{{ uploadMessage }}</p>
</template>
    


<script>
import axios from 'axios';

export default {
    data() {
        return {
            myTasks: [],
            message: '',
            selectedFile: null,
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
        },
        handleFileChange(event) {
            const file = event.target.files[0];
            this.selectedFile = file;
        },
        async uploadDocument() {
            if (!this.selectedFile) {
                this.uploadMessage = 'Please select a file to upload.';
                return;
            }
            const formData = new FormData();
            formData.append('document', this.selectedFile);

            try {
                const token = localStorage.getItem('token');
                const response = await axios.post(
                    'http://127.0.0.1:5000/upload_document',
                    formData,
                    {
                        headers: {
                            'Content-Type': 'multipart/form-data',
                            Authorization: `Bearer ${token}`
                        }
                    }
                );
                this.uploadMessage = response.data.msg || 'Document uploaded successfully!';
                this.selectedFile = null;
            } catch (error) {
                this.uploadMessage = error.response?.data?.message || 'Failed to upload document.';
                console.error('Error uploading document:', error);
            }
        },
    }
};
</script>