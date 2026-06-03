import sqlite3

def init_db():
    # Подключаемся к файлу базы данных
    conn = sqlite3.connect("energy_data.db")
    cursor = conn.cursor()
    
    # Создаем таблицу (комментарии SQL пишутся через две черточки --)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hourly_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT UNIQUE,  -- Дата и час (например, "2026-05-22 21:00")
            price_net REAL,         -- Чистая цена биржи (snt/kWh)
            price_total REAL        -- Цена с доставкой и налогом (snt/kWh)
        )
    """)
    
    conn.commit()
    conn.close()
    print("База данных успешно инициализирована! Создан файл energy_data.db")

if __name__ == "__main__":
    init_db()