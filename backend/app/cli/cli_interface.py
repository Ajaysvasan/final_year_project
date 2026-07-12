from config import get_logger

logger = get_logger(__name__)


def cli_interface():
    logger.info("CLI session started.")
    try:
        while True:
            query = input("Enter the query (Press ctrl + c to exit) : ")
            if query.lower() == "exit":
                logger.info("User requested exit from CLI session.")
                print("Exiting the system. Goodbye!")
                break
            logger.info(f"Received user query: '{query}'")
            print(f"Processing query: {query}")
            logger.debug(f"Executing query pipeline for: '{query}'")
            # some stuff
    except KeyboardInterrupt:
        logger.info("CLI session interrupted by user (KeyboardInterrupt).")
        print("\nExiting the system. Goodbye!")
    except Exception as e:
        logger.error(f"Error encountered during CLI session: {e}", exc_info=True)
        raise
