from fastapi import FastAPI

from backend.routes import health, recommend, webhook

app = FastAPI(title="AgriExport Advisor")
app.include_router(health.router)
app.include_router(recommend.router)
app.include_router(webhook.router)
