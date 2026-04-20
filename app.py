from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import hashlib
from flask import session
from datetime import date, datetime, time, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify
import re

app = Flask(__name__)

CLINIC_HOURS = {
    "weekday": {
        "open": time(7, 30),
        "close": time(17, 30)
    },
    "saturday": {
        "open": time(7, 30),
        "close": time(14, 0)
    }
}

INTENTS = {
 
    'greeting': [
        r'\b(hi|hello|hey|howdy|good\s*(morning|afternoon|evening|day)|greetings|sup|what\'?s\s*up)\b',
        r'^(hi|hey|hello)$',
    ],
 
    'booking': [
        r'\b(book|booking|schedule|appointment|reserve|make\s+an?\s+appointment|set\s+up\s+an?\s+appointment)\b',
        r'\b(i\s*(want|need|would\s+like|\'d\s+like)\s+to\s+(see|visit|come\s+in|come\s+over|meet)\s+a?\s+dentist)\b',
        r'\b(can\s+i\s+(come\s+in|get\s+an?\s+appointment|see\s+a\s+dentist))\b',
        r'\b(available|availability|slot|slots|opening)\b',
        r'\b(today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|this\s+week|next\s+week|weekend)\b',
        r'\b(what\s+days?|which\s+days?|when\s+can\s+i)\b',
    ],
 
    'clinic_hours': [
        r'\b(hour|hours|open|opening|closing|close|time|times|schedule|when\s+are\s+you|when\s+do\s+you)\b',
        r'\b(are\s+you\s+open|is\s+the\s+clinic\s+open|do\s+you\s+open)\b',
        r'\b(open\s+(today|now|on\s+(sunday|saturday|weekend|weekday)))\b',
        r'\b(what\s+time\s+do\s+you|what\s+are\s+your\s+hours)\b',
    ],
 
    'services': [
        r'\b(service|services|treatment|treatments|procedure|procedures|offer|offering|provide|do\s+you\s+do|what\s+do\s+you)\b',
        r'\b(clean|cleaning|whitening|whiten|filling|fillings|extraction|implant|implants|braces|crown|crowns|root\s+canal|checkup|check.?up|x.?ray)\b',
        r'\b(dental\s+work|teeth|tooth|gum|gums|orthodont|pediatric|child|children|kids)\b',
        r'\b(what\s+can\s+you\s+(do|treat|help\s+with))\b',
    ],
 
    'contact': [
        r'\b(contact|phone|call|email|address|location|located|find\s+you|where\s+are\s+you|directions|get\s+to\s+you)\b',
        r'\b(reach\s+you|speak\s+to|talk\s+to|get\s+in\s+touch)\b',
        r'\b(nairobi|upper\s*hill|clinic)\b',
    ],
 
    'cancel_reschedule': [
        r'\b(cancel|cancellation|reschedule|rescheduling|change|modify|move|postpone|push\s+back)\b',
        r'\b(cancel\s+my|change\s+my|reschedule\s+my)\s+(appointment|booking)\b',
        r'\b(i\s+(want|need|would\s+like)\s+to\s+(cancel|reschedule|change|move)\s+my)\b',
        r'\b(appointment\s+management|manage\s+my\s+appointment)\b',
    ],
 
    'pricing': [
        r'\b(price|prices|pricing|cost|costs|fee|fees|charge|charges|how\s+much|payment|pay|afford|expensive|cheap|rates)\b',
        r'\b(do\s+you\s+(accept|take)\s+(insurance|nhif|cash))\b',
        r'\b(insurance|nhif|cover|covered)\b',
    ],
 
    'duration': [
        r'\b(how\s+long|duration|time\s+taken|how\s+many\s+(minutes|hours)|length\s+of|takes\s+how)\b',
        r'\b(quick|fast|long\s+does\s+it\s+take|how\s+long\s+(will|does|is))\b',
    ],
 
    'emergency': [
        r'\b(emergency|urgent|urgently|immediately|right\s+now|asap|as\s+soon\s+as\s+possible)\b',
        r'\b(pain|painful|toothache|ache|aching|bleeding|broken\s+tooth|chipped|swollen|swelling|abscess|infection)\b',
        r'\b(it\s+hurts|my\s+tooth\s+hurts|severe\s+pain|bad\s+pain|bad\s+tooth)\b',
    ],
 
    'thanks': [
        r'\b(thank|thanks|thank\s+you|thank\s+u|ty|cheers|appreciate|grateful|many\s+thanks)\b',
        r'\b(that\s+(helped|was\s+helpful)|great\s+help|very\s+helpful|super\s+helpful)\b',
    ],
 
    'goodbye': [
        r'\b(bye|goodbye|good\s*bye|see\s+you|later|take\s+care|have\s+a\s+(good|great|nice)|ciao|farewell)\b',
        r'\b(that\'?s\s+all|that\s+is\s+all|i\'?m\s+done|all\s+good\s+thanks)\b',
    ],
 
    'affirmation': [
        r'^(yes|yeah|yep|yup|sure|ok|okay|alright|absolutely|definitely|of\s+course|please|go\s+ahead)$',
        r'\b(yes\s+please|yes\s+i\s+(do|would|want)|that\'?s\s+right|correct|exactly)\b',
    ],
 
    'negation': [
        r'^(no|nope|nah|not\s+really|no\s+thanks|no\s+thank\s+you)$',
        r'\b(don\'?t\s+need|not\s+now|maybe\s+later|i\'?m\s+good|that\'?s\s+fine|i\'?m\s+fine)\b',
    ],

    'tour': [
        r'\b(tour|show\s+me\s+around|walk\s+me\s+through|guide\s+me|how\s+does\s+this\s+(page|work)|what\s+can\s+i\s+do\s+here|orientation)\b',
    ],
}

