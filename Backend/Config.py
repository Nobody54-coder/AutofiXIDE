import os
import logging
from dotenv import load_dotenv

# Load environment variables from a .env file (if present)
load_dotenv()

class Config:
    """Centralized configuration settings for AutoFixIDE"""

    # ====== 🔑 API Keys & Authentication ======
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    if not OPENAI_API_KEY:
        raise ValueError("❌ ERROR: OPENAI_API_KEY is missing! Set it in your .env file or system environment.")

    # ====== ⚙️ Server Configuration ======
    HOST = os.getenv("HOST", "0.0.0.0")  # Server host (default: all interfaces)
    PORT = int(os.getenv("PORT", 8000))  # FastAPI default port

    # ====== 🏃 Code Execution Settings ======
    EXECUTION_TIMEOUT = int(os.getenv("EXECUTION_TIMEOUT", 5))  # Max runtime per code execution (seconds)
    SAFE_MODE = os.getenv("SAFE_MODE", "true").lower() == "true"  # Sandbox mode for execution safety

    # ====== 🧠 AI Model Settings ======
    AI_MODEL = os.getenv("AI_MODEL", "gpt-4")  # Default AI model (e.g., GPT-4, GPT-3.5-turbo)
    AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", 512))  # Limit response length
    AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", 0.2))  # Controls randomness in AI responses

    # ====== 🔗 WebSocket Configuration ======
    WS_MAX_CONNECTIONS = int(os.getenv("WS_MAX_CONNECTIONS", 50))  # Max concurrent WebSocket connections
    WS_TIMEOUT = int(os.getenv("WS_TIMEOUT", 30))  # WebSocket timeout in seconds

    # ====== 🔒 Security & CORS Settings ======
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")  # Frontend domains allowed to access API
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", 100))  # Max API requests per minute
    ENABLE_AUTH = os.getenv("ENABLE_AUTH", "false").lower() == "true"  # Toggle authentication (if needed)

    # ====== 📜 Logging Settings ======
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()  # Default log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    LOG_FILE = os.getenv("LOG_FILE", "autofixide.log")  # Log file name
    LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"

    @classmethod
    def configure_logging(cls):
        """Setup application logging"""
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL, logging.INFO),
            format=cls.LOG_FORMAT,
            handlers=[
                logging.StreamHandler(),  # Print logs to console
                logging.FileHandler(cls.LOG_FILE, mode="a"),  # Save logs to a file
            ],
        )
        logging.info("✅ Logging configured successfully.")

# Validate API Key and Initialize Logging on Startup
Config.configure_logging()
