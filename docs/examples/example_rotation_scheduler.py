"""
Example: Scheduling Log Rotation for Pravaha Applications

This example demonstrates how to set up log rotation scheduling
in a FastAPI application using Pravaha with Nibandha logging.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from pravaha.domain.logging.utils.rotation_utils import LogRotationUtils
from pravaha.domain.logging.manager.logging_manager import PravphaLoggingManager


async def rotation_scheduler():
    """
    Background task that periodically checks for log rotation.
    
    Runs every hour to:
    1. Check if rotation is needed (based on size or time)
    2. Perform rotation if needed
    3. Clean up old archived logs
    """
    logger = PravphaLoggingManager.get_logger()
    
    while True:
        # Wait 1 hour between checks
        await asyncio.sleep(3600)
        
        try:
            # Get Nibandha instance
            nb = PravphaLoggingManager.get_instance()
            
            if nb:
                # Check and rotate if needed
                if LogRotationUtils.check_and_rotate(nb):
                    logger.info("Log rotation performed successfully")
                
                # Cleanup old archives
                deleted_count = LogRotationUtils.cleanup_old_logs(nb)
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} old archive file(s)")
                    
        except Exception as e:
            logger.error(f"Error in rotation scheduler: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.
    Manages background tasks for the application lifecycle.
    """
    logger = PravphaLoggingManager.get_logger()
    logger.info("Starting log rotation scheduler")
    
    # Start rotation scheduler task
    rotation_task = asyncio.create_task(rotation_scheduler())
    
    yield  # Application runs
    
    # Cleanup on shutdown
    logger.info("Stopping log rotation scheduler")
    rotation_task.cancel()
    try:
        await rotation_task
    except asyncio.CancelledError:
        pass


def create_app_with_rotation() -> FastAPI:
    """
    Example: Create FastAPI app with log rotation enabled.
    """
    # 1. Setup log rotation configuration (production defaults)
    LogRotationUtils.setup_rotation(
        max_size_mb=50,              # Rotate when log exceeds 50MB
        rotation_interval_hours=24,   # Or every 24 hours
        archive_retention_days=30     # Keep archives for 30 days
    )
    
    # 2. Initialize logger
    logger = PravphaLoggingManager.get_logger()
    logger.info("Application starting with log rotation enabled")
    
    # 3. Create FastAPI app with lifespan management
    app = FastAPI(
        title="Example Application with Log Rotation",
        lifespan=lifespan
    )
    
    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "logging": "Nibandha with rotation"
        }
    
    @app.post("/rotate-logs-now")
    async def trigger_rotation():
        """Manual endpoint to trigger log rotation."""
        nb = PravphaLoggingManager.get_instance()
        if nb:
            rotated = LogRotationUtils.check_and_rotate(nb)
            return {
                "rotated": rotated,
                "message": "Rotation performed" if rotated else "Rotation not needed"
            }
        return {"error": "Nibandha not initialized"}
    
    logger.info("Application initialized successfully")
    return app


if __name__ == "__main__":
    import uvicorn
    
    app = create_app_with_rotation()
    
    # Run the application
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=None  # Disable uvicorn's default logging to use only Nibandha
    )
