from fastapi import FastAPI

from backend.routes import chat_tester, fpo_dashboard, health, recommend, webhook

app = FastAPI(title="AgriExport Advisor")
app.include_router(health.router)
app.include_router(recommend.router)
app.include_router(webhook.router)
app.include_router(fpo_dashboard.router)
app.include_router(chat_tester.router)
