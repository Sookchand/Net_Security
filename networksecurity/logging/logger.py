import logging
import os
from datetime import datetime

# Create a logs directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")
    
# Create a log file with the current date and time
# The log file will be named in the format "MM_DD_YYYY_HH_MM_SS.log"
LOG_FILE=f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

# Create a logs directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")
# Create a logs directory with the current date and time    
logs_path=os.path.join(os.getcwd(),"logs",LOG_FILE)

# Create a logs directory if it doesn't exist
os.makedirs(logs_path,exist_ok=True)

# Create a log file with the current date and time
LOG_FILE_PATH=os.path.join(logs_path,LOG_FILE)

# Configure logging
# Set up logging configuration
logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)