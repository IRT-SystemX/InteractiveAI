"""Shared in-process store for the latest recommendation from InteractiveAI.

The simulator app's ``POST /api/v1/recommendations`` endpoint writes the
recommendation here, and the simulation loop reads it back directly. Because
both live in the same process, this avoids any HTTP round-trip from the app to
itself (which is fragile behind a reverse proxy / loopback and was returning
404 Not Found).

This module intentionally imports nothing from the rest of the application so
it can be shared by both the Flask routes and ``Communicate`` without creating
a circular import.
"""


class RecommendationStore:
    """Holds the most recent recommendation payload in memory."""

    def __init__(self):
        self._data = {}

    def set(self, data):
        """Store a recommendation payload received from InteractiveAI."""
        self._data = data or {}

    def pop(self):
        """Return the stored recommendation and clear it (single consumption)."""
        data = self._data
        self._data = {}
        return data

    def peek(self):
        """Return the stored recommendation without clearing it."""
        return self._data


# Process-wide singleton shared by the API endpoints and the simulation loop.
store = RecommendationStore()
