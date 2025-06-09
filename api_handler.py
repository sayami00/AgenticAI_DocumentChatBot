from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from rag_model import query_rag,QueryResponse
app = FastAPI()

class SubmitRequest(BaseModel):
    requesttext:str


@app.get("/")
def index():
    return {"hello":"world"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "FastAPI OLLAMA backend is running"}

@app.post("/submit_query")
def submit_query_endpoint(request:SubmitRequest) -> QueryResponse:
    query_response= query_rag(request.requesttext)
    return query_response


if __name__ == "__main__":
    #
    port = 8000
    print (f"Running fastAPI server on port {port}")
    uvicorn.run("api_handler:app",host ="127.0.0.1",port=port)
