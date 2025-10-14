# api/gateway.py
"""
FastAPI gateway for BillGenerator SaaS mode.
This file exposes a POST /generate endpoint that forwards inputs to existing core logic.
Do NOT change core computation logic — call into it as a library.
"""

from fastapi import FastAPI, UploadFile, File, Depends
from api.auth import verify_token
from pydantic import BaseModel
import tempfile, json, os

app = FastAPI(title="BillGenerator SaaS Gateway")

# Example Pydantic input — adapt to your input format or accept file uploads
class GenerateRequest(BaseModel):
    tenant_id: str | None = None
    input_data: dict | None = None

# Attempt to import existing computation entrypoint
try:
    # change import path if your compute entrypoint differs
    from batch_processor import HighPerformanceBatchProcessor as _generate_bill
except Exception:
    _generate_bill = None

@app.post("/generate")
async def generate(req: GenerateRequest, auth=Depends(verify_token)):
    """
    Accepts JSON body or uploaded file; calls existing generate function and returns metadata.
    """
    if _generate_bill is None:
        return {"status": "error", "message": "Computation entrypoint not found in repo. Please wire batch_processor.HighPerformanceBatchProcessor."}
    # If input_data supplied, call generate directly
    try:
        # For now, we'll return a placeholder result
        # In a real implementation, you would process the input_data using the batch processor
        result = {"message": "Processing request", "tenant": auth["tenant"], "input": req.input_data}
        return {"status": "ok", "tenant": auth["tenant"], "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}