# AgriExport Advisor

A WhatsApp-first crop recommendation agent that ranks agronomically-viable crops by export demand. A farmer messages their location, land size, and last season's crop, and gets back a ranked list of crops that are viable on their land right now and seeing rising export demand — with a plain-language explanation and a local-market reality check, delivered entirely inside a WhatsApp conversation.

## Status

Stage 0 — repo scaffold. See the build spec for the full staged plan.

## Project layout

```
/data              raw + processed datasets
/model             training script output + saved model file
/backend           FastAPI app
/backend/routes    webhook + health endpoints
/backend/services  suitability, export-ranking, price-check, composer modules
/scripts           one-off data prep scripts
```

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