RESPONSES = {
 
    'greeting': [
        ("Hello! 😊 Welcome to <strong>Upper Hill Dental Centre</strong>. "
         "I'm Denta, your virtual assistant. How can I help you today?",
         ['Book Appointment', 'Clinic Hours', 'Services', 'Contact Us']),
 
        ("Hi there! 👋 Great to see you at <strong>Upper Hill Dental Centre</strong>. "
         "What can I help you with?",
         ['Book Appointment', 'Clinic Hours', 'Services', 'Contact Us']),
 
        ("Hey! I'm Denta 🦷, the virtual assistant for <strong>Upper Hill Dental Centre</strong>. "
         "What brings you here today?",
         ['Book Appointment', 'Clinic Hours', 'Services', 'Contact Us']),
    ],
 
    'booking': [
        ("📅 Sure! To book an appointment, scroll up and use the "
         "<strong>Book New Appointment</strong> form — pick your preferred dentist, date, and time, "
         "then hit <em>Confirm Booking</em>. It only takes a moment!",
         ['Clinic Hours', 'How long does it take?', 'Services']),
 
        ("Of course! 😊 Head to the <strong>Book New Appointment</strong> section at the top of this page. "
         "Choose your dentist, select a date and time, and you're all set.",
         ['Clinic Hours', 'Services', 'Contact Us']),
 
        ("Happy to help you book! 📋 Use the booking form on this page — "
         "select a dentist, choose your preferred date and time, then confirm. Simple as that!",
         ['Clinic Hours', 'How long does it take?', 'Services']),
    ],
 
    'booking_context_followup': [
        ("I can help with that! 📅 Use the <strong>Book New Appointment</strong> form at the top "
         "of this page to pick a date and time that works for you.",
         ['Clinic Hours', 'Services']),
    ],
 
    'clinic_hours': [
        ("🕐 Our clinic is open:<br>"
         "• <strong>Monday – Friday:</strong> 7:30 am – 5:30 pm<br>"
         "• <strong>Saturday:</strong> 7:30 am – 2:00 pm<br>"
         "• <strong>Sunday:</strong> Closed<br><br>"
         "Feel free to book an appointment at any of these times🤗",
         ['Book Appointment', 'Contact Us']),
 
        ("Here are our opening hours 📅<br>"
         "• <strong>Weekdays (Mon–Fri):</strong> 7:30 am – 5:30 pm<br>"
         "• <strong>Saturday:</strong> 7:30 am – 2:00 pm<br>"
         "• <strong>Sunday:</strong> We're closed on Sundays.<br><br>"
         "Feel free to book an appointment at any of these times🤗",
         ['Book Appointment', 'Contact Us']),
    ],
 
    'open_today': [
        # Dynamically built — see get_open_today_response()
    ],
 
    'services': [
        ("🦷 We offer a wide range of dental services including:<br>"
         "• General & Preventive Check-ups<br>"
         "• Teeth Cleaning & Whitening<br>"
         "• Fillings & Root Canal Treatment<br>"
         "• Dental Implants & Crowns<br>"
         "• Orthodontics (Braces)<br>"
         "• Paediatric Dentistry<br>"
         "• X-rays & Oral Health Consultations<br><br>"
         "You can book a consultation for any of these.",
         ['Book Appointment', 'Pricing', 'Clinic Hours']),
 
        ("Great question! Here's what we offer at UHDC 😊<br>"
         "• Routine check-ups & cleanings<br>"
         "• Whitening, fillings, and extractions<br>"
         "• Root canals, implants, and crowns<br>"
         "• Orthodontics and children's dentistry<br><br>"
         "Feel free to book a consultation and we'll recommend the best treatment for you.",
         ['Book Appointment', 'Pricing', 'Contact Us']),
    ],
 
    'contact': [
        ("📍 You can find us at:<br>"
         "<strong>Upper Hill Dental Centre</strong><br>"
         "Upper Hill, Nairobi, Kenya<br><br>"
         "📞 Give us a call during clinic hours and our reception team will be happy to assist!",
         ['Clinic Hours', 'Book Appointment']),
 
        ("We're located in <strong>Upper Hill, Nairobi</strong>. 🗺️<br><br>"
         "You can reach our reception team by phone during clinic hours. "
         "They'll be able to answer any specific questions.",
         ['Clinic Hours', 'Book Appointment']),
    ],
 
    'cancel_reschedule': [
        ("✏️ To manage an existing appointment, head to <strong>My Appointments</strong> "
         "in the sidebar. From there you can view, reschedule, or cancel any upcoming visit.",
         ['Book Appointment', 'Clinic Hours']),
 
        ("No problem! 👍 Go to the <strong>My Appointments</strong> page using the sidebar — "
         "you'll find all your appointments there and can make changes as needed.",
         ['Book Appointment', 'Clinic Hours']),
    ],
 
    'pricing': [
        ("💰 Our pricing varies by treatment. The best way to get an accurate quote is "
         "to book a consultation — our team will assess your needs and walk you through the costs.<br><br>"
         "We also accept <strong>NHIF</strong> and various insurance covers.",
         ['Book Appointment', 'Services', 'Contact Us']),
 
        ("Costs depend on the type of treatment needed. 😊 We'd recommend booking a "
         "consultation so our dentists can give you a personalised quote.<br><br>"
         "We accept <strong>NHIF</strong>, insurance, and cash payments.",
         ['Book Appointment', 'Services', 'Contact Us']),
    ],
 
    'duration': [
        ("⏱️ It depends on the treatment! A routine check-up is usually <strong>30–45 minutes</strong>. "
         "More involved procedures like root canals or extractions may take longer. "
         "Your dentist will give you a better estimate when you book.",
         ['Book Appointment', 'Services']),
 
        ("Most standard appointments take around <strong>30–60 minutes</strong>. ⏰ "
         "Complex treatments may require more time or multiple visits. "
         "We'll always let you know in advance!",
         ['Book Appointment', 'Services']),
    ],
 
    'emergency': [
        ("🚨 For dental emergencies, please <strong>call us immediately</strong> during clinic hours "
         "so we can prioritise your care. If it's outside our hours, "
         "please visit your nearest emergency medical facility.<br><br>"
         "Don't wait — dental pain can worsen quickly!",
         ['Clinic Hours', 'Contact Us']),
 
        ("Oh no! 😟 For urgent dental pain or emergencies, call the clinic straight away during opening hours "
         "and we'll fit you in as a priority. For after-hours emergencies, please head to the nearest hospital.",
         ['Clinic Hours', 'Contact Us']),
    ],
 
    'thanks': [
        ("You're very welcome! 😊 Don't hesitate to ask if you need anything else.",
         ['Book Appointment', 'Clinic Hours']),
 
        ("Happy to help! 🦷 Is there anything else I can assist you with?",
         ['Book Appointment', 'Services']),
 
        ("Glad I could help! Feel free to come back anytime. 😊",
         ['Book Appointment', 'Clinic Hours']),
    ],
 
    'goodbye': [
        ("Goodbye! 👋 Take care of that smile — we look forward to seeing you at "
         "<strong>Upper Hill Dental Centre</strong> soon!",
         []),
 
        ("See you soon! 😊 Don't forget to keep up with your regular check-ups. Take care! 🦷",
         []),
    ],
 
    'affirmation_booking': [
        ("Perfect! 😊 Go ahead and use the <strong>Book New Appointment</strong> form at the top of this page. "
         "Choose your dentist, pick a date and time, and confirm.",
         ['Clinic Hours', 'Services']),
    ],
 
    'negation_response': [
        ("No worries at all! 😊 Let me know whenever you need anything.",
         ['Book Appointment', 'Clinic Hours', 'Services']),
 
        ("That's perfectly fine! Feel free to ask if anything comes up. 👍",
         ['Book Appointment', 'Clinic Hours', 'Services']),
    ],
 
    'fallback': [
        ("Hmm, I'm not quite sure I understood that. 🤔 Here are a few things I can help you with:",
         ['Book Appointment', 'Clinic Hours', 'Services', 'Contact Us']),
 
        ("I didn't quite catch that — sorry! 😊 Try asking me about one of these:",
         ['Book Appointment', 'Clinic Hours', 'Services', 'Contact Us']),
 
        ("I'm still learning! 🦷 I'm best at helping with appointments, clinic hours, and our services. "
         "What would you like to know?",
         ['Book Appointment', 'Clinic Hours', 'Services', 'Contact Us']),
    ],

    'tour': [
        (
            "",
            ['Next →', 'Skip Tour'],
            {'highlight': '.topbar', 'step': 1, 'total': 6}
        ),
        (
            "🔔 This is your <strong>Notifications Bell</strong>. Click it to see when appointments are approved or cancelled by your dentist.",
            ['Next →', 'Skip Tour'],
            {'highlight': '.notif-btn', 'step': 2, 'total': 6}
        ),
        (
            "🕐 Here are the <strong>Clinic Hours</strong> — so you always know when we're open before you book.",
            ['Next →', 'Skip Tour'],
            {'highlight': '.clinic-hours-card', 'step': 3, 'total': 6}
        ),
        (
            "✅ This section shows your <strong>Upcoming Approved Appointments</strong>. Click the edit icon on any card to manage it.",
            ['Next →', 'Skip Tour'],
            {'highlight': '#upcoming-section', 'step': 4, 'total': 6}
        ),
        (
            "🕐 These are appointments <strong>Awaiting Approval</strong> — booked but not yet confirmed by your dentist.",
            ['Next →', 'Skip Tour'],
            {'highlight': '#awaiting-section', 'step': 5, 'total': 6}
        ),
        (
            "📅 Finally, this is the <strong>Book New Appointment</strong> form. Pick a dentist, date, and time — then hit <em>Confirm Booking</em>. That's the full tour! 🎉",
            ['End Tour'],
            {'highlight': '#book-appointment', 'step': 6, 'total': 6}
        ),
    ],
}

