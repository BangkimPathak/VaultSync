let currentUser = null;

// ── Toast helpers ──────────────────────────────────────────────
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

// ── Load profile from DB ───────────────────────────────────────
async function loadProfile() {
    try {
        const response = await fetch('/api/user/profile');

        if (response.status === 401) {
            window.location.href = '/';
            return;
        }

        if (!response.ok) {
            showToast('Failed to load profile data.', 'error');
            return;
        }

        const result = await response.json();
        currentUser = result.user;

        // ── Populate Edit Credentials form ──────────────────────
        const profileNameInput = document.getElementById('profileName');
        if (profileNameInput) profileNameInput.value = currentUser.name || '';
        
        const altEmailInput = document.getElementById('profileAltEmail');
        if (altEmailInput) altEmailInput.value = currentUser.alt_email || currentUser.alternative_email || '';

        document.getElementById('profileEmail').value = currentUser.email        || '';
        document.getElementById('profilePhone').value = currentUser.phone_number  || '';
        document.getElementById('profileAge').value   = currentUser.age          || '';
        
        const dobInput = document.getElementById('profileDob');
        if (dobInput) dobInput.value = currentUser.dob || '';

        // ── Populate Profile Card Widget (live view of saved data)
        document.getElementById('widgetName').textContent  = currentUser.name         || '—';
        if (document.getElementById('displayFullName')) {
            document.getElementById('displayFullName').textContent = currentUser.name || '—';
        }
        document.getElementById('widgetEmail').textContent = currentUser.email        || '—';
        const widgetAltEmail = document.getElementById('widgetAltEmail');
        if (widgetAltEmail) {
            widgetAltEmail.textContent = currentUser.alt_email || currentUser.alternative_email || '—';
        }
        document.getElementById('widgetPhone').textContent = currentUser.phone_number  || '—';
        document.getElementById('widgetAge').textContent   = currentUser.age          || '—';
        
        if (document.getElementById('widgetDob')) {
            document.getElementById('widgetDob').textContent = currentUser.dob || '—';
        }
        if (document.getElementById('widgetCreatedAt')) {
            document.getElementById('widgetCreatedAt').textContent = currentUser.created_at || '—';
        }

        // ── Avatar (initials fallback) ───────────────────────────
        const defaultAvatar = `https://ui-avatars.com/api/?name=${encodeURIComponent(currentUser.name || 'User')}&background=007B8A&color=fff`;
        const avatarSrc = currentUser.profile_picture
            ? `/static/uploads/${currentUser.profile_picture}`
            : defaultAvatar;
        document.getElementById('widgetAvatar').src = avatarSrc;

    } catch (err) {
        console.error('Error loading user profile', err);
        showToast('Failed to load user profile.', 'error');
    }
}

// ── Save Changes (UPDATE users SET name, phone_number, age, alt_email, dob) ────
document.getElementById('profileForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const nameInput = document.getElementById('profileName');
    const name = nameInput ? nameInput.value.trim() : (currentUser ? currentUser.name : '');
    const altEmailInput = document.getElementById('profileAltEmail');
    const altEmail = altEmailInput ? altEmailInput.value.trim() : '';
    const phone = document.getElementById('profilePhone').value.trim();
    const age   = document.getElementById('profileAge').value.trim();
    const dobInput = document.getElementById('profileDob');
    const dob = dobInput ? dobInput.value : '';

    // Basic validation
    if (!name || !phone || !age) {
        showToast('Name, phone number and age are required.', 'error');
        return;
    }
    if (isNaN(age) || Number(age) <= 0 || Number(age) > 120) {
        showToast('Please enter a valid age.', 'error');
        return;
    }

    // Show loading state on button
    const saveBtn = document.getElementById('saveBtn');
    const originalText = saveBtn.textContent;
    saveBtn.textContent = 'Saving…';
    saveBtn.disabled = true;

    const formData = new FormData();
    formData.append('name',         name);
    formData.append('alt_email',    altEmail);
    formData.append('phone_number', phone);
    formData.append('age',          age);
    formData.append('dob',          dob);

    try {
        const response = await fetch('/api/user/profile', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok && result.status === 'success') {
            showToast('Profile updated successfully!', 'success');
            // Refresh widget to show new data
            loadProfile();
            // Hide edit form
            const widget = document.getElementById('editCredentialsWidget');
            if (widget) widget.classList.add('hidden');
        } else {
            showToast(result.message || 'Failed to update profile.', 'error');
        }

    } catch (err) {
        console.error(err);
        showToast('An error occurred. Please try again.', 'error');
    } finally {
        saveBtn.textContent = originalText;
        saveBtn.disabled = false;
    }
});

// ── Logout ─────────────────────────────────────────────────────
async function handleLogout() {
    if (!confirm('Confirm logging out of VaultSync?')) return;
    try {
        const response = await fetch('/api/logout', { method: 'POST' });
        const result   = await response.json();
        if (response.ok) {
            localStorage.removeItem('currentUser');
            window.location.href = result.redirect;
        }
    } catch (err) {
        console.error('Logout failed', err);
    }
}

// ── Toggle Edit Credentials Widget ──────────────────────────────
function toggleEditCredentials() {
    const widget = document.getElementById('editCredentialsWidget');
    if (!widget) return;
    if (widget.classList.contains('hidden')) {
        widget.classList.remove('hidden');
        widget.scrollIntoView({ behavior: 'smooth' });
    } else {
        widget.classList.add('hidden');
    }
}

// ── On page load ───────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
    loadProfile();
});
