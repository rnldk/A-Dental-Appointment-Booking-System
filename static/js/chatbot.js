/* ============================================================
   UPPERHILL DENTAL CENTRE — Chatbot Widget
   File: static/js/chatbot.js
   ============================================================ */

(function () {
    'use strict';

    /* ── DOM refs ─────────────────────────────────────────── */
    const bubble    = document.getElementById('chatbot-bubble');
    const win       = document.getElementById('chatbot-window');
    const messages  = document.getElementById('chatbot-messages');
    const input     = document.getElementById('chatbot-input');
    const sendBtn   = document.getElementById('chatbot-send');
    const unreadDot = document.getElementById('chatbot-unread-dot');

    if (!bubble || !win) return;

    /* ── Intro tooltip on page load ───────────────────────────── */
    setTimeout(function () {
        var intro = document.createElement('div');
        intro.className = 'chatbot-intro-tip';
        intro.innerHTML =
            '<button class="chatbot-intro-close">✕</button>' +
            '<strong>Hey! I\'m Denta 🦷</strong>' +
            '<p>Your virtual assistant at Upper Hill Dental Centre. Ask me anything or take a tour!</p>';
        document.body.appendChild(intro);

        // Position above the bubble
        function positionIntro() {
            var rect = bubble.getBoundingClientRect();
            intro.style.bottom = (window.innerHeight - rect.top + 12) + 'px';
            intro.style.right  = (window.innerWidth - rect.right + 4) + 'px';
        }
        positionIntro();
        window.addEventListener('resize', positionIntro);

        // Close button
        intro.querySelector('.chatbot-intro-close').addEventListener('click', function () {
            intro.classList.add('hide');
            setTimeout(function () { intro.remove(); }, 250);
        });

        // Also dismiss when user opens the chat
        bubble.addEventListener('click', function () {
            if (intro.parentNode) {
                intro.classList.add('hide');
                setTimeout(function () { intro.remove(); }, 250);
            }
        });
    }, 1500);

    let isOpen = false;

    /* ── Toggle window ────────────────────────────────────── */
    bubble.addEventListener('click', function () {
        isOpen = !isOpen;
        win.classList.toggle('open', isOpen);
        bubble.classList.toggle('open', isOpen);
        unreadDot.style.display = 'none';
        if (isOpen) { input.focus(); scrollToBottom(); }
    });

    /* ── Helpers ──────────────────────────────────────────── */
    function getTime() {
        return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function scrollToBottom() {
        messages.scrollTop = messages.scrollHeight;
    }

    function appendMessage(text, role, quickReplies) {
        const wrap = document.createElement('div');
        wrap.className = 'chat-msg ' + role;

        const bub = document.createElement('div');
        bub.className = 'chat-bubble';
        bub.innerHTML = text;

        const time = document.createElement('div');
        time.className = 'chat-time';
        time.textContent = getTime();

        wrap.appendChild(bub);
        wrap.appendChild(time);

        if (quickReplies && quickReplies.length) {
            const chips = document.createElement('div');
            chips.className = 'quick-replies';
            quickReplies.forEach(function (label) {
                const chip = document.createElement('button');
                chip.className = 'quick-chip';
                chip.textContent = label;
                chip.addEventListener('click', function () {
                    // Only remove chips if it's not the tour button
                    if (label !== 'Take a Tour') {
                        chips.remove();
                    }
                    sendMessage(label);
                });
                chips.appendChild(chip);
            });
            wrap.appendChild(chips);
        }

        messages.appendChild(wrap);
        scrollToBottom();
        return wrap;
    }

    function showTyping() {
        const wrap = document.createElement('div');
        wrap.className = 'chat-msg bot typing-indicator';
        wrap.innerHTML = '<div class="chat-bubble"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span></div>';
        messages.appendChild(wrap);
        scrollToBottom();
        return wrap;
    }

/* ── Tour tooltip ─────────────────────────────────────────── */
var tourTooltip = null;

function removeTourTooltip() {
    if (tourTooltip) {
        tourTooltip.remove();
        tourTooltip = null;
    }
    document.querySelectorAll('.tour-highlight').forEach(function (el) {
        el.classList.remove('tour-highlight');
    });
}

function showTourTooltip(selector, message, step, total, quickReplies) {
    removeTourTooltip();

    var el = null;
    var selectors = selector.split(',').map(function(s) { return s.trim(); });
    for (var i = 0; i < selectors.length; i++) {
        el = document.querySelector(selectors[i]);
        if (el) break;
    }
    if (!el) return;

    el.classList.add('tour-highlight');
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });

    // Close the chat window so it doesn't block the view
    if (isOpen) {
        isOpen = false;
        win.classList.remove('open');
        bubble.classList.remove('open');
    }

    // Build tooltip
    var tip = document.createElement('div');
    tip.className = 'tour-tooltip';

    // Buttons row from quick replies
    var buttonsHtml = '';
    if (quickReplies && quickReplies.length) {
        buttonsHtml = '<div class="tour-tooltip-actions">';
        quickReplies.forEach(function (label) {
            var cls = label === 'Skip Tour'
                ? 'tour-tooltip-btn skip'
                : 'tour-tooltip-btn';
            buttonsHtml += '<button class="' + cls + '">' + label + '</button>';
        });
        buttonsHtml += '</div>';
    }

    tip.innerHTML =
        '<div class="tour-tooltip-step">' + step + ' / ' + total + '</div>' +
        '<div class="tour-tooltip-msg">' + message + '</div>' +
        buttonsHtml +
        '<button class="tour-tooltip-close" title="Close">✕</button>';

    document.body.appendChild(tip);
    tourTooltip = tip;

    // Wire up the action buttons to send as if the user typed them
    tip.querySelectorAll('.tour-tooltip-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var text = btn.textContent.trim();
            removeTourTooltip();
            sendTourMessage(text);
        });
    });

    // Close button
    tip.querySelector('.tour-tooltip-close').addEventListener('click', function () {
        removeTourTooltip();
        sendTourMessage('Skip Tour');
    });

    // Close button
    tip.querySelector('.tour-tooltip-close').addEventListener('click', function () {
        removeTourTooltip();
        // Send skip so the server resets tour state
        isOpen = true;
        win.classList.add('open');
        bubble.classList.add('open');
        sendMessage('Skip Tour');
    });

    setTimeout(function () {
        positionTooltip(tip, el);
    }, 420);
}

