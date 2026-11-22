from tiny_struct_log import create_logger

general_logger = create_logger(
    name="general",
    console=True,
    persist=True,
    console_level="debug",
    persist_level="info",
    log_dir="log",
    max_bytes=10 * 1024 * 1024,
    backup_count=5,
)


# general_logger.debug("General logger initialized successfully.")
# general_logger.info("General logger initialized successfully.")
# general_logger.warning("General logger initialized successfully.")
# general_logger.exception("General logger initialized successfully.")


__all__ = ["general_logger"]
