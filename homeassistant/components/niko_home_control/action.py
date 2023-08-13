"""A Niko Action."""


class Action:
    """A Niko Action."""

    def __init__(self, action):
        """Init Niko Action."""
        self._state = action._state

    @property
    def state(self):
        """A Niko Action state."""
        return self._state

    @property
    def action_type(self):
        """The Niko Action type."""
        return self._state["type"]