function positionTooltip(tip, el) {
    var rect = el.getBoundingClientRect();
    var tipH = tip.offsetHeight;
    var tipW = tip.offsetWidth;
    var margin = 14;
    var top, left;

    // Prefer above; fall back to below if not enough room
    if (rect.top - tipH - margin > 0) {
        top = rect.top + window.scrollY - tipH - margin;
    } else {
        top = rect.bottom + window.scrollY + margin;
    }

    // Centre horizontally over element, clamp to viewport
    left = rect.left + window.scrollX + rect.width / 2 - tipW / 2;
    left = Math.max(12, Math.min(left, window.innerWidth - tipW - 12));

    tip.style.top  = top  + 'px';
    tip.style.left = left + 'px';
    tip.style.opacity = '1';
    tip.style.transform = 'translateY(0)';
}

/* ── Tour step labels (shown in the tooltip, not the chat) ── */
var TOUR_LABELS = {
    '.topbar':             'Your welcome bar — shows your name and today\'s summary.',
    '.notif-btn':          'Notification bell — tap to see appointment updates.',
    '.clinic-hours-card':  'Clinic hours — check when we\'re open before booking.',
    '#upcoming-section':   'Upcoming appointments — your confirmed and approved visits are listed here.',
    '#awaiting-section':   'Awaiting approval — appointments you\'ve booked that are pending dentist confirmation.',
    '#book-appointment':   'Book here — pick a dentist, date & time, then hit Confirm Booking.'
};

