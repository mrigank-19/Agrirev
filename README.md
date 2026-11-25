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

Run the API:

```powershell
uvicorn backend.main:app --reload
```

## WhatsApp (Twilio sandbox)

1. Create a free account at [twilio.com](https://www.twilio.com/try-twilio) and open the WhatsApp sandbox under Messaging → Try it out.
2. From your own WhatsApp, send the sandbox's `join <code>` message to its number to connect.
3. Expose your local server (e.g. `ngrok http 8000`) and set the sandbox's "When a message comes in" webhook to `https://<your-ngrok-domain>/webhook`.
4. Message the sandbox number to run through the district → land size → last crop flow and get a recommendation back.

(Optional) Set `AGMARKNET_API_KEY` as an environment variable to enable live local mandi prices; without it, the bot still replies, just without a price figure.
