# GlassBox Prompt Optimizer v2.0

## Quick Start

```bash
# 1. Set your Boeing PAT (required)
setx BCAI_PAT_B64 "your_base64_encoded_token"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
streamlit run glassbox/app.py
```

## Requirements

Create `requirements.txt`:
```
streamlit>=1.30.0
plotly>=5.18.0
requests>=2.31.0
chromadb>=0.4.22
graphviz>=0.20.1
python-pptx>=0.6.21
PyMuPDF>=1.23.0
```
