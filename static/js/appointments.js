/* ============================================================
   appointments.js
   Handles: edit modal, cancel modal, success modal
   Used by: patient_appointments.html
   ============================================================ */

let currentAppointmentId = null;
let cancelUrl = null;

// ── Initialise on DOM ready ─────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {

    // Bind Edit buttons
    document.querySelectorAll('.edit-btn').forEach(function (button) {
        button.addEventListener('click', function () {
            const appointmentId = this.getAttribute('data-appointment-id');
            openEditModal(parseInt(appointmentId));
        });
    });

    // Bind Cancel buttons
    document.querySelectorAll('.cancel-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            cancelUrl = btn.dataset.cancelUrl;
            document.getElementById('cancelModal').classList.add('active');
        });
    });

    // Reopen edit modal if there was a validation error on the previous submit
    if (typeof window.editAppointmentId !== 'undefined') {
        setTimeout(function () {
            openEditModal(parseInt(window.editAppointmentId));
        }, 100);
    }

    // Show success modal for booking or edit success
    const successModal = document.getElementById('successModal');
    const successTitle  = document.getElementById('successModalTitle');
    const successMsg    = document.getElementById('successModalMessage');

    if (successModal && successTitle) {
        if (window.bookingSuccess) {
            successTitle.textContent = 'Appointment Booked Successfully!';
            if (successMsg) {
                successMsg.textContent = 'Your appointment has been submitted and is awaiting approval.';
                successMsg.style.display = 'block';
            }
            successModal.classList.add('active');
        } else if (window.editSuccess) {
            successTitle.textContent = 'Appointment Updated Successfully!';
            if (successMsg) successMsg.style.display = 'none';
            successModal.classList.add('active');
        }
    }
});

// ── Edit Modal ──────────────────────────────────────────────
function openEditModal(appointmentId) {
    currentAppointmentId = appointmentId;
    const modal = document.getElementById('editModal');
    const form  = document.getElementById('editForm');
    if (form)  form.action = '/patient/edit/' + appointmentId;
    if (modal) modal.classList.add('active');
}

function closeEditModal() {
    const modal = document.getElementById('editModal');
    if (modal) modal.classList.remove('active');
}

// ── Cancel Modal ────────────────────────────────────────────
function closeCancelModal() {
    document.getElementById('cancelModal').classList.remove('active');
    cancelUrl = null;
}

function confirmCancel() {
    if (cancelUrl) window.location.href = cancelUrl;
}

// ── Success Modal ───────────────────────────────────────────
function closeSuccessModal() {
    const modal = document.getElementById('successModal');
    if (modal) modal.classList.remove('active');
}

// ── Close modals on backdrop click ──────────────────────────
window.addEventListener('click', function (event) {
    const editModal    = document.getElementById('editModal');
    const cancelModal  = document.getElementById('cancelModal');
    const successModal = document.getElementById('successModal');

    if (event.target === editModal)    closeEditModal();
    if (event.target === cancelModal)  closeCancelModal();
    if (event.target === successModal) closeSuccessModal();
});

// ── Close modals with Escape key ────────────────────────────
document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
        closeEditModal();
        closeSuccessModal();
        closeCancelModal();
    }
});

// ── Sidebar Toggle (shared) ─────────────────────────────────
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