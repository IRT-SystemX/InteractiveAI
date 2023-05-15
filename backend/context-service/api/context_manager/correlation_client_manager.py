import multiprocessing

from ..clients.correlation_client import CorrelationClient
from settings import logger
import itertools


class CorrelationClientManager:
    def __init__(self) -> None:
        self.correaltion_client = CorrelationClient()

        # correlation queue and process
        self.correlation_app_queue = multiprocessing.Queue()
        self.correlation_request_process = multiprocessing.Process(
            target=self.send_correlation)
        self.correlation_request_process.start()

    def add_correlation(self, data):
        logger.info("Added data new correaltion data")
        self.correlation_app_queue.put(data)

    def send_correlation(self):
        raw = []
        while True:
            try:
                logger.info("Data sending")
                # Remove the oldest element if there are already 12 elements in the list
                if len(raw) == 12:
                    raw.pop(0)
                # Add the latest data to the list
                new_data = self.correlation_app_queue.get()
                raw.append(new_data)
                # Send the last 12 elements
                params = list(itertools.chain(*raw))
                self.correaltion_client.send_correlation(params)
            except Exception as err:
                logger.error(f"Failed to add correlation with error {err}")
