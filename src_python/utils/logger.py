# src_python/utils/logger.py
import logging
import structlog

# Log structuré (JSON) pour faciliter l'analyse
logger = structlog.get_logger()
logger.info("scan_started", zone="main", job_id="abc123")