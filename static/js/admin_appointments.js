let approveUrl     = null;
let adminCancelUrl = null;
let rescheduleUrl  = null;
let restoreUrl     = null;

document.addEventListener('DOMContentLoaded', function () {

    document.querySelectorAll('.approve-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            approveUrl = btn.dataset.approveUrl;
            document.getElementById('approveModal').classList.add('active');
        });
    });

    document.querySelectorAll('.admin-cancel-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            adminCancelUrl = btn.dataset.cancelUrl;
            document.getElementById('adminCancelModal').classList.add('active');
        });
    });

    document.querySelectorAll('.reschedule-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            rescheduleUrl = btn.dataset.rescheduleUrl;
            document.getElementById('reschedulePatientName').textContent = btn.dataset.patient;
            document.getElementById('rescheduleDate').textContent        = btn.dataset.date;
            document.getElementById('rescheduleTime').textContent        = btn.dataset.time;
            // Clear previous window values
            document.getElementById('rescheduleFrom').value = '';
            document.getElementById('rescheduleTo').value   = '';
            document.getElementById('rescheduleModal').classList.add('active');
        });
    });

    document.querySelectorAll('.restore-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            restoreUrl = btn.dataset.restoreUrl;
            document.getElementById('restoreModal').classList.add('active');
        });
    });
});

function closeApproveModal()     { document.getElementById('approveModal').classList.remove('active'); approveUrl = null; }
function confirmApprove()        { if (approveUrl) window.location.href = approveUrl; }

function closeAdminCancelModal() { document.getElementById('adminCancelModal').classList.remove('active'); adminCancelUrl = null; }
function confirmAdminCancel()    { if (adminCancelUrl) window.location.href = adminCancelUrl; }

function closeRescheduleModal()  { document.getElementById('rescheduleModal').classList.remove('active'); rescheduleUrl = null; }
function confirmReschedule() {
    if (!rescheduleUrl) return;
    const from = document.getElementById('rescheduleFrom').value;
    const to   = document.getElementById('rescheduleTo').value;
    // Append the optional window as query params so the backend can store them
    const url = new URL(rescheduleUrl, window.location.origin);
    if (from) url.searchParams.set('window_from', from);
    if (to)   url.searchParams.set('window_to', to);
    window.location.href = url.toString();
}

function closeRestoreModal()     { document.getElementById('restoreModal').classList.remove('active'); restoreUrl = null; }
function confirmRestore()        { if (restoreUrl) window.location.href = restoreUrl; }

function openFilterModal()       { document.getElementById('filterModal').classList.add('active'); }
function closeFilterModal()      { document.getElementById('filterModal').classList.remove('active'); }

// Close any modal when clicking the backdrop
window.addEventListener('click', function (e) {
    ['approveModal', 'adminCancelModal', 'rescheduleModal', 'restoreModal', 'filterModal'].forEach(id => {
        const m = document.getElementById(id);
        if (e.target === m) m.classList.remove('active');
    });
});

// ── Sidebar Toggle ──
const STORAGE_KEY = 'uhdc_sidebar_collapsed';
const shell   = document.querySelector('.shell');
const sidebar = document.getElementById('sidebar');

function toggleSidebar() {
    const isCollapsed = sidebar.classList.toggle('collapsed');
    shell.classList.toggle('sidebar-collapsed', isCollapsed);
    localStorage.setItem(STORAGE_KEY, isCollapsed ? 'true' : 'false');
}

(function () {
    if (localStorage.getItem(STORAGE_KEY) === 'true') {
        sidebar.classList.add('collapsed');
        shell.classList.add('sidebar-collapsed');
    }
})();