def normalise(text: str) -> str:
    """Lowercase, strip extra whitespace, remove punctuation noise."""
    text = text.lower().strip()
    # collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)
    # remove trailing punctuation that can confuse patterns
    text = re.sub(r'[?!.,;:]+$', '', text).strip()
    return text
 
 
def match_intent(text: str) -> str | None:
    """Return the first intent whose patterns match the normalised text."""
    for intent, patterns in INTENTS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return intent
    return None
 
 
def pick_response(key: str, session_counter: dict) -> tuple:
    """
    Rotate through response variants. Returns (reply_html, quick_replies, tour_step_or_None).
    """
    pool = RESPONSES.get(key)
    if not pool:
        pool = RESPONSES['fallback']
        key = 'fallback'

    idx = session_counter.get(key, 0) % len(pool)
    session_counter[key] = idx + 1

    entry = pool[idx]
    # Support both 2-tuple and 3-tuple entries
    if len(entry) == 3:
        return entry[0], entry[1], entry[2]
    return entry[0], entry[1], None
 
 
def get_open_today_response() -> tuple:
    """Dynamically check if the clinic is open today."""
    day = datetime.now().weekday()  # 0=Mon … 6=Sun
    hour = datetime.now().hour
 
    if day < 5:  # Monday–Friday
        if 7 <= hour < 17:
            reply = ("✅ Yes, we're open right now! Our weekday hours are "
                     "<strong>7:30 am – 5:30 pm</strong>. "
                     "You're welcome to come in or book an appointment.")
        elif hour < 7:
            reply = ("We're not open just yet today — we open at <strong>7:30 am</strong> on weekdays. "
                     "You can book an appointment in advance though!")
        else:
            reply = ("We've closed for today (weekdays close at <strong>5:30 pm</strong>). "
                     "We'll be back tomorrow morning at 7:30 am!")
    elif day == 5:  # Saturday
        if 7 <= hour < 14:
            reply = ("✅ Yes, we're open today (Saturday)! Hours are "
                     "<strong>7:30 am – 2:00 pm</strong>.")
        elif hour < 7:
            reply = ("It's Saturday — we open at <strong>7:30 am</strong> and close at 2:00 pm. "
                     "Come in a little later!")
        else:
            reply = ("We've closed for today — Saturdays we close at <strong>2:00 pm</strong>. "
                     "See you Monday morning at 7:30 am!")
    else:  # Sunday
        reply = ("We're closed on Sundays. 😊 We're back on <strong>Monday at 7:30 am</strong>. "
                 "You can still book an appointment online right now!")
 
    return reply, ['Book Appointment', 'Contact Us']
 
 
def is_asking_about_today(text: str) -> bool:
    return bool(re.search(r'\b(today|now|currently|right\s+now|at\s+the\s+moment|open\s+now)\b', text))
 
 
def is_time_reference(text: str) -> bool:
    """Detects if message is a bare time/day reference (context-dependent)."""
    return bool(re.search(
        r'\b(today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|'
        r'next\s+week|this\s+week|morning|afternoon|evening|weekend|[0-9]+\s*(am|pm))\b',
        text
    ))

app.secret_key = "school_project_secret"

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="ronniekn2",
        database="dental_booking"
    )

def get_ordinal_suffix(day):
    """Returns the ordinal suffix for a given day (st, nd, rd, th)"""
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return suffix

# Register the filter with Jinja
app.jinja_env.filters['ordinal'] = get_ordinal_suffix

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/users")
def users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, email, role FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("users.html", users=users)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["full_name"]
        email = request.form["email"]
        password = request.form["password"]
        role = "patient"


        # Hash password (simple & acceptable for school)
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()
            return render_template(
                "register.html",
                error="An account with this email already exists."
            )


        cursor.execute(
            "INSERT INTO users (full_name, email, password, role) VALUES (%s, %s, %s, %s)",
            (full_name, email, hashed_password, role)
        )

        conn.commit()
        # Log the user in immediately after registration
        session["user_id"] = cursor.lastrowid
        session["role"] = "patient"
        session["name"] = full_name

        return redirect(url_for("patient_dashboard"))

        cursor.close()
        conn.close()

        

    return render_template("register.html")

@app.route("/admin/register-dentist", methods=["GET", "POST"])
def register_dentist():
    if not login_required("admin"):
        return redirect(url_for("login"))

    if request.method == "POST":
        full_name = request.form["full_name"]
        email = request.form["email"]
        password = request.form["password"]
        role = "dentist"

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()
            session['register_error'] = "An account with this email already exists."
            return redirect(url_for("admin_dashboard"))
            
        cursor.execute(
            """
            INSERT INTO users (full_name, email, password, role)
            VALUES (%s, %s, %s, %s)
            """,
            (full_name, email, hashed_password, role)
        )

        conn.commit()
        cursor.close()
        conn.close()

        session['register_success'] = f"Dentist {full_name} registered successfully!"
        return redirect(url_for("admin_dashboard"))

    return redirect(url_for("admin_dashboard"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, hashed_password)
        )
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session["name"] = user["full_name"]

            # Redirect based on role
            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            elif user["role"] == "dentist":
                return redirect(url_for("dentist_dashboard"))
            else:
                return redirect(url_for("patient_dashboard"))
        else:
            return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")

def login_required(role=None):
    if "user_id" not in session:
        return False
    if role and session.get("role") != role:
        return False
    return True


