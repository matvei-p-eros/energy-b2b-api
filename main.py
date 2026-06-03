from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import requests

app = FastAPI(title="B2B Energy API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

URL = "https://api.porssisahko.net/v1/latest-prices.json"
FIXED_COSTS = 8.50

def save_all_prices_to_db():
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            data = response.json()
            conn = sqlite3.connect("energy_data.db")
            cursor = conn.cursor()
            
            for entry in data["prices"]:
                timestamp = entry["startDate"]
                price_net = (entry["price"] / 10) * 1.24
                price_total = price_net + FIXED_COSTS
                
                cursor.execute("""
                    INSERT OR IGNORE INTO hourly_prices (timestamp, price_net, price_total)
                    VALUES (?, ?, ?)
                """, (timestamp, price_net, price_total))
                
            conn.commit()
            conn.close()
            return True
    except:
        return False

@app.get("/api/v1/current-price")
def get_current_price():
    # Проверяем, пустая ли база. Если пустая — заполняем.
    conn = sqlite3.connect("energy_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM hourly_prices")
    count = cursor.fetchone()[0]
    conn.close()
    
    if count == 0:
        save_all_prices_to_db()
        
    # Берем именно ПОСЛЕДНЮЮ ДОБАВЛЕННУЮ запись по ID (это текущий/ближайший час)
    conn = sqlite3.connect("energy_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, price_net, price_total FROM hourly_prices ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "timestamp": row[0],
            "price_net_snt": round(row[1], 2),
            "price_total_snt": round(row[2], 2)
        }
    return {"error": "No data"}

@app.get("/api/v1/forecast-prices")
def get_forecast_prices():
    conn = sqlite3.connect("energy_data.db")
    cursor = conn.cursor()
    # Берем последние 24 записи, но сортируем их строго по времени от старых к новым
    cursor.execute("""
        SELECT timestamp, price_total FROM (
            SELECT timestamp, price_total FROM hourly_prices ORDER BY timestamp DESC LIMIT 24
        ) ORDER BY timestamp ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    forecast = []
    for row in rows:
        forecast.append({
            "raw_date": row[0],
            "price": round(row[1], 2)
        })
        
    return {"forecast": forecast}