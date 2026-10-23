# ?? Python Automation & API Suite

[![CI Workflow](https://github.com/peacefulcoder-911/python-automation-suite/actions/workflows/ci.yml/badge.svg)](https://github.com/peacefulcoder-911/python-automation-suite/actions)
![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688)
![License](https://img.shields.io/badge/license-MIT-green)

A modular, production-ready Python automation framework and REST API control plane. Designed for high reliability, concurrent endpoint monitoring, asynchronous workflows, and cloud-native execution.

---

## ?? Key Features

* **? Async API Client (`src/client.py`)**: Built on `httpx` with automatic exponential backoff retries, configurable timeouts, and telemetry.
* **?? Endpoint Diagnostics & Health Checks (`src/automation.py`)**: Concurrent ping and latency measurement with formatted Rich terminal tables.
* **?? REST API Control Plane (`src/api.py`)**: FastAPI application exposing endpoints to trigger workflows, run diagnostics, and inspect health (`/docs` interactive Swagger).
* **??? Rich CLI (`main.py`)**: Terminal dashboard for immediate diagnostics or launching the API service.
* **?? Layered Configuration (`config/config.yaml`)**: Type-safe settings via Pydantic v2 and YAML fallback.
* **?? Cloud CI/CD Pipeline (`.github/workflows/ci.yml`)**: Multi-version automated testing on GitHub Actions across Python 3.10, 3.11, and 3.12.

---

## ?? Repository Layout

```text
python-automation-suite/
??? .github/
?   ??? workflows/
?       ??? ci.yml             # GitHub Actions CI workflow
??? config/
?   ??? config.yaml            # Environment and scheduler configuration
??? src/
?   ??? __init__.py
?   ??? api.py                 # FastAPI web service
?   ??? automation.py          # Concurrent diagnostics and automation engine
?   ??? client.py              # Robust HTTPX async client with retries
?   ??? config.py              # Pydantic v2 settings schema
??? tests/
?   ??? __init__.py
?   ??? test_automation.py     # Pytest unit and integration tests
??? .gitignore                 # Python git ignore rules
??? main.py                    # Unified CLI entrypoint
??? README.md                  # Project documentation
??? requirements.txt           # Production dependencies
```

---

## ?? Quick Start

### 1. Clone & Set Up Virtual Environment
```bash
git clone https://github.com/peacefulcoder-911/python-automation-suite.git
cd python-automation-suite

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Diagnostics CLI
```bash
python main.py run
```

### 3. Start the FastAPI Control Server
```bash
python main.py server
```
* **Interactive API Documentation:** Open `http://localhost:8000/docs` in your browser.
* **Health Check API:** `GET http://localhost:8000/health`
* **Trigger Workflow:** `POST http://localhost:8000/trigger/health-checks`

### 4. Run Test Suite
```bash
pytest -v
```

---

## ??? Configuration

Edit `config/config.yaml` to customize target endpoints, port, or alert webhooks:

```yaml
app:
  name: "Python Automation Suite"
  version: "1.0.0"
  environment: "development"

api:
  host: "0.0.0.0"
  port: 8000

automation:
  schedule_interval_minutes: 15
  health_check_urls:
    - name: "GitHub API Status"
      url: "https://api.github.com"
      timeout_seconds: 5
```

---

## ?? License
Distributed under the MIT License.