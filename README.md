# Modbus RTU IO 8CH Control System

# Charakterystyka rozwiązania SVG + PWA + PHP + HTML + JS

**Architektura i główne komponenty**  
Rozwiązanie łączące interaktywny interfejs SVG z osadzonym HTML/JS, backendem w PHP oraz działaniem jako Progressive Web App (PWA) składa się z następujących warstw:

1. **Warstwa prezentacji (SVG + HTML/JS)**
    - SVG z `` osadzającym przyciski, wskaźniki i etykiety jako elementy HTML.
    - Stylowanie i animacje przy pomocy CSS wewnątrz `` w ``.
    - Dynamiczna interakcja (kliknięcia, animacje, aktualizacja stanu) za pomocą czystego JavaScriptu, m.in. wykorzystującego `fetch()` do wywołań API.

2. **Warstwa aplikacji (PWA)**
    - Manifest web app manifest (`manifest.json`) definiujący nazwę, ikony i tryby wyświetlania.
    - Service Worker do cache’owania zasobów SVG, skryptów i odpowiedzi API, co umożliwia pracę offline.
    - Obsługa zdarzeń instalacji (Add to Home Screen), powiadomień push i synchronizacji w tle.

3. **Warstwa backendu (PHP)**
    - Wczytywanie konfiguracji z pliku `.env` i przekazywanie jej do front-endu (adres API, port, interwały odświeżania).
    - Endpoints PHP (np. `/control`, `/status`) pośredniczące w komunikacji z rzeczywistym urządzeniem Modbus RTU.
    - Możliwość rozbudowy o uwierzytelnianie, logowanie zdarzeń i zapis danych historycznych.

4. **Komunikacja z urządzeniami zewnętrznymi**
    - PHP używa bibliotek Modbus RTU do odczytu stanu wejść/wyjść.
    - Kanoniczne API REST zwraca JSON z tablicami `inputs`, `outputs` i flagą `connected`.

**Kluczowe zalety**
- **Responsywność i skalowalność**: SVG zachowuje płynność skalowania na dowolnych rozdzielczościach i urządzeniach.
- **Offline-first**: dzięki PWA interfejs działa bez dostępu do sieci, co jest krytyczne w środowiskach przemysłowych.
- **Lekka warstwa front-end**: brak ciężkich frameworków – czysty JS i HTML minimalizują rozmiar paczki.
- **Elastyczność stylizacji**: CSS w SVG pozwala na tworzenie zaawansowanych efektów (animowane gradienty, wskaźniki stanu).

# Potencjał w różnych niszach

## 1. Automatyka przemysłowa i IoT
- **Sterowanie i wizualizacja maszyn**: interaktywny panel SVG odzwierciedlający stan czujników i przekaźników w czasie rzeczywistym.
- **Mobilne aplikacje operatorskie**: PWA umożliwia instalację na tabletach i smartfonach, zapewniając szybką reakcję techników na linii produkcyjnej.
- **Przewaga offline**: niezawodne działanie bez sieci w halach produkcyjnych[1].

## 2. Dashboardy analityczne i BI
- **Wizualizacje KPI**: SVG umożliwia tworzenie niestandardowych wykresów, map ciepła i diagramów, które można interaktywnie filtrować.
- **Przestrzeń oszczędności pasma**: cache’owanie elementów SVG i danych czyni PWA bardziej wydajnym niż tradycyjne aplikacje webowe[2].

## 3. GIS i mapowanie
- **Dynamiczne mapy wektorowe**: warstwy SVG z regionami interaktywnymi i geostanami, sterowane API PHP.
- **Aplikacje terenowe**: offline’owy dostęp do map i pomiarów pola z instalacją „Add to Home Screen”.

## 4. Edukacja i szkolenia
- **Symulatory**: interaktywne modele fizyczne (np. układy elektroniczne, maszyny) z przyciskami sterującymi w SVG.
- **Multiplatformowość**: działanie w przeglądarkach na desktopie i mobilnie bez instalacji natywnej.

## 5. Marketing i prezentacje produktowe
- **Interaktywne infografiki**: animowane SVG w postaci aplikacji webowej, dostępne offline.
- **Łatwa dystrybucja**: PWA można „zainstalować” z witryny bez konieczności publikacji w sklepach.