@app.route("/admin")
def admin_dashboard():
    if not login_required("admin"):
        return redirect(url_for("login"))
 
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
 
    # Total appointments
    cursor.execute("SELECT COUNT(*) as total FROM appointments")
    total_appointments = cursor.fetchone()['total']
 
    # Total registered patients
    cursor.execute("SELECT COUNT(*) as total FROM users WHERE role='patient'")
    total_patients = cursor.fetchone()['total']
 
    # Today's appointments
    cursor.execute(
        """
        SELECT
            DATE_FORMAT(a.appointment_date, '%d/%m/%Y') AS appointment_date,
            TIME_FORMAT(a.appointment_time, '%H:%i') AS appointment_time,
            a.status,
            p.full_name AS patient_name,
            d.full_name AS dentist_name
        FROM appointments a
        JOIN users p ON a.patient_id = p.id
        JOIN users d ON a.dentist_id = d.id
        WHERE DATE(a.appointment_date) = CURDATE()
        ORDER BY a.appointment_time ASC
        """
    )
    today_appointments = cursor.fetchall()
 
    # ── Chart data 1: Status breakdown (all time) ──
    cursor.execute(
        """
        SELECT status, COUNT(*) as count
        FROM appointments
        GROUP BY status
        """
    )
    rows = cursor.fetchall()
    status_counts = {'approved': 0, 'booked': 0, 'cancelled': 0}
    for row in rows:
        if row['status'] in status_counts:
            status_counts[row['status']] = row['count']
 
    # ── Chart data 2: Appointments per month for current year ──
    current_year = datetime.now().year
    cursor.execute(
        """
        SELECT MONTH(appointment_date) as month, COUNT(*) as count
        FROM appointments
        WHERE YEAR(appointment_date) = %s
        GROUP BY MONTH(appointment_date)
        ORDER BY month ASC
        """,
        (current_year,)
    )
    monthly_rows = cursor.fetchall()
    # Build a full 12-month array (0 for months with no appointments)
    monthly_counts = [0] * 12
    for row in monthly_rows:
        monthly_counts[row['month'] - 1] = row['count']
 
    cursor.close()
    conn.close()
 
    return render_template(
        "admin.html",
        total_appointments=total_appointments,
        total_patients=total_patients,
        today_appointments=today_appointments,
        status_counts=status_counts,
        monthly_counts=monthly_counts,
        current_year=current_year
    )

@app.route("/dentist")
def dentist_dashboard():
    if not login_required("dentist"):
        return redirect(url_for("login"))
 
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    dentist_id = session["user_id"]
 
    # ── Stat 1: Total appointments ──
    cursor.execute(
        "SELECT COUNT(*) as total FROM appointments WHERE dentist_id = %s",
        (dentist_id,)
    )
    total_appointments = cursor.fetchone()['total']
 
    # ── Stat 2: Upcoming approved appointments (future) ──
    cursor.execute(
        """
        SELECT COUNT(*) as total FROM appointments
        WHERE dentist_id = %s
          AND status = 'approved'
          AND CONCAT(appointment_date, ' ', appointment_time) >= NOW()
        """,
        (dentist_id,)
    )
    upcoming_count = cursor.fetchone()['total']
 
    # ── Stat 3: Completed (past approved appointments) ──
    cursor.execute(
        """
        SELECT COUNT(*) as total FROM appointments
        WHERE dentist_id = %s
          AND status = 'approved'
          AND CONCAT(appointment_date, ' ', appointment_time) < NOW()
        """,
        (dentist_id,)
    )
    completed_count = cursor.fetchone()['total']
 
    # ── Today's appointments ──
    cursor.execute(
        """
        SELECT
            u.full_name AS patient_name,
            TIME_FORMAT(a.appointment_time, '%H:%i') AS appointment_time
        FROM appointments a
        JOIN users u ON a.patient_id = u.id
        WHERE a.dentist_id = %s
          AND a.status = 'approved'
          AND DATE(a.appointment_date) = CURDATE()
        ORDER BY a.appointment_time ASC
        """,
        (dentist_id,)
    )
    today_appointments = cursor.fetchall()
 
    # ── Pending appointments awaiting approval ──
    cursor.execute(
        """
        SELECT
            a.id AS appointment_id,
            u.full_name AS patient_name,
            DATE_FORMAT(a.appointment_date, '%d/%m/%y') AS appointment_date,
            TIME_FORMAT(a.appointment_time, '%H:%i') AS appointment_time
        FROM appointments a
        JOIN users u ON a.patient_id = u.id
        WHERE a.dentist_id = %s
          AND a.status = 'booked'
          AND CONCAT(a.appointment_date, ' ', a.appointment_time) >= NOW()
        ORDER BY a.appointment_date ASC, a.appointment_time ASC
        """,
        (dentist_id,)
    )
    pending_appointments = cursor.fetchall()
 
    # ── Calendar schedule: all future + this month's approved appointments ──
    cursor.execute(
        """
        SELECT
            DATE_FORMAT(a.appointment_date, %s) AS date,
            u.full_name AS patient,
            TIME_FORMAT(a.appointment_time, %s) AS time
        FROM appointments a
        JOIN users u ON a.patient_id = u.id
        WHERE a.dentist_id = %s
        AND a.status = 'approved'
        ORDER BY a.appointment_date ASC, a.appointment_time ASC
        """,
        ('%Y-%m-%d', '%H:%i', dentist_id)
    )
    schedule_rows = cursor.fetchall()
    # Convert to plain list of dicts for JSON serialisation
    schedule_json = [
        {'date': r['date'], 'patient': r['patient'], 'time': r['time']}
        for r in schedule_rows
    ]
 
    cursor.close()
    conn.close()
 
    return render_template(
        "dentist.html",
        total_appointments=total_appointments,
        upcoming_count=upcoming_count,
        completed_count=completed_count,
        today_appointments=today_appointments,
        pending_appointments=pending_appointments,
        schedule_json=schedule_json
    )

@app.route("/patient")
def patient_dashboard():
    if not login_required("patient"):
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get dentists list for the booking form
    cursor.execute("SELECT id, full_name FROM users WHERE role='dentist'")
    dentists = cursor.fetchall()
    
    # Get upcoming approved appointments
    cursor.execute(
        """
        SELECT 
            a.appointment_date,
            a.appointment_time,
            u.full_name AS dentist_name,
            DAY(a.appointment_date) AS day,
            DATE_FORMAT(a.appointment_date, '%b') AS month_short,
            DATE_FORMAT(a.appointment_time, '%H:%i') AS time_formatted
        FROM appointments a
        JOIN users u ON a.dentist_id = u.id
        WHERE a.patient_id = %s 
          AND a.status = 'approved'
          AND CONCAT(a.appointment_date, ' ', a.appointment_time) >= NOW()
        ORDER BY a.appointment_date ASC, a.appointment_time ASC
        LIMIT 5
        """,
        (session["user_id"],)
    )
    upcoming_appointments = cursor.fetchall()
    
    # Get appointments awaiting approval
    cursor.execute(
        """
        SELECT 
            a.appointment_date,
            a.appointment_time,
            u.full_name AS dentist_name,
            DAY(a.appointment_date) AS day,
            DATE_FORMAT(a.appointment_date, '%b') AS month_short,
            DATE_FORMAT(a.appointment_time, '%H:%i') AS time_formatted
        FROM appointments a
        JOIN users u ON a.dentist_id = u.id
        WHERE a.patient_id = %s 
          AND a.status = 'booked'
          AND CONCAT(a.appointment_date, ' ', a.appointment_time) >= NOW()
        ORDER BY a.appointment_date ASC, a.appointment_time ASC
        LIMIT 5
        """,
        (session["user_id"],)
    )
    awaiting_appointments = cursor.fetchall()
    
    # Get unread notifications (and delete old ones first)
    cursor.execute(
        "DELETE FROM notifications WHERE created_at < DATE_SUB(NOW(), INTERVAL 24 HOUR) AND is_read = TRUE"
    )
    conn.commit()
    
    cursor.execute(
    """
    SELECT 
        id,
        type,
        dentist_name,
        DATE_FORMAT(appointment_date, '%d/%m/%Y') AS formatted_date,
        DATE_FORMAT(appointment_time, '%H:%i') AS formatted_time,
        is_read,
        DATE_FORMAT(window_from, '%d/%m/%Y %H:%i') AS window_from,
        DATE_FORMAT(window_to,   '%d/%m/%Y %H:%i') AS window_to
    FROM notifications
    WHERE patient_id = %s
    ORDER BY created_at DESC
    """,
    (session["user_id"],)
    )
    notifications = cursor.fetchall()
    
    # Count unread notifications
    unread_count = sum(1 for n in notifications if not n['is_read'])
    
    # Check if there are new unread notifications
    has_new_notifications = unread_count > 0
    
    cursor.close()
    conn.close()
    
    return render_template(
        "patient.html", 
        dentists=dentists,
        upcoming_appointments=upcoming_appointments,
        awaiting_appointments=awaiting_appointments,
        notifications=notifications,
        unread_count=unread_count,
        has_new_notifications=has_new_notifications
    )

