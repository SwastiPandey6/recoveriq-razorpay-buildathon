from fastapi import FastAPI

app = FastAPI(
    title="RecoverIQ API",
    description="Autonomous Revenue Recovery Agent",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "name": "RecoverIQ",
        "status": "running",
        "message": "Autonomous Revenue Recovery Agent API",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }