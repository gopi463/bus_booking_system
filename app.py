"""
app.py — Youth Travels Bus Booking System
Stack: Python · Streamlit · PostgreSQL
"""
import datetime
import streamlit as st

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="Youth Travels — Bus Booking",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Local imports ────────────────────────────────────────────────────────────
from database import init_db
from auth import is_logged_in, register_user, authenticate_user, logout_user
from bus_search import search_buses, POPULAR_CITIES, POPULAR_ROUTES
from booking import render_seat_selector
from dashboard import render_dashboard
from payment import render_payment_page
from booking_success import render_booking_success

# ── Initialise DB (once per process) ─────────────────────────────────────────
init_db()

# ── Session defaults ──────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state["page"] = "home"
if "search_results" not in st.session_state:
    st.session_state["search_results"] = None
if "selected_bus" not in st.session_state:
    st.session_state["selected_bus"] = None
if "search_from" not in st.session_state:
    st.session_state["search_from"] = ""
if "search_to" not in st.session_state:
    st.session_state["search_to"] = ""
if "search_date" not in st.session_state:
    st.session_state["search_date"] = datetime.date.today()

# ── Premium Global CSS ────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    :root {
        --primary: #8b5cf6;
        --primary-glow: rgba(139,92,246,0.35);
        --secondary: #10b981;
        --dark-bg: #0b071e;
        --card-bg: rgba(255,255,255,0.04);
        --card-border: rgba(255,255,255,0.09);
        --text-main: #f3f4f6;
        --text-muted: #9ca3af;
    }

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif !important;
    }

    /* Animated gradient background */
    .stApp {
        background: linear-gradient(-45deg, #1e1b4b, #2e1065, #0f172a, #064e3b, #701a75, #1e293b) !important;
        background-size: 400% 400% !important;
        animation: rainbowBG 25s ease infinite !important;
    }
    @keyframes rainbowBG {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Remove default top padding */
    .block-container { padding-top: 1rem !important; }

    /* Hide Streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }

    /* Navbar */
    .yt-navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.9rem 2.5rem;
        background: rgba(11,7,30,0.85);
        backdrop-filter: blur(18px);
        border-bottom: 1px solid var(--card-border);
        border-radius: 0 0 16px 16px;
        margin-bottom: 2rem;
        position: sticky;
        top: 0;
        z-index: 999;
    }
    .yt-brand {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #fff 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 0.5px;
    }
    .yt-nav-links { display: flex; gap: 1.5rem; align-items: center; }
    .yt-nav-links a {
        color: var(--text-muted);
        text-decoration: none;
        font-size: 0.9rem;
        font-weight: 500;
        transition: color 0.25s;
    }
    .yt-nav-links a:hover { color: var(--primary); }

    /* Hero section */
    .hero-section {
        text-align: center;
        padding: 4rem 1rem 3rem;
    }
    .hero-title {
        font-size: clamp(2.2rem, 5vw, 3.8rem);
        font-weight: 700;
        background: linear-gradient(135deg, #fff 0%, #a78bfa 60%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
        margin-bottom: 1rem;
    }
    .hero-sub {
        color: var(--text-muted);
        font-size: 1.1rem;
        max-width: 600px;
        margin: 0 auto 2.5rem;
        line-height: 1.7;
    }

    /* Search box */
    .search-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(139,92,246,0.3);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        max-width: 860px;
        margin: 0 auto 3rem;
        box-shadow: 0 0 40px rgba(139,92,246,0.12);
    }

    /* Bus result card */
    .bus-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        transition: border-color 0.3s, transform 0.25s, box-shadow 0.3s;
    }
    .bus-card:hover {
        border-color: rgba(139,92,246,0.5);
        transform: translateY(-3px);
        box-shadow: 0 8px 32px rgba(139,92,246,0.2);
    }

    /* Stats section */
    .stat-item {
        text-align: center;
        padding: 1.5rem;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        line-height: 1;
    }
    .stat-label { color: var(--text-muted); font-size: 0.9rem; margin-top: 6px; }

    /* Testimonial card */
    .test-card {
        background: linear-gradient(145deg,rgba(255,255,255,0.04) 0%,rgba(255,255,255,0.01) 100%);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 1.75rem;
        height: 100%;
    }

    /* Buttons override */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 500 !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 16px rgba(139,92,246,0.4) !important;
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stDateInput > div > div > input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 10px !important;
        color: var(--text-main) !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #070314; }
    ::-webkit-scrollbar-thumb { background: #272145; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--primary); }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─── Navbar ────────────────────────────────────────────────────────────────────
def render_navbar():
    logged = is_logged_in()
    name   = st.session_state.get("user_name", "")

    col_brand, col_spacer, col_links = st.columns([3, 5, 4])
    with col_brand:
        if st.button("🚌 Youth Travels", key="nav_brand",
                     help="Go to Home",
                     use_container_width=False):
            st.session_state["page"] = "home"
            st.rerun()

    with col_links:
        if logged:
            n1, n2, n3 = st.columns(3)
            with n1:
                if st.button("🏠 Home", key="nav_home", use_container_width=True):
                    st.session_state["page"] = "home"
                    st.rerun()
            with n2:
                if st.button("📋 Dashboard", key="nav_dash", use_container_width=True):
                    st.session_state["page"] = "dashboard"
                    st.rerun()
            with n3:
                if st.button(f"👤 {name[:10]}", key="nav_user", use_container_width=True):
                    st.session_state["page"] = "dashboard"
                    st.rerun()
        else:
            n1, n2 = st.columns(2)
            with n1:
                if st.button("🔑 Login", key="nav_login", use_container_width=True):
                    st.session_state["page"] = "login"
                    st.rerun()
            with n2:
                if st.button("📝 Register", key="nav_register", use_container_width=True):
                    st.session_state["page"] = "register"
                    st.rerun()

    st.markdown("<hr style='border-color:rgba(255,255,255,0.07);margin:-0.5rem 0 1.5rem'>",
                unsafe_allow_html=True)


# ─── Home / Search Page ────────────────────────────────────────────────────────
def render_home():
    # Hero
    st.markdown(
        """
        <div class="hero-section">
            <div class="hero-title">WELCOME TO YOUTH TRAVELS</div>
            <div class="hero-sub">
                Tomorrow's destination, arrive today.<br>
                Safe, premium, and reliable bus services across India.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Search Card ──────────────────────────────────────────────────────────
    st.markdown('<div class="search-card">', unsafe_allow_html=True)
    st.markdown("#### 🔍 Search Buses")

    sc1, sc2, sc3, sc4 = st.columns([2, 2, 2, 1])
    with sc1:
        from_city = st.selectbox(
            "📍 From City",
            options=[""] + POPULAR_CITIES,
            index=0,
            key="sb_from",
        )
    with sc2:
        to_city = st.selectbox(
            "🏁 To City",
            options=[""] + POPULAR_CITIES,
            index=0,
            key="sb_to",
        )
    with sc3:
        travel_date = st.date_input(
            "📅 Travel Date",
            value=datetime.date.today(),
            min_value=datetime.date.today(),
            key="sb_date",
        )
    with sc4:
        st.markdown("<div style='margin-top:1.85rem'>", unsafe_allow_html=True)
        search_clicked = st.button("🔍 Search", type="primary",
                                   use_container_width=True, key="search_btn")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if search_clicked:
        if not from_city or not to_city:
            st.warning("⚠️ Please select both a **From** and a **To** city.")
        elif from_city == to_city:
            st.warning("⚠️ Origin and destination cannot be the same city.")
        else:
            with st.spinner("🔎 Searching available buses…"):
                results = search_buses(from_city, to_city)
            st.session_state["search_results"] = results
            st.session_state["search_from"]    = from_city
            st.session_state["search_to"]      = to_city
            st.session_state["search_date"]    = travel_date
            st.session_state["selected_bus"]   = None

    # ── Search Results ────────────────────────────────────────────────────────
    if st.session_state["search_results"] is not None:
        results   = st.session_state["search_results"]
        from_city = st.session_state["search_from"]
        to_city   = st.session_state["search_to"]
        s_date    = st.session_state["search_date"]

        st.markdown("---")
        st.markdown(
            f"### 🚌 Buses from **{from_city}** → **{to_city}**  "
            f"<span style='color:#9ca3af;font-size:0.95rem;font-weight:400'>"
            f"on {s_date.strftime('%d %b %Y')}</span>",
            unsafe_allow_html=True,
        )

        if not results:
            st.markdown(
                """
                <div style="text-align:center;padding:3rem;background:rgba(255,255,255,0.03);
                            border-radius:16px;border:1px dashed rgba(255,255,255,0.1)">
                    <div style="font-size:3rem">🚌</div>
                    <h4 style="color:#ef4444;margin:1rem 0 0.5rem">No Buses Found</h4>
                    <p style="color:#9ca3af;font-size:0.9rem">
                        We couldn't find buses on this route. Try a different city pair.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.caption(f"Found **{len(results)} bus(es)** available on this route.")
            for bus in results:
                _render_bus_card(bus, from_city, to_city, s_date)

    # ── If a bus is selected → show seat selector ──────────────────────────
    if st.session_state["selected_bus"]:
        st.markdown("---")
        render_seat_selector(
            st.session_state["selected_bus"],
            st.session_state["search_date"],
            st.session_state["search_from"],
            st.session_state["search_to"],
        )

    # ── Popular Routes ────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🗺️ Popular Routes")
    pr_cols = st.columns(len(POPULAR_ROUTES))
    for col, route in zip(pr_cols, POPULAR_ROUTES):
        with col:
            card_clicked = st.button(
                f"🗺️ {route['from']} ➔ {route['to']}\n({route['desc']})",
                key=f"pop_route_{route['from']}_{route['to']}",
                use_container_width=True
            )
            if card_clicked:
                st.session_state["sb_from"] = route["from"]
                st.session_state["sb_to"] = route["to"]
                # Trigger search
                results = search_buses(route["from"], route["to"])
                st.session_state["search_results"] = results
                st.session_state["search_from"]    = route["from"]
                st.session_state["search_to"]      = route["to"]
                st.session_state["selected_bus"]   = None
                st.rerun()

    # ── Stats ─────────────────────────────────────────────────────────────────
    st.markdown("---")
    s1, s2, s3, s4 = st.columns(4)
    stats = [
        ("500+", "Active Bus Routes", "#8b5cf6"),
        ("50+",  "Major Indian Cities", "#10b981"),
        ("10K+", "Happy Travelers", "#ec4899"),
        ("4.8★", "Average Rating", "#f59e0b"),
    ]
    for col, (num, label, color) in zip([s1, s2, s3, s4], stats):
        with col:
            st.markdown(
                f"""
                <div class="stat-item">
                    <div class="stat-number" style="color:{color}">{num}</div>
                    <div class="stat-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── Testimonials ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 💬 What Our Passengers Say")

    testimonials = [
        {"name": "Rahul Sharma",  "role": "Software Engineer",
         "text": "Booking through Youth Travels is incredibly smooth. The UI is gorgeous and I got my ticket in under a minute!", "stars": 5},
        {"name": "Divya Teja",    "role": "Frequent Traveler",
         "text": "Love the route search! The interface is exceptionally polished and the results are always accurate.", "stars": 5},
        {"name": "Suresh Kumar",  "role": "Business Manager",
         "text": "Reliable search made booking my Ongole to Chennai trip extremely simple. Highly recommended!", "stars": 4},
    ]

    t1, t2, t3 = st.columns(3)
    for col, t in zip([t1, t2, t3], testimonials):
        with col:
            stars = "⭐" * t["stars"]
            st.markdown(
                f"""
                <div class="test-card">
                    <div style="margin-bottom:0.75rem">{stars}</div>
                    <p style="color:#d1d5db;font-style:italic;line-height:1.65;font-size:0.9rem">
                        "{t['text']}"
                    </p>
                    <div style="margin-top:1.25rem">
                        <strong style="color:#8b5cf6;display:block;font-size:0.92rem">{t['name']}</strong>
                        <span style="color:#6b7280;font-size:0.8rem">{t['role']}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_bus_card(bus: dict, from_city: str, to_city: str, travel_date):
    """Render a single bus result card with a 'Select Seats' button."""
    stops_str = " ➔ ".join(bus["stops"])
    stars_html = "⭐" * int(bus["rating"])
    is_selected = (
        st.session_state["selected_bus"] is not None
        and st.session_state["selected_bus"]["id"] == bus["id"]
    )

    with st.container():
        st.markdown(f'<div class="bus-card">', unsafe_allow_html=True)

        col_info, col_fare, col_btn = st.columns([4, 2, 2])

        with col_info:
            st.markdown(
                f"""
                <div>
                    <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
                        <h4 style="margin:0;color:#f3f4f6">{bus['company']}</h4>
                        <span style="background:rgba(245,158,11,0.15);color:#f59e0b;
                                     padding:2px 10px;border-radius:20px;font-size:0.78rem;font-weight:600">
                            {bus['rating']:.1f} ★
                        </span>
                        <span style="background:rgba(16,185,129,0.12);color:#10b981;
                                     padding:2px 10px;border-radius:20px;font-size:0.78rem">
                            ⏱ {bus['duration']}
                        </span>
                    </div>
                    <p style="margin:4px 0 0;color:#9ca3af;font-size:0.85rem">
                        {bus['name']}
                    </p>
                    <p style="margin:8px 0 0;color:#6b7280;font-size:0.8rem">
                        🛣️ {stops_str}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_fare:
            st.markdown(
                f"""
                <div style="text-align:center;padding-top:0.5rem">
                    <div style="font-size:1.8rem;font-weight:700;color:#10b981">
                        ₹{bus['fare']}
                    </div>
                    <div style="color:#9ca3af;font-size:0.78rem">per seat</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_btn:
            btn_label = "✅ Selected" if is_selected else "🪑 Select Seats"
            if st.button(btn_label, key=f"sel_bus_{bus['id']}",
                         type="primary" if not is_selected else "secondary",
                         use_container_width=True):
                if is_selected:
                    st.session_state["selected_bus"] = None
                else:
                    st.session_state["selected_bus"] = bus
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# ─── Login Page ────────────────────────────────────────────────────────────────
def render_login():
    st.markdown(
        """
        <div style="max-width:440px;margin:3rem auto 0">
            <h1 style="text-align:center;font-size:2rem;font-weight:700;
                       background:linear-gradient(135deg,#fff,#a78bfa);
                       -webkit-background-clip:text;-webkit-text-fill-color:transparent">
                Welcome Back 👋
            </h1>
            <p style="text-align:center;color:#9ca3af;margin-bottom:2rem">
                Sign in to your Youth Travels account
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        st.markdown(
            '<div style="max-width:440px;margin:0 auto;background:rgba(255,255,255,0.04);'
            'border:1px solid rgba(139,92,246,0.3);border-radius:18px;padding:2rem 2.5rem">',
            unsafe_allow_html=True,
        )
        email    = st.text_input("📧 Email Address", placeholder="you@example.com", key="login_email")
        password = st.text_input("🔒 Password",      placeholder="••••••••",        type="password", key="login_pw")

        submitted = st.form_submit_button("🔑 Sign In", type="primary", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Please fill in all fields.")
            else:
                success, msg = authenticate_user(email.strip(), password)
                if success:
                    st.success(msg)
                    st.session_state["page"] = "home"
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div style='text-align:center;margin-top:1.5rem;color:#9ca3af;font-size:0.88rem'>"
        "Don't have an account? </div>",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns([2, 2, 2])
    with c2:
        if st.button("📝 Register Here", use_container_width=True):
            st.session_state["page"] = "register"
            st.rerun()


# ─── Register Page ─────────────────────────────────────────────────────────────
def render_register():
    st.markdown(
        """
        <div style="max-width:500px;margin:3rem auto 0">
            <h1 style="text-align:center;font-size:2rem;font-weight:700;
                       background:linear-gradient(135deg,#fff,#a78bfa);
                       -webkit-background-clip:text;-webkit-text-fill-color:transparent">
                Join Youth Travels 🚌
            </h1>
            <p style="text-align:center;color:#9ca3af;margin-bottom:2rem">
                Create your account to start booking bus tickets instantly
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("register_form"):
        col1, col2 = st.columns(2)
        with col1:
            name    = st.text_input("👤 Full Name",       placeholder="John Doe")
            email   = st.text_input("📧 Email",            placeholder="john@example.com")
            contact = st.text_input("📞 Mobile Number",    placeholder="9876543210")
        with col2:
            dob     = st.date_input("🎂 Date of Birth",
                                    value=datetime.date(2000, 1, 1),
                                    min_value=datetime.date(1940, 1, 1),
                                    max_value=datetime.date.today())
            gender  = st.selectbox("⚧ Gender", ["", "Male", "Female", "Other"])
            password  = st.text_input("🔒 Password",         placeholder="Min 6 characters", type="password")
            password2 = st.text_input("🔒 Confirm Password", placeholder="Repeat password",   type="password")

        submitted = st.form_submit_button("📝 Create Account", type="primary", use_container_width=True)

        if submitted:
            errors = []
            if not name.strip():              errors.append("Full name is required.")
            if not email.strip():             errors.append("Email is required.")
            if not contact.strip():           errors.append("Mobile number is required.")
            if not gender:                    errors.append("Gender is required.")
            if len(password) < 6:             errors.append("Password must be at least 6 characters.")
            if password != password2:         errors.append("Passwords do not match.")

            if errors:
                for err in errors:
                    st.error(f"❌ {err}")
            else:
                success, msg = register_user(
                    name.strip(), email.strip(), password,
                    contact.strip(), dob, gender
                )
                if success:
                    st.success(f"🎉 {msg}")
                    st.session_state["page"] = "home"
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

    st.markdown(
        "<div style='text-align:center;margin-top:1.5rem;color:#9ca3af;font-size:0.88rem'>"
        "Already have an account? </div>",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns([2, 2, 2])
    with c2:
        if st.button("🔑 Login Here", use_container_width=True):
            st.session_state["page"] = "login"
            st.rerun()


# ─── Router ────────────────────────────────────────────────────────────────────
def main():
    render_navbar()

    page = st.session_state.get("page", "home")

    if page == "home":
        render_home()
    elif page == "login":
        render_login()
    elif page == "register":
        render_register()
    elif page == "dashboard":
        if is_logged_in():
            render_dashboard()
        else:
            st.warning("⚠️ Please login to view your dashboard.")
            st.session_state["page"] = "login"
            st.rerun()
    elif page == "payment":
        if is_logged_in():
            render_payment_page()
        else:
            st.warning("⚠️ Please login to complete your booking.")
            st.session_state["page"] = "login"
            st.rerun()
    elif page == "booking_success":
        render_booking_success()
    else:
        render_home()

    # ── Footer ─────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="text-align:center;padding:3rem 0 2rem;color:#374151;font-size:0.82rem;
                    border-top:1px solid rgba(255,255,255,0.05);margin-top:4rem">
            🚌 <strong style="color:#8b5cf6">Youth Travels</strong> &nbsp;•&nbsp;
            Built with Python · Streamlit · PostgreSQL &nbsp;•&nbsp;
            © 2024 All rights reserved
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
