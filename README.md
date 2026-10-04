#  Tourist Crowd Level Planner

> **"Plan your sightseeing around expected crowd levels."**

A modern, full-stack web application designed to help tourists beat the queues and optimize their sightseeing itineraries by analyzing historical tourist data, calculating crowd scores, visualizing visitor trends, and recommending ideal visiting time windows.

---

##  Key Features

1. **Interactive Dashboard & Search**: Select popular tourist attractions (*Taj Mahal, Golden Temple, India Gate, Red Fort, Qutub Minar, Jaipur City Palace, Manali Mall Road*), pick a date and planned visit time.
2. **Predictive Crowd Scoring Engine**:
   - Calculates an estimated **Crowd Score (0–100)** based on baseline popularity, day of week (weekend surges), seasonality (peak tourism months/weather), gazetted holidays, and hourly curves.
   - Categorizes crowd levels into **Low (0-30)**, **Moderate (31-60)**, **High (61-80)**, and **Very High (81-100)**.
3. **Smart Visiting Recommendations**: Identifies the golden-hour time slots with lowest crowd scores and highlights peak rush hours to avoid.
4. **Interactive Chart Visualizations**:
   - **Hourly Crowd Score Curve (24-hour line timeline)**
   - **Crowd Level by Day of Week (Bar comparison)**
   - **Monthly Visitor Density Trends (Seasonal area graph)**
   - **Crowd Category Ratio (Doughnut breakdown)**
5. **Destination Comparison Tool**: Compare two attractions side-by-side on the same date to pick the best destination.
6. **Historical Data Explorer**: Query, search, and filter sample historical logs stored in a local SQLite database. Includes a form to insert custom sample records live!

---

## 🛠️ Technology Stack

- **Backend Framework:** Python Flask (REST API Architecture)
- **Database Engine:** SQLite3 (Local file-based database `crowd_planner.db`)
- **Data Processing:** Python, Pandas, NumPy
- **Frontend UI & Styling:** HTML5, Modern Responsive CSS3 (Glassmorphism, CSS Custom Properties, Flexbox & Grid)
- **Data Visualization:** Chart.js 4 & FontAwesome 6 Icons

---

## ⚡ How the Scoring Logic Works

The application implements three core Python functions in `crowd_model.py`:

```python
# 1. Calculates estimated crowd score between 0 and 100
calculate_crowd_score(attraction, date, time)

# 2. Maps crowd score to standardized category badge
get_crowd_category(score)
# Returns: Low (0-30), Moderate (31-60), High (61-80), Very High (81-100)

# 3. Identifies hours with lower historical crowd density
recommend_best_time(attraction, date)
```

---

## 🚀 Getting Started & Local Execution

### Prerequisites
- Python 3.9+ (or `py` launcher on Windows)
- `pip` (Python package installer)

### Installation Steps

1. **Navigate to project directory:**
   ```bash
   cd tourist_crowd_planner
   ```

2. **(Optional) Create a virtual environment:**
   ```bash
   py -m venv venv
   # Activate on Windows:
   .\venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   py -m pip install -r requirements.txt
   ```

4. **Initialize Database & Run Application:**
   ```bash
   py app.py
   ```

5. **Open Application in Browser:**
   Navigate to `http://127.0.0.1:5000` in your web browser.

---

## 📂 Project Structure

```
tourist_crowd_planner/
├── app.py                      # Flask backend API server & route handlers
├── database.py                 # SQLite database setup & sample data generator
├── crowd_model.py              # Predictive algorithm & recommendation engine
├── requirements.txt            # Python dependencies
├── README.md                   # Setup guide and technical documentation
├── static/
│   ├── css/
│   │   └── style.css           # Modern Glassmorphic dark design system
│   └── js/
│       ├── app.js              # SPA router, state management, event listeners
│       └── charts.js           # Chart.js visualizations setup
└── templates/
    └── index.html              # Master single-page dashboard HTML template
```

---

## 📷 Demonstration Flow for Project Expo

1. **Dashboard Home:** Select **Taj Mahal**, pick a Saturday date. Observe expected crowd score (e.g., `74/100`), **High** category, recommended golden hour (`06:00 AM – 08:30 AM`), and 4 interactive charts.
2. **Crowd Planner:** Compare **Taj Mahal** vs **Golden Temple** side-by-side.
3. **Attractions:** Explore detailed cards with ticket prices, opening hours, and baseline scores.
4. **Historical Trends:** Filter sample dataset by month or attraction. Click **"+ Add Sample Record"** to insert a new entry and observe live updates.
