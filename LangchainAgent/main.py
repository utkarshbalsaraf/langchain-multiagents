
from fastapi import FastAPI
import uvicorn

from routes import agent_route


app =FastAPI()

@app.get("/")
def read_root():
    return "Welcome to LangChain Agent"

app.include_router(agent_route.router, prefix="/api", tags=["Agent"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)