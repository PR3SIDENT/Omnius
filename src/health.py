"""Health check module for Omnius bot."""
import os
import psutil
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def check_disk_usage(path: str = "/app/data") -> Dict[str, Any]:
    """Check disk usage for data directory."""
    usage = psutil.disk_usage(path)
    return {
        "total": usage.total,
        "used": usage.used,
        "free": usage.free,
        "percent": usage.percent
    }

def check_memory_usage() -> Dict[str, Any]:
    """Check memory usage of the bot process."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return {
        "rss": memory_info.rss,  # Resident Set Size
        "vms": memory_info.vms,  # Virtual Memory Size
        "percent": process.memory_percent()
    }

def check_health() -> Dict[str, Any]:
    """Perform health check and return status."""
    try:
        # Import key dependencies
        import discord
        import openai
        import chromadb
        
        # Check system resources
        disk_status = check_disk_usage()
        memory_status = check_memory_usage()
        
        # Define health thresholds
        disk_warning = disk_status["percent"] > 80
        memory_warning = memory_status["percent"] > 80
        
        status = {
            "status": "healthy" if not (disk_warning or memory_warning) else "warning",
            "dependencies": {
                "discord": True,
                "openai": True,
                "chromadb": True
            },
            "disk": disk_status,
            "memory": memory_status,
            "warnings": []
        }
        
        # Add warnings if thresholds exceeded
        if disk_warning:
            status["warnings"].append(f"High disk usage: {disk_status['percent']}%")
        if memory_warning:
            status["warnings"].append(f"High memory usage: {memory_status['percent']}%")
        
        return status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        } 