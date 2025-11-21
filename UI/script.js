// Configuration
const API_URL = 'http://localhost:8000';

// State Management
const state = {
    todos: [],
    filteredTodos: [],
    currentFilter: 'all',
    editingId: null,
};

// DOM Elements
const todoForm = document.getElementById('todoForm');
const titleInput = document.getElementById('title');
const descriptionInput = document.getElementById('description');
const priorityInput = document.getElementById('priority');
const todosList = document.getElementById('todosList');
const searchInput = document.getElementById('searchInput');
const healthStatus = document.getElementById('healthStatus');
const statusText = document.getElementById('statusText');
const totalCount = document.getElementById('totalCount');
const highCount = document.getElementById('highCount');
const mediumCount = document.getElementById('mediumCount');
const lowCount = document.getElementById('lowCount');
const deleteAllBtn = document.getElementById('deleteAllBtn');
const exportBtn = document.getElementById('exportBtn');
const editModal = document.getElementById('editModal');
const editForm = document.getElementById('editForm');
const cancelEditBtn = document.getElementById('cancelEditBtn');
const filterButtons = document.querySelectorAll('.filter-btn');

// Toast Function
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Check API Health
async function checkHealth() {
    try {
        const response = await fetch(`${API_URL}/health/`);
        if (response.ok) {
            healthStatus.style.background = '#10b981';
            statusText.textContent = 'Connected';
            return true;
        }
    } catch (error) {
        healthStatus.style.background = '#ef4444';
        statusText.textContent = 'Disconnected';
    }
    return false;
}

// Fetch all todos
async function fetchTodos() {
    try {
        const response = await fetch(`${API_URL}/todos/`);
        if (!response.ok) throw new Error('Failed to fetch todos');
        state.todos = await response.json();
        updateStats();
        applyFilter();
        renderTodos();
    } catch (error) {
        console.error('Error fetching todos:', error);
        showToast('Failed to load todos', 'error');
    }
}

