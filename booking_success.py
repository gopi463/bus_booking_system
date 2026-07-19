"""
booking_success.py — Confirmation screen with PDF ticket download.
"""
import streamlit as st
from ticket_pdf import generate_ticket_pdf
from auth import get_current_user


def render_booking_success():
    """Show booking success screen with ticket download button."""
    confirmed = st.session_state.get("confirmed_booking")
    if not confirmed:
        st.session_state["page"] = "home"
        st.rerun()
        return

    user = get_current_user()
    bus  = confirmed["bus"]

    # ── Success banner ────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="text-align:center;padding:3rem 1rem 2rem">
            <div style="font-size:4rem">🎉</div>
            <h1 style="background:linear-gradient(135deg,#10b981,#8b5cf6);
                       -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                       font-size:2.2rem;margin:0.5rem 0">
                Booking Confirmed!
            </h1>
            <p style="color:#9ca3af;font-size:1rem">
                Your seats are reserved. Have a wonderful journey!
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    ref = f"YT{confirmed['booking_id']:06d}"

    # ── Ticket Preview Card ───────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="max-width:620px;margin:0 auto;
                    background:linear-gradient(135deg,rgba(139,92,246,0.12),rgba(16,185,129,0.08));
                    border:2px solid rgba(139,92,246,0.4);border-radius:20px;
                    padding:2rem;margin-bottom:2rem">

            <!-- Ref -->
            <div style="display:flex;justify-content:space-between;margin-bottom:1.5rem">
                <div>
                    <span style="color:#9ca3af;font-size:0.78rem;text-transform:uppercase">
                        Booking Reference
                    </span>
                    <div style="font-size:1.4rem;font-weight:700;color:#10b981;letter-spacing:2px">
                        {ref}
                    </div>
                </div>
                <div style="text-align:right">
                    <span style="background:#10b981;color:#fff;padding:4px 14px;
                                 border-radius:20px;font-size:0.82rem;font-weight:600">
                        ✅ CONFIRMED
                    </span>
                </div>
            </div>

            <!-- Route -->
            <div style="text-align:center;background:rgba(255,255,255,0.05);
                        border-radius:12px;padding:1rem;margin-bottom:1.2rem">
                <span style="font-size:1.5rem;font-weight:700;color:#f3f4f6">
                    {confirmed['from_stop']}
                </span>
                <span style="margin:0 1rem;font-size:1.5rem;color:#8b5cf6">→</span>
                <span style="font-size:1.5rem;font-weight:700;color:#f3f4f6">
                    {confirmed['to_stop']}
                </span>
            </div>

            <!-- Details grid -->
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem">
                <div>
                    <span style="color:#9ca3af;font-size:0.75rem">BUS</span>
                    <p style="margin:2px 0;font-weight:600;color:#f3f4f6">{bus['name']}</p>
                    <p style="margin:0;color:#9ca3af;font-size:0.8rem">{bus['company']}</p>
                </div>
                <div>
                    <span style="color:#9ca3af;font-size:0.75rem">DATE</span>
                    <p style="margin:2px 0;font-weight:600;color:#f3f4f6">
                        {confirmed['travel_date'].strftime('%d %B %Y') if hasattr(confirmed['travel_date'],'strftime') else confirmed['travel_date']}
                    </p>
                </div>
                <div>
                    <span style="color:#9ca3af;font-size:0.75rem">SEATS</span>
                    <p style="margin:2px 0;font-weight:600;color:#8b5cf6">
                        {', '.join(sorted(confirmed['seats']))}
                    </p>
                </div>
                <div>
                    <span style="color:#9ca3af;font-size:0.75rem">TOTAL PAID</span>
                    <p style="margin:2px 0;font-size:1.3rem;font-weight:700;color:#10b981">
                        ₹{confirmed['total_fare']:,}
                    </p>
                </div>
            </div>

            <hr style="border-color:rgba(255,255,255,0.1);margin:1.2rem 0">
            <p style="color:#9ca3af;font-size:0.82rem;margin:0;text-align:center">
                👤 Passenger: <strong style="color:#f3f4f6">{user['name'] if user else 'Passenger'}</strong>
                &nbsp;|&nbsp; 📧 {user['email'] if user else ''}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── PDF Download Button ───────────────────────────────────────────────────
    st.markdown(
        """
        <div style="text-align:center;margin-bottom:0.5rem">
            <p style="color:#9ca3af;font-size:0.9rem">
                📄 Download your ticket as a PDF to save offline or print it out.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        # Generate PDF bytes
        pdf_bytes = generate_ticket_pdf(
            booking_id     = confirmed["booking_id"],
            passenger_name = user["name"] if user else "Passenger",
            passenger_email= user["email"] if user else "",
            bus_name       = bus["name"],
            bus_company    = bus["company"],
            from_stop      = confirmed["from_stop"],
            to_stop        = confirmed["to_stop"],
            travel_date    = confirmed["travel_date"],
            seats          = confirmed["seats"],
            fare_per_seat  = confirmed["fare_each"],
            booked_at      = confirmed["booked_at"],
        )

        st.download_button(
            label      = "⬇️ Download Ticket PDF",
            data       = pdf_bytes,
            file_name  = f"YouthTravels_{ref}.pdf",
            mime       = "application/pdf",
            use_container_width=True,
            type       = "primary",
        )

    # ── Navigation buttons ────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    nc1, nc2, nc3 = st.columns(3)
    with nc1:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.pop("confirmed_booking", None)
            st.session_state["page"] = "home"
            st.rerun()
    with nc2:
        if st.button("📋 View My Bookings", use_container_width=True):
            st.session_state.pop("confirmed_booking", None)
            st.session_state["page"] = "dashboard"
            st.rerun()
    with nc3:
        if st.button("🚌 Book Another Bus", use_container_width=True):
            st.session_state.pop("confirmed_booking", None)
            st.session_state["search_results"] = None
            st.session_state["selected_bus"] = None
            st.session_state["page"] = "home"
            st.rerun()
