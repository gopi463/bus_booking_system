# 🚌 Youth Travels — Bus Booking System

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-1.35.0+-FF4B4B.svg)](https://streamlit.io/)
[![Database](https://img.shields.io/badge/PostgreSQL-14+-336791.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**Youth Travels** is a premium, modern, and fully-featured Bus Booking System built using Python, Streamlit, and PostgreSQL. It delivers a high-fidelity booking experience powered by custom glassmorphism styles, responsive navigation, dynamic seat maps, a secure payment simulator, and automatic PDF e-ticket generation.

---

## ✨ Features

- **🔒 Advanced User Authentication**: 
  - Register and login with secure password hashing powered by `bcrypt`.
  - Detailed profiles including contact number, date of birth, and gender.
  - Interactive passenger session states.
- **🔍 Intelligent Bus Search**:
  - Direct search with support for popular Indian cities (e.g., Hyderabad, Bengaluru, Mumbai, Pune, Chennai).
  - Bidirectional route containment: automatically finds buses stopping at both your origin and destination, even as intermediate stops (using PostgreSQL array containment queries).
  - One-click shortcuts for high-traffic routes.
- **🪑 Interactive Seat Selector**:
  - Live seat-map grid displaying available, selected, and already-booked seats.
  - Dynamically calculates occupancy and total fares.
- **💳 Simulated Secure Payment**:
  - Luhn algorithm verification for credit/debit card numbers.
  - Live card brand detection (Visa, Mastercard, RuPay, Amex).
  - Alternate instant UPI payment simulation.
- **📄 Professional PDF Tickets**:
  - Dynamic A4 PDF ticket generator built with ReportLab.
  - Embedded invoice breakdown, booking reference code, journey details, and terms.
  - Available for offline download immediately upon booking.
- **📋 User Dashboard**:
  - Visual summary metrics (Total Trips, Seats Booked, Latest Journey).
  - Access to complete travel history.
  - Print/re-download options for any past booking.
  - Danger Zone option for permanent account deletion.
- **🔌 Resilient Database Fallback**:
  - If a local PostgreSQL instance is unavailable, the application gracefully prompts the developer/user to paste a connection URI (e.g., from Neon Console) directly within the running web browser UI.

---

## 🛠️ Tech Stack

- **UI Framework**: [Streamlit](https://streamlit.io/) (v1.35.0+)
- **Database Client**: [psycopg2-binary](https://pypi.org/project/psycopg2-binary/)
- **Password Security**: [bcrypt](https://pypi.org/project/bcrypt/)
- **PDF Engine**: [ReportLab](https://www.reportlab.com/) (installed via `reportlab` library)
- **Styling**: Injected CSS (Google Fonts: Poppins, gradient backgrounds, hover micro-animations)

---

## 📂 Project Structure

```text
streamlit_app/
│
├── .streamlit/
│   └── config.toml          # Custom Streamlit layout and theme settings
│
├── app.py                   # Main entrypoint, global styling, and navigation routing
├── auth.py                  # Login/logout operations and bcrypt hashing
├── database.py              # PostgreSQL connectivity, schema definition, and query helpers
├── bus_search.py            # Bus search matching queries and rating/fare generation
├── booking.py               # Interactive seat layout grid UI and selections
├── payment.py               # Simulated secure checkout form and payment validation
├── booking_success.py       # Successful booking confirmation screen
├── ticket_pdf.py            # Formulates and compiles professional A4 PDF tickets
├── dashboard.py             # User dashboard, booking logs, and account deletion
└── requirements.txt         # Package dependencies list
```

---

## 💾 Database Schema

The database consists of three primary tables linked by constraints:

```mermaid
erDiagram
    USERS {
        int id PK
        varchar name
        varchar email UK
        text password_hash
        varchar contact
        date dob
        varchar gender
        timestamptz created_at
    }
    BUSES {
        int id PK
        varchar name
        varchar company
        text_array stops
        timestamptz created_at
    }
    BOOKINGS {
        int id PK
        int user_id FK
        int bus_id FK
        varchar from_stop
        varchar to_stop
        date travel_date
        text_array seats
        timestamptz booked_at
    }
    USERS ||--o{ BOOKINGS : places
    BUSES ||--o{ BOOKINGS : includes
```

### Table Details:
1. **`users`**: Contains passenger profiles. Password hashes are saved using `bcrypt`.
2. **`buses`**: Contains bus listings, operational companies, and a PostgreSQL Array (`TEXT[]`) of city stops along the route.
3. **`bookings`**: Stores tickets reserved by users. Integrates lists of selected seats and route sub-stops.

---

## 🚀 Setup & Installation

### 1. Prerequisites
Ensure you have Python 3.9+ and PostgreSQL installed on your system. 

### 2. Clone the Repository
```bash
git clone https://github.com/gopi463/bus_booking_system.git
cd Bus-Booking-Project/streamlit_app
```

### 3. Install Dependencies
Install the required packages. Note that `reportlab` must be installed to compile the e-ticket PDFs:
```bash
pip install -r requirements.txt
pip install reportlab
```

### 4. Database Setup
The application is designed to be self-configuring. When run, it attempts connection to PostgreSQL:
- **Local Autoconfiguration**: It searches for a local server running on `localhost:5432` with username `postgres` and password `postgres`. If the database `bus_booking` does not exist, it will attempt to create it automatically.
- **Environment Variables**: Alternatively, configure your credentials by setting a `DATABASE_URL` environment variable or adding it inside `.streamlit/secrets.toml`:
  ```toml
  DATABASE_URL = "postgresql://username:password@host:port/database"
  ```
- **UI Backup Input**: If both local connection and environment variables are absent, the app presents a clean input block in the UI. Paste any PostgreSQL URI (e.g., from [Neon.tech](https://neon.tech/)) to dynamically connect and initialize schemas on the fly.

### 5. Running the Application
Fire up the server using Streamlit:
```bash
streamlit run app.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## 📝 Usage Walkthrough

1. **User Accounts**: Click **Register** on the navigation bar to create a profile. Once created, you are automatically logged in.
2. **Search Routes**: Select your departure and arrival cities, pick a travel date, and press **Search**. (e.g., *Hyderabad* to *Tirupati*).
3. **Choose Bus & Seats**: Browse matching bus cards, check ratings, review fares, and click **Select Seats** to open the seat grid. Select your seats (e.g., `A1`, `A2`) and click **Proceed to Payment**.
4. **Checkout Simulation**: Fill in the payment form (or input a dummy UPI code). The Luhn formula validates card patterns instantly. Click **Pay & Confirm**.
5. **Download Ticket**: The confirmation page displays a preview of your booking. Click **Download Ticket PDF** to save your A4 PDF offline.
6. **Manage Bookings**: Check your profile stats, view past booking cards, or reprint tickets at any time under the **Dashboard** page.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