// Get stats
async function updateStats() {
    try {
        const response = await fetch(`${API_URL}/todos/stats/`);
        if (!response.ok) throw new Error('Failed to fetch stats');
        const stats = await response.json();
        
        totalCount.textContent = state.todos.length;
        highCount.textContent = stats.High || 0;
        mediumCount.textContent = stats.Medium || 0;
        lowCount.textContent = stats.Low || 0;
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

// Create new todo
async function createTodo(todoData) {
    try {
        const response = await fetch(`${API_URL}/todos/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: '',
                ...todoData,
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create todo');
        }

        await fetchTodos();
        todoForm.reset();
        showToast('Todo created successfully!', 'success');
    } catch (error) {
        console.error('Error creating todo:', error);
        showToast(error.message || 'Failed to create todo', 'error');
    }
}

// Update todo
async function updateTodo(id, todoData) {
    try {
        const response = await fetch(`${API_URL}/todos/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id,
                ...todoData,
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to update todo');
        }

        await fetchTodos();
        closeEditModal();
        showToast('Todo updated successfully!', 'success');
    } catch (error) {
        console.error('Error updating todo:', error);
        showToast(error.message || 'Failed to update todo', 'error');
    }
}

// Delete todo
async function deleteTodo(id) {
    if (!confirm('Are you sure you want to delete this todo?')) return;

    try {
        const response = await fetch(`${API_URL}/todos/${id}`, {
            method: 'DELETE',
        });

        if (!response.ok) throw new Error('Failed to delete todo');

        await fetchTodos();
        showToast('Todo deleted successfully!', 'success');
    } catch (error) {
        console.error('Error deleting todo:', error);
        showToast('Failed to delete todo', 'error');
    }
}

// Delete all todos
async function deleteAllTodos() {
    if (!confirm('Are you sure you want to delete ALL todos? This cannot be undone!')) return;

    try {
        const response = await fetch(`${API_URL}/todos/`, {
            method: 'DELETE',
        });

        if (!response.ok) throw new Error('Failed to delete all todos');

        await fetchTodos();
        showToast('All todos deleted!', 'success');
    } catch (error) {
        console.error('Error deleting all todos:', error);
        showToast('Failed to delete all todos', 'error');
    }
}

// Search todos
async function searchTodos(query) {
    if (!query.trim()) {
        applyFilter();
        renderTodos();
        return;
    }

    try {
        const response = await fetch(`${API_URL}/todos/search/?query=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('Failed to search todos');
        
        state.filteredTodos = await response.json();
        renderTodos();
    } catch (error) {
        console.error('Error searching todos:', error);
        showToast('Failed to search todos', 'error');
    }
}

// Apply filter
function applyFilter() {
    if (state.currentFilter === 'all') {
        state.filteredTodos = [...state.todos];
    } else {
        state.filteredTodos = state.todos.filter(
            todo => todo.priority === state.currentFilter
        );
    }
}

// Render todos
function renderTodos() {
    if (state.filteredTodos.length === 0) {
        todosList.innerHTML = '<div class="empty-state"><p>No todos found. 🔍</p></div>';
        return;
    }

    todosList.innerHTML = state.filteredTodos.map(todo => `
        <div class="todo-item ${todo.priority.toLowerCase()}">
            <input 
                type="checkbox" 
                class="todo-checkbox"
                ${Math.random() > 0.5 ? 'checked' : ''}
            >
            <div class="todo-content">
                <div class="todo-title">${escapeHtml(todo.title)}</div>
                ${todo.description ? `<div class="todo-description">${escapeHtml(todo.description)}</div>` : ''}
                <div class="todo-meta">
                    <span class="todo-priority ${todo.priority.toLowerCase()}">
                        ${todo.priority}
                    </span>
                </div>
            </div>
            <div class="todo-actions">
                <button class="btn-sm btn-edit" onclick="openEditModal('${todo.id}', '${escapeHtml(todo.title)}', '${escapeHtml(todo.description || '')}', '${todo.priority}')">
                    Edit
                </button>
                <button class="btn-sm btn-delete" onclick="deleteTodo('${todo.id}')">
                    Delete
                </button>
            </div>
        </div>
    `).join('');
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Edit Modal Functions
function openEditModal(id, title, description, priority) {
    state.editingId = id;
    document.getElementById('editTitle').value = title;
    document.getElementById('editDescription').value = description;
    document.getElementById('editPriority').value = priority;
    editModal.classList.add('active');
}

function closeEditModal() {
    editModal.classList.remove('active');
    state.editingId = null;
}

// Export todos
function exportTodos() {
    const dataStr = JSON.stringify(state.todos, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `todos_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    showToast('Todos exported successfully!', 'success');
}

// Event Listeners
todoForm.addEventListener('submit', (e) => {
    e.preventDefault();
    createTodo({
        title: titleInput.value,
        description: descriptionInput.value,
        priority: priorityInput.value,
    });
});

editForm.addEventListener('submit', (e) => {
    e.preventDefault();
    updateTodo(state.editingId, {
        title: document.getElementById('editTitle').value,
        description: document.getElementById('editDescription').value,
        priority: document.getElementById('editPriority').value,
    });
});

searchInput.addEventListener('input', (e) => {
    searchTodos(e.target.value);
});

filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        filterButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.currentFilter = btn.dataset.filter;
        applyFilter();
        renderTodos();
    });
});

deleteAllBtn.addEventListener('click', deleteAllTodos);
exportBtn.addEventListener('click', exportTodos);
cancelEditBtn.addEventListener('click', closeEditModal);

// Close modal when clicking outside
editModal.addEventListener('click', (e) => {
    if (e.target === editModal) {
        closeEditModal();
    }
});

// Modal close button
document.querySelector('.modal-close').addEventListener('click', closeEditModal);

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    await checkHealth();
    await fetchTodos();
    
    // Refresh health status every 10 seconds
    setInterval(checkHealth, 10000);
});

// Export for use in HTML
window.deleteTodo = deleteTodo;
window.openEditModal = openEditModal;
