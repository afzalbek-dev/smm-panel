"""Runtime entrypoint for SMM Panel server."""

import uvicorn
from smm_panel.config import get_settings
from smm_panel.app import create_app


def main():
    settings = get_settings()
    app = create_app(settings=settings)
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