## 6. Sztuka cyfrowa i grafika generatywna
- **Eksperymenty wizualne**: SVG jako medium do tworzenia generatywnej sztuki, z danymi sterowanymi PHP.
- **Eventy i instalacje**: PWA jako mobilny kiosk interaktywnych instalacji, gdzie praca offline jest atutem.

**Podsumowanie**  
Rozwiązanie łączące SVG, PWA, PHP, HTML i JavaScript stanowi **uniwersalną platformę** do tworzenia lekkich, responsywnych i offline-first aplikacji w obszarach przemysłu, analityki, GIS, edukacji, marketingu i sztuki. Dzięki elastyczności SVG i niezawodności PWA może być wykorzystywane w wymagających środowiskach produkcyjnych, jak również w interaktywnych prezentacjach i narzędziach edukacyjnych.

[1] https://dockyard.com/blog/2017/08/01/svg-assets-in-pwas
[2] https://dev.to/ctannerweb/how-inline-svg-s-improve-performance-4k37
[3] https://www.risevision.com/manufacturing-dashboards
[4] https://www.svgator.com/blog/interactive-svg-examples/
[5] https://matics.live/blog/how-to-build-a-dynamic-manufacturing-dashboard/
[6] https://getuikit.com/docs/svg
[7] https://stackoverflow.com/questions/64427667/how-to-use-svg-as-pwa-icon
[8] https://www.industrialinfo.com/analytics_forecasting/tableau-dashboard-article.jsp
[9] https://helpcenter.flourish.studio/hc/en-us/articles/8761539216911-Interactive-SVG-An-overview
[10] https://github.com/webmaxru/progressive-web-apps-logo
[11] https://github.com/nilshoell/dashboard-pwa
[12] https://www.youtube.com/watch?v=aZGf522Ykcg
[13] https://web.dev/case-studies/svgcode
[14] https://flowfuse.com/blog/2024/04/dashboard-milestones-pwa-new-components/
[15] https://www.einpresswire.com/article/828085178/axialis-iconvectors-the-essential-lightweight-svg-icon-editor-for-developers-and-ui-designers
[16] https://vite-pwa-org.netlify.app/assets-generator/
[17] https://elements.envato.com/web-templates/admin-templates/pwa
[18] https://stackoverflow.com/questions/79578932/interactive-svg-without-smil-js-foreignobject-and-checked
[19] https://alexop.dev/posts/create-pwa-vue3-vite-4-steps/
[20] https://flowfuse.com/blog/dashboard/



**FULLY FUNCTIONAL** Web-based control system for Waveshare Modbus RTU IO 8CH device with PHP SVG interface and FastAPI backend integrated with mod.py shell functionality.

## ✅ System Status: **WORKING**

- ✅ **Real-time Hardware Control**: Output channels toggle via web interface
- ✅ **Auto Hardware Detection**: Uses mod.py for USB port auto-detection  
- ✅ **Live Status Updates**: Real-time monitoring of inputs/outputs
- ✅ **Error Handling**: Graceful fallbacks and proper error responses
- ✅ **Cross-Platform**: Works on Linux with USB-to-RS485 adapters

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │◄──►│   PHP Server    │◄──►│  FastAPI Server │
│ (User Interface)│    │  :8080/svg      │    │     :8090       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │ HTTP                  │ REST API              │ mod.py shell
         v                       v                       v
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Interactive SVG │    │   JavaScript    │    │ ModbusRTUClient │
│   Interface     │    │  + Minimal PHP  │    │  (Auto-detect)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        │ USB/RS485
                                                        v
                                              ┌─────────────────┐
                                              │ Modbus RTU IO   │
                                              │    8CH Device   │
                                              │  8DI + 8DO      │
                                              └─────────────────┘
