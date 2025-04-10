import sys
import logging
from networksecurity.logging import logger

class NetworkSecurityException(Exception):
    def __init__(self, error_message, error_detail: sys, filename="N/A", lineno="N/A"):
        super().__init__(error_message)
        _, _, exc_tb = error_detail.exc_info()
        if exc_tb is None:
            logging.warning("Exception traceback is None. Using default filename and line number.")
        self.error_message = error_message
        self.lineno = exc_tb.tb_lineno if exc_tb else lineno  # Use provided lineno if exc_tb is None
        self.filename = exc_tb.tb_frame.f_code.co_filename if exc_tb else filename  # Use provided filename if exc_tb is None

    def __str__(self):
        return f"Error occured in python script name [{self.filename}] line number [{self.lineno}] error message [{self.error_message}]"
        
if __name__=='__main__':
    try:
        logger.logging.info("Enter the try block")
        a=1/0
        print("This will not be printed",a)
    except Exception as e:
           raise NetworkSecurityException(e,sys)