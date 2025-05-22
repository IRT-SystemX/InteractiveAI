import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
IS_PAUSED = True

def set_pause(state: bool):
    """
    Sets the pause state of the simulation.

    Args:
        state: True to pause, False to resume.
    """
    global IS_PAUSED
    IS_PAUSED = state

def get_pause_status():
    """
    Retrieve the current pause status of the simulation.
    Returns:
        bool: The current pause status.
              True if the simulation is paused, False otherwise.
    """
    global IS_PAUSED
    return IS_PAUSED