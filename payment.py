"""
payment.py — Card payment form UI (mock/demo payment processing).
"""
import re
import streamlit as st
from database import execute_returning, fetch_one
from ticket_pdf import generate_ticket_pdf


# ─── Helpers ──────────────────────────────────────────────────────────────────
def _luhn_check(card_number: str) -> bool:
    """Basic Luhn algorithm to validate card number format."""
    digits = [int(d) for d in card_number if d.isdigit()]
    if len(digits) < 13:
        return False
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def _card_type(number: str) -> str:
    n = number.replace(" ", "")
    if n.startswith("4"):
        return "💳 Visa"
    elif n[:2] in ("51","52","53","54","55") or (2221 <= int(n[:4] or "0") <= 2720):
        return "💳 Mastercard"
    elif n[:2] in ("34","37"):
        return "💳 American Express"
    elif n.startswith("6"):
        return "💳 RuPay"
    return "💳 Card"


def _format_card(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)[:16]
    return " ".join(digits[i:i+4] for i in range(0, len(digits), 4))


# ─── Payment Form ─────────────────────────────────────────────────────────────
def render_payment_page():
    """
    Full payment page: shows order summary + card form.
    Reads pending booking from st.session_state["pending_booking"].
    """
    pending = st.session_state.get("pending_booking")
    if not pending:
        st.warning("No booking in progress. Please search for a bus first.")
        if st.button("← Back to Home"):
            st.session_state["page"] = "home"
            st.rerun()
        return

    bus       = pending["bus"]
    seats     = pending["seats"]
    from_stop = pending["from_stop"]
    to_stop   = pending["to_stop"]
    travel_date = pending["travel_date"]
    fare_each = bus["fare"]
    total_fare = fare_each * len(seats)

    # ── Order Summary Card ────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,rgba(139,92,246,0.15),rgba(16,185,129,0.08));
                    border:1px solid rgba(139,92,246,0.35);border-radius:16px;
                    padding:1.5rem 2rem;margin-bottom:2rem">
            <h3 style="margin:0 0 1rem;color:#a78bfa">🎟️ Order Summary</h3>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem">
                <div>
                    <span style="color:#9ca3af;font-size:0.78rem">ROUTE</span>
                    <p style="margin:4px 0;font-weight:700;font-size:1.05rem;color:#f3f4f6">
                        {from_stop} → {to_stop}
                    </p>
                </div>
                <div>
                    <span style="color:#9ca3af;font-size:0.78rem">BUS</span>
                    <p style="margin:4px 0;font-weight:600;color:#f3f4f6">{bus['name']}</p>
                    <p style="margin:0;color:#9ca3af;font-size:0.8rem">{bus['company']}</p>
                </div>
                <div>
                    <span style="color:#9ca3af;font-size:0.78rem">DATE</span>
                    <p style="margin:4px 0;font-weight:600;color:#f3f4f6">
                        {travel_date.strftime('%d %b %Y') if hasattr(travel_date, 'strftime') else travel_date}
                    </p>
                </div>
            </div>
            <hr style="border-color:rgba(255,255,255,0.1);margin:1rem 0">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <div>
                    <span style="color:#9ca3af;font-size:0.78rem">SEATS</span>
                    <span style="margin-left:8px;color:#8b5cf6;font-weight:600">
                        {', '.join(sorted(seats))}
                    </span>
                    <span style="margin-left:8px;color:#9ca3af;font-size:0.82rem">
                        ({len(seats)} seat × ₹{fare_each:,})
                    </span>
                </div>
                <div style="text-align:right">
                    <span style="color:#9ca3af;font-size:0.82rem">TOTAL PAYABLE</span>
                    <div style="font-size:1.8rem;font-weight:700;color:#10b981">
                        ₹{total_fare:,}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Payment Form ──────────────────────────────────────────────────────────
    st.markdown("### 💳 Payment Details")
    st.markdown(
        """
        <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);
                    border-radius:10px;padding:0.75rem 1rem;margin-bottom:1.5rem;
                    font-size:0.85rem;color:#10b981">
            🔒 <strong>Secure Payment</strong> — Your card details are encrypted and never stored.
            This is a <strong>demo application</strong>; no real charges are made.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("payment_form", clear_on_submit=False):
        # Cardholder name
        cardholder = st.text_input(
            "👤 Cardholder Name",
            placeholder="As printed on card",
            key="pay_name",
        )

        # Card number with live type detection
        raw_card = st.text_input(
            "💳 Card Number",
            placeholder="1234 5678 9012 3456",
            max_chars=19,
            key="pay_card",
        )
        formatted = _format_card(raw_card or "")
        if raw_card:
            ctype = _card_type(formatted)
            st.caption(f"Detected: **{ctype}**")

        col_exp, col_cvv = st.columns(2)
        with col_exp:
            expiry = st.text_input(
                "📅 Expiry (MM/YY)",
                placeholder="MM/YY",
                max_chars=5,
                key="pay_exp",
            )
        with col_cvv:
            cvv = st.text_input(
                "🔑 CVV",
                placeholder="3 or 4 digits",
                type="password",
                max_chars=4,
                key="pay_cvv",
            )

        # UPI alternative
        st.markdown("---")
        st.markdown("##### Or pay via UPI")
        upi_id = st.text_input(
            "UPI ID (optional)",
            placeholder="yourname@upi",
            key="pay_upi",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        pay_btn = st.form_submit_button(
            f"🔒 Pay ₹{total_fare:,} & Confirm Booking",
            type="primary",
            use_container_width=True,
        )

    if pay_btn:
        errors = []

        # Validate either card OR UPI
        using_upi = bool(upi_id.strip())
        using_card = bool((raw_card or "").strip())

        if not using_upi and not using_card:
            errors.append("Please enter a card number or UPI ID.")
        if using_card:
            if not cardholder.strip():
                errors.append("Cardholder name is required.")
            clean_card = re.sub(r"\D", "", raw_card)
            if not _luhn_check(clean_card):
                errors.append("Invalid card number.")
            if not re.match(r"^(0[1-9]|1[0-2])\/\d{2}$", expiry.strip()):
                errors.append("Expiry must be in MM/YY format.")
            if not re.match(r"^\d{3,4}$", cvv.strip()):
                errors.append("CVV must be 3 or 4 digits.")
        if using_upi:
            if not re.match(r"^[\w.\-]+@[\w]+$", upi_id.strip()):
                errors.append("Invalid UPI ID format (example: name@upi).")

        if errors:
            for e in errors:
                st.error(f"❌ {e}")
        else:
            # ── Save booking to DB ────────────────────────────────────────────
            with st.spinner("🔄 Processing payment…"):
                import time; time.sleep(1.2)   # simulate gateway call

            try:
                row = execute_returning(
                    """
                    INSERT INTO bookings
                        (user_id, bus_id, from_stop, to_stop, travel_date, seats)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING *;
                    """,
                    (
                        st.session_state["user_id"],
                        bus["id"],
                        from_stop,
                        to_stop,
                        travel_date,
                        list(seats),
                    ),
                )
                booking_id = row["id"]
                booked_at  = row["booked_at"]

                # Clear pending booking
                st.session_state.pop("pending_booking", None)

                # Store confirmed booking info for download
                st.session_state["confirmed_booking"] = {
                    "booking_id":  booking_id,
                    "booked_at":   booked_at,
                    "bus":         bus,
                    "seats":       list(seats),
                    "from_stop":   from_stop,
                    "to_stop":     to_stop,
                    "travel_date": travel_date,
                    "fare_each":   fare_each,
                    "total_fare":  total_fare,
                }
                st.session_state["page"] = "booking_success"
                st.rerun()

            except Exception as e:
                st.error(f"❌ Booking failed: {e}")

    # Back button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Seat Selection"):
        st.session_state["page"] = "home"
        st.rerun()