```

## Key Features

### 🎛️ **Web Interface**
- **8 Digital Output Controls**: Toggle buttons with real-time LED feedback
- **8 Digital Input Monitors**: Live status indicators with HIGH/LOW labels  
- **Connection Status**: Visual connection indicator
- **Responsive Design**: Works on desktop and mobile browsers

### 🔧 **Backend Integration**
- **mod.py Integration**: Uses proven ModbusRTUClient for hardware communication
- **Auto Port Detection**: Automatically finds USB-to-RS485 adapters
- **FastAPI REST API**: Modern async endpoints for control and status
- **Background Updates**: Continuous device state monitoring

### 🔌 **Hardware Support**
- **Auto-Detection**: Finds Modbus devices on available serial ports
- **Multiple Adapters**: Supports various USB-to-RS485 converters
- **Error Recovery**: Automatic reconnection on device disconnection

## Hardware Wiring

```
Computer/Server                    Modbus RTU IO 8CH
┌─────────────────┐               ┌────────────────────┐
│                 │               │                    │
│  USB Port       │               │  Power: 7-36V DC   │
│     │           │               │  ┌─────────────┐   │
│     v           │               │  │   Power     │   │
│ ┌─────────────┐ │               │  │   Input     │   │
│ │USB-to-RS485 │ │               │  └─────────────┘   │
│ │  Converter  │ │               │                    │
│ │             │ │ RS485 Cable   │  ┌─────────────┐   │
│ │   A+ ───────┼─┼───────────────┼──┤ 485 A+      │   │
│ │   B- ───────┼─┼───────────────┼──┤ 485 B-      │   │
│ │   GND ──────┼─┼───────────────┼──┤ DGND        │   │
│ └─────────────┘ │               │  └─────────────┘   │
│                 │               │                    │
└─────────────────┘               │  ┌─────────────┐   │
                                  │  │   DI1-DI8   │   │
                                  │  │ Digital In  │   │
                                  │  └─────────────┘   │
                                  │                    │
                                  │  ┌─────────────┐   │
                                  │  │   DO1-DO8   │   │
                                  │  │Digital Out  │   │
                                  │  └─────────────┘   │
                                  └────────────────────┘
```

## Features

- **8 Digital Outputs**: Control via interactive buttons in the web interface
- **8 Digital Inputs**: Real-time status monitoring with LED indicators
- **Web Interface**: Modern SVG-based interface with PHP backend
- **REST API**: FastAPI backend for programmatic control
- **Auto-refresh**: Interface updates every 2 seconds
- **Modbus RTU**: Standard protocol communication via USB-to-RS485

## Hardware Requirements

- Waveshare Modbus RTU IO 8CH module
- USB-to-RS485 converter (RS485 CAN HAT or similar)
- Linux system with USB port

## Software Requirements

- Python 3.7+
- PHP 7.4+ with web server (Apache/Nginx)
- USB-to-RS485 driver support

## Installation

1. **Install Python dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Connect hardware:**
   - Connect USB-to-RS485 converter to computer
   - Connect RS485 A/B lines to Modbus RTU IO 8CH
   - Power the Modbus device (7-36V DC)

3. **Configure device settings (if needed):**
   - Default: Address 0x01, 9600 baud, N,8,1
   - Modify `MODBUS_DEVICE_ADDRESS` and `MODBUS_PORT` in `api.py` if different

## Usage

### Modbus RTU Client Tool (mod.py)

The `mod.py` script provides a standalone Modbus RTU client for testing and interacting with Modbus devices. It automatically loads configuration from the `.env` file.

#### Prerequisites

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Ensure proper permissions:**
   ```bash
   sudo usermod -aG dialout $USER
   # Logout and login again for changes to take effect
   ```

3. **Verify device connection:**
   ```bash
   ls -l /dev/ttyACM*
   # Should show your USB-RS485 adapter
   ```

#### Configuration

The script reads configuration from `.env` file:
- `MODBUS_PORT` - Serial port (default: `/dev/ttyUSB0`)
- `MODBUS_BAUDRATE` - Communication speed (default: `9600`)
- `MODBUS_TIMEOUT` - Timeout in seconds (default: `1.0`)

Current configuration from `.env`:
```
MODBUS_PORT=/dev/ttyACM0
MODBUS_BAUDRATE=9600
MODBUS_TIMEOUT=1
```

#### Usage Modes

**1. Demo Mode (default):**
```bash
python mod.py
```
Runs predefined examples showing how to read/write coils and registers.

**2. Interactive Mode:**
```bash
python mod.py --interactive
```

**3. Command-Line Mode (Direct Control):**
```bash
python mod.py <command> <args>
```
Execute single Modbus commands directly from command line.

**4. As Python Library (Programmatic):**
Import and use the `ModbusRTUClient` class in your own Python scripts.

#### Command-Line Usage (Direct Control)

You can control Modbus devices directly from the command line using the same shortcuts as interactive mode:

**Basic Syntax:**
```bash
python mod.py <command> <address> <value/count> [unit]
```

**Available Commands:**
- `rc <addr> <count> [unit]` - Read coils
- `rh <addr> <count> [unit]` - Read holding registers  
- `ri <addr> <count> [unit]` - Read input registers
- `rd <addr> <count> [unit]` - Read discrete inputs
- `wc <addr> <value> [unit]` - Write coil (0=OFF, 1=ON)
- `wr <addr> <value> [unit]` - Write register

**Examples:**

**Control Outputs:**
```bash
# Turn ON output 0
python mod.py wc 0 1

