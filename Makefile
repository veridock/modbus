.PHONY: install dev-install test lint clean build publish run-rest run-mqtt run-cli help

# Default target
help:
	@echo "ModbusAPI Makefile"
	@echo ""
	@echo "Dostępne komendy:"
	@echo "  make install       - Instalacja paczki modbusapi"
	@echo "  make dev-install   - Instalacja paczki w trybie developerskim"
	@echo "  make test          - Uruchomienie testów jednostkowych"
	@echo "  make lint          - Sprawdzenie kodu pod kątem błędów stylistycznych"
	@echo "  make clean         - Usunięcie plików tymczasowych i artefaktów"
	@echo "  make build         - Zbudowanie paczki do dystrybucji"
	@echo "  make publish       - Publikacja paczki w PyPI"
	@echo "  make run-rest      - Uruchomienie serwera REST API"
	@echo "  make run-mqtt      - Uruchomienie serwera MQTT"
	@echo "  make run-cli       - Uruchomienie interfejsu CLI"
	@echo "  make integration-test - Uruchomienie testów integracyjnych"

# Instalacja paczki
install:
	pip install -e .

# Instalacja paczki w trybie developerskim
dev-install:
	pip install -e ".[dev]"

# Uruchomienie testów jednostkowych
test:
	pytest modbusapi/tests/

# Sprawdzenie kodu pod kątem błędów stylistycznych
lint:
	flake8 modbusapi/
	pylint modbusapi/

# Usunięcie plików tymczasowych i artefaktów
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.pyd" -delete
	find . -name ".pytest_cache" -type d -exec rm -rf {} +
	find . -name ".coverage" -delete
	find . -name "htmlcov" -type d -exec rm -rf {} +

# Zbudowanie paczki do dystrybucji
build: clean
	python setup.py sdist bdist_wheel

# Publikacja paczki w PyPI
publish: build
	twine upload dist/*

# Uruchomienie serwera REST API
run-rest:
	python -m modbusapi rest

# Uruchomienie serwera MQTT
run-mqtt:
	python -m modbusapi mqtt

# Uruchomienie interfejsu CLI
run-cli:
	python -m modbusapi shell

# Testy integracyjne
integration-test:
	@echo "Uruchamianie testów integracyjnych REST API..."
	@echo "Test 1: Sprawdzanie statusu API"
	curl -s http://localhost:5000/status | grep "ok" || echo "Test 1 failed"
	@echo "Test 2: Odczyt stanu cewki 0"
	curl -s http://localhost:5000/coil/0 | grep -E "true|false" || echo "Test 2 failed"
	@echo "Test 3: Przełączenie cewki 0"
	curl -s -X POST http://localhost:5000/toggle/0 | grep "success" || echo "Test 3 failed"
	@echo "Test 4: Skanowanie urządzeń"
	curl -s http://localhost:5000/scan | grep "devices" || echo "Test 4 failed"
	@echo "Testy integracyjne zakończone"
