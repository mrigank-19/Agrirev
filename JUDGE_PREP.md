# AgriExport Advisor — Judge Prep

Everything you might be asked, with the honest answer. Read this once before presenting.

---

## 1. Problem statement (short version)

Farmers choose crops by habit, with no way to check if that crop suits their land's soil/climate or whether its export demand is rising — missing out on better income.

## 2. One-sentence pitch

A WhatsApp bot where a farmer messages their district, land size, and last crop, and gets back a ranked list of crops that are agronomically viable on their land *and* seeing rising export demand — with a plain-language reason, a revenue estimate, and a local-market reality check.

## 3. Why WhatsApp

Rural adoption dies at the app-install step. WhatsApp is a channel farmers already use daily — no install, no onboarding screen, just a phone number to message.

## 4. How a farmer actually finds out about this (adoption path)

Distribution runs through institutions farmers already trust: Common Service Centres (CSCs), Krishi Vigyan Kendras (KVKs), and local Farmer Producer Organizations (FPOs) — the same channels that already run government agri-advisory outreach. A farmer hears about the number from a local extension worker or FPO meeting, not an ad.

---

## 5. System architecture

```
Farmer (WhatsApp)
        |
        v
WhatsApp webhook --> FastAPI backend
        |
        +---------+---------+---------+
        v         v         v         v
  Suitability  Export    Price     Rotation/
  (ML model)   Ranking   Check     Weather
        |         |         |         |
        +---------+---------+---------+
                  v
         Recommendation Composer
      (ranks, explains, flags risk,
         estimates revenue)
                  |
                  v
          Reply via WhatsApp
```

Each box is effectively its own "agent" with one job — pull a specific kind of data and analyze it — coordinated by the Composer. See §13 for how to frame this if asked about "AI agents."

---

## 6. What's real data vs. approximation (the most important section — know this cold)

| Component | Status | Source |
|---|---|---|
| **Crop suitability model** | Real, trained | Kaggle Crop Recommendation Dataset, 2200 rows, 22 crops, Random Forest, **99.55% test accuracy** |
| **Export value & growth** | Real government data | APEDA AgriXchange (DGCIS-sourced), FY2023-24 to FY2025-26, 44 product lines |
| **Export → crop matching** | Real but partial | Only **6 of 44** APEDA lines map to the model's 22 crops (rice ×2, maize, grapes, mango ×2) — APEDA reports pulses/cereals as aggregates, not split by variety |
| **Export-implied price per quintal** | Real data, approximate conversion | export value ÷ export quantity from APEDA, converted at an **indicative** USD→INR rate (83.5, not a live FX feed) |
| **District rainfall** | Real, (near) full coverage | Ministry of Earth Sciences, "District Rainfall Normal 1951-2000" (data.gov.in) — **640 of ~766 districts** |
| **Soil N/P/K, temperature, humidity, pH** | **Static approximation, NOT real per-district data** | Hand-set for 12 major states + one national fallback — a known, declared MVP simplification |
| **Live weather (optional)** | Real if enabled | OpenWeatherMap free tier — only active if `OPENWEATHERMAP_API_KEY` is set; otherwise falls back to the static numbers above |
| **Local mandi price** | Real if entered/configured | FPO-reported via `/fpo` dashboard (checked first) → Agmarknet via data.gov.in (needs `AGMARKNET_API_KEY`) → "not available" |
| **Crop rotation soil effect** | Agronomic rule, not measured | Legume / heavy-feeder / melon-vine / perennial-fruit categories adjust N/P/K — real agronomic principle (nitrogen fixation vs. depletion), applied as a fixed estimate, not soil-tested |
| **Typical crop yield** | Published averages, not measured | `backend/services/crop_yield.py` — national average yields, not this farmer's actual field |
| **Revenue projection** | Computed, never fabricated | acres × yield × price, using export price first, local price as fallback; shows nothing rather than guessing when data's missing |

**The one sentence to say if a judge asks "is this all real data?":** *"Rainfall, export stats, and the ML model are real government/public data. Soil nutrients and typical yields are informed approximations because true per-field data doesn't exist at this scale — we built the system to be upgraded with real data when available, and we say so explicitly in the code and README rather than hiding it."*

---

## 7. Key numbers to have ready

- **99.55%** — suitability model test accuracy
- **22** — crop labels the model predicts
- **2,200** — training rows (Kaggle dataset)
- **640** — districts with real rainfall data (out of ~766 total in India)
- **44** — APEDA export product lines processed; **6** map to model crops
- **12** — states with hand-set soil defaults (+ 1 national fallback)
- **4** — district names that exist in more than one state (disambiguated by checking if the state name is also mentioned)

---

## 8. What's NOT working / known gaps (say this before they ask)

