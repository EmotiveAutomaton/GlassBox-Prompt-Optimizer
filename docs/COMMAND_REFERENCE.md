# GlassBox Prompt Optimizer — Command Reference Guide

> **Version:** 2.0  
> **Last Updated:** 2026-01-19

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Environment Setup](#environment-setup)
3. [Running the Application](#running-the-application)
4. [CLI Commands](#cli-commands)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

```bash
# 1. Navigate to project directory
cd "e:\Work\Boeing\GlassBox Prompt Optimizer"

# 2. Create virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set Boeing API credentials
setx BCAI_PAT_B64 "your_base64_encoded_token_here"

# 5. Run the application
streamlit run glassbox/app.py
```

---

## Environment Setup

### Required Environment Variables

| Variable | Description | How to Set |
|----------|-------------|------------|
| `BCAI_PAT_B64` | Boeing AI Gateway Personal Access Token (Base64) | `setx BCAI_PAT_B64 "token"` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BCAI_BASE_URL` | Boeing API base URL | `https://bcai-test.web.boeing.com` |
| `BCAI_CA_BUNDLE` | Path to custom CA certificate bundle | System default |

### Encoding Your PAT

If you have a raw PAT, encode it to Base64:

```python
import base64
token = "your_raw_pat_here"
encoded = base64.b64encode(token.encode()).decode()
print(encoded)  # Use this value for BCAI_PAT_B64
```

---

## Running the Application

### Standard Run

```bash
streamlit run glassbox/app.py
```

The application will open at `http://localhost:8501`

### Custom Port

```bash
streamlit run glassbox/app.py --server.port 8080
```

### Headless (No Browser Auto-Open)

```bash
streamlit run glassbox/app.py --server.headless true
```

### Production Mode

```bash
streamlit run glassbox/app.py --server.headless true --server.enableCORS false
```

---

## CLI Commands

### Dependency Management

```bash
# Install all dependencies
pip install -r requirements.txt

# Check for outdated packages
pip list --outdated

# Update a specific package
pip install --upgrade streamlit
```

### Theme Configuration

The dark theme is pre-configured in `glassbox/config/config.toml`. To use it:

```bash
# Copy theme to Streamlit config directory
mkdir -p ~/.streamlit
cp glassbox/config/config.toml ~/.streamlit/config.toml
```

### Running Tests (Future)

```bash
# Run all tests
pytest glassbox/tests/ -v

# Run specific test file
pytest glassbox/tests/test_opro_engine.py -v

# Run with coverage
pytest glassbox/tests/ --cov=glassbox --cov-report=html
```

---

## Configuration

### config.toml Options

Located at `glassbox/config/config.toml`:

```toml
[theme]
primaryColor = "#20C20E"      # Boeing Console Green
backgroundColor = "#0E1117"   # Deep Gray/Black
secondaryBackgroundColor = "#31333F"
textColor = "#FAFAFA"
font = "monospace"
```

### Engine-Specific Configuration

Each engine can be configured via the sidebar at runtime:

| Engine | Key Parameters |
|--------|----------------|
| OPro | Temperature, Generations per Step, Stop Threshold |
| APE | Input-Output Examples (set via Test Bench) |
| Promptbreeder | Population Size (default: 8), Mutation Operators |
| S2A | Noise Level, Top-K Retrieval |

---

## Troubleshooting

### Common Errors

#### 401 Unauthorized

```
Error: Unauthorized - Check PAT format
```

**Solution:** Verify your `BCAI_PAT_B64` is:
- Properly Base64 encoded
- Has no whitespace
- Is set in your current terminal session

```bash
# Check if variable is set
echo %BCAI_PAT_B64%

# Re-set if needed
setx BCAI_PAT_B64 "your_token"
# Restart terminal for changes to take effect
```

#### 403 Forbidden

```
Error: Access Denied - Check network access/VPN
```

**Solution:** 
- Ensure you're connected to Boeing VPN
- Verify your PAT has required permissions

#### SSL Certificate Error

```
Error: SSL Error - Check CA bundle path
```

**Solution:**
```bash
# Set custom CA bundle path
setx BCAI_CA_BUNDLE "C:\path\to\boeing-ca-bundle.crt"
```

#### Streamlit Import Errors

```
ModuleNotFoundError: No module named 'glassbox'
```

**Solution:** Run from project root:
```bash
cd "e:\Work\Boeing\GlassBox Prompt Optimizer"
streamlit run glassbox/app.py
```

Or add to Python path:
```bash
set PYTHONPATH=%PYTHONPATH%;e:\Work\Boeing\GlassBox Prompt Optimizer
```

### Getting Help

- Check `docs/living_specs.md` for detailed feature specifications
- Review `docs/Original_Boeing_Requirements.md` for API compliance details
- File issues in the project repository

---

## File Structure

```
GlassBox Prompt Optimizer/
├── glassbox/
│   ├── app.py              # Main entry point
│   ├── config/             # Theme and settings
│   ├── core/               # Engines, API, Evaluator
│   ├── models/             # Data models
│   ├── prompts/            # Meta-prompt templates
│   ├── rag/                # RAG simulator (future)
│   ├── ui/                 # Streamlit UI zones
│   └── utils/              # Utilities
├── docs/                   # Documentation
├── requirements.txt        # Dependencies
└── README.md              # Quick start guide
```

---

## Quick Reference Card

| Action | Command |
|--------|---------|
| **Start App** | `streamlit run glassbox/app.py` |
| **Set PAT** | `setx BCAI_PAT_B64 "token"` |
| **Install Deps** | `pip install -r requirements.txt` |
| **Custom Port** | `streamlit run glassbox/app.py --server.port 8080` |
| **Check Health** | Open app, check "Status" indicator |
