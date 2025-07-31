# Modular Modbus Control System

System modularnych widgetów SVG do kontroli urządzeń Modbus RTU.

## 🚀 Szybki start

### Główna aplikacja:
```bash
chmod +x start.sh
./start.sh
```

### Moduł wyjściowy (standalone):
```bash
# Uruchom moduł dla kanału 1 na porcie 5002
chmod +x output_module.py
./output_module.py 1 --port 5002
```

## 📋 Koncepcja

Każdy element UI (przycisk, wskaźnik, przełącznik) to **osobny moduł SVG**, który:
- Jest niezależnym endpointem HTTP
- Wykonuje akcje backend poprzez `mod.py` przy każdym wywołaniu
- Może być osadzony w dowolnym HTML poprzez `<iframe>` lub `<img>`
- Automatycznie odświeża swój stan

## 🔧 Dostępne moduły

### 1. **Output Button** (`/module/output/<channel>`)
Prosty przycisk do przełączania wyjść cyfrowych. Dostępny jako:
- Endpoint w głównej aplikacji: `/module/output/<channel>`
- Samodzielny moduł: `./output_module.py <channel>`

Przykład użycia:
```html
<iframe src="http://localhost:5002/module/output/0" width="100" height="100"></iframe>
```

Uruchomienie samodzielnego modułu:
```bash
# Uruchomienie dla kanału 0 na domyślnym porcie 5001
./output_module.py 0

# Z niestandardowym portem i hostem
./output_module.py 0 --port 8080 --host 0.0.0.0
```

Dostępne parametry:
- `channel` - numer kanału (wymagany, 0-7)
- `--port` - port serwera (domyślnie: 5001)
- `--host` - adres hosta (domyślnie: 0.0.0.0)

### 2. **Switch Widget** (`/widget/switch/<channel>`)
Przełącznik w stylu iOS.
```html
<iframe src="/widget/switch/0" width="200" height="80"></iframe>
```

### 3. **LED Indicator** (`/module/led/<channel>`)
Wskaźnik LED dla wejść cyfrowych.
```html
<img src="/module/led/0" width="50" height="50">
```

### 4. **Gauge Widget** (`/widget/gauge/<register>`)
Wskaźnik analogowy dla rejestrów.
```html
<iframe src="/widget/gauge/0" width="150" height="150"></iframe>
```

### 5. **Register Control** (`/widget/register/<register>`)
Odczyt i zapis rejestrów.
```html
<iframe src="/widget/register/0" width="250" height="120"></iframe>
```

### 6. **Command Button** (`/widget/command/<cmd>`)
Przyciski wykonujące predefiniowane komendy.
```html
<iframe src="/widget/command/all_on" width="100" height="50"></iframe>
```

## 📡 Jak to działa?

1. **Kliknięcie/Odświeżenie** → Widget wysyła żądanie HTTP
2. **Flask Backend** → Wykonuje komendę `mod.py`
3. **mod.py** → Komunikuje się z urządzeniem Modbus
4. **Odpowiedź** → Widget aktualizuje swój wygląd

### Przykład przepływu dla przycisku:
```
User clicks button → GET /action/toggle/0
    ↓
Flask: execute_mod_command(['rc', '0', '1'])  # Read current state
    ↓
mod.py: python mod.py rc 0 1
    ↓
Flask: execute_mod_command(['wc', '0', '1'])  # Write new state
    ↓
mod.py: python mod.py wc 0 1
    ↓
Redirect → GET /module/output/0 (refreshed view)
```

## 🎨 Tworzenie własnych dashboardów

### Przykład 1: Prosty panel
```html
<!DOCTYPE html>
<html>
<head>
    <title>My Control Panel</title>
</head>
<body>
    <h1>Motor Control</h1>
    
    <!-- Przełącznik dla silnika -->
    <iframe src="http://localhost:5001/widget/switch/0" 
            width="200" height="80" frameborder="0"></iframe>
    
    <!-- Status czujnika -->
    <img src="http://localhost:5001/module/led/0" 
         width="50" height="50" id="sensor1">
    
    <script>
        // Auto-refresh czujnika co sekundę
        setInterval(() => {
            document.getElementById('sensor1').src = 
                'http://localhost:5001/module/led/0?t=' + Date.now();
        }, 1000);
    </script>
</body>
</html>
```

### Przykład 2: Grid kontrolek
```html
<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;">
    <iframe src="/module/button/0" width="100" height="100"></iframe>
    <iframe src="/module/button/1" width="100" height="100"></iframe>
    <iframe src="/module/button/2" width="100" height="100"></iframe>
    <iframe src="/module/button/3" width="100" height="100"></iframe>
</div>
```

## 🛠️ API bezpośrednich komend

### POST `/execute`
Wykonaj dowolną komendę mod.py:
```javascript
fetch('http://localhost:5001/execute', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({command: 'rc 0 8'})
})
.then(r => r.json())
.then(data => console.log(data));
```

### Odpowiedź:
```json
{
    "success": true,
    "output": "Coils [0-7]: [True, False, True, False, False, False, False, False]",
    "command": "rc 0 8"
}
```

## 🔍 Debugowanie

### Testowanie komend mod.py:
```bash
# Test bezpośredni
python mod.py rc 0 8

# Test przez API
curl -X POST http://localhost:5001/execute \
     -H "Content-Type: application/json" \
     -d '{"command": "rc 0 8"}'
```

### Sprawdzanie logów:
```bash
# Logi Flask
tail -f flask.log

# Test połączenia Modbus
python mod.py --interactive
```

## 📝 Własne widgety

Aby stworzyć własny widget, dodaj endpoint do `app_modular.py`:

```python
@app.route('/widget/custom/<param>')
def custom_widget(param):
    # Wykonaj komendę
    result = execute_mod_command(['rc', '0', '1'])
    
    # Zwróć SVG
    return Response(f'''
        <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
            <!-- Your SVG content -->
        </svg>
    ''', mimetype='image/svg+xml')
```

## 🌐 Osadzanie w zewnętrznych aplikacjach

Widgety można osadzać w dowolnej aplikacji webowej:

```html
<!-- W WordPress -->
<iframe src="http://your-server:5001/widget/switch/0" 
        width="200" height="80"></iframe>

<!-- W aplikacji React -->
<img src={`http://your-server:5001/module/led/${channel}`} 
     width="50" height="50" />

<!-- W Node-RED Dashboard -->
<iframe src="{{msg.payload}}" width="100" height="100"></iframe>
```

## ⚡ Zalety tego podejścia

1. **Modularność** - każdy widget jest niezależny
2. **Prostota** - brak skomplikowanego JavaScript
3. **Uniwersalność** - działa wszędzie gdzie można osadzić iframe/img
4. **Backend-driven** - cała logika w Pythonie
5. **Stateless** - nie wymaga sesji ani WebSockets
6. **Cacheable** - można używać z proxy/CDN

## 🔐 Bezpieczeństwo

Dla produkcji dodaj:
- Autentykację (np. API key)
- HTTPS
- Rate limiting
- CORS dla określonych domen
- Walidację parametrów

## 📚 Przykłady użycia

- System automatyki domowej
- Panel kontrolny maszyn
- Monitoring czujników
- Sterowanie oświetleniem
- System alarmowy
- Kontrola dostępu