1. **WhatsApp is not live-connected.** The webhook, conversation flow, and reply formatting are fully built and tested (via `/chat` and curl), but Twilio changed its trial-account policy — custom webhooks, WhatsApp sender registration, and the Conversations API all require a paid upgrade now. **We verified this directly against Twilio's API** (not just assumed): `Messages.json` came back empty, the Conversations API returned `"not available on a Trial account"`, and the WhatsApp senders page says `"Upgrade to set up a WhatsApp sender."` We chose not to pay for a hackathon demo and built/tested the identical logic offline instead.
2. **Soil N/P/K, temperature, humidity, pH are state-level, not per-district.** Declared clearly in the README and code comments.
3. **No authentication on the FPO dashboard (`/fpo`).** Anyone with the URL can submit a price. Fine for a demo with known users; would need access control for real deployment.
4. **Export price is a single national average**, not adjusted for quality grade, specific buyer, or region.
5. **Revenue estimates ignore risk** — weather failure, pest loss, price volatility, input costs are not modeled. It's a projection, not a guarantee.
6. **Crop rotation / yield tables cover ~30 named crops** (the model's 22 + ~10 common Indian crops like onion, wheat, sugarcane). An unrecognized `last_crop` or revenue request for an uncovered crop is silently skipped, not estimated.
7. **Location matching is simple substring text-matching** on district/state names — not a geocoding service. Works well for clear inputs ("Nashik, Maharashtra"), could mismatch on ambiguous free text.

---

## 9. Anticipated questions & answers

**Q: Why does it only recommend from 22 crops?**
A: That's the full label set of the Kaggle crop-suitability dataset we trained on. Expanding it means retraining on a larger labeled dataset — a real next step, not done here due to time.

**Q: Why do only 6 crops show export data?**
A: APEDA's own public reporting groups many crops into aggregates (e.g. "pulses" isn't split into lentil/chickpea/kidneybeans). We only mapped where the match was agronomically honest, not forced.

**Q: Is the revenue number guaranteed/accurate?**
A: No — it's acres × a published average yield × a known price (export-market price preferred, local price as fallback). It's a directional estimate to help a farmer compare options, not a quoted contract price.

**Q: Does it use AI/LLM agents?**
A: The build uses one trained ML model (Random Forest) plus deterministic rule-based logic across several specialized components (suitability, export ranking, price check, rotation, revenue) coordinated by a composer — a legitimate multi-agent-style pipeline, but no LLM is called at runtime. Claude (Anthropic) was used as the development tool to build the system, not as a live component of it.

**Q: Why WhatsApp if it's not actually connected?**
A: The entire conversational logic (the webhook, the Q&A flow, the reply formatting) is built and fully tested — we can demo the exact same code path via a browser-based chat tester (`/chat`). Only the final wire to a live phone number is blocked by Twilio's current trial policy, which we verified rather than guessed at.

**Q: What happens if the farmer's district isn't recognized?**
A: Falls back gracefully to a generic national soil/climate average, and the reply explicitly tells the farmer this (`data_coverage_note`) rather than silently guessing with false confidence.

**Q: What stops this from just recommending one crop?**
A: A hard-coded diversification guardrail — recommendations are always split (50/30/20, 60/40, or 70%), never 100% into one crop.

**Q: What if a crop has great export growth but no local buyer?**
A: Flagged explicitly with a ⚠️ warning telling the farmer to check with their local APMC/FPO before committing significant land — we never silently recommend an export crop with no confirmed way to sell it locally.

**Q: Where's data stored?**
A: Flat JSON files in the repo (`data/manual_mandi_prices.json` for FPO prices) — fine for hackathon scale, would need a real database for concurrent production use.

---

## 10. Tech stack

- **Backend:** FastAPI, Python
- **ML:** scikit-learn (Random Forest), pandas
- **WhatsApp (built, not live):** Twilio SDK, TwiML
- **External APIs (optional):** OpenWeatherMap, Agmarknet (data.gov.in)
- **Hosting:** local during dev; code at [github.com/mrigank-19/Agrirev](https://github.com/mrigank-19/Agrirev)

## 11. How to run it live in front of judges

| Page | URL | Shows |
|---|---|---|
| WhatsApp chat tester | `http://127.0.0.1:8000/chat` | Full Q&A conversation, exactly like real WhatsApp |
| FPO price dashboard | `http://127.0.0.1:8000/fpo` | Submit/view local mandi prices |
| API docs | `http://127.0.0.1:8000/docs` | Try `/recommend` directly, see raw JSON |

Also runnable without a server: `python scripts/demo_scenarios.py` prints 3 pre-set conversations (Maharashtra, Punjab, West Bengal) — useful if live demo WiFi/setup fails. A backup screen-recording also exists (`agriexport-whatsapp-demo.gif`, sent to you earlier).

## 12. Build history (if asked "how was this organized")

One git commit per build stage, in order — a clean, reviewable history: repo scaffold → trained model → export dataset → working API → WhatsApp flow → guardrails/explainability → demo prep → (post-demo improvements: real district rainfall, crop rotation, live weather, FPO dashboard, export-based revenue). All on GitHub.

## 13. If judging criteria specifically require "AI agents"

Frame the existing pipeline honestly as a multi-agent system by role, not by LLM-calling:

| "Agent" | Pulls | Analyzes |
|---|---|---|
| Suitability Agent | Soil/climate inputs | Ranks viable crops via the trained model |
| Export Market Agent | APEDA export dataset | Ranks by export growth/value |
| Price Agent | FPO/Agmarknet prices | Confirms local market access |
| Rotation Agent | Last crop grown | Adjusts soil state for what it leaves behind |
| Revenue Agent | Yield + price data | Projects and compares earnings |
| Composer | All of the above | Merges into one ranked, explained, guardrailed decision |

Be upfront that none of these call an LLM at runtime — they're deterministic code plus one ML model. If asked to add a real LLM agent (e.g. a natural-language explainer), say it's a planned next step, not done due to time.
