from fastapi import  HTTPException
import logging
import functools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_endpoint_errors(func):
    """Decorator to handle common endpoint errors."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except FileNotFoundError:
            print("Resource not found")
            raise HTTPException(status_code=404, detail="Resource not found")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Endpoint error: {e}")
            raise HTTPException(500, "Internal error")
    return wrapper