# Turn OFF output 0  
python mod.py wc 0 0

# Turn ON output 3
python mod.py wc 3 1

# Turn OFF all outputs (0-7)
python mod.py wc 0 0
python mod.py wc 1 0
python mod.py wc 2 0
python mod.py wc 3 0
python mod.py wc 4 0
python mod.py wc 5 0
python mod.py wc 6 0
python mod.py wc 7 0
```

**Read Status:**
```bash
# Read all 8 outputs status
python mod.py rc 0 8

# Read 4 holding registers
python mod.py rh 0 4

# Read 2 input registers  
python mod.py ri 0 2

# Read 8 discrete inputs
python mod.py rd 0 8
```

**Write Registers:**
```bash
# Write value 1234 to register 0
python mod.py wr 0 1234

# Write value 500 to register 1
python mod.py wr 1 500
```

**Advanced Usage with Unit ID:**
```bash
# Control device with slave ID 2
python mod.py wc 0 1 2

# Read from device with slave ID 3
python mod.py rc 0 8 3
```

**Get Help:**
```bash
python mod.py --help
```

**Example Output:**
```bash
$ python mod.py wc 0 1
2025-07-30 16:00:15,123 - INFO - Initializing Modbus RTU client on /dev/ttyACM0
2025-07-30 16:00:15,124 - INFO - Configuration loaded from .env: port=/dev/ttyACM0, baudrate=9600, timeout=1.0
Coil 0 set to ON

$ python mod.py rc 0 8
Coils [0-7]: [True, False, False, False, False, False, False, False]
```

**Automation Examples:**
```bash
# Simple automation script
#!/bin/bash
echo "Turning on outputs 0, 2, 4..."
python mod.py wc 0 1
python mod.py wc 2 1  
python mod.py wc 4 1

sleep 5

echo "Turning off all outputs..."
for i in {0..7}; do
    python mod.py wc $i 0
done

echo "Final status:"
python mod.py rc 0 8
```

#### Programmatic Usage (Non-Interactive)

You can import and use `mod.py` as a library in your own Python scripts:

```python
from mod import ModbusRTUClient, auto_detect_modbus_port

# Option 1: Use auto-detection
port = auto_detect_modbus_port()
if port:
    modbus = ModbusRTUClient(port=port)
else:
    modbus = ModbusRTUClient()  # Uses .env configuration

# Option 2: Manual configuration
modbus = ModbusRTUClient(
    port='/dev/ttyACM0',
    baudrate=9600,
    parity='N',
    timeout=1.0
)

# Connect and perform operations
if modbus.connect():
    # Read 8 coils from address 0
    coils = modbus.read_coils(0, 8, unit=1)
    print(f"Coils: {coils}")
    
    # Write coil at address 0
    success = modbus.write_coil(0, True, unit=1)
    print(f"Write successful: {success}")
    
    # Read holding registers
    registers = modbus.read_holding_registers(0, 4, unit=1)
    print(f"Registers: {registers}")
    
    # Write register
    success = modbus.write_register(1, 1234, unit=1)
    print(f"Register write successful: {success}")
    
    modbus.disconnect()
