import argparse
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import Config
from cli.cli_interface import cli_interface

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            Config.LOG_FILE, encoding="utf-8"
        ),  # Uncomment to log to a file
    ],
)
logger = logging.getLogger("backend_main")


def parse_arguments():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Final Year Project Backend - Command Line Interface"
    )
    parser.add_argument(
        "--query", "-q", type=str, help="Run a single query directly and exit"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose debug logging"
    )
    return parser.parse_args()


def main():
    """
    Main runner function.
    """
    args = parse_arguments()

    # Adjust log level if verbose is set
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled.")

    logger.info(f"Initializing {Config.APP_NAME}...")

    try:
        if args.query:
            # Single query execution mode
            logger.info(f"Executing single query: '{args.query}'")
            # For demonstration, we print it directly. You can route this
            # to your query processing logic.
            print(f"Result for '{args.query}': [Processing placeholder]")
        else:
            # Interactive CLI mode
            logger.info("Starting interactive CLI interface...")
            cli_interface()

    except Exception as e:
        logger.critical(f"Unhandled exception in main execution: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
