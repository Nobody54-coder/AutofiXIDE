import os
import asyncio
import subprocess
import tempfile
import functools
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import openai

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("autofixide")

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")

app = FastAPI(title="AutoFixIDE")

# Pydantic model for receiving code from the client
class CodeRequest(BaseModel):
    code: str

@app.get("/")
async def home():
    """
    Health-check endpoint.
    """
    return {"message": "AutoFixIDE is running!"}

@app.post("/run")
async def run_code(request: CodeRequest):
    """
    Asynchronously execute user-submitted Python code and return output/errors.
    """
    # Write code to a temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp_file:
        tmp_file.write(request.code)
        tmp_file_name = tmp_file.name

    try:
        process = await asyncio.create_subprocess_exec(
            "python3", tmp_file_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=5)
        except asyncio.TimeoutError:
            process.kill()
            await process.communicate()
            logger.error("Code execution timed out.")
            return {"error": "Execution timed out."}

        output = stdout.decode().strip()
        errors = stderr.decode().strip()

        return {"output": output, "errors": errors}

    except Exception as e:
        logger.exception("Error during code execution:")
        return {"error": str(e)}

    finally:
        try:
            os.remove(tmp_file_name)
        except Exception as e:
            logger.warning(f"Could not remove temporary file {tmp_file_name}: {e}")

async def call_openai(prompt: str, max_tokens: int, temperature: float):
    """
    Asynchronously call the OpenAI API using a thread executor.
    """
    loop = asyncio.get_event_loop()
    try:
        response = await loop.run_in_executor(
            None,
            functools.partial(
                openai.Completion.create,
                model="text-davinci-003",
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        )
        return response.choices[0].text.strip()
    except Exception as e:
        logger.exception("OpenAI API call failed:")
        raise

@app.post("/debug")
async def debug_code(request: CodeRequest):
    """
    Use OpenAI's GPT to analyze the submitted code for bugs/issues and provide suggestions.
    """
    if not openai.api_key or openai.api_key == "YOUR_OPENAI_API_KEY":
        raise HTTPException(status_code=400, detail="OpenAI API key not set.")

    prompt = f"""
You are a Python expert. The user has submitted the following code:

{request.code}

Please do the following:
1. Identify any bugs or issues in the code.
2. Provide a brief explanation of the problem.
3. Offer a corrected version of the code if applicable.
    """
    try:
        ai_answer = await call_openai(prompt, max_tokens=512, temperature=0.2)
        return {"analysis": ai_answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time code suggestions.
    Receives code snippets and returns AI-generated suggestions.
    """
    await websocket.accept()
    if not openai.api_key or openai.api_key == "YOUR_OPENAI_API_KEY":
        await websocket.send_text("OpenAI API key not set.")
        await websocket.close()
        return

    try:
        while True:
            data = await websocket.receive_text()
            prompt = f"""
You are a Python coding assistant. The user wants real-time suggestions for the following code snippet:

{data}

Please:
- Identify potential bugs or improvements.
- Suggest concise changes or best practices.
            """
            try:
                suggestions = await call_openai(prompt, max_tokens=256, temperature=0.2)
                await websocket.send_text(suggestions)
            except Exception as e:
                error_message = f"Error generating suggestions: {e}"
                logger.error(error_message)
                await websocket.send_text(error_message)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected.")
    except Exception as e:
        logger.exception("Unexpected WebSocket error:")
        await websocket.send_text(f"Error: {str(e)}")
        await websocket.close()
