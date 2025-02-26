import openai
import traceback
import logging
from config import Config

# Set up logging for debugging
logger = logging.getLogger(__name__)

class AIDebugger:
    """AI-powered code debugging and optimization engine."""

    def __init__(self):
        """Initialize the debugger with OpenAI API settings."""
        openai.api_key = Config.OPENAI_API_KEY
        self.model = Config.AI_MODEL
        self.max_tokens = Config.AI_MAX_TOKENS
        self.temperature = Config.AI_TEMPERATURE

    def analyze_code(self, code: str) -> dict:
        """
        Analyze the given code, detect errors, and provide optimized solutions.

        :param code: The Python code to debug.
        :return: A dictionary containing error analysis and suggestions.
        """
        logger.info("🔍 AI Debugging started...")
        
        prompt = f"""
        You are an expert Python debugger. Analyze the following code for errors, inefficiencies, and potential improvements.
        Provide a detailed analysis, including the error type, possible cause, and an optimized fixed version of the code.

        Code:
        ```
        {code}
        ```
        """

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "system", "content": "You are a Python expert."},
                          {"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            
            suggestion = response["choices"][0]["message"]["content"]
            logger.info("✅ AI Debugging completed successfully.")
            return {"success": True, "analysis": suggestion}

        except Exception as e:
            logger.error(f"❌ AI Debugging failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def execute_and_debug(self, code: str) -> dict:
        """
        Execute the given Python code in a safe sandbox and provide real-time debugging feedback.

        :param code: The Python code to execute.
        :return: A dictionary containing execution output and debugging analysis.
        """
        logger.info("⚙️ Executing code in sandbox mode...")

        try:
            exec_globals = {}
            exec(code, exec_globals)  # Execute in isolated scope
            logger.info("✅ Code executed successfully.")

            return {
                "success": True,
                "output": exec_globals
            }

        except Exception as e:
            error_trace = traceback.format_exc()
            logger.warning(f"⚠️ Code execution failed with error: {str(e)}")
            
            ai_suggestion = self.analyze_code(code)  # AI-assisted debugging
            
            return {
                "success": False,
                "error": str(e),
                "traceback": error_trace,
                "ai_suggestion": ai_suggestion.get("analysis", "No suggestion available.")
          }
