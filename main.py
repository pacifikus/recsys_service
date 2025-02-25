import os

import uvicorn
from prometheus_fastapi_instrumentator import Instrumentator

from service.api.app import create_app
from service.settings import get_config

config = get_config()
app = create_app(config)


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    Instrumentator().instrument(app).expose(app)

    uvicorn.run(app, host=host, port=port)
