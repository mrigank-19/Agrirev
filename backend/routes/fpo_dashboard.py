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
        f"<td>{r['market']}</td><td>₹{r['price_per_quintal']}</td><td>{r['reported_by']}</td>"
        f"<td>{r['updated_at'][:16].replace('T', ' ')}</td></tr>"
        for r in list_prices()
    )
    banner = f'<p style="color:green">{message}</p>' if message else ""

    return f"""
    <html>
    <head>
        <title>FPO Mandi Price Reporting</title>
        <style>
            body {{ font-family: sans-serif; max-width: 800px; margin: 40px auto; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: left; }}
            th {{ background: #f0f0f0; }}
            label {{ display: block; margin-top: 10px; }}
            input {{ width: 100%; padding: 6px; box-sizing: border-box; }}
            button {{ margin-top: 15px; padding: 8px 16px; background: #25D366; color: white; border: none; border-radius: 4px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <h2>Report a local mandi price</h2>
        <p>FPOs and CSCs can enter the price they're actually seeing at their mandi — this is used instead of Agmarknet whenever available.</p>
        {banner}
        <form method="post" action="/fpo/prices">
            <label>Crop<input name="crop" required placeholder="e.g. maize"></label>
            <label>State<input name="state" required placeholder="e.g. Maharashtra"></label>
            <label>District<input name="district" required placeholder="e.g. Nashik"></label>
            <label>Market / Mandi name<input name="market" required placeholder="e.g. Nashik APMC"></label>
            <label>Price (₹ per quintal)<input name="price_per_quintal" type="number" step="0.01" required></label>
            <label>Your name/FPO<input name="reported_by" required placeholder="e.g. Nashik Farmers FPO"></label>
            <button type="submit">Submit price</button>
        </form>

        <h3>Recently reported prices</h3>
        <table>
            <tr><th>Crop</th><th>State</th><th>District</th><th>Market</th><th>Price/quintal</th><th>Reported by</th><th>Updated</th></tr>
            {rows if rows else '<tr><td colspan="7">No prices reported yet.</td></tr>'}
        </table>
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