@app.route("/book", methods=["GET", "POST"])
def book_appointment():
    if not login_required("patient"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get all dentists
    cursor.execute("SELECT id, full_name FROM users WHERE role='dentist'")
    dentists = cursor.fetchall()

    if request.method == "POST":
        dentist_id = request.form["dentist_id"]
        appointment_date = request.form["appointment_date"]
        appointment_time = request.form["appointment_time"]

        appointment_datetime = datetime.strptime(
            f"{appointment_date} {appointment_time}",
            "%Y-%m-%d %H:%M"
        )

        now = datetime.now()

        # 1️⃣ Prevent past bookings
        if appointment_datetime < now:
            cursor.close()
            conn.close()
            session['booking_error'] = "You cannot book an appointment in the past."
            return redirect(url_for("patient_dashboard"))

        # Determine opening and closing times
        day_of_week = appointment_datetime.weekday()
        appointment_clock_time = appointment_datetime.time()

        # Sunday
        if day_of_week == 6:
            cursor.close()
            conn.close()
            session['booking_error'] = "The clinic is closed on Sundays."
            return redirect(url_for("patient_dashboard"))

        # Weekdays
        if day_of_week in range(0, 5):
            open_time = CLINIC_HOURS["weekday"]["open"]
            close_time = CLINIC_HOURS["weekday"]["close"]

        # Saturday
        elif day_of_week == 5:
            open_time = CLINIC_HOURS["saturday"]["open"]
            close_time = CLINIC_HOURS["saturday"]["close"]

        # Adjust booking window
        earliest_booking = (datetime.combine(date.today(), open_time) 
                            + timedelta(minutes=30)).time()

        latest_booking = (datetime.combine(date.today(), close_time) 
                        - timedelta(hours=1)).time()

        # Final validation
        if not (earliest_booking <= appointment_clock_time <= latest_booking):
            cursor.close()
            conn.close()
            session['booking_error'] = (
                f"Appointments can only be booked from "
                f"{earliest_booking.strftime('%H:%M')} "
                f"to "
                f"{latest_booking.strftime('%H:%M')}."
            )
            return redirect(url_for("patient_dashboard"))

        # 3️⃣ Check time range
        if not (open_time <= appointment_clock_time <= close_time):
            cursor.close()
            conn.close()
            session['booking_error'] = "Appointment time is outside clinic working hours."
            return redirect(url_for("patient_dashboard"))

        patient_id = session["user_id"]

        # Check for conflicting appointments within 15 minutes (900 seconds)
        cursor.execute(
            """
            SELECT id
            FROM appointments
            WHERE dentist_id = %s
            AND appointment_date = %s
            AND status != 'cancelled'
            AND ABS(
                TIME_TO_SEC(
                    TIMEDIFF(appointment_time, %s)
                )
            ) < 900
            """,
            (dentist_id, appointment_date, appointment_time)
        )

        conflict = cursor.fetchone()

        if conflict:
            cursor.close()
            conn.close()
            session['booking_error'] = "This dentist already has an appointment within 15 minutes of the selected time."
            return redirect(url_for("patient_dashboard"))

        cursor.execute(
            """
            INSERT INTO appointments (patient_id, dentist_id, appointment_date, appointment_time)
            VALUES (%s, %s, %s, %s)
            """,
            (patient_id, dentist_id, appointment_date, appointment_time)
        )
        conn.commit()

        cursor.close()
        conn.close()

        session['show_booking_success_modal'] = True  # Add this flag
        return redirect(url_for("patient_appointments"))

    cursor.close()
    conn.close()
    return render_template("book_appointment.html", dentists=dentists)

@app.route("/my-appointments")
def patient_appointments():
    if not login_required("patient"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT 
            a.id AS appointment_id,
            a.appointment_date AS raw_date,
            a.appointment_time AS raw_time,
            DATE_FORMAT(a.appointment_date, '%d/%m/%y') AS appointment_date,
            TIME_FORMAT(a.appointment_time, '%H:%i') AS appointment_time,
            a.status,
            u.full_name AS dentist_name,
            CONCAT(a.appointment_date, ' ', a.appointment_time) < NOW() AS is_past
        FROM appointments a
        JOIN users u ON a.dentist_id = u.id
        WHERE a.patient_id = %s
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """,
        (session["user_id"],)
    )

    appointments = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("patient_appointments.html", appointments=appointments)

@app.route("/admin/appointments")
def admin_appointments():
    if not login_required("admin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get filter parameters
    dentist_filter = request.args.get('dentist_filter', '')
    date_filter = request.args.get('date_filter', '')
    status_filter = request.args.get('status_filter', '')
    
    # Build query with filters
    query = """
        SELECT 
            a.id,
            DATE_FORMAT(a.appointment_date, '%d/%m/%y') AS appointment_date,
            TIME_FORMAT(a.appointment_time, '%H:%i') AS appointment_time,
            a.status,
            p.full_name AS patient_name,
            d.full_name AS dentist_name,
            CONCAT(a.appointment_date, ' ', a.appointment_time) < NOW() AS is_past
        FROM appointments a
        JOIN users p ON a.patient_id = p.id
        JOIN users d ON a.dentist_id = d.id
        WHERE 1=1
    """
    
    params = []
    
    if dentist_filter:
        query += " AND a.dentist_id = %s"
        params.append(dentist_filter)
    
    if date_filter:
        query += " AND a.appointment_date = %s"
        params.append(date_filter)
    
    if status_filter:
        query += " AND a.status = %s"
        params.append(status_filter)
    
    query += " ORDER BY a.appointment_date DESC, a.appointment_time DESC"
    
    cursor.execute(query, params)
    appointments = cursor.fetchall()
    
    # Get all dentists for filter dropdown
    cursor.execute("SELECT id, full_name FROM users WHERE role='dentist'")
    dentists = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin_appointments.html",
        appointments=appointments,
        dentists=dentists
    )


@app.route("/admin/approve-all", methods=["POST"])
def approve_all_appointments():
    if not login_required("admin"):
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get only future booked appointments to create notifications
    cursor.execute(
        """
        SELECT a.id, a.patient_id, a.appointment_date, a.appointment_time, u.full_name AS dentist_name
        FROM appointments a
        JOIN users u ON a.dentist_id = u.id
        WHERE a.status = 'booked'
        AND CONCAT(a.appointment_date, ' ', a.appointment_time) >= NOW()
        """
    )
    appointments = cursor.fetchall()
    
    # Approve only future booked appointments
    cursor.execute(
        """
        UPDATE appointments 
        SET status='approved' 
        WHERE status='booked'
        AND CONCAT(appointment_date, ' ', appointment_time) >= NOW()
        """
    )
    
    # Create notifications for all approved appointments
    for appt in appointments:
        cursor.execute(
            """
            INSERT INTO notifications (patient_id, appointment_id, type, dentist_name, appointment_date, appointment_time)
            VALUES (%s, %s, 'approved', %s, %s, %s)
            """,
            (appt['patient_id'], appt['id'], appt['dentist_name'], appt['appointment_date'], appt['appointment_time'])
        )
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for("admin_dashboard"))

@app.route("/approve/<int:appointment_id>")
def approve_appointment(appointment_id):
    if not login_required("admin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get appointment details before updating
    cursor.execute(
        """
        SELECT a.patient_id, a.appointment_date, a.appointment_time, u.full_name AS dentist_name
        FROM appointments a
        JOIN users u ON a.dentist_id = u.id
        WHERE a.id = %s
        """,
        (appointment_id,)
    )
    appointment = cursor.fetchone()

    # Update appointment status
    cursor.execute(
        "UPDATE appointments SET status='approved' WHERE id=%s",
        (appointment_id,)
    )

    # Create notification for patient
    if appointment:
        cursor.execute(
            """
            INSERT INTO notifications (patient_id, appointment_id, type, dentist_name, appointment_date, appointment_time)
            VALUES (%s, %s, 'approved', %s, %s, %s)
            """,
            (appointment['patient_id'], appointment_id, appointment['dentist_name'], 
             appointment['appointment_date'], appointment['appointment_time'])
        )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("admin_appointments"))

@app.route("/cancel/<int:appointment_id>")
def cancel_appointment(appointment_id):
    if not login_required("admin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get appointment details before updating
    cursor.execute(
        """
        SELECT a.patient_id, a.appointment_date, a.appointment_time, u.full_name AS dentist_name
        FROM appointments a
        JOIN users u ON a.dentist_id = u.id
        WHERE a.id = %s
        """,
        (appointment_id,)
    )
    appointment = cursor.fetchone()

    # Update appointment status
    cursor.execute(
        "UPDATE appointments SET status='cancelled' WHERE id=%s",
        (appointment_id,)
    )

    # Create notification for patient
    if appointment:
        cursor.execute(
            """
            INSERT INTO notifications (patient_id, appointment_id, type, dentist_name, appointment_date, appointment_time)
            VALUES (%s, %s, 'cancelled', %s, %s, %s)
            """,
            (appointment['patient_id'], appointment_id, appointment['dentist_name'], 
             appointment['appointment_date'], appointment['appointment_time'])
        )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("admin_appointments"))

@app.route("/admin/reschedule/<int:appointment_id>")
def admin_request_reschedule(appointment_id):
    if not login_required("admin"):
        return redirect(url_for("login"))

    window_from = request.args.get('window_from') or None
    window_to   = request.args.get('window_to')   or None

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT a.id, a.patient_id, a.appointment_date, a.appointment_time, u.full_name AS dentist_name
        FROM appointments a
        JOIN users u ON a.dentist_id = u.id
        WHERE a.id = %s AND a.status != 'cancelled'
        """,
        (appointment_id,)
    )
    appointment = cursor.fetchone()

    if appointment:
        cursor.execute(
            """
            UPDATE appointments SET status = 'booked' WHERE id = %s
            """,
            (appointment_id,)
        )

        cursor.execute(
            """
            INSERT INTO notifications
                (patient_id, appointment_id, type, dentist_name, appointment_date, appointment_time, window_from, window_to)
            VALUES (%s, %s, 'reschedule', %s, %s, %s, %s, %s)
            """,
            (
                appointment['patient_id'],
                appointment_id,
                appointment['dentist_name'],
                appointment['appointment_date'],
                appointment['appointment_time'],
                window_from,
                window_to
            )
        )
        conn.commit()

    cursor.close()
    conn.close()
    return redirect(url_for("admin_appointments"))

@app.route("/dentist/appointments")
def dentist_appointments():
    if not login_required("dentist"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get filter parameters
    date_filter   = request.args.get('date_filter', '')
    status_filter = request.args.get('status_filter', '')
    name_filter   = request.args.get('name_filter', '')

    query = """
        SELECT
            a.id AS appointment_id,
            DATE_FORMAT(a.appointment_date, '%d/%m/%y') AS appointment_date,
            TIME_FORMAT(a.appointment_time, '%H:%i') AS appointment_time,
            a.status,
            u.full_name AS patient_name,
            CONCAT(a.appointment_date, ' ', a.appointment_time) < NOW() AS is_past
        FROM appointments a
        JOIN users u ON a.patient_id = u.id
        WHERE a.dentist_id = %s
    """
    params = [session["user_id"]]

    if date_filter:
        query += " AND a.appointment_date = %s"
        params.append(date_filter)

    if status_filter:
        query += " AND a.status = %s"
        params.append(status_filter)

    if name_filter:
        query += " AND u.full_name LIKE %s"
        params.append(f"%{name_filter}%")

    query += " ORDER BY a.appointment_date DESC, a.appointment_time DESC"

    cursor.execute(query, params)
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        "dentist_appointments.html",
        appointments=appointments,
        date_filter=date_filter,
        status_filter=status_filter,
        name_filter=name_filter
    )

@app.route("/restore/<int:appointment_id>")
def restore_appointment(appointment_id):
    if not login_required("admin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE appointments SET status='approved' WHERE id=%s",
        (appointment_id,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("admin_appointments"))



@app.route("/patient/edit/<int:appointment_id>", methods=["GET", "POST"])
def edit_appointment(appointment_id):
    if not login_required("patient"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch appointment & ownership check
    cursor.execute(
        """
        SELECT * FROM appointments
        WHERE id = %s AND patient_id = %s AND status != 'cancelled'
        """,
        (appointment_id, session["user_id"])
    )

    appointment = cursor.fetchone()

    if not appointment:
        cursor.close()
        conn.close()
        return redirect(url_for("patient_appointments"))

    if request.method == "POST":
        appointment_date = request.form["appointment_date"]
        appointment_time = request.form["appointment_time"]

        # 🔁 VALIDATION (reuse your rules)
        appointment_datetime = datetime.strptime(
            f"{appointment_date} {appointment_time}",
            "%Y-%m-%d %H:%M"
        )

        now = datetime.now()
        if appointment_datetime < now:
            cursor.close()
            conn.close()
            # Store error AND appointment ID in session
            session['edit_error'] = "You cannot book an appointment in the past."
            session['edit_appointment_id'] = appointment_id
            return redirect(url_for("patient_appointments"))

        day_of_week = appointment_datetime.weekday()
        appointment_clock_time = appointment_datetime.time()

        if day_of_week == 6:
            cursor.close()
            conn.close()
            session['edit_error'] = "The clinic is closed on Sundays."
            session['edit_appointment_id'] = appointment_id
            return redirect(url_for("patient_appointments"))

        if day_of_week in range(0, 5):
            open_time = CLINIC_HOURS["weekday"]["open"]
            close_time = CLINIC_HOURS["weekday"]["close"]
        else:
            open_time = CLINIC_HOURS["saturday"]["open"]
            close_time = CLINIC_HOURS["saturday"]["close"]

        earliest_booking = (
            datetime.combine(date.today(), open_time)
            + timedelta(minutes=30)
        ).time()

        latest_booking = (
            datetime.combine(date.today(), close_time)
            - timedelta(hours=1)
        ).time()

        if not (earliest_booking <= appointment_clock_time <= latest_booking):
            cursor.close()
            conn.close()
            session['edit_error'] = "Selected time is outside clinic booking hours."
            session['edit_appointment_id'] = appointment_id
            return redirect(url_for("patient_appointments"))

        # 15-minute gap check (exclude this appointment itself)
        cursor.execute(
            """
            SELECT id FROM appointments
            WHERE dentist_id = %s
              AND appointment_date = %s
              AND status != 'cancelled'
              AND id != %s
              AND ABS(
                  TIME_TO_SEC(
                      TIMEDIFF(appointment_time, %s)
                  )
              ) < 900
            """,
            (
                appointment["dentist_id"],
                appointment_date,
                appointment_id,
                appointment_time
            )
        )

        if cursor.fetchone():
            cursor.close()
            conn.close()
            session['edit_error'] = "This dentist already has an appointment within 15 minutes of the selected time."
            session['edit_appointment_id'] = appointment_id
            return redirect(url_for("patient_appointments"))

        # ✅ UPDATE (not insert)
        cursor.execute(
            """
            UPDATE appointments
            SET appointment_date = %s,
                appointment_time = %s,
                status = 'booked'
            WHERE id = %s
            """,
            (appointment_date, appointment_time, appointment_id)
        )

        conn.commit()
        cursor.close()
        conn.close()

        session['edit_success'] = "Appointment updated successfully!"
        return redirect(url_for("patient_appointments"))

    cursor.close()
    conn.close()
    return redirect(url_for("patient_appointments"))


@app.route("/patient/cancel/<int:appointment_id>")
def patient_cancel_appointment(appointment_id):
    if not login_required("patient"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Ensure appointment belongs to logged-in patient
    cursor.execute(
        """
        UPDATE appointments
        SET status = 'cancelled'
        WHERE id = %s AND patient_id = %s
        """,
        (appointment_id, session["user_id"])
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("patient_appointments"))

@app.route("/notifications/mark-read", methods=["POST"])
def mark_notifications_read():
    if not login_required("patient"):
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE notifications SET is_read = TRUE WHERE patient_id = %s AND is_read = FALSE",
        (session["user_id"],)
    )
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for("patient_dashboard"))

@app.route("/admin/registrations")
def admin_registrations():
    if not login_required("admin"):
        return redirect(url_for("login"))
    return render_template("admin_registrations.html")

@app.route("/admin/reports")
def admin_reports():
    if not login_required("admin"):
        return redirect(url_for("login"))
 
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
 
    cursor.execute(
        """
        SELECT
            id,
            patient_name,
            dentist_name,
            service,
            appointment_status,
            appointment_info,
            details,
            DATE_FORMAT(created_at, '%d/%m/%Y %H:%i') AS created_date
        FROM reports
        ORDER BY created_at DESC
        """
    )
    reports = cursor.fetchall()
 
    cursor.close()
    conn.close()
 
    return render_template("admin_reports.html", reports=reports)

@app.route("/dentist/reports")
def dentist_reports():
    if not login_required("dentist"):
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all reports created by this dentist
    cursor.execute(
        """
        SELECT 
            id,
            patient_name,
            appointment_info,
            service,
            appointment_status,
            details,
            DATE_FORMAT(created_at, '%d/%m/%Y %H:%i') AS created_date
        FROM reports
        WHERE dentist_name = %s
        ORDER BY created_at DESC
        """,
        (session["name"],)
    )
    
    reports = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("dentist_reports.html", reports=reports)

@app.route("/dentist/create-report", methods=["GET", "POST"])
def create_report():
    if not login_required("dentist"):
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all patients for the dropdown
    cursor.execute("SELECT full_name FROM users WHERE role='patient' ORDER BY full_name")
    patients = cursor.fetchall()
    
    if request.method == "POST":
        patient_name = request.form["patient_name"]
        appointment_info = request.form.get("appointment_info", "")
        service = request.form["service"]
        appointment_status = request.form["appointment_status"]
        details = request.form["details"]
        dentist_name = session["name"]
        
        # Insert report into database
        cursor.execute(
            """
            INSERT INTO reports (dentist_name, patient_name, appointment_info, service, appointment_status, details)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (dentist_name, patient_name, appointment_info, service, appointment_status, details)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        session['report_success'] = "Report created successfully!"
        return redirect(url_for("dentist_reports"))
    
    cursor.close()
    conn.close()
    
    return render_template("create_report.html", patients=patients)

@app.route("/dentist/get-appointments/<patient_name>")
def get_patient_appointments(patient_name):
    if not login_required("dentist"):
        return jsonify([])
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get today's approved appointments for the selected patient (ignoring time)
    cursor.execute(
        """
        SELECT 
            a.id,
            p.full_name AS patient_name,
            d.full_name AS dentist_name,
            DATE_FORMAT(a.appointment_date, '%d/%m/%Y') AS formatted_date,
            TIME_FORMAT(a.appointment_time, '%H:%i') AS appointment_time
        FROM appointments a
        JOIN users p ON a.patient_id = p.id
        JOIN users d ON a.dentist_id = d.id
        WHERE p.full_name = %s 
          AND a.status = 'approved'
          AND DATE(a.appointment_date) = CURDATE()
        ORDER BY a.appointment_time
        """,
        (patient_name,)
    )
    
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(appointments)


# ── Add these two routes to app.py ──────────────────────────────────────────

@app.route("/dentist/edit-report/<int:report_id>", methods=["POST"])
def edit_report(report_id):
    if not login_required("dentist"):
        return redirect(url_for("login"))

    service            = request.form["service"]
    appointment_status = request.form["appointment_status"]
    details            = request.form["details"]

    conn   = get_db_connection()
    cursor = conn.cursor()

    # Only allow the dentist who created the report to edit it
    cursor.execute(
        """
        UPDATE reports
        SET service = %s,
            appointment_status = %s,
            details = %s
        WHERE id = %s AND dentist_name = %s
        """,
        (service, appointment_status, details, report_id, session["name"])
    )

    conn.commit()
    cursor.close()
    conn.close()

    session["report_success"] = "Report updated successfully!"
    return redirect(url_for("dentist_reports"))


@app.route("/dentist/delete-report/<int:report_id>")
def delete_report(report_id):
    if not login_required("dentist"):
        return redirect(url_for("login"))

    conn   = get_db_connection()
    cursor = conn.cursor()

    # Only allow the dentist who created the report to delete it
    cursor.execute(
        "DELETE FROM reports WHERE id = %s AND dentist_name = %s",
        (report_id, session["name"])
    )

    conn.commit()
    cursor.close()
    conn.close()

    session["report_success"] = "Report deleted successfully!"
    return redirect(url_for("dentist_reports"))

# 2. Dentist approve appointment
@app.route("/dentist/approve/<int:appointment_id>")
def dentist_approve_appointment(appointment_id):
    if not login_required("dentist"):
        return redirect(url_for("login"))
 
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
 
    # Verify the appointment belongs to this dentist before approving
    cursor.execute(
        "SELECT id, patient_id, appointment_date, appointment_time FROM appointments WHERE id = %s AND dentist_id = %s",
        (appointment_id, session["user_id"])
    )
    appointment = cursor.fetchone()
 
    if appointment:
        cursor.execute(
            "UPDATE appointments SET status = 'approved' WHERE id = %s",
            (appointment_id,)
        )
 
        # Notify the patient
        cursor.execute(
            """
            INSERT INTO notifications (patient_id, appointment_id, type, dentist_name, appointment_date, appointment_time)
            VALUES (%s, %s, 'approved', %s, %s, %s)
            """,
            (
                appointment['patient_id'],
                appointment_id,
                session["name"],
                appointment['appointment_date'],
                appointment['appointment_time']
            )
        )
 
        conn.commit()
 
    cursor.close()
    conn.close()
 
    return redirect(url_for("dentist_appointments"))
 
 
# 3. Dentist request reschedule — sends notification without changing appointment status
@app.route("/dentist/reschedule/<int:appointment_id>")
def dentist_request_reschedule(appointment_id):
    if not login_required("dentist"):
        return redirect(url_for("login"))
 
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
 
    cursor.execute(
        """
        SELECT id, patient_id, appointment_date, appointment_time
        FROM appointments
        WHERE id = %s AND dentist_id = %s AND status != 'cancelled'
        """,
        (appointment_id, session["user_id"])
    )
    appointment = cursor.fetchone()
 
    if appointment:
        # Only inserts a notification — appointment status is intentionally unchanged
        # The patient sees the message and books a new time themselves
        cursor.execute(
            """
            INSERT INTO notifications
                (patient_id, appointment_id, type, dentist_name, appointment_date, appointment_time)
            VALUES (%s, %s, 'reschedule', %s, %s, %s)
            """,
            (
                appointment['patient_id'],
                appointment_id,
                session["name"],
                appointment['appointment_date'],
                appointment['appointment_time']
            )
        )
        conn.commit()
 
    cursor.close()
    conn.close()
    return redirect(url_for("dentist_appointments"))
 
 
# 4. Dentist restore (undo) a cancelled appointment → sets back to 'booked'
@app.route("/dentist/restore/<int:appointment_id>")
def dentist_restore_appointment(appointment_id):
    if not login_required("dentist"):
        return redirect(url_for("login"))
 
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
 
    # Verify the appointment belongs to this dentist and is currently cancelled
    cursor.execute(
        """
        SELECT id FROM appointments
        WHERE id = %s AND dentist_id = %s AND status = 'cancelled'
        """,
        (appointment_id, session["user_id"])
    )
    appointment = cursor.fetchone()
 
    if appointment:
        # Restore to 'booked' so it awaits approval again
        cursor.execute(
            "UPDATE appointments SET status = 'booked' WHERE id = %s",
            (appointment_id,)
        )
        conn.commit()
 
    cursor.close()
    conn.close()
 
    return redirect(url_for("dentist_appointments"))

@app.route('/chat', methods=['POST'])
def chat():
    data    = request.get_json(silent=True) or {}
    raw_msg = data.get('message', '').strip()
    if not raw_msg:
        return jsonify({'reply': "I didn't catch that — could you try again? 😊", 'quick_replies': []})

    msg = normalise(raw_msg)

    if 'chatbot_counters' not in session:
        session['chatbot_counters'] = {}
    counters = session['chatbot_counters']

    last_intent = session.get('chatbot_last_intent')

    # ── Tour navigation ──────────────────────────────────────
    # "Next →" during a tour advances to the next step
    tour_step = session.get('chatbot_tour_step', 0)

    if raw_msg == 'Next →' and last_intent == 'tour' and tour_step > 0:
        pool = RESPONSES['tour']
        # tour_step is 1-indexed; advance to next (0-indexed in pool)
        next_idx = tour_step  # current step was tour_step, so next is tour_step (0-indexed)
        if next_idx < len(pool):
            entry = pool[next_idx]
            reply, quick_replies, tour_data = entry[0], entry[1], entry[2]
            session['chatbot_tour_step'] = tour_data['step']
            session['chatbot_last_intent'] = 'tour'
            session.modified = True
            return jsonify({'reply': reply, 'quick_replies': quick_replies, 'tour_step': tour_data})
        else:
            # Tour finished
            session['chatbot_tour_step'] = 0
            session['chatbot_last_intent'] = None
            session.modified = True
            return jsonify({'reply': "That's the end of the tour! 🎉 Let me know if you have any questions.", 'quick_replies': ['Book Appointment', 'Clinic Hours', 'Services']})

    if raw_msg == 'Skip Tour':
        session['chatbot_tour_step'] = 0
        session['chatbot_last_intent'] = None
        session.modified = True
        return jsonify({'reply': "No problem! Feel free to explore on your own. 😊 I'm here if you need anything.", 'quick_replies': ['Book Appointment', 'Clinic Hours', 'Services']})

    # ── Intent detection ─────────────────────────────────────
    intent = match_intent(msg)

    if intent is None and last_intent == 'booking' and is_time_reference(msg):
        intent = 'booking_context_followup'

    if intent == 'affirmation' and last_intent == 'booking':
        intent = 'affirmation_booking'

    if intent == 'negation':
        intent = 'negation_response'

    if intent == 'clinic_hours' and is_asking_about_today(msg):
        reply, quick_replies = get_open_today_response()
        session['chatbot_last_intent'] = 'clinic_hours'
        session.modified = True
        return jsonify({'reply': reply, 'quick_replies': quick_replies})

    # ── Tour start ───────────────────────────────────────────
    if intent == 'tour':
        pool = RESPONSES['tour']
        entry = pool[0]
        reply, quick_replies, tour_data = entry[0], entry[1], entry[2]
        session['chatbot_tour_step'] = tour_data['step']
        session['chatbot_last_intent'] = 'tour'
        session.modified = True
        return jsonify({'reply': reply, 'quick_replies': quick_replies, 'tour_step': tour_data})

    # ── Build response ───────────────────────────────────────
    if intent and intent in RESPONSES:
        result = pick_response(intent, counters)
    else:
        result = pick_response('fallback', counters)
        intent = 'fallback'

    reply, quick_replies, tour_data = result

    session['chatbot_last_intent'] = intent
    session['chatbot_counters'] = counters
    session.modified = True

    response = {'reply': reply, 'quick_replies': quick_replies}
    if tour_data:
        response['tour_step'] = tour_data
    return jsonify(response)
 
     

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
