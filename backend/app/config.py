import os


class Config:
    """
    Configuration class for the backend application.
    Modify or extend these attributes as needed for your final year project.
    """

    APP_NAME = "Final Year Project Backend"
    DEBUG = False
    LOG_FILE = "log/app.log"
    ABS_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(ABS_PATH, "data")
    # Add other configurations here (e.g., DB credentials, API keys)
