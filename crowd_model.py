import datetime
from database import get_db_connection, get_crowd_category

# Known gazetted holidays & festival periods (MM-DD)
HOLIDAY_DATES = {
    "01-01": "New Year's Day",
    "01-26": "Republic Day",
    "08-15": "Independence Day",
    "10-02": "Gandhi Jayanti",
    "11-01": "Diwali Season",
    "12-25": "Christmas Day",
    "12-31": "New Year's Eve"
}

def parse_date(date_input):
    """Normalizes date input into datetime object and formatted strings."""
    if isinstance(date_input, datetime.date) or isinstance(date_input, datetime.datetime):
        dt = date_input
    else:
        try:
            dt = datetime.datetime.strptime(str(date_input), "%Y-%m-%d")
        except ValueError:
            dt = datetime.datetime.now()
    
    return dt

def parse_time_hour(time_input):
    """Converts time string (HH:MM or HH:MM AM/PM) into integer hour 0-23."""
    if not time_input:
        return 12
    
    time_str = str(time_input).strip()
    try:
        if "AM" in time_str.upper() or "PM" in time_str.upper():
            dt = datetime.datetime.strptime(time_str, "%I:%M %p")
            return dt.hour
        elif ":" in time_str:
            parts = time_str.split(":")
            return int(parts[0])
        else:
            return int(time_str)
    except Exception:
        return 12

