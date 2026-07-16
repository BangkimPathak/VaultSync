let cachedPasswords = [];
let currentUser = null;

function openModal(id) {
    document.getElementById(id).classList.add('active');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('active');
}

// JS Helper Functions
function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function escapeJsString(str) {
    if (!str) return '';
    return str
        .replace(/\\/g, '\\\\')
        .replace(/'/g, "\\'")
        .replace(/"/g, '\\"')
        .replace(/\n/g, '\\n')
        .replace(/\r/g, '\\r');
}

async function copyText(text, label) {
    try {
        await navigator.clipboard.writeText(text);
        showToast(`${label} copied to clipboard!`, 'success');
    } catch (err) {
        console.error('Failed to copy: ', err);
        showToast('Failed to copy to clipboard.', 'error');
    }
}

function togglePasswordVisibility(inputId, btn) {
    const input = document.getElementById(inputId);
    const icon = btn.querySelector('i');
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'far fa-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'far fa-eye';
    }
}

function toggleCardPassword(btn, id) {
    const pwdVal = document.getElementById(`pwd-val-${id}`);
    const icon = btn.querySelector('i');
    
    if (pwdVal.dataset.visible === "false") {
        pwdVal.textContent = pwdVal.dataset.realPassword;
        pwdVal.dataset.visible = "true";
        icon.className = "far fa-eye-slash";
    } else {
        pwdVal.textContent = "••••••••";
        pwdVal.dataset.visible = "false";
        icon.className = "far fa-eye";
    }
}

// --- PROFILE LOADING ---
async function loadProfile() {
    try {
        const response = await fetch('/api/user/profile');
        if (response.ok) {
            const result = await response.json();
            currentUser = result.user;
        } else if (response.status === 401) {
            window.location.href = '/';
        }
    } catch (err) {
        console.error("Error loading user profile", err);
    }
}

// --- PASSWORD VAULT CONTROLLER ---
async function fetchPasswords() {
    const grid = document.getElementById('passwordsGrid');
    const emptyState = document.getElementById('passwordEmptyState');
    grid.innerHTML = '';
    
    try {
        const response = await fetch('/api/passwords');
        if (response.ok) {
            const result = await response.json();
            cachedPasswords = result.passwords;
            
            if (cachedPasswords.length === 0) {
                emptyState.style.display = 'block';
                return;
            }
            emptyState.style.display = 'none';

            cachedPasswords.forEach(item => {
                const card = document.createElement('div');
                card.className = 'vault-card glass';
                card.id = `pwd-card-${item.id}`;
                card.innerHTML = `
                    <div>
                        <div class="card-header">
                            <div class="card-icon">${item.website_name.substring(0, 2).toUpperCase()}</div>
                            <div class="card-title-group">
                                <h4 class="card-site-name">${escapeHtml(item.website_name)}</h4>
                                <p class="card-username">${escapeHtml(item.username)}</p>
                            </div>
                            <button class="btn-icon" title="Copy Username" onclick="copyText('${escapeJsString(item.username)}', 'Username')">
                                <i class="far fa-user"></i>
                            </button>
                        </div>
                        <div class="card-body">
                            <span class="card-password-val" id="pwd-val-${item.id}" data-real-password="${escapeHtml(item.password)}" data-visible="false">••••••••</span>
                            <div style="display: flex; gap: 0.35rem;">
                                <button class="btn-icon" style="padding: 0.35rem;" onclick="toggleCardPassword(this, ${item.id})">
                                    <i class="far fa-eye"></i>
                                </button>
                                <button class="btn-icon" style="padding: 0.35rem;" title="Copy Password" onclick="copyText('${escapeJsString(item.password)}', 'Password')">
                                    <i class="far fa-copy"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="card-actions">
                        <button class="btn btn-secondary btn-icon" style="padding: 0.45rem 0.75rem;" onclick="triggerEditPassword(${item.id})">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="btn btn-danger btn-icon" style="padding: 0.45rem 0.75rem;" onclick="deletePasswordRecord(${item.id})">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                `;
                grid.appendChild(card);
            });
        }
    } catch (err) {
        console.error("Error retrieving passwords", err);
        showToast("Failed to fetch passwords.", "error");
    }
}

document.getElementById('addPasswordForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const website_name = document.getElementById('addWebName').value;
    const username = document.getElementById('addUsername').value;
    const password = document.getElementById('addPassword').value;
    const confirmPassword = document.getElementById('addConfirmPassword').value;

    if (password !== confirmPassword) {
        showToast("Passwords do not match.", "error");
        return;
    }

    try {
        const response = await fetch('/api/passwords', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ website_name, username, password })
        });
        const result = await response.json();
        if (response.ok) {
            showToast(result.message, 'success');
            closeModal('addPasswordModal');
            document.getElementById('addPasswordForm').reset();
            fetchPasswords();
        } else {
            showToast(result.message, 'error');
        }
    } catch (err) {
        console.error(err);
        showToast("Failed to save password.", "error");
    }
});

