import os
from flask import Flask, render_template, request, jsonify
from database import init_db, get_db_connection, get_crowd_category
from crowd_model import calculate_crowd_score, get_crowd_details, recommend_best_time, get_attraction_trends

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tourist-crowd-planner-secret-key-2026'

# Initialize SQLite database on startup
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/attractions', methods=['GET'])
def get_attractions():
    """Returns list of all available tourist attractions."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attractions ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()

    attractions = [dict(row) for row in rows]
    return jsonify({"success": True, "attractions": attractions})

@app.route('/api/predict', methods=['POST'])
def predict_crowd():
    """
    Core API to calculate crowd score (0-100), category, wait times, 
    and recommended visiting windows.
    """
    data = request.json or {}
    attraction = data.get('attraction', 'Taj Mahal')
    date_val = data.get('date', '')
    time_val = data.get('time', '12:00')

    try:
        result = get_crowd_details(attraction, date_val, time_val)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/recommend', methods=['GET'])
def recommend():
    """Identifies lower historical crowd time slots for a specific date."""
    attraction = request.args.get('attraction', 'Taj Mahal')
    date_val = request.args.get('date', '')
    
    try:
        result = recommend_best_time(attraction, date_val)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/trends', methods=['GET'])
def get_trends():
    """Returns Chart.js data series for hourly, daily, and monthly trends."""
    attraction = request.args.get('attraction', 'Taj Mahal')
    try:
        result = get_attraction_trends(attraction)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/historical', methods=['GET'])
def get_historical_data():
    """Retrieves filterable and paginated historical crowd records from SQLite."""
    attraction = request.args.get('attraction', '')
    month = request.args.get('month', '')
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM historical_crowd WHERE 1=1"
    params = []

    if attraction and attraction != 'All':
        query += " AND attraction_name = ?"
        params.append(attraction)

    if month and month != 'All':
        query += " AND month = ?"
        params.append(month)

    if category and category != 'All':
        query += " AND crowd_category = ?"
        params.append(category)

    if search:
        query += " AND (attraction_name LIKE ? OR day_of_week LIKE ? OR time_slot LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])

    # Count total matching rows
    count_query = f"SELECT COUNT(*) FROM ({query})"
    cursor.execute(count_query, params)
    total_records = cursor.fetchone()[0]

    # Add sorting and pagination
    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    offset = (page - 1) * per_page
    params.extend([per_page, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    records = [dict(row) for row in rows]

    return jsonify({
        "success": True,
        "records": records,
        "total": total_records,
        "page": page,
        "per_page": per_page,
        "total_pages": max(1, (total_records + per_page - 1) // per_page)
    })

@app.route('/api/historical/add', methods=['POST'])
def add_historical_record():
    """Allows user to manually insert sample historical crowd record."""
    data = request.json or {}
    attraction = data.get('attraction')
    date_str = data.get('date')
    time_slot = data.get('time_slot', '12:00')
    visitor_count = int(data.get('visitor_count', 500))

    if not attraction or not date_str:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    score = calculate_crowd_score(attraction, date_str, time_slot)
    category = get_crowd_category(score)

    import datetime
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    month_str = dt.strftime("%b")
    day_str = dt.strftime("%A")
    hour = int(time_slot.split(":")[0]) if ":" in time_slot else 12
    is_weekend = 1 if day_str in ["Saturday", "Sunday"] else 0

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO historical_crowd
        (attraction_name, date_str, month, day_of_week, time_slot, hour, visitor_count, crowd_score, crowd_category, is_weekend, is_holiday)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (attraction, date_str, month_str, day_str, time_slot, hour, visitor_count, score, category, is_weekend, 0))
    
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Record added successfully!", "calculated_score": score, "category": category})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Returns high-level statistics across the dataset."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM historical_crowd")
    total_logs = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(crowd_score), AVG(visitor_count) FROM historical_crowd")
    avg_score, avg_visitors = cursor.fetchone()

    cursor.execute("SELECT attraction_name, AVG(crowd_score) as avg_sc FROM historical_crowd GROUP BY attraction_name ORDER BY avg_sc DESC LIMIT 1")
    busiest = cursor.fetchone()

    cursor.execute("SELECT attraction_name, AVG(crowd_score) as avg_sc FROM historical_crowd GROUP BY attraction_name ORDER BY avg_sc ASC LIMIT 1")
    quietest = cursor.fetchone()

    conn.close()

    return jsonify({
        "success": True,
        "total_records": total_logs,
        "avg_crowd_score": round(avg_score or 50, 1),
        "avg_visitor_count": int(avg_visitors or 0),
        "busiest_attraction": busiest["attraction_name"] if busiest else "Taj Mahal",
        "busiest_score": round(busiest["avg_sc"], 1) if busiest else 75,
        "quietest_attraction": quietest["attraction_name"] if quietest else "Qutub Minar",
        "quietest_score": round(quietest["avg_sc"], 1) if quietest else 45
    })

if __name__ == '__main__':
    print("Starting Tourist Crowd Level Planner server on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
