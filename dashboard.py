"""
dashboard.py — User dashboard: profile info and booking history.
"""
import streamlit as st
from database import fetch_all, execute
from auth import get_current_user, logout_user
from ticket_pdf import generate_ticket_pdf


def render_dashboard():
    user = get_current_user()
    if not user:
        st.error("Please login to view your dashboard.")
        return

    # ── Header ─────────────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#8b5cf6,#10b981);
                    border-radius:16px;padding:2rem 2.5rem;margin-bottom:2rem">
            <h1 style="margin:0;color:#fff;font-size:2rem">👋 Hello, {user['name']}!</h1>
            <p style="margin:0.5rem 0 0 0;color:rgba(255,255,255,0.85);font-size:1rem">
                Welcome to your Youth Travels Dashboard
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Profile Info ───────────────────────────────────────────────────────────
    with st.expander("👤 My Profile", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Name:** {user['name']}")
            st.markdown(f"**Email:** {user['email']}")
            st.markdown(f"**Contact:** {user.get('contact') or '—'}")
        with c2:
            st.markdown(f"**Gender:** {user.get('gender') or '—'}")
            dob = user.get("dob")
            st.markdown(f"**Date of Birth:** {dob.strftime('%d %b %Y') if dob else '—'}")
            st.markdown(f"**Member Since:** {user['created_at'].strftime('%d %b %Y')}")

    # ── Booking History ────────────────────────────────────────────────────────
    st.markdown("### 🎟️ My Bookings")

    bookings = fetch_all(
        """
        SELECT bk.id, bk.from_stop, bk.to_stop, bk.travel_date,
               bk.seats, bk.booked_at,
               b.name  AS bus_name,
               b.company
        FROM   bookings bk
        JOIN   buses    b ON b.id = bk.bus_id
        WHERE  bk.user_id = %s
        ORDER  BY bk.booked_at DESC;
        """,
        (user["id"],),
    )

    if not bookings:
        st.info("You haven't booked any buses yet. Search for a route on the Home page!")
        if st.button("🔍 Search Buses", type="primary"):
            st.session_state["page"] = "home"
            st.rerun()
    else:
        # Summary stats
        s1, s2, s3 = st.columns(3)
        total_seats = sum(len(b["seats"]) for b in bookings)
        s1.metric("Total Trips", len(bookings))
        s2.metric("Total Seats Booked", total_seats)
        s3.metric("Latest Booking", bookings[0]["booked_at"].strftime("%d %b %Y"))

        st.markdown("---")

        for bk in bookings:
            with st.container():
                st.markdown(
                    f"""
                    <div style="background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.25);
                                border-radius:12px;padding:1.25rem 1.5rem;margin-bottom:1rem">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start">
                            <div>
                                <h4 style="margin:0;color:#a78bfa">{bk['bus_name']}</h4>
                                <p style="margin:4px 0 0;color:#9ca3af;font-size:0.85rem">{bk['company']}</p>
                            </div>
                            <span style="background:#10b981;color:#fff;padding:3px 12px;
                                         border-radius:20px;font-size:0.78rem;font-weight:600">
                                Confirmed
                            </span>
                        </div>
                        <hr style="border-color:rgba(255,255,255,0.08);margin:0.75rem 0">
                        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem">
                            <div>
                                <span style="color:#9ca3af;font-size:0.78rem">FROM</span>
                                <p style="margin:0;font-weight:600">{bk['from_stop']}</p>
                            </div>
                            <div>
                                <span style="color:#9ca3af;font-size:0.78rem">TO</span>
                                <p style="margin:0;font-weight:600">{bk['to_stop']}</p>
                            </div>
                            <div>
                                <span style="color:#9ca3af;font-size:0.78rem">DATE</span>
                                <p style="margin:0;font-weight:600">{bk['travel_date'].strftime('%d %b %Y')}</p>
                            </div>
                        </div>
                        <p style="margin:0.75rem 0 0;color:#d1d5db;font-size:0.88rem">
                            🪑 <strong>Seats:</strong> {', '.join(bk['seats'])} &nbsp;&nbsp;
                            📅 <strong>Booked on:</strong> {bk['booked_at'].strftime('%d %b %Y, %I:%M %p')}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Download ticket button for each booking
                user_obj = get_current_user()
                pdf_bytes = generate_ticket_pdf(
                    booking_id      = bk["id"],
                    passenger_name  = user_obj["name"] if user_obj else user["name"],
                    passenger_email = user_obj["email"] if user_obj else "",
                    bus_name        = bk["bus_name"],
                    bus_company     = bk["company"],
                    from_stop       = bk["from_stop"],
                    to_stop         = bk["to_stop"],
                    travel_date     = bk["travel_date"],
                    seats           = bk["seats"],
                    fare_per_seat   = 550,   # default display fare
                    booked_at       = bk["booked_at"],
                )
                ref = f"YT{bk['id']:06d}"
                st.download_button(
                    label           = f"⬇️ Download Ticket PDF ({ref})",
                    data            = pdf_bytes,
                    file_name       = f"YouthTravels_{ref}.pdf",
                    mime            = "application/pdf",
                    key             = f"dl_{bk['id']}",
                    use_container_width=True,
                )
                st.markdown("<br>", unsafe_allow_html=True)

    # ── Danger Zone ────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### ⚠️ Account Actions")
    col_a, col_b = st.columns([1, 4])
    with col_a:
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.session_state["page"] = "home"
            st.rerun()
    with col_b:
        with st.expander("🗑️ Delete Account (Permanent)"):
            st.warning("This will permanently delete your account and all bookings.")
            confirm_del = st.text_input(
                "Type your email to confirm deletion:", key="confirm_delete_email"
            )
            if st.button("Delete My Account", type="primary", key="delete_account_btn"):
                if confirm_del.strip().lower() == user["email"].lower():
                    execute("DELETE FROM users WHERE id = %s;", (user["id"],))
                    logout_user()
                    st.success("Account deleted. Redirecting…")
                    st.session_state["page"] = "home"
                    st.rerun()
                else:
                    st.error("Email does not match. Deletion cancelled.")
