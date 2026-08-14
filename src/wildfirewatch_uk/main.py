from fastapi import FastAPI

from wildfirewatch_uk.core.settings import get_settings

app = FastAPI(
    title="WildfireWatch UK",
    version="0.1.0",
    description="AI-assisted wildfire risk and situational intelligence for the UK.",
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.service_name,
        "environment": settings.app_env,
    }
