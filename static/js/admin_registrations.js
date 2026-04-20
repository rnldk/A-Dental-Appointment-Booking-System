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