/* ── Send logic ───────────────────────────────────────────── */
function sendMessage(text) {
    text = (text || input.value).trim();
    if (!text) return;

    // Intercept Tour chip before sending to server
    if (text === 'Take a Tour') {
        input.value = '';
        sendTourMessage('give me a tour');
        return;
    }

    var typing = showTyping();

    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
    })
    .then(function (res) { return res.json(); })
    .then(function (data) {
        typing.remove();

        // Only append to chat if there's something to say
        if (data.reply && data.reply.trim()) {
            appendMessage(data.reply, 'bot', data.quick_replies || []);
        }

        if (data.tour_step && data.tour_step.highlight) {
            var selector     = data.tour_step.highlight;
            var label        = TOUR_LABELS[selector] || '';
            var step         = data.tour_step.step;
            var total        = data.tour_step.total;
            var quickReplies = data.quick_replies || [];
            setTimeout(function () {
                showTourTooltip(selector, label, step, total, quickReplies);
            }, 500);
        }

        if (!isOpen) { unreadDot.style.display = 'block'; }
    })
    .catch(function () {
        typing.remove();
        appendMessage("Sorry, I'm having trouble connecting. Please try again.", 'bot');
    });
}

/* ── Silent send for tour navigation (no chat open/close) ── */
function sendTourMessage(text) {
    // Handle End Tour entirely on the client — no server call needed
    if (text === 'End Tour') {
        removeTourTooltip();
        isOpen = false;
        win.classList.remove('open');
        bubble.classList.remove('open');
        session['chatbot_tour_step'] = 0;
        // Reset server-side tour state
        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: 'Skip Tour' })
        });
        return;
    }

    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
    })
    .then(function (res) { return res.json(); })
    .then(function (data) {
        if (data.tour_step && data.tour_step.highlight) {
            var selector     = data.tour_step.highlight;
            var label        = TOUR_LABELS[selector] || '';
            var step         = data.tour_step.step;
            var total        = data.tour_step.total;
            var quickReplies = data.quick_replies || [];
            setTimeout(function () {
                showTourTooltip(selector, label, step, total, quickReplies);
            }, 300);
        } else {
            // Tour ended or skipped — open chat to show the final message
            isOpen = true;
            win.classList.add('open');
            bubble.classList.add('open');
            appendMessage(data.reply, 'bot', data.quick_replies || []);
        }
    })
    .catch(function () {
        appendMessage("Sorry, I'm having trouble connecting. Please try again.", 'bot');
    });
}

    /* ── Event listeners ──────────────────────────────────── */
    sendBtn.addEventListener('click', function () { sendMessage(); });

    input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            var text = input.value.trim();
            if (!text) return;
            input.value = '';
            appendMessage(text, 'user');

            var typing = showTyping();

            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                typing.remove();
                if (data.reply && data.reply.trim()) {
                    appendMessage(data.reply, 'bot', data.quick_replies || []);
                }
                if (data.tour_step && data.tour_step.highlight) {
                    var selector     = data.tour_step.highlight;
                    var label        = TOUR_LABELS[selector] || '';
                    var step         = data.tour_step.step;
                    var total        = data.tour_step.total;
                    var quickReplies = data.quick_replies || [];
                    setTimeout(function () {
                        showTourTooltip(selector, label, step, total, quickReplies);
                    }, 500);
                }
                if (!isOpen) { unreadDot.style.display = 'block'; }
            })
            .catch(function () {
                typing.remove();
                appendMessage("Sorry, I'm having trouble connecting. Please try again.", 'bot');
            });
        }
    });

    /* ── Welcome message on first open ───────────────────────── */
    let welcomed = false;
    // REPLACE with this:
    bubble.addEventListener('click', function () {
        if (!welcomed) {
            welcomed = true;
            setTimeout(function () {
                var chips = ['Book Appointment', 'Clinic Hours', 'Contact Us', 'Services'];
                if (window.location.pathname === '/patient') {
                    chips.push('Take a Tour');
                }
                appendMessage(
                    "👋 Hi there! I'm <strong>Denta</strong>, your virtual assistant at <strong>Upper Hill Dental Centre</strong>. How can I help you today?",
                    'bot',
                    chips
                );
            }, 400);
        }
    });

})();