from fastapi import FastAPI, UploadFile
import batch_processor
import tempfile
import os

app = FastAPI(title="BillGenerator API")

@app.post("/generate")
async def generate(file: UploadFile):
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Create a temporary directory for output
        output_dir = tempfile.mkdtemp()
        
        # Process the file using batch_processor
        result = batch_processor.process_batch(tmp_path, output_dir)
        
        # Clean up temporary files
        os.unlink(tmp_path)
        # Note: In a real implementation, you'd want to return the generated files
        # For now, we're just returning the result status
        
        return {"status": "success", "result": result}
    except Exception as e:
        # Clean up temporary files
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        return {"status": "error", "message": str(e)}