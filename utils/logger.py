import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from paths import get_project_root


# Setting log directory
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M')}.log"
logs_dir = os.path.join(get_project_root(), "logs")

# Creating log directory
os.makedirs(logs_dir, exist_ok=True)

# Configuring full log path 
LOGS_FILE_PATH = os.path.join(logs_dir, LOG_FILE)

# Rotating Handler: 5MB max size, keep 
# handler = RotatingFileHandler("mylog.log", maxBytes=5*1024*1024, backupCount=3)

# Configuring logging
logging.basicConfig(
    filename=LOGS_FILE_PATH,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Testing if logging working
if __name__ == "__main__":
    logging.info("check logging")