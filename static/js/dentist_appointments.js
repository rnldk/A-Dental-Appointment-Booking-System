let approveUrl    = null;
let rescheduleUrl = null;
let restoreUrl    = null;

/* ══════════ BIND BUTTONS ══════════ */
document.addEventListener('DOMContentLoaded', function () {

    document.querySelectorAll('.dentist-approve-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            approveUrl = btn.dataset.approveUrl;
            document.getElementById('approveModal').classList.add('active');
        });
    });

    document.querySelectorAll('.dentist-reschedule-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            rescheduleUrl = btn.dataset.rescheduleUrl;
            document.getElementById('reschedulePatientName').textContent = btn.dataset.patient;
            document.getElementById('rescheduleDate').textContent        = btn.dataset.date;
            document.getElementById('rescheduleTime').textContent        = btn.dataset.time;
            document.getElementById('rescheduleModal').classList.add('active');
        });
    });

    document.querySelectorAll('.dentist-restore-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            restoreUrl = btn.dataset.restoreUrl;
            document.getElementById('restorePatientName').textContent = btn.dataset.patient;
            document.getElementById('restoreModal').classList.add('active');
        });
    });
});

/* ══════════ MODAL CONTROLS ══════════ */
function closeApproveModal()    { document.getElementById('approveModal').classList.remove('active'); approveUrl = null; }
function confirmApprove()       { if (approveUrl) window.location.href = approveUrl; }

function closeRescheduleModal() { document.getElementById('rescheduleModal').classList.remove('active'); rescheduleUrl = null; }
function confirmReschedule()    { if (rescheduleUrl) window.location.href = rescheduleUrl; }

function closeRestoreModal()    { document.getElementById('restoreModal').classList.remove('active'); restoreUrl = null; }
function confirmRestore()       { if (restoreUrl) window.location.href = restoreUrl; }

/* Close on backdrop click */
window.addEventListener('click', function (e) {
    ['approveModal', 'rescheduleModal', 'restoreModal'].forEach(id => {
        const m = document.getElementById(id);
        if (e.target === m) m.classList.remove('active');
    });
});

/* ══════════ SIDEBAR TOGGLE ══════════ */
const STORAGE_KEY = 'uhdc_sidebar_collapsed';
const shell       = document.querySelector('.shell');
const sidebar     = document.getElementById('sidebar');

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