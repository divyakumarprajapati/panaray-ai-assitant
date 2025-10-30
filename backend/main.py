"""Main entry point for the Feature Assistant backend application."""

import uvicorn
from app.main import app


def serve(host='0.0.0.0', port=8000):
    """Serves on the given port.
    
    Args:
        host: Host address to bind to (default: 0.0.0.0)
        port: Port number to listen on (default: 8000)
    """
    print(f"Starting server on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    try:
        print("=" * 50)
        print("Feature Assistant Backend - Starting")
        print("=" * 50)
        serve()
    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("Server has stopped")
        print("=" * 50)
