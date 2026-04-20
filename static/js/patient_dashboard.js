/* ============================================================
   patient_dashboard.js
   Handles: sidebar toggle, notification modal, smooth book scroll
   ============================================================ */

// ── Sidebar Toggle ──────────────────────────────────────────
const STORAGE_KEY = 'uhdc_sidebar_collapsed';
const shell       = document.querySelector('.shell');
const sidebar     = document.getElementById('sidebar');
const menuToggle  = document.getElementById('menuToggle');
const overlay     = document.getElementById('sidebarOverlay');

// ── Desktop collapse toggle ──────────────────────────────────
function toggleSidebar() {
    const isCollapsed = sidebar.classList.toggle('collapsed');
    shell.classList.toggle('sidebar-collapsed', isCollapsed);
    localStorage.setItem(STORAGE_KEY, isCollapsed);
}

// Restore desktop state on load
if (localStorage.getItem(STORAGE_KEY) === 'true' && window.innerWidth > 640) {
    sidebar.classList.add('collapsed');
    shell.classList.add('sidebar-collapsed');
}

// ── Mobile drawer toggle ─────────────────────────────────────
function openMobileSidebar() {
    sidebar.classList.add('mobile-open');
    overlay.classList.add('is-active');
}

function closeMobileSidebar() {
    sidebar.classList.remove('mobile-open');
    overlay.classList.remove('is-active');
}

menuToggle.addEventListener('click', openMobileSidebar);
overlay.addEventListener('click', closeMobileSidebar);

// Close on resize back to desktop
window.addEventListener('resize', () => {
    if (window.innerWidth > 640) {
        closeMobileSidebar();
    }
});

function toggleSidebar() {
    const isCollapsed = sidebar.classList.toggle('collapsed');
    shell.classList.toggle('sidebar-collapsed', isCollapsed);
    localStorage.setItem(STORAGE_KEY, isCollapsed ? 'true' : 'false');
}

// Restore saved state on load — default is OPEN
(function () {
    if (localStorage.getItem(STORAGE_KEY) === 'true') {
        sidebar.classList.add('collapsed');
        shell.classList.add('sidebar-collapsed');
    }
})();

// ── Notification Modal ──────────────────────────────────────
function openNotificationModal() {
    document.getElementById('notificationModal').classList.add('active');
}

function closeNotificationModal() {
    document.getElementById('notificationModal').classList.remove('active');
}

// Close notification modal when clicking the backdrop
window.addEventListener('click', function (e) {
    const modal = document.getElementById('notificationModal');
    if (modal && e.target === modal) {
        closeNotificationModal();
    }
});

// ── Smooth scroll to book appointment section ───────────────
document.addEventListener('DOMContentLoaded', function () {
    const bookLink = document.querySelector('a[href="#book-appointment"]');
    if (bookLink) {
        bookLink.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.getElementById('book-appointment');
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    }
});