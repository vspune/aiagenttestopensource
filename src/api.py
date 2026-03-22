from fastapi import FastAPI
from pydantic import BaseModel
from src.agent import WeatherAgent

# ── Create FastAPI app ────────────────
app = FastAPI(
    title       = "Weather Agent API",
    description = "Weather Agent POC",
    version     = "1.0.0"
)

# ── Create agent instance ─────────────
agent = WeatherAgent()

class Chatrequest(BaseModel): #BaseModel comes fomr class inside pydantic! which have imported
    message: str  

class Chatresponse(BaseModel):
    response: str = None
    tool_called: str   = None
    tool_result: dict  = None
    latency_sec: float = None
    error:       str   = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(request: Chatrequest):# fastapi read the json from request body and validate against Chatrequest 
    result = agent.chat(request.message) # this is define in weather agent which will return a dict with response, tool_called, tool_result, latency_sec, error
    return Chatresponse(**result) # this is for unpacking the dic , this will convert the dict result into Chatresponse model which will be returned as json response to the client 
    # with double star we have
    # 
    # )


