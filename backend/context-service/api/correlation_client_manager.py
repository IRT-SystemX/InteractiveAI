import multiprocessing

from .clients.correlation_client import CorrelationClient
from settings import logger


class CorrelationClientManager:
    def __init__(self) -> None:
        self.correaltion_client = CorrelationClient()

        # correlation queue and process
        self.correlation_app_queue = multiprocessing.Queue()
        correlation_request_process = multiprocessing.Process(
            target=self.send_correlation)
        correlation_request_process.start()

    def add_correlation(self, data):
        logger.info("Added data new correaltion data")
        self.correlation_app_queue.put(data)

    def send_correlation(self):
        while True:
            try:
                logger.info("Data sending")
                params = self.correlation_app_queue.get()
                self.correaltion_client.send_correlation(params)
            except Exception as err:
                logger.error(f"Failed to add correlation with error {err}")
