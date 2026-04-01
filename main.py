from core.logging import get_logger
from api.app import create_app
import uvicorn


app = create_app()
logger = get_logger(__name__)


if __name__ == "__main__":
    logger.info("Server started on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000,access_log=False,log_level="critical")