else:
    print("Failed to connect to Modbus device")
```

#### Complete Example Script

Create a file `my_modbus_script.py`:

```python
#!/usr/bin/env python3
"""
Example script showing how to use mod.py as a library
"""

from mod import ModbusRTUClient, auto_detect_modbus_port
import time

def main():
    print("=== Custom Modbus Script ===")
    
    # Auto-detect Modbus device
    print("Detecting Modbus device...")
    port = auto_detect_modbus_port()
    
    if not port:
        print("No Modbus device found!")
        return
    
    print(f"Found Modbus device on: {port}")
    
    # Create client
    modbus = ModbusRTUClient(port=port)
    
    if not modbus.connect():
        print("Failed to connect!")
        return
    
    try:
        # Read current state of all 8 outputs
        print("\n--- Reading current output states ---")
        coils = modbus.read_coils(0, 8, unit=1)
        if coils:
            for i, state in enumerate(coils):
                print(f"Output {i}: {'ON' if state else 'OFF'}")
        
        # Turn on outputs 0, 2, 4 (every other one)
        print("\n--- Setting outputs 0, 2, 4 to ON ---")
        for output in [0, 2, 4]:
            success = modbus.write_coil(output, True, unit=1)
            print(f"Output {output}: {'✓' if success else '✗'}")
            time.sleep(0.1)  # Small delay between commands
        
        # Wait 2 seconds
        print("\nWaiting 2 seconds...")
        time.sleep(2)
        
        # Turn off all outputs
        print("\n--- Turning off all outputs ---")
        for output in range(8):
            success = modbus.write_coil(output, False, unit=1)
            print(f"Output {output}: {'✓' if success else '✗'}")
            time.sleep(0.1)
        
        # Read final state
        print("\n--- Final output states ---")
        coils = modbus.read_coils(0, 8, unit=1)
        if coils:
            for i, state in enumerate(coils):
                print(f"Output {i}: {'ON' if state else 'OFF'}")
    
    except KeyboardInterrupt:
        print("\nScript interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        modbus.disconnect()
        print("\nDisconnected from Modbus device")

if __name__ == "__main__":
    main()
```

Run your custom script:
```bash
python my_modbus_script.py
```

#### Available Methods

**Connection:**
- `connect()` - Connect to device
- `disconnect()` - Disconnect from device

**Read Operations:**
- `read_coils(address, count, unit=1)` - Read coils (outputs)
- `read_discrete_inputs(address, count, unit=1)` - Read discrete inputs
- `read_holding_registers(address, count, unit=1)` - Read holding registers
- `read_input_registers(address, count, unit=1)` - Read input registers

**Write Operations:**
- `write_coil(address, value, unit=1)` - Write single coil
- `write_register(address, value, unit=1)` - Write single register
- `write_coils(address, values, unit=1)` - Write multiple coils
- `write_registers(address, values, unit=1)` - Write multiple registers

**Utility Functions:**
- `auto_detect_modbus_port()` - Auto-detect Modbus device port
- `find_serial_ports()` - List all available serial ports
- `test_modbus_port(port, baudrate)` - Test if port has Modbus device

### Starting the Service

```bash
./start.sh
```

This will:
- Install/update Python dependencies
- Start the FastAPI backend on http://localhost:8090
- Create log and PID files for monitoring

### Stopping the Service

```bash
./stop.sh
```

### Web Interface

1. Configure your web server to serve the PHP file:
   ```apache
   # Apache virtual host example
   <VirtualHost *:80>
       DocumentRoot /path/to/modbus/
       <Directory /path/to/modbus/>
           AllowOverride All
           Require all granted
       </Directory>
   </VirtualHost>
   ```

2. Access the interface:
   ```
   http://your-server/modbus.php.svg
   ```

### API Endpoints

- **GET /status** - Get current input/output status
- **POST /control** - Control individual output channel
- **POST /control/all** - Control all outputs at once
- **GET /device/info** - Get device information
- **GET /docs** - Interactive API documentation

### API Examples

```bash
# Get status
curl http://localhost:8090/status

# Turn on output channel 0
curl -X POST http://localhost:8090/control \
  -H "Content-Type: application/json" \
  -d '{"channel": 0, "action": "on"}'

# Toggle output channel 1
curl -X POST http://localhost:8090/control \
  -H "Content-Type: application/json" \
  -d '{"channel": 1, "action": "toggle"}'

# Turn off all outputs
curl -X POST http://localhost:8090/control/all \
  -H "Content-Type: application/json" \
  -d 'false'
```

## Configuration

### Modbus Settings

Edit `api.py` to change device settings:

```python
MODBUS_DEVICE_ADDRESS = 0x01  # Device address (1-255)
MODBUS_BAUDRATE = 9600        # Baud rate
MODBUS_PORT = '/dev/ttyUSB0'  # USB-to-RS485 port
```

### Web Interface

Edit `modbus.php.svg` to change API endpoint:

```php
$API_BASE_URL = 'http://localhost:8090';
```

## Troubleshooting

### Connection Issues

1. **Check USB device:**
   ```bash
   ls -la /dev/ttyUSB*
   dmesg | grep tty
   ```

2. **Check permissions:**
   ```bash
   sudo usermod -a -G dialout $USER
   # Logout and login again
   ```

3. **Test Modbus communication:**
   ```bash
   # Install modbus tools
   sudo apt-get install mbpoll
   
   # Test reading inputs
   mbpoll -a 1 -b 9600 -t 1 -r 1 -c 8 /dev/ttyUSB0
   ```

### Service Issues

1. **Check logs:**
   ```bash
   tail -f modbus.log
   ```

2. **Check if service is running:**
   ```bash
   ps aux | grep api.py
   ```

3. **Manual start for debugging:**
   ```bash
   python api.py
   ```

### Web Interface Issues

1. **Check PHP errors:**
   ```bash
   tail -f /var/log/apache2/error.log
   ```

2. **Test API connectivity:**
   ```bash
   curl http://localhost:8090/status
   ```

## File Structure

```
modbus/
├── modbus.php.svg     # PHP SVG web interface
├── api.py             # FastAPI backend service
├── start.sh           # Service start script
├── stop.sh            # Service stop script
├── requirements.txt   # Python dependencies
└── README.md          # This documentation
```

## Related Documentation

### Main Project
- **[Project README](../README.md)** - Main project documentation and overview
- **[PHP Client Documentation](../php-client/README.md)** - PHP+SVG applications guide
- **[SVG Applications Guide](../php-client/svg/README.md)** - Detailed SVG+PHP documentation
- **[Test Suite Documentation](../php-client/svg/tests/README.md)** - Comprehensive testing framework

### System Components
- **[Python FastAPI Server](../python-server/)** - Backend API documentation
- **[Docker Configuration](../docker-compose.yml)** - Container orchestration
- **[Environment Variables](../.env)** - System configuration

### Tools and Utilities
- **[PHP+SVG Validator](../php-client/svg/validator.php)** - Code validation tool
- **[Test Runner](../php-client/svg/tests/run_tests.php)** - Automated testing

## Integration with Main Project

This Modbus component can be integrated with the main microservices architecture:

1. **MQTT Integration**: Modbus events can be published to MQTT broker
2. **REST API**: Modbus control through unified FastAPI backend
3. **SVG Interface**: Modbus controls in PHP+SVG applications
4. **Docker Deployment**: Containerized alongside other services

### Example Integration

```python
# In python-server/main.py - add Modbus endpoints
@app.get("/api/modbus/status")
async def get_modbus_status():
    # Modbus RTU communication
    return {"inputs": inputs, "outputs": outputs}

@app.post("/api/modbus/output/{channel}")
async def set_modbus_output(channel: int, state: bool):
    # Set output and publish to MQTT
    if mqtt_client:
        mqtt_client.publish(f"modbus/output/{channel}", str(state))
    return {"channel": channel, "state": state}
```

---

**Status**: ✅ Functional | **Integration**: Available for main project  
**Last Update**: 2025-07-30

For complete system setup and integration, see **[main project documentation](../README.md)**.