function triggerEditPassword(id) {
    const item = cachedPasswords.find(p => p.id === id);
    if (!item) return;

    document.getElementById('editPasswordId').value = item.id;
    document.getElementById('editWebName').value = item.website_name;
    document.getElementById('editUsername').value = item.username;
    document.getElementById('editPasswordVal').value = item.password;
    
    openModal('editPasswordModal');
}

document.getElementById('editPasswordForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('editPasswordId').value;
    const website_name = document.getElementById('editWebName').value;
    const username = document.getElementById('editUsername').value;
    const password = document.getElementById('editPasswordVal').value;

    try {
        const response = await fetch(`/api/passwords/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ website_name, username, password })
        });
        const result = await response.json();
        if (response.ok) {
            showToast(result.message, 'success');
            closeModal('editPasswordModal');
            fetchPasswords();
        } else {
            showToast(result.message, 'error');
        }
    } catch (err) {
        console.error(err);
        showToast("Failed to update credentials.", "error");
    }
});

async function deletePasswordRecord(id) {
    if (!confirm("Are you sure you want to delete these credentials?")) return;

    try {
        const response = await fetch(`/api/passwords/${id}`, {
            method: 'DELETE'
        });
        const result = await response.json();
        if (response.ok) {
            showToast(result.message, 'success');
            fetchPasswords();
        } else {
            showToast(result.message, 'error');
        }
    } catch (err) {
        console.error(err);
        showToast("Failed to delete record.", "error");
    }
}

function filterPasswords() {
    const query = document.getElementById('searchPasswords').value.toLowerCase();
    const cards = document.querySelectorAll('#passwordsGrid .vault-card');
    
    cards.forEach(card => {
        const siteName = card.querySelector('.card-site-name').textContent.toLowerCase();
        const username = card.querySelector('.card-username').textContent.toLowerCase();
        if (siteName.includes(query) || username.includes(query)) {
            card.style.display = 'flex';
        } else {
            card.style.display = 'none';
        }
    });
}

// Toast notification helpers
function showToast(message, type) {
    const toast = document.getElementById('toast-message');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.remove('hidden');
    setTimeout(hideToast, 3000);
}

function hideToast() {
    const toast = document.getElementById('toast-message');
    toast.className = 'toast hidden';
}

// --- LOGOUT CONTROLLER ---
async function handleLogout() {
    if (!confirm("Confirm logging out of VaultSync?")) return;
    try {
        const response = await fetch('/api/logout', { method: 'POST' });
        const result = await response.json();
        if (response.ok) {
            localStorage.removeItem('currentUser');
            window.location.href = result.redirect;
        }
    } catch (err) {
        console.error("Logout failed", err);
    }
}

// Run on Mount
window.addEventListener('DOMContentLoaded', () => {
    loadProfile();
    fetchPasswords();
});
