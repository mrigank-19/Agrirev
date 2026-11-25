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

## WhatsApp (Twilio sandbox)

1. Create a free account at [twilio.com](https://www.twilio.com/try-twilio) and open the WhatsApp sandbox under Messaging → Try it out.
2. From your own WhatsApp, send the sandbox's `join <code>` message to its number to connect.
3. Expose your local server (e.g. `ngrok http 8000`) and set the sandbox's "When a message comes in" webhook to `https://<your-ngrok-domain>/webhook`.
4. Message the sandbox number to run through the district → land size → last crop flow and get a recommendation back.

## Demo prep

Run the canned, known-good scenarios offline (no WiFi/WhatsApp dependency) to rehearse or sanity-check:

```powershell
python scripts/demo_scenarios.py
```

This prints the formatted reply for three districts (Maharashtra, Punjab, West Bengal) that are confirmed to produce clean, varied output — use these during judging instead of live, unpredictable input.

**Screen-capture backup:** once your Twilio sandbox is connected (see above), record a short screen capture of the WhatsApp conversation for one or two of the scenarios above, in case live demo WiFi fails. This step needs your own connected sandbox and hasn't been recorded yet.
