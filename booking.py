"""
booking.py — Seat selection UI and ticket booking with PostgreSQL.
"""
import streamlit as st
from database import fetch_one, fetch_all, execute_returning
from auth import is_logged_in


def get_booked_seats(bus_id: int, travel_date) -> set:
    """Return set of already-booked seat labels for a bus+date."""
    rows = fetch_all(
        "SELECT seats FROM bookings WHERE bus_id = %s AND travel_date = %s;",
        (bus_id, travel_date),
    )
    booked = set()
    for row in rows:
        booked.update(row["seats"])
    return booked


def render_seat_selector(bus: dict, travel_date, from_stop: str, to_stop: str):
    """
    Render an interactive seat-map grid and handle booking.
    Returns True if booking was successfully completed.
    """
    bus_id = bus["id"]
    booked_seats = get_booked_seats(bus_id, travel_date)

    st.markdown("### 🪑 Select Your Seats")
    st.caption(f"**Route:** {from_stop} → {to_stop}  |  **Date:** {travel_date}  |  **Fare/seat:** ₹{bus['fare']}")

    # Build seat grid (40 seats: rows A-J, cols 1-4 with aisle after 2)
    rows_labels  = list("ABCDEFGHIJ")
    col_labels   = ["1", "2", "A", "3", "4"]   # "A" = aisle placeholder
    TOTAL_COLS   = 4

    selected_key = f"sel_seats_{bus_id}"
    if selected_key not in st.session_state:
        st.session_state[selected_key] = set()

    # Legend
    leg_cols = st.columns(4)
    for lc, (color, label) in zip(leg_cols, [
        ("#1e293b", "Available"),
        ("#8b5cf6", "Selected"),
        ("#374151", "Booked"),
        ("#10b981", ""),
    ]):
        lc.markdown(
            f'<span style="display:inline-block;width:18px;height:18px;'
            f'background:{color};border-radius:4px;border:1px solid #555;'
            f'vertical-align:middle;margin-right:6px"></span>{label}',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Render seat grid using Streamlit columns
    # Each row: [col1] [col2] [aisle gap] [col3] [col4]
    header_cols = st.columns([1, 1, 0.4, 1, 1])
    for hc, lbl in zip(header_cols, ["1", "2", "", "3", "4"]):
        hc.markdown(f"<center style='color:#9ca3af;font-size:0.8rem'>{lbl}</center>", unsafe_allow_html=True)

    changed = False
    for row_label in rows_labels:
        cols = st.columns([1, 1, 0.4, 1, 1])
        for ci, col_num in enumerate(["1", "2", None, "3", "4"]):
            with cols[ci]:
                if col_num is None:
                    st.markdown(
                        "<div style='text-align:center;color:#4b5563;font-size:0.75rem;padding-top:6px'>│</div>",
                        unsafe_allow_html=True,
                    )
                    continue
                seat_id = f"{row_label}{col_num}"
                is_booked  = seat_id in booked_seats
                is_selected = seat_id in st.session_state[selected_key]

                if is_booked:
                    st.markdown(
                        f'<div style="background:#374151;border-radius:6px;'
                        f'padding:6px 4px;text-align:center;color:#6b7280;'
                        f'font-size:0.78rem;margin:2px;cursor:not-allowed">{seat_id}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    bg = "#8b5cf6" if is_selected else "#1e293b"
                    btn = st.button(
                        seat_id,
                        key=f"seat_{bus_id}_{seat_id}",
                        help="Click to select/deselect",
                    )
                    if btn:
                        if is_selected:
                            st.session_state[selected_key].discard(seat_id)
                        else:
                            st.session_state[selected_key].add(seat_id)
                        changed = True

    selected = sorted(st.session_state[selected_key])
    total_fare = len(selected) * bus["fare"]

    st.markdown("---")
    if selected:
        st.success(f"✅ **Selected:** {', '.join(selected)}  |  **Total:** ₹{total_fare:,}")
    else:
        st.info("👆 Click seats above to select them.")

    # Proceed to Payment button
    if selected:
        if not is_logged_in():
            st.warning("⚠️ Please **Login** to complete your booking.")
            if st.button("Go to Login", key=f"goto_login_{bus_id}"):
                st.session_state["page"] = "login"
                st.rerun()
        else:
            if st.button(
                f"💳 Proceed to Payment — ₹{total_fare:,}",
                type="primary",
                key=f"confirm_{bus_id}",
                use_container_width=True,
            ):
                # Store pending booking in session state → redirect to payment
                st.session_state["pending_booking"] = {
                    "bus":         bus,
                    "seats":       set(selected),
                    "from_stop":   from_stop,
                    "to_stop":     to_stop,
                    "travel_date": travel_date,
                }
                st.session_state[selected_key] = set()
                st.session_state["page"] = "payment"
                st.rerun()
    return False

