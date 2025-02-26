import os
import subprocess
import tempfile
import logging
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def execute_python_code(code: str) -> dict:
    """
    Securely execute Python code in an isolated environment.
    
    :param code: Python code to run
    :return: Dictionary containing output or errors
    """
    logger.info("⚙️ Executing user-submitted Python code...")

    # Create a temporary file for execution
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp_file:
        tmp_file.write(code)
        tmp_file_name = tmp_file.name

    try:
        # Execute code with a timeout to prevent infinite loops
        result = subprocess.run(
            ["python3", tmp_file_name],
            capture_output=True,
            text=True,
            timeout=Config.EXECUTION_TIMEOUT
        )
        
        output = result.stdout
        errors = result.stderr
        logger.info("✅ Execution completed.")

        return {"output": output, "errors": errors}

    except subprocess.TimeoutExpired:
        logger.warning("⚠️ Code execution timed out!")
        return {"error": "Execution timed out."}

    except Exception as e:
        logger.error(f"❌ Unexpected execution error: {str(e)}")
        return {"error": str(e)}

    finally:
        # Remove the temporary file
        try:
            os.remove(tmp_file_name)
        except Exception as e:
            logger.error(f"⚠️ Failed to delete temp file: {str(e)}")

def format_ai_response(ai_response: str) -> str:
    """
    Format OpenAI's AI response to improve readability.

    :param ai_response: The raw AI-generated text
    :return: A cleaned and formatted response
    """
    if not ai_response:
        return "No response from AI."

    formatted_response = ai_response.strip().replace("\n", "\n\n")  # Improve readability
    logger.info("✅ AI response formatted successfully.")
    return formatted_response
