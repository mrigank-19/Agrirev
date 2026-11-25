"""A simple dashboard for FPOs/CSCs to report local mandi prices directly.

No authentication — fine for a hackathon MVP where only trusted local staff
have the URL, but would need access control before any real deployment.
"""

from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from backend.services.manual_price_store import add_price, list_prices

router = APIRouter()


def _render_page(message: str | None = None) -> str:
    rows = "".join(
        f"<tr><td>{r['crop'].title()}</td><td>{r['state'].title()}</td><td>{r['district']}</td>"
        f"<td>{r['market']}</td><td>₹{r['price_per_quintal']:,.0f}</td><td>{r['reported_by']}</td>"
        f"<td>{r['updated_at'][:16].replace('T', ' ')}</td></tr>"
        for r in list_prices()
    )
    banner = f'<div class="banner">✓ {message}</div>' if message else ""

    return f"""
    <html>
    <head>
        <title>FPO Mandi Price Reporting — AgriExport Advisor</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            :root {{
                --green: #1f7a3f;
                --green-dark: #155c2e;
                --bg: #f4f7f4;
                --card: #ffffff;
                --border: #dfe6df;
                --text: #1c1c1c;
                --muted: #6b7a6c;
            }}
            * {{ box-sizing: border-box; }}
            body {{
                font-family: "Segoe UI", Roboto, sans-serif;
                background: var(--bg);
                color: var(--text);
                margin: 0;
                padding: 32px 16px;
            }}
            .wrap {{ max-width: 860px; margin: 0 auto; }}
            .header {{
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 24px;
            }}
            .header .emoji {{ font-size: 32px; }}
            .header h1 {{ font-size: 22px; margin: 0; }}
            .header p {{ margin: 2px 0 0; color: var(--muted); font-size: 14px; }}
            .card {{
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 10px;
                padding: 24px;
                margin-bottom: 24px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            }}
            .card h2 {{ margin-top: 0; font-size: 17px; }}
            .banner {{
                background: #e6f4ea;
                color: var(--green-dark);
                border: 1px solid #b8e0c4;
                border-radius: 6px;
                padding: 10px 14px;
                margin-bottom: 16px;
                font-size: 14px;
            }}
            .grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 14px;
            }}
            .field {{ display: flex; flex-direction: column; gap: 4px; }}
            .field.full {{ grid-column: 1 / -1; }}
            label {{ font-size: 13px; font-weight: 600; color: var(--muted); }}
            input {{
                padding: 9px 11px;
                border: 1px solid var(--border);
                border-radius: 6px;
                font-size: 14px;
                width: 100%;
            }}
            input:focus {{ outline: none; border-color: var(--green); }}
            button {{
                margin-top: 18px;
                padding: 10px 20px;
                background: var(--green);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
            }}
            button:hover {{ background: var(--green-dark); }}
            table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
            th, td {{ padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--border); }}
            th {{ color: var(--muted); font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.03em; }}
            tr:last-child td {{ border-bottom: none; }}
            .empty {{ color: var(--muted); padding: 16px 0; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="wrap">
            <div class="header">
                <div class="emoji">🌾</div>
                <div>
                    <h1>FPO Mandi Price Reporting</h1>
                    <p>Report the price your FPO/mandi is actually seeing — it's used before Agmarknet.</p>
                </div>
            </div>

            <div class="card">
                <h2>Report a price</h2>
                {banner}
                <form method="post" action="/fpo/prices">
                    <div class="grid">
                        <div class="field"><label>Crop</label><input name="crop" required placeholder="e.g. maize"></div>
                        <div class="field"><label>State</label><input name="state" required placeholder="e.g. Maharashtra"></div>
                        <div class="field"><label>District</label><input name="district" required placeholder="e.g. Nashik"></div>
                        <div class="field"><label>Market / Mandi name</label><input name="market" required placeholder="e.g. Nashik APMC"></div>
                        <div class="field"><label>Price (₹ per quintal)</label><input name="price_per_quintal" type="number" step="0.01" required></div>
                        <div class="field"><label>Your name / FPO</label><input name="reported_by" required placeholder="e.g. Nashik Farmers FPO"></div>
                    </div>
                    <button type="submit">Submit price</button>
                </form>
            </div>

            <div class="card">
                <h2>Recently reported prices</h2>
                {f'<table><tr><th>Crop</th><th>State</th><th>District</th><th>Market</th><th>Price/quintal</th><th>Reported by</th><th>Updated</th></tr>{rows}</table>' if rows else '<div class="empty">No prices reported yet.</div>'}
            </div>
        </div>
    </body>
    </html>
    """


@router.get("/fpo", response_class=HTMLResponse)
def fpo_dashboard():
    return _render_page()


@router.post("/fpo/prices")
def submit_price(
    crop: str = Form(...),
    state: str = Form(...),
    district: str = Form(...),
    market: str = Form(...),
    price_per_quintal: float = Form(...),
    reported_by: str = Form(...),
):
    add_price(crop, state, district, market, price_per_quintal, reported_by)
    return RedirectResponse(url="/fpo", status_code=303)
