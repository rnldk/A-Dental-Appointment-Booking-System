/* ══════════════════════════════
   APPROVE MODAL
══════════════════════════════ */
let approveUrl = null;

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.dentist-approve-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            approveUrl = btn.dataset.approveUrl;
            const modal = document.getElementById('approveModal');
            modal.style.display = 'flex';
        });
    });
});

function closeApproveModal() {
    document.getElementById('approveModal').style.display = 'none';
    approveUrl = null;
}

function confirmApprove() {
    if (approveUrl) window.location.href = approveUrl;
}

window.addEventListener('click', function (e) {
    const m = document.getElementById('approveModal');
    if (e.target === m) closeApproveModal();
});

/* ══════════════════════════════
   CALENDAR
══════════════════════════════ */
const scheduleMap = {};
scheduleData.forEach(appt => {
    if (!scheduleMap[appt.date]) scheduleMap[appt.date] = [];
    scheduleMap[appt.date].push(appt);
});
console.log('scheduleData:', scheduleData);
console.log('scheduleMap:', scheduleMap);

const monthNames = [
    'January','February','March','April','May','June',
    'July','August','September','October','November','December'
];
let currentYear  = new Date().getFullYear();
let currentMonth = new Date().getMonth();
let selectedDate = null;

function pad(n) { return String(n).padStart(2, '0'); }

function renderCalendar() {
    const label       = document.getElementById('calMonthLabel');
    const grid        = document.getElementById('calGrid');
    const today       = new Date();
    const todayStr    = `${today.getFullYear()}-${pad(today.getMonth()+1)}-${pad(today.getDate())}`;

    label.textContent = `${monthNames[currentMonth]} ${currentYear}`;
    grid.innerHTML    = '';

    const firstDay    = new Date(currentYear, currentMonth, 1).getDay();
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

    for (let i = 0; i < firstDay; i++) {
        grid.appendChild(document.createElement('div'));
    }

    for (let d = 1; d <= daysInMonth; d++) {
        const dateStr    = `${currentYear}-${pad(currentMonth+1)}-${pad(d)}`;
        const hasAppts   = !!scheduleMap[dateStr];
        const isToday    = dateStr === todayStr;
        const isSelected = dateStr === selectedDate;

        const cell = document.createElement('div');
        cell.style.cssText = `
            text-align:center; padding:6px 2px; border-radius:8px; cursor:pointer;
            font-size:13px; font-weight:${isToday ? '700' : '500'};
            position:relative; transition:background 0.15s, color 0.15s;
            background:${isSelected ? '#764ba2' : isToday ? '#f0ebfa' : 'transparent'};
            color:${isSelected ? 'white' : isToday ? '#764ba2' : '#2d1b4e'};
        `;
        cell.textContent = d;

        if (hasAppts) {
            const dot = document.createElement('div');
            dot.style.cssText = `width:5px;height:5px;border-radius:50%;margin:2px auto 0;
                background:${isSelected ? 'rgba(255,255,255,0.7)' : '#764ba2'};`;
            cell.appendChild(dot);
        }

        cell.addEventListener('mouseenter', function () {
            if (dateStr !== selectedDate) this.style.background = '#f0ebfa';
        });
        cell.addEventListener('mouseleave', function () {
            if (dateStr !== selectedDate) this.style.background = isToday ? '#f0ebfa' : 'transparent';
        });
        cell.addEventListener('click', function () {
            selectedDate = dateStr;
            renderCalendar();
            showDayPanel(dateStr, d);
        });

        grid.appendChild(cell);
    }
}

function showDayPanel(dateStr, day) {
    const panel = document.getElementById('calDayPanel');
    const title = document.getElementById('calDayTitle');
    const list  = document.getElementById('calDayList');
    const appts = scheduleMap[dateStr] || [];

    title.textContent = `${monthNames[currentMonth]} ${day}, ${currentYear}`;
    list.innerHTML    = '';

    if (appts.length === 0) {
        list.innerHTML = '<p style="color:#b0a0c8;font-size:13px;margin:0;">No approved appointments on this day.</p>';
    } else {
        appts.forEach(appt => {
            const row = document.createElement('div');
            row.style.cssText = 'display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid #f0ebfa;';
            row.innerHTML = `
                <div style="width:36px;height:36px;background:#f0ebfa;border-radius:8px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                    <svg width="16" height="16" fill="none" stroke="#764ba2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
                    </svg>
                </div>
                <div style="flex:1;">
                    <div style="font-size:13px;font-weight:600;color:#2d1b4e;">${appt.patient}</div>
                    <div style="font-size:12px;color:#8b7aaa;margin-top:2px;">⏰ ${appt.time}</div>
                </div>
            `;
            list.appendChild(row);
        });
        if (list.lastChild) list.lastChild.style.borderBottom = 'none';
    }

    panel.style.display = 'block';
}

function changeMonth(dir) {
    currentMonth += dir;
    if (currentMonth > 11) { currentMonth = 0; currentYear++; }
    if (currentMonth < 0)  { currentMonth = 11; currentYear--; }
    selectedDate = null;
    document.getElementById('calDayPanel').style.display = 'none';
    renderCalendar();
}

renderCalendar();

/* ══════════════════════════════
   SIDEBAR TOGGLE
══════════════════════════════ */
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