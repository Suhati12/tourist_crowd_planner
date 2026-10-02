import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "crowd_planner.db")

SAMPLE_ATTRACTIONS = [
    {
        "name": "Taj Mahal",
        "location": "Agra, Uttar Pradesh",
        "category": "World Heritage Monument",
        "base_score": 75,
        "best_time": "06:00 AM – 08:30 AM (Sunrise)",
        "peak_hours": "11:00 AM – 03:30 PM",
        "description": "One of the Seven Wonders of the World, an iconic white marble mausoleum attracting millions annually.",
        "opening_hours": "30 mins before sunrise to 30 mins before sunset (Closed Fridays)",
        "ticket_price": "₹50 (Indian) / ₹1100 (Foreigner)",
        "image_url": "https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Golden Temple",
        "location": "Amritsar, Punjab",
        "category": "Spiritual Shrine",
        "base_score": 70,
        "best_time": "04:00 AM – 06:30 AM or 10:00 PM – 11:30 PM",
        "peak_hours": "12:00 PM – 04:00 PM & 06:30 PM – 09:00 PM",
        "description": "The holiest Gurdwara of Sikhism, famous for its gilded architecture and 24/7 community kitchen (Langar).",
        "opening_hours": "Open 24 Hours Daily",
        "ticket_price": "Free Entry",
        "image_url": "https://images.unsplash.com/photo-1514222709107-a180c68d72b4?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "India Gate",
        "location": "New Delhi",
        "category": "Public Memorial & Park",
        "base_score": 60,
        "best_time": "07:00 AM – 09:30 AM or After 09:00 PM",
        "peak_hours": "05:00 PM – 08:30 PM",
        "description": "A prominent war memorial standing 42 meters high, surrounded by lush lawns popular for evening strolls.",
        "opening_hours": "Open 24 Hours Daily",
        "ticket_price": "Free Entry",
        "image_url": "https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Red Fort",
        "location": "Old Delhi",
        "category": "Historical Fort",
        "base_score": 65,
        "best_time": "09:30 AM – 11:00 AM",
        "peak_hours": "01:00 PM – 04:30 PM",
        "description": "Historic red sandstone fort built by Emperor Shah Jahan, serving as the main residence of Mughal emperors.",
        "opening_hours": "09:30 AM – 04:30 PM (Closed Mondays)",
        "ticket_price": "₹35 (Indian) / ₹500 (Foreigner)",
        "image_url": "https://images.unsplash.com/photo-1598324789736-4861f89564a0?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Qutub Minar",
        "location": "New Delhi",
        "category": "Heritage Monument",
        "base_score": 50,
        "best_time": "08:00 AM – 10:00 AM or 04:30 PM – 06:00 PM",
        "peak_hours": "12:00 PM – 03:30 PM",
        "description": "A 73-meter tall minaret and UNESCO World Heritage Site built in 1192, featuring intricate carvings.",
        "opening_hours": "07:00 AM – 05:00 PM Daily",
        "ticket_price": "₹35 (Indian) / ₹550 (Foreigner)",
        "image_url": "https://images.unsplash.com/photo-1592639296346-560c37a0f711?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Jaipur City Palace",
        "location": "Jaipur, Rajasthan",
        "category": "Royal Palace & Museum",
        "base_score": 58,
        "best_time": "09:30 AM – 11:00 AM",
        "peak_hours": "12:30 PM – 03:30 PM",
        "description": "Royal residence blending Rajput, Mughal, and European architecture with stunning courtyards and museums.",
        "opening_hours": "09:30 AM – 05:00 PM & Night Tour 07:00 PM – 10:00 PM",
        "ticket_price": "₹200 (Indian) / ₹700 (Foreigner)",
        "image_url": "https://images.unsplash.com/photo-1599661046827-dacff0c0f09a?auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Manali Mall Road",
        "location": "Manali, Himachal Pradesh",
        "category": "Hill Station Promenade",
        "base_score": 72,
        "best_time": "10:00 AM – 01:00 PM or Early Evening",
        "peak_hours": "05:00 PM – 09:00 PM",
        "description": "Vibrant street market in the heart of Himachal Pradesh, famous for local handicrafts, street food, and mountain views.",
        "opening_hours": "09:00 AM – 10:00 PM Daily",
        "ticket_price": "Free Public Access",
        "image_url": "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=800&q=80"
    }
]

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_crowd_category(score):
    if score <= 30:
        return "Low"
    elif score <= 60:
        return "Moderate"
    elif score <= 80:
        return "High"
    else:
        return "Very High"

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create attractions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attractions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        location TEXT NOT NULL,
        category TEXT NOT NULL,
        base_score INTEGER NOT NULL,
        best_time TEXT NOT NULL,
        peak_hours TEXT NOT NULL,
        description TEXT NOT NULL,
        opening_hours TEXT NOT NULL,
        ticket_price TEXT NOT NULL,
        image_url TEXT NOT NULL
    )
    """)

    # Create historical_crowd table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historical_crowd (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attraction_name TEXT NOT NULL,
        date_str TEXT NOT NULL,
        month TEXT NOT NULL,
        day_of_week TEXT NOT NULL,
        time_slot TEXT NOT NULL,
        hour INTEGER NOT NULL,
        visitor_count INTEGER NOT NULL,
        crowd_score INTEGER NOT NULL,
        crowd_category TEXT NOT NULL,
        is_weekend INTEGER NOT NULL,
        is_holiday INTEGER NOT NULL,
        FOREIGN KEY (attraction_name) REFERENCES attractions (name)
    )
    """)

    # Seed attractions if table is empty
    cursor.execute("SELECT COUNT(*) FROM attractions")
    if cursor.fetchone()[0] == 0:
        for item in SAMPLE_ATTRACTIONS:
            cursor.execute("""
            INSERT INTO attractions (name, location, category, base_score, best_time, peak_hours, description, opening_hours, ticket_price, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item["name"], item["location"], item["category"], item["base_score"],
                item["best_time"], item["peak_hours"], item["description"],
                item["opening_hours"], item["ticket_price"], item["image_url"]
            ))

    # Seed historical crowd data if empty
    cursor.execute("SELECT COUNT(*) FROM historical_crowd")
    if cursor.fetchone()[0] == 0:
        seed_historical_data(cursor)

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def seed_historical_data(cursor):
    """
    Generates realistic historical data across 12 months, days of week, and hourly slots.
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    hours = list(range(6, 22))  # 6 AM to 9 PM (21:00)

    # List of sample dates over past year
    start_date = datetime(2025, 1, 1)
    
    # Generate around 600 records across attractions
    records = []
    
    for attraction in SAMPLE_ATTRACTIONS:
        attr_name = attraction["name"]
        base = attraction["base_score"]
        
        # Select 15 sample dates for each attraction across different months
        for i in range(15):
            date_obj = start_date + timedelta(days=i * 24 + random.randint(0, 5))
            month_str = date_obj.strftime("%b")
            day_str = date_obj.strftime("%A")
            date_formatted = date_obj.strftime("%Y-%m-%d")
            
            is_weekend = 1 if day_str in ["Saturday", "Sunday"] else 0
            is_holiday = 1 if (is_weekend and random.random() > 0.6) or (month_str in ["Oct", "Nov", "Dec", "Jan"] and random.random() > 0.7) else 0

            # Generate hourly logs for this day
            for hour in [6, 8, 10, 12, 14, 16, 18, 20]:
                time_slot = f"{hour:02d}:00"
                
                # Hourly distribution factor
                if 11 <= hour <= 15:
                    time_factor = 1.4
                elif 16 <= hour <= 18:
                    time_factor = 1.2
                elif 8 <= hour <= 10:
                    time_factor = 0.75
                else:
                    time_factor = 0.45

                # Weekend / Holiday factor
                day_factor = 1.35 if is_weekend else 1.0
                holiday_factor = 1.25 if is_holiday else 1.0

                # Seasonal factor
                if attr_name == "Manali Mall Road":
                    season_factor = 1.4 if month_str in ["May", "Jun", "Dec"] else 0.8
                else:
                    season_factor = 1.3 if month_str in ["Oct", "Nov", "Dec", "Jan", "Feb"] else 0.85

                # Calculate crowd score between 0 and 100
                calc_score = int(base * time_factor * day_factor * holiday_factor * season_factor + random.randint(-4, 5))
                calc_score = max(5, min(99, calc_score))

                # Visitor count calculation derived from crowd score
                visitor_count = int(calc_score * random.uniform(85.0, 140.0))
                category = get_crowd_category(calc_score)

                records.append((
                    attr_name, date_formatted, month_str, day_str, time_slot, hour,
                    visitor_count, calc_score, category, is_weekend, is_holiday
                ))

    cursor.executemany("""
    INSERT INTO historical_crowd 
    (attraction_name, date_str, month, day_of_week, time_slot, hour, visitor_count, crowd_score, crowd_category, is_weekend, is_holiday)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, records)
    print(f"Seeded {len(records)} historical crowd records!")

if __name__ == "__main__":
    init_db()
