"""Formats a recommendation dict into plain-language WhatsApp reply text."""


def format_recommendation(recommendation: dict) -> str:
    recs = recommendation["recommendations"]
    if not recs:
        return (
            "Sorry, we couldn't find a confident crop match for your land right now. "
            "Please try again with a nearby district name."
        )

    lines = [f"Here's what we recommend for {recommendation['location']}:\n"]

    if recommendation.get("rotation_note"):
        lines.append(f"🌱 Soil note: {recommendation['rotation_note']}.\n")
    for rec in recs:
        price = rec["local_price"]
        price_text = (
            f"local mandi price ~₹{price['modal_price_per_quintal']}/quintal"
            if price.get("available")
            else "local mandi price not available right now"
        )
        lines.append(
            f"• {rec['crop'].title()} — plant ~{rec['suggested_allocation_pct']}% of your land.\n"
            f"  {rec['why']} {price_text.capitalize()}."
        )
        if rec.get("local_market_flag"):
            lines.append(f"  ⚠️ {rec['local_market_note']}")

    lines.append(f"\n{recommendation['guardrail_note']}")

    if recommendation.get("data_coverage_note"):
        lines.append(f"\nℹ️ {recommendation['data_coverage_note']}")

    return "\n".join(lines)
