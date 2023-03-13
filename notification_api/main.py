import logging

import uvicorn
from fastapi import FastAPI

from api.v1.notification import router as notification_router
from api.v1.notification import logger as notification_logger
from dependencies.config import get_settings
from utils.rabbitmq_client import rabbitmq_client
from utils.rabbitmq_client import logger as rabbitmq_logger


settings = get_settings()

logger = logging.getLogger(__name__)


app = FastAPI(title="Notification API", description="Сервис уведомлений", version="1.0.0",)


@app.on_event("startup")
async def startup():
    logger.info("Startup app")
    await rabbitmq_client.initialize()


@app.on_event("shutdown")
async def shutdown() -> None:
    logger.info("Shutdown app")
    await rabbitmq_client.close()


app.include_router(
    notification_router, prefix="/app/v1/notification", tags=["notifications"],
)

if __name__ == "__main__":

    loggers_list = [
        notification_logger,
        rabbitmq_logger,
    ]
    for logger in loggers_list:
        logger.setLevel("INFO")

    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa S104