def calculate_crowd_score(attraction, date_input, time_input):
    """
    Calculates estimated crowd score (0-100) based on historical patterns, 
    day of week, seasonality, holidays, and time slot.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get attraction baseline info
    cursor.execute("SELECT * FROM attractions WHERE name = ?", (attraction,))
    attr = cursor.fetchone()
    
    if not attr:
        # Fallback if attraction not matched exactly
        cursor.execute("SELECT * FROM attractions LIMIT 1")
        attr = cursor.fetchone()

    base_score = attr["base_score"] if attr else 60
    attr_name = attr["name"] if attr else attraction

    dt = parse_date(date_input)
    hour = parse_time_hour(time_input)

    day_name = dt.strftime("%A")
    month_name = dt.strftime("%b")
    mm_dd = dt.strftime("%m-%d")

    # 1. Day of Week Multiplier
    if day_name == "Sunday":
        day_mult = 1.35
    elif day_name == "Saturday":
        day_mult = 1.30
    elif day_name == "Friday":
        day_mult = 1.15
    else:
        day_mult = 1.00

    # 2. Seasonality Multiplier
    if attr_name == "Manali Mall Road":
        # Hill station peak in summer (May-Jun) and winter snow (Dec-Jan)
        if month_name in ["May", "Jun", "Dec", "Jan"]:
            season_mult = 1.35
        elif month_name in ["Jul", "Aug"]:
            season_mult = 0.75  # Monsoon low
        else:
            season_mult = 1.00
    else:
        # Heritage & North India monuments peak in Oct-Mar
        if month_name in ["Oct", "Nov", "Dec", "Jan", "Feb"]:
            season_mult = 1.25
        elif month_name in ["May", "Jun"]:
            season_mult = 0.85  # Peak summer heat low
        else:
            season_mult = 1.00

    # 3. Holiday / Special Event Multiplier
    is_weekend = day_name in ["Saturday", "Sunday"]
    is_holiday = mm_dd in HOLIDAY_DATES
    holiday_mult = 1.30 if is_holiday else (1.10 if is_weekend else 1.00)

    # 4. Hourly Crowd Curve
    if attr_name == "Golden Temple":
        # Golden Temple has early morning Prakash & late evening Aarti peaks
        if 4 <= hour <= 7:
            time_mult = 1.10
        elif 11 <= hour <= 15:
            time_mult = 1.35
        elif 18 <= hour <= 21:
            time_mult = 1.30
        elif 22 <= hour <= 23 or 0 <= hour <= 3:
            time_mult = 0.50
        else:
            time_mult = 0.80
    elif attr_name == "India Gate":
        # India Gate peak is late evening/night
        if 17 <= hour <= 21:
            time_mult = 1.45
        elif 12 <= hour <= 16:
            time_mult = 1.10
        elif 6 <= hour <= 9:
            time_mult = 0.45
        else:
            time_mult = 0.70
    else:
        # Standard Monument Curve (Taj Mahal, Red Fort, Qutub Minar, City Palace)
        if 6 <= hour <= 8:
            time_mult = 0.40  # Peaceful early morning
        elif 9 <= hour <= 10:
            time_mult = 0.75
        elif 11 <= hour <= 15:
            time_mult = 1.40  # Midday peak rush
        elif 16 <= hour <= 17:
            time_mult = 1.15
        elif 18 <= hour <= 21:
            time_mult = 0.65
        else:
            time_mult = 0.30

    # 5. Query Historical Data Averages for smooth blending
    cursor.execute("""
        SELECT AVG(crowd_score) as avg_score, AVG(visitor_count) as avg_visitors
        FROM historical_crowd
        WHERE attraction_name = ? AND (day_of_week = ? OR is_weekend = ?)
    """, (attr_name, day_name, 1 if is_weekend else 0))
    hist_row = cursor.fetchone()
    
    hist_score = hist_row["avg_score"] if hist_row and hist_row["avg_score"] else base_score

    # Model Score Combination
    calculated = (base_score * 0.35 + hist_score * 0.25) * day_mult * season_mult * holiday_mult * time_mult
    final_score = int(max(5, min(99, round(calculated))))

    conn.close()
    return final_score

def get_crowd_details(attraction, date_input, time_input):
    """Returns comprehensive payload for prediction dashboard."""
    score = calculate_crowd_score(attraction, date_input, time_input)
    category = get_crowd_category(score)
    
    dt = parse_date(date_input)
    date_formatted = dt.strftime("%B %d, %Y")
    day_name = dt.strftime("%A")
    hour = parse_time_hour(time_input)
    
    # Estimated waiting time & condition text
    if category == "Low":
        wait_time = "0 – 15 mins"
        condition = "Quiet & serene visit. Very short lines at entrance and ticketing counters."
        status_color = "#10b981"  # Emerald Green
        icon = "fa-smile-beam"
    elif category == "Moderate":
        wait_time = "15 – 35 mins"
        condition = "Manageable crowd. Steady entry movement with moderate photo spot availability."
        status_color = "#f59e0b"  # Amber Orange
        icon = "fa-user-friends"
    elif category == "High":
        wait_time = "35 – 65 mins"
        condition = "Busy and congested. Long lines at entry security and major photo vantage points."
        status_color = "#ef4444"  # Rose Red
        icon = "fa-users"
    else:  # Very High
        wait_time = "65 – 100+ mins"
        condition = "Heavy rush & peak congestion. Expect extended wait times and high traffic density."
        status_color = "#881337"  # Dark Crimson/Purple
        icon = "fa-user-slash"

    recommendation = recommend_best_time(attraction, date_input)

    return {
        "attraction": attraction,
        "date": date_formatted,
        "raw_date": dt.strftime("%Y-%m-%d"),
        "day_of_week": day_name,
        "time_slot": f"{hour:02d}:00",
        "crowd_score": score,
        "crowd_category": category,
        "estimated_wait_time": wait_time,
        "condition_description": condition,
        "status_color": status_color,
        "icon": icon,
        "recommended_time": recommendation["best_time_window"],
        "peak_hours_to_avoid": recommendation["peak_hours"],
        "hourly_curve": recommendation["hourly_curve"]
    }

def recommend_best_time(attraction, date_input):
    """
    Identifies the time windows with relatively lower historical crowd scores on the selected date.
    """
    dt = parse_date(date_input)
    date_str = dt.strftime("%Y-%m-%d")

    # Evaluate hours from 6 AM to 9 PM
    hourly_curve = []
    for h in range(6, 22):
        time_str = f"{h:02d}:00"
        score = calculate_crowd_score(attraction, date_str, time_str)
        hourly_curve.append({
            "hour": h,
            "time_label": f"{h if h <= 12 else h - 12}:00 {'AM' if h < 12 else 'PM'}",
            "score": score,
            "category": get_crowd_category(score)
        })

    # Sort to find lowest scores
    sorted_slots = sorted(hourly_curve, key=lambda x: x["score"])
    best_slot = sorted_slots[0]
    
    # Group contiguous best hours
    best_hours = [s for s in hourly_curve if s["score"] <= best_slot["score"] + 12]
    best_start = min(b["hour"] for b in best_hours)
    best_end = max(b["hour"] for b in best_hours) + 1

    best_time_window = f"{best_start:02d}:00 {'AM' if best_start < 12 else 'PM'} – {best_end:02d}:00 {'AM' if best_end < 12 else 'PM'}"

    # Find peak hours
    peak_slots = [s for s in hourly_curve if s["score"] >= 65]
    if peak_slots:
        peak_start = min(p["hour"] for p in peak_slots)
        peak_end = max(p["hour"] for p in peak_slots) + 1
        peak_hours = f"{peak_start:02d}:00 {'AM' if peak_start < 12 else 'PM'} – {peak_end:02d}:00 {'AM' if peak_end < 12 else 'PM'}"
    else:
        peak_hours = "12:00 PM – 03:30 PM (Midday Rush)"

    return {
        "attraction": attraction,
        "best_time_window": best_time_window,
        "best_score": best_slot["score"],
        "best_category": get_crowd_category(best_slot["score"]),
        "peak_hours": peak_hours,
        "hourly_curve": hourly_curve
    }

def get_attraction_trends(attraction):
    """Retrieves aggregated trend metrics for Chart.js graphics."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Hourly Trend
    cursor.execute("""
        SELECT time_slot, hour, AVG(crowd_score) as avg_score, AVG(visitor_count) as avg_visitors
        FROM historical_crowd
        WHERE attraction_name = ?
        GROUP BY hour
        ORDER BY hour ASC
    """, (attraction,))
    hourly_rows = cursor.fetchall()

    hourly_data = {
        "labels": [f"{r['hour']:02d}:00" for r in hourly_rows],
        "scores": [round(r["avg_score"], 1) for r in hourly_rows],
        "visitors": [int(r["avg_visitors"]) for r in hourly_rows]
    }

    # 2. Day of Week Trend
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    cursor.execute("""
        SELECT day_of_week, AVG(crowd_score) as avg_score
        FROM historical_crowd
        WHERE attraction_name = ?
        GROUP BY day_of_week
    """, (attraction,))
    day_rows = {r["day_of_week"]: round(r["avg_score"], 1) for r in cursor.fetchall()}

    daily_data = {
        "labels": days_order,
        "scores": [day_rows.get(d, 50) for d in days_order]
    }

    # 3. Monthly Trend
    months_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    cursor.execute("""
        SELECT month, AVG(crowd_score) as avg_score, AVG(visitor_count) as avg_visitors
        FROM historical_crowd
        WHERE attraction_name = ?
        GROUP BY month
    """, (attraction,))
    month_rows = {r["month"]: (round(r["avg_score"], 1), int(r["avg_visitors"])) for r in cursor.fetchall()}

    monthly_data = {
        "labels": months_order,
        "scores": [month_rows.get(m, (50, 0))[0] for m in months_order],
        "visitors": [month_rows.get(m, (50, 0))[1] for m in months_order]
    }

    conn.close()

    return {
        "attraction": attraction,
        "hourly": hourly_data,
        "daily": daily_data,
        "monthly": monthly_data
    }
