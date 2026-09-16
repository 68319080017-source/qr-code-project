// QR Asset Management - Main JavaScript Module

const API_BASE = '/api/v1';

function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

async function apiGet(endpoint) {
    const resp = await fetch(`${API_BASE}${endpoint}`, {
        headers: getAuthHeaders()
    });
    if (resp.status === 401) {
        window.location.href = '/login';
        return null;
    }
    return resp.json();
}

async function apiPost(endpoint, data) {
    const resp = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...getAuthHeaders()
        },
        body: JSON.stringify(data)
    });
    if (resp.status === 401) {
        window.location.href = '/login';
        return null;
    }
    return resp;
}

async function apiDelete(endpoint) {
    const resp = await fetch(`${API_BASE}${endpoint}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
    });
    return resp;
}

// Format number with commas
function formatNumber(num) {
    return new Intl.NumberFormat('th-TH').format(num);
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('th-TH', {
        style: 'currency',
        currency: 'THB'
    }).format(amount);
}

// Status badge helper
function statusBadge(status) {
    const map = {
        'ปกติ': 'bg-success',
        'ชำรุด': 'bg-danger',
        'รอซ่อม': 'bg-warning text-dark',
        'จำหน่ายแล้ว': 'bg-secondary',
        'ค้างตรวจสอบ': 'bg-info text-dark',
        'สูญหาย': 'bg-dark'
    };
    const cls = map[status] || 'bg-secondary';
    return `<span class="badge ${cls}">${status}</span>`;
}

// Toast notification
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;

    const icon = type === 'success' ? 'fa-check-circle text-success' : 'fa-exclamation-circle text-danger';
    const html = `
        <div class="toast show align-items-center border-0 mb-2" role="alert" style="background: var(--dark); border: 1px solid var(--glass-border) !important;">
            <div class="d-flex">
                <div class="toast-body text-light">
                    <i class="fa-solid ${icon} me-2"></i>${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    toastContainer.insertAdjacentHTML('beforeend', html);
    setTimeout(() => {
        const toast = toastContainer.querySelector('.toast:first-child');
        if (toast) toast.remove();
    }, 4000);
}
