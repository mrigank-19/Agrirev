"""Formats a recommendation dict into plain-language WhatsApp reply text."""


def format_recommendation(recommendation: dict) -> str:
    recs = recommendation["recommendations"]
    if not recs:
        return (
            "Sorry, we couldn't find a confident crop match for your land right now. "
            "Please try again with a nearby district name."
        )

    lines = [f"Here's what we recommend for {recommendation['location']}:\n"]
    for rec in recs:
        growth = rec["export_growth_pct"]
        growth_text = f"{growth:+.1f}% export growth" if growth is not None else "export data not available"
        price = rec["local_price"]
        price_text = (
            f"local mandi price ~₹{price['modal_price_per_quintal']}/quintal"
            if price.get("available")
            else "local mandi price not available right now"
        )
        lines.append(
            f"• {rec['crop'].title()} — plant ~{rec['suggested_allocation_pct']}% of your land. "
            f"{growth_text}, {price_text}."
        )

    lines.append(f"\n{recommendation['guardrail_note']}")
    return "\n".join(lines)
