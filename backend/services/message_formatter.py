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
            f"• {rec['crop'].title()} — plant ~{rec['suggested_allocation_pct']}% of your land "
            f"({rec['allocated_acres']} acres).\n"
            f"  {rec['why']} {price_text.capitalize()}."
        )
        if rec.get("projected_revenue_inr") is not None:
            lines.append(f"  💰 Estimated revenue: ~₹{rec['projected_revenue_inr']:,.0f}")
        if rec.get("local_market_flag"):
            lines.append(f"  ⚠️ {rec['local_market_note']}")

    revenue_comparison = recommendation.get("revenue_comparison")
    if revenue_comparison:
        base = revenue_comparison["baseline_crop"].title()
        base_rev = revenue_comparison["baseline_revenue_inr"]
        proj_rev = revenue_comparison["projected_total_revenue_inr"]
        if revenue_comparison["revenue_increase_pct"] is not None:
            pct = revenue_comparison["revenue_increase_pct"]
            direction = "increase" if pct >= 0 else "decrease"
            lines.append(
                f"\n💰 Compared to sticking with {base} on all your land "
                f"(~₹{base_rev:,.0f}), this plan projects ~₹{proj_rev:,.0f} — "
                f"a {abs(pct):.0f}% {direction}."
            )
        else:
            lines.append(
                f"\n💰 Sticking with {base} on all your land would project ~₹{base_rev:,.0f}. "
                f"We could only estimate revenue for part of this plan (~₹{proj_rev:,.0f} so far) "
                "due to missing price data for some crops — not a fair full comparison yet."
            )

    lines.append(f"\n{recommendation['guardrail_note']}")

    if recommendation.get("data_coverage_note"):
        lines.append(f"\nℹ️ {recommendation['data_coverage_note']}")

    return "\n".join(lines)
