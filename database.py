"""
database.py — PostgreSQL connection, schema initialisation, and query helpers.
"""
import psycopg2
import psycopg2.extras
import streamlit as st

# ─── Connection config ────────────────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "bus_booking",
    "user": "postgres",
    "password": "postgres",
}

# ─── Connection helper ────────────────────────────────────────────────────────
def get_connection():
    """Return a psycopg2 connection, creating the DB if it doesn't exist."""
    # 1. Check if user already supplied a valid connection URI in session state
    db_url = st.session_state.get("db_url")
    
    # 2. Otherwise check if it is defined in st.secrets
    if not db_url:
        try:
            db_url = st.secrets.get("DATABASE_URL")
        except Exception:
            db_url = None
        
    # 3. Default to localhost config
    if not db_url:
        db_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"

    try:
        # Try to connect with current db_url
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        st.session_state["db_url"] = db_url
        return conn
    except psycopg2.OperationalError as e:
        # If localhost fails and database doesn't exist, try creating it
        if "does not exist" in str(e) and "localhost" in db_url:
            try:
                admin_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/postgres"
                admin_conn = psycopg2.connect(admin_url)
                admin_conn.autocommit = True
                with admin_conn.cursor() as cur:
                    cur.execute(f"CREATE DATABASE {DB_CONFIG['dbname']};")
                admin_conn.close()
                conn = psycopg2.connect(db_url)
                conn.autocommit = True
                st.session_state["db_url"] = db_url
                return conn
            except Exception as create_err:
                st.error(f"❌ Could not create local database: {create_err}")
        
        # If connection still fails (e.g. Postgres not running locally, or invalid credentials),
        # display a beautiful connection string input form in the UI.
        st.markdown(
            """
            <div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);
                        border-radius:12px;padding:1.5rem;margin-bottom:1.5rem">
                <h4 style="color:#ef4444;margin:0">🔌 Database Connection Required</h4>
                <p style="color:#9ca3af;font-size:0.9rem;margin:8px 0 0">
                    We couldn't connect to a local PostgreSQL instance. Please paste your <strong>Neon</strong> 
                    or external PostgreSQL connection URI below to start the application.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        user_url = st.text_input(
            "🔑 PostgreSQL / Neon Connection URI:",
            value=st.session_state.get("db_url", ""),
            placeholder="postgresql://neondb_owner:xxxx@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require",
            help="Copy the PostgreSQL connection string from your Neon dashboard."
        )
        
        if user_url:
            try:
                # Validate the new URL
                test_conn = psycopg2.connect(user_url)
                test_conn.close()
                st.session_state["db_url"] = user_url
                st.success("✅ Successfully connected! Reloading application...")
                st.rerun()
            except Exception as conn_err:
                st.error(f"❌ Failed to connect with this URI: {conn_err}")
                
        st.info("💡 Tip: On your Neon Console, select your project, go to 'Connection Details', copy the URI, and paste it here.")
        st.stop()


# ─── Schema initialisation ────────────────────────────────────────────────────
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(120)  NOT NULL,
    email       VARCHAR(200)  NOT NULL UNIQUE,
    password_hash TEXT        NOT NULL,
    contact     VARCHAR(20),
    dob         DATE,
    gender      VARCHAR(20)   NOT NULL,
    created_at  TIMESTAMPTZ   DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS buses (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(120)  NOT NULL,
    company     VARCHAR(120)  NOT NULL,
    stops       TEXT[]        NOT NULL,
    created_at  TIMESTAMPTZ   DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bookings (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER       NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    bus_id      INTEGER       NOT NULL REFERENCES buses(id),
    from_stop   VARCHAR(120)  NOT NULL,
    to_stop     VARCHAR(120)  NOT NULL,
    travel_date DATE          NOT NULL,
    seats       TEXT[]        NOT NULL,
    booked_at   TIMESTAMPTZ   DEFAULT NOW()
);
"""

SEED_BUS_SQL = """
INSERT INTO buses (name, company, stops) VALUES

-- ═══ ANDHRA PRADESH / TELANGANA ROUTES ═══

-- Hyderabad → Ongole direction
('AP-01 Superfast',      'APSRTC',          ARRAY['Hyderabad','Ongole','Nellore','Tirupati']),
('AP-02 Volvo',          'Orange Travels',  ARRAY['Hyderabad','Vijayawada','Guntur','Ongole']),
('AP-12 Night AC',       'SRS Travels',     ARRAY['Hyderabad','Kurnool','Nellore','Ongole']),
('AP-13 Express',        'Green Travels',   ARRAY['Hyderabad','Guntur','Ongole','Tirupati']),

-- Ongole → Hyderabad direction
('AP-14 Return Express', 'APSRTC',          ARRAY['Ongole','Vijayawada','Hyderabad']),
('AP-15 Volvo Return',   'Orange Travels',  ARRAY['Ongole','Nellore','Kurnool','Hyderabad']),
('AP-16 Night Return',   'Parveen Travels', ARRAY['Tirupati','Nellore','Ongole','Hyderabad']),

-- Hyderabad → Bengaluru (forward)
('AP-03 Sleeper',        'VRL Travels',     ARRAY['Hyderabad','Kurnool','Bengaluru']),
('MH-10 HYD-BLR',        'SRS Travels',     ARRAY['Hyderabad','Kurnool','Hospet','Bengaluru']),
('TS-10 Volvo',          'IntrCity',        ARRAY['Hyderabad','Bengaluru','Mysuru']),

-- Bengaluru → Hyderabad (return)
('KA-10 Return',         'KSRTC',           ARRAY['Bengaluru','Kurnool','Hyderabad']),
('KA-11 Sleeper Ret',    'VRL Travels',     ARRAY['Mysuru','Bengaluru','Hyderabad']),
('KA-12 AC Return',      'Orange Travels',  ARRAY['Bengaluru','Hyderabad']),

-- Hyderabad → Chennai (forward)
('TS-01 Hyderabad',      'TSRTC',           ARRAY['Hyderabad','Nellore','Chennai']),
('AP-20 Chennai Exp',    'Parveen Travels', ARRAY['Hyderabad','Vijayawada','Nellore','Chennai']),

-- Chennai → Hyderabad (return)
('TN-10 Chennai-HYD',    'SETC',            ARRAY['Chennai','Nellore','Hyderabad']),
('TN-11 Night Ret',      'SRS Travels',     ARRAY['Chennai','Vijayawada','Hyderabad']),

-- Vijayawada ↔ Hyderabad
('AP-30 VJA Express',    'APSRTC',          ARRAY['Vijayawada','Hyderabad']),
('AP-31 HYD-VJA',        'APSRTC',          ARRAY['Hyderabad','Vijayawada']),

-- Vijayawada ↔ Bengaluru
('AP-32 VJA-BLR',        'APSRTC',          ARRAY['Vijayawada','Ongole','Nellore','Bengaluru']),
('KA-20 BLR-VJA',        'KSRTC',           ARRAY['Bengaluru','Nellore','Ongole','Vijayawada']),

-- ═══ KARNATAKA / TAMIL NADU ROUTES ═══

-- Bengaluru → Mysuru / Goa (forward)
('KA-01 Express',        'KSRTC',           ARRAY['Bengaluru','Mysuru','Hubballi','Dharwad']),
('KA-02 Goa Express',    'KSRTC',           ARRAY['Bengaluru','Mysuru','Goa']),
('TN-01 Express',        'SETC',            ARRAY['Chennai','Bengaluru','Mysuru','Goa']),

-- Mysuru / Goa → Bengaluru (return)
('KA-03 Mysuru Ret',     'KSRTC',           ARRAY['Mysuru','Bengaluru']),
('KA-04 Goa Return',     'KSRTC',           ARRAY['Goa','Mysuru','Bengaluru','Chennai']),
('KA-05 Dharwad Ret',    'VRL Travels',     ARRAY['Dharwad','Hubballi','Mysuru','Bengaluru']),

-- Chennai ↔ Bengaluru
('TN-20 MAS-BLR',        'SETC',            ARRAY['Chennai','Bengaluru']),
('KA-21 BLR-MAS',        'KSRTC',           ARRAY['Bengaluru','Chennai']),
('TN-21 Sleeper',        'SRS Travels',     ARRAY['Chennai','Bengaluru','Mysuru']),

-- Kochi ↔ Bengaluru
('KL-01 Coast',          'KSRTC-Kerala',    ARRAY['Kochi','Kozhikode','Mysuru','Bengaluru']),
('KA-30 BLR-Kochi',      'KSRTC',           ARRAY['Bengaluru','Mysuru','Kozhikode','Kochi']),

-- ═══ MAHARASHTRA / GOA ROUTES ═══

-- Mumbai ↔ Pune
('MH-01 Highway',        'SRS Travels',     ARRAY['Mumbai','Pune','Hyderabad','Bengaluru']),
('MH-02 Pune Exp',       'MSRTC',           ARRAY['Mumbai','Pune']),
('MH-03 Return',         'MSRTC',           ARRAY['Pune','Mumbai']),
('MH-04 Volvo',          'Orange Travels',  ARRAY['Pune','Mumbai','Goa']),

-- Mumbai / Pune → Goa (forward)
('MH-05 Goa Exp',        'SRS Travels',     ARRAY['Mumbai','Pune','Goa']),
('GJ-10 Goa Express',    'GSRTC',           ARRAY['Ahmedabad','Surat','Mumbai','Goa']),

-- Goa → Mumbai / Pune (return)
('MH-06 Goa Ret',        'Kadamba',         ARRAY['Goa','Pune','Mumbai']),
('MH-07 Night Return',   'SRS Travels',     ARRAY['Goa','Pune','Mumbai','Nashik']),

-- ═══ NORTH INDIA ROUTES ═══

-- Delhi ↔ Jaipur / Rajasthan
('DL-01 Heritage',       'RSRTC',           ARRAY['Delhi','Jaipur','Ajmer','Jodhpur']),
('DL-02 Return',         'RSRTC',           ARRAY['Jodhpur','Ajmer','Jaipur','Delhi']),
('DL-03 Jaipur Exp',     'IntrCity',        ARRAY['Delhi','Jaipur']),
('DL-04 Jaipur Ret',     'IntrCity',        ARRAY['Jaipur','Delhi']),

-- Delhi ↔ Agra / UP
('DL-10 Agra Exp',       'UP Roadways',     ARRAY['Delhi','Agra','Lucknow']),
('DL-11 Ret',            'UP Roadways',     ARRAY['Lucknow','Agra','Delhi']),

-- ═══ WEST BENGAL / ODISHA ═══

('WB-01 Kolkata',        'NBSTC',           ARRAY['Kolkata','Bhubaneswar','Visakhapatnam']),
('WB-02 Return',         'NBSTC',           ARRAY['Visakhapatnam','Bhubaneswar','Kolkata']),
('WB-03 Puri Exp',       'OSRTC',           ARRAY['Kolkata','Bhubaneswar','Puri']),

-- ═══ GUJARAT ═══

('GJ-01 Express',        'GSRTC',           ARRAY['Ahmedabad','Surat','Pune','Goa']),
('GJ-02 Return',         'GSRTC',           ARRAY['Goa','Pune','Surat','Ahmedabad']),
('GJ-03 Surat-Mum',      'GSRTC',           ARRAY['Surat','Mumbai']),
('GJ-04 Mum-Surat',      'GSRTC',           ARRAY['Mumbai','Surat','Ahmedabad']),

-- ═══ MULTI-CITY / PAN-INDIA ═══

('AP-05 Night Rider',    'Green Travels',   ARRAY['Vijayawada','Hyderabad','Pune','Mumbai']),
('IN-01 Grand Tour',     'SRS Travels',     ARRAY['Chennai','Bengaluru','Pune','Mumbai']),
('IN-02 East-West',      'Orange Travels',  ARRAY['Kolkata','Bhubaneswar','Visakhapatnam','Vijayawada','Hyderabad']),
('IN-03 South Link',     'VRL Travels',     ARRAY['Mumbai','Pune','Hyderabad','Bengaluru','Chennai']),
('IN-04 Coastal',        'Parveen Travels', ARRAY['Goa','Mangaluru','Kochi','Thiruvananthapuram']),
('IN-05 North-South',    'SRS Travels',     ARRAY['Delhi','Agra','Nagpur','Hyderabad','Bengaluru']),
('IN-06 Coastal Rev',    'Kadamba',         ARRAY['Thiruvananthapuram','Kochi','Mangaluru','Goa']),
('IN-07 AP Coastal',     'APSRTC',          ARRAY['Tirupati','Nellore','Ongole','Vijayawada','Visakhapatnam']),
('IN-08 AP Rev',         'APSRTC',          ARRAY['Visakhapatnam','Vijayawada','Ongole','Nellore','Tirupati'])

ON CONFLICT DO NOTHING;
"""


@st.cache_resource
def init_db():
    """Initialise schema and seed data exactly once (cached per session)."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(SCHEMA_SQL)
        # Seed if fewer than 30 buses exist (handles fresh DB or old 13-bus seed)
        cur.execute("SELECT COUNT(*) FROM buses;")
        count = cur.fetchone()[0]
        if count < 30:
            cur.execute(SEED_BUS_SQL)
    return conn


# ─── Query helpers ────────────────────────────────────────────────────────────
def fetch_one(sql: str, params=()) -> dict | None:
    conn = get_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def fetch_all(sql: str, params=()) -> list[dict]:
    conn = get_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def execute(sql: str, params=()) -> None:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql, params)


def execute_returning(sql: str, params=()):
    conn = get_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        return cur.fetchone()
