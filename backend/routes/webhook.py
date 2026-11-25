"""Twilio WhatsApp sandbox webhook: receives incoming messages, runs the
sequential Q&A flow, and replies with the composed recommendation."""

from fastapi import APIRouter, Request, Response
from twilio.twiml.messaging_response import MessagingResponse

from backend.services.message_formatter import format_recommendation
from backend.services.recommendation_service import build_recommendation
from backend.services.session_store import create_session, get_session, reset_session, update_session

router = APIRouter()

PROMPTS = {
    "district": "🌾 Welcome to AgriExport Advisor! What's your district/village?",
    "land_size": "How much land (in acres) are you planting this season?",
    "last_crop": "What did you grow last season? (or type 'skip')",
}


@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    from_number = form.get("From", "unknown")
    body = (form.get("Body") or "").strip()

    reply_text = handle_incoming_message(from_number, body)

    twiml = MessagingResponse()
    twiml.message(reply_text)
    return Response(content=str(twiml), media_type="application/xml")


def handle_incoming_message(from_number: str, body: str) -> str:
    session = get_session(from_number)

    if session is None:
        create_session(from_number)
        return PROMPTS["district"]

    step = session["step"]

    if step == "district":
        session["district"] = body
        session["step"] = "land_size"
        update_session(from_number, session)
        return PROMPTS["land_size"]

    if step == "land_size":
        try:
            session["land_size"] = float(body)
        except ValueError:
            return "Please reply with a number for your land size in acres, e.g. 2.5"
        session["step"] = "last_crop"
        update_session(from_number, session)
        return PROMPTS["last_crop"]

    if step == "last_crop":
        last_crop = None if body.lower() == "skip" else body
        recommendation = build_recommendation(
            location=session["district"],
            land_size=session["land_size"],
            last_crop=last_crop,
        )
        reset_session(from_number)
        return format_recommendation(recommendation)

    reset_session(from_number)
    return PROMPTS["district"]
