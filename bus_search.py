"""
bus_search.py — Bus search logic using PostgreSQL ILIKE + array containment.
"""
from database import fetch_all


POPULAR_CITIES = [
    'Hyderabad', 'Ongole', 'Nellore', 'Tirupati', 'Vijayawada',
    'Guntur', 'Visakhapatnam', 'Chennai', 'Bengaluru', 'Mumbai',
    'Pune', 'Delhi', 'Jaipur', 'Kolkata', 'Goa', 'Mysuru', 'Kochi',
    'Hubballi', 'Dharwad', 'Ajmer', 'Jodhpur', 'Kozhikode',
    'Bhubaneswar', 'Ahmedabad', 'Surat',
]

POPULAR_ROUTES = [
    {"from": "Hyderabad",  "to": "Bengaluru", "desc": "Direct sleeper routes daily"},
    {"from": "Ongole",     "to": "Bengaluru", "desc": "AC sleeper services"},
    {"from": "Mumbai",     "to": "Pune",      "desc": "Express highway runs"},
    {"from": "Delhi",      "to": "Jaipur",    "desc": "Heritage line route"},
]


def _bus_extras(bus: dict) -> dict:
    """
    Deterministically calculate rating, duration, and fare from bus name hash.
    Mirrors the original JS logic.
    """
    name_hash = sum(ord(c) for c in bus["name"])
    bus["rating"]   = round(((name_hash % 10) / 10) + 4.0, 1)
    dur_h           = (name_hash % 5) + 3
    dur_m           = (name_hash % 4) * 15
    bus["duration"] = f"{dur_h}h {dur_m}m" if dur_m else f"{dur_h}h"
    bus["fare"]     = (name_hash % 300) + 450          # ₹450–₹750
    return bus


def search_buses(start: str, end: str) -> list[dict]:
    """
    Return all buses whose stops array contains BOTH start and end city.
    Bidirectional — buses run both ways, so no direction constraint applied.
    """
    sql = """
        SELECT b.*
        FROM   buses b
        WHERE  EXISTS (
            SELECT 1 FROM unnest(b.stops) s WHERE s ILIKE %s
        )
        AND EXISTS (
            SELECT 1 FROM unnest(b.stops) s WHERE s ILIKE %s
        );
    """
    rows = fetch_all(sql, (start.strip(), end.strip()))
    return [_bus_extras(dict(r)) for r in rows]
