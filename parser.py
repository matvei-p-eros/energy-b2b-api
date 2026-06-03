import requests
import time # Импортируем модуль для управления временем

url = "https://api.porssisahko.net/v1/latest-prices.json"

# Запускаем бесконечный цикл
while True:
    print("Выполняю плановое обновление данных...")
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            latest_entry = data["prices"][0]
            
            price_mw = latest_entry["price"]
            porssi_clean = (price_mw / 10) * 1.24
            fixed_costs = 8.50                     
            porssi_total = porssi_clean + fixed_costs
            
            if porssi_clean < 5.0:
                status_text = "🟢 HALPAA"
                status_color = "#2e7d32"
                status_bg = "#e8f5e9"
            elif 5.0 <= porssi_clean <= 12.0:
                status_text = "🟡 NORMAALI"
                status_color = "#f57c00"
                status_bg = "#fff3e0"
            else:
                status_text = "🔴 KALLISTA"
                status_color = "#c62828"
                status_bg = "#ffebee"
                
            pc_porssi = (porssi_total * 0.4) / 100
            oven_porssi = (porssi_total * 2.0) / 100
            washer_porssi = (porssi_total * 1.8) / 100

            fix_base = 12.00
            fix_total = fix_base + fixed_costs
            pc_fix = (fix_total * 0.4) / 100
            oven_fix = (fix_total * 2.0) / 100
            washer_fix = (fix_total * 1.8) / 100
            
            if porssi_clean < 6.0:
                eco_text = "🍃 PUHDAS ENERGIA"
                eco_color = "#1b5e20"
                eco_bg = "#c8e6c9"
                eco_desc = "Verkossa on paljon uusiutuvaa energiaa. Hyvä aika pestä pyykkiä!"
            else:
                eco_text = "⚠️ KORKEA KUORMITUS"
                eco_color = "#e65100"
                eco_bg = "#ffe0b2"
                eco_desc = "Verkko kuormittunut (fossiilinen energia). Säästä ympäristöä, odota hetki."

            # ВАЖНО: Добавляем тег <meta http-equiv="refresh" content="30"> в HTML.
            # Он заставит браузер сам обновлять страницу каждые 30 секунд.
            html_content = f"""<!DOCTYPE html>
<html lang="fi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="30">
    <title>Oma Koti - Älykäs Energianäkymä</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f6f9;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }}
        .tabs {{
            display: flex;
            gap: 8px;
            margin-bottom: 15px;
        }}
        .tab-btn {{
            background: #e2e8f0;
            border: none;
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            color: #4a5568;
            transition: 0.2s;
        }}
        .tab-btn.active {{
            background: #3182ce;
            color: white;
        }}
        .energy-widget {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            padding: 24px;
            width: 350px;
            text-align: center;
        }}
        .widget-title {{
            font-size: 14px;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 12px;
        }}
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 16px;
        }}
        .price-display {{
            font-size: 36px;
            font-weight: 800;
            color: #212529;
            margin-bottom: 4px;
        }}
        .price-unit {{
            font-size: 16px;
            color: #6c757d;
            font-weight: 400;
        }}
        .sub-text {{
            font-size: 13px;
            color: #adb5bd;
            margin-bottom: 20px;
        }}
        .appliances-list {{
            text-align: left;
            border-top: 1px solid #dee2e6;
            padding-top: 16px;
        }}
        .appliance-item {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            font-size: 14px;
            color: #495057;
        }}
        .appliance-cost {{
            font-weight: bold;
            color: #212529;
        }}
    </style>
</head>
<body>

    <div class="tabs">
        <button class="tab-btn active" onclick="switchTariff('porssi')">Pörssisähkö</button>
        <button class="tab-btn" onclick="switchTariff('kiintea')">Kiinteä hinta</button>
    </div>

    <div class="energy-widget">
        <div class="widget-title" id="widget-title-text">Sähkön hinta nyt</div>
        <div class="status-badge" id="status-badge" style="background-color: {status_bg}; color: {status_color};">{status_text}</div>
        <div class="price-display" id="price-main">{porssi_total:.2f}<span class="price-unit"> snt/kWh</span></div>
        <div class="sub-text" id="sub-text-info">Sisältää siirron, verot ja ALV:n</div>
        
        <div class="appliances-list">
            <div class="appliance-item">
                <span>💻 Pelitietokone (1h)</span>
                <span class="appliance-cost" id="cost-pc">{pc_porssi:.2f} €</span>
            </div>
            <div class="appliance-item">
                <span>🍕 Sähköuuni (1h)</span>
                <span class="appliance-cost" id="cost-oven">{oven_porssi:.2f} €</span>
            </div>
            <div class="appliance-item">
                <span>🧺 Pesukone (1h)</span>
                <span class="appliance-cost" id="cost-washer">{washer_porssi:.2f} €</span>
            </div>
        </div>
    </div>

    <script>
        function switchTariff(tariffType) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            const badge = document.getElementById('status-badge');
            const priceMain = document.getElementById('price-main');
            const subText = document.getElementById('sub-text-info');
            const title = document.getElementById('widget-title-text');
            const cPC = document.getElementById('cost-pc');
            const cOven = document.getElementById('cost-oven');
            const cWasher = document.getElementById('cost-washer');
            
            if (tariffType === 'porssi') {{
                title.innerText = "Sähkön hinta nyt";
                badge.innerText = "{status_text}";
                badge.style.backgroundColor = "{status_bg}";
                badge.style.color = "{status_color}";
                priceMain.innerHTML = "{porssi_total:.2f}<span class='price-unit'> snt/kWh</span>";
                subText.innerText = "Sisältää siirron, verot ja ALV:n";
                
                cPC.innerText = "{pc_porssi:.2f} €";
                cOven.innerText = "{oven_porssi:.2f} €";
                cWasher.innerText = "{washer_porssi:.2f} €";
            }} else if (tariffType === 'kiintea') {{
                title.innerText = "Ympäristövaikutus nyt";
                badge.innerText = "{eco_text}";
                badge.style.backgroundColor = "{eco_bg}";
                badge.style.color = "{eco_color}";
                priceMain.innerHTML = "{fix_total:.2f}<span class='price-unit'> snt/kWh</span>";
                subText.innerText = "{eco_desc}";
                
                cPC.innerText = "{pc_fix:.2f} €";
                cOven.innerText = "{oven_fix:.2f} €";
                cWasher.innerText = "{washer_fix:.2f} €";
            }}
        }}
    </script>

</body>
</html>"""
            
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(html_content)
                
            print("Данные успешно обновлены на диске!")
                
        else:
            print(f"Ошибка сервера: {response.status_code}")
            
    except Exception as e:
        print(f"Ошибка: {e}")
        
    # Засыпаем на 15 минут (900 секунд) перед следующим запросом к бирже
    print("Скрипт засыпает на 15 минут...\n")
    time.sleep(900)