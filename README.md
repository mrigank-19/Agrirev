# AgriExport Advisor

A WhatsApp-first crop recommendation agent that ranks agronomically-viable crops by export demand.

**One sentence:** A farmer messages their location, land size, and last season's crop on WhatsApp, and gets back a ranked list of crops that are (a) agronomically viable on their land right now and (b) seeing rising export demand — with a plain-language explanation and a local-market reality check, delivered entirely inside the conversation.

**Why WhatsApp, not an app:** rural adoption dies at the app-install step. WhatsApp is a channel farmers already use daily — no install, no onboarding screen, no app-store listing, just a phone number to message.

## Status

All 6 build stages complete — demo-ready.

## How a farmer actually adopts this

A farmer doesn't need to discover this on their own: the distribution path runs through people and institutions they already trust. The WhatsApp number gets shared through Common Service Centres (CSCs), Krishi Vigyan Kendras (KVKs), and local Farmer Producer Organizations (FPOs) — the same channels that already run government agri-advisory outreach — so a farmer hears about it from a local extension worker or FPO meeting, not an ad. From there, there's nothing to install: they message the number like they'd message a relative, answer three short questions, and get a reply in the same chat. That's the entire onboarding funnel.

## System architecture

```
Farmer (WhatsApp)
        |
        v
WhatsApp Business API webhook --> FastAPI backend
        |
        +--------------------+--------------------+
        v                    v                     v
 Suitability Engine   Export-Ranking Layer   Local Price Check
 (trained ML model)  (static dataset lookup)  (Agmarknet API)
        |                    |                     |
        +--------------------+---------------------+
                             v
                  Recommendation Composer
              (ranks + explains + flags risk)
                             |
                             v
                Reply sent back via WhatsApp
```

## Project layout

```
/data              raw + processed datasets
/model             training script output + saved model file
/backend           FastAPI app
/backend/routes    webhook + recommend + health endpoints
/backend/services  suitability, export-ranking, price-check, composer modules
/scripts           data prep, training, and demo-rehearsal scripts
```

## Data sources

| Data need | Source | Notes |
|---|---|---|
| Soil NPK / climate → crop suitability | Kaggle crop-recommendation dataset | Trained once, shipped as `model/suitability_model.pkl` |
| Agri export value/growth by commodity | APEDA AgriXchange (DGCIS-sourced) | Pre-downloaded, static — `data/apeda_export_raw.csv` / `data/export_rankings.csv` |
| Local mandi prices | Agmarknet via data.gov.in | Live API call, cached, graceful fallback if no key/unavailable |
| District-level soil defaults | Static lookup table | `backend/services/soil_defaults.py`, state-level for the MVP |

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the API:

```powershell
uvicorn backend.main:app --reload
```

(Optional) Set `AGMARKNET_API_KEY` as an environment variable to enable live local mandi prices; without it, the bot still replies, just without a price figure.

## WhatsApp (webhook built and tested, not live-wired for this demo)

`backend/routes/webhook.py` implements the full Twilio-format sandbox webhook — the district → land size → last crop conversational flow, session state, and plain-language reply are all built and verified (see `scripts/demo_scenarios.py` and the test transcript below). It is not wired to a live WhatsApp number for this submission: Twilio changed its trial-account policy so that any custom webhook, WhatsApp sender, or the Conversations API now requires a paid upgrade — confirmed directly against the API (`Messages`, `Conversations`, and WhatsApp sender registration all return trial-restriction errors). Free alternatives (Meta Cloud API, Gupshup) exist but need significantly more setup than hackathon time allows here.

To wire it up yourself once you have a paid Twilio account or a Meta Cloud API app:
1. Point the provider's incoming-message webhook at `https://<your-public-url>/webhook`.
2. If using Meta instead of Twilio, adjust the form-parsing in `whatsapp_webhook()` to Meta's JSON payload shape.

## Demo prep

Run the canned, known-good scenarios (no WiFi/WhatsApp dependency) to show the bot's actual conversational output during judging:

```powershell
python scripts/demo_scenarios.py
```

This prints the formatted reply for three districts (Maharashtra, Punjab, West Bengal) that are confirmed to produce clean, varied output.

You can also demonstrate the webhook logic itself is real and working by simulating a Twilio-format conversation locally:

```powershell
curl -X POST http://127.0.0.1:8000/webhook --data-urlencode "From=whatsapp:+91XXXXXXXXXX" --data-urlencode "Body=hi"
curl -X POST http://127.0.0.1:8000/webhook --data-urlencode "From=whatsapp:+91XXXXXXXXXX" --data-urlencode "Body=Nashik, Maharashtra"
curl -X POST http://127.0.0.1:8000/webhook --data-urlencode "From=whatsapp:+91XXXXXXXXXX" --data-urlencode "Body=5"
curl -X POST http://127.0.0.1:8000/webhook --data-urlencode "From=whatsapp:+91XXXXXXXXXX" --data-urlencode "Body=skip"
```

Each call returns real TwiML with the next prompt, ending in a full formatted recommendation — this is the actual code path a connected WhatsApp number would run, just driven by curl instead of a live sandbox.
