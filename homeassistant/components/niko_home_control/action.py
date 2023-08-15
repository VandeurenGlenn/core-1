"""A Niko Action."""
import asyncio


class Action:
    """A Niko Action."""

    def __init__(self, action):
        """Init Niko Action."""
        self._action_id = action["id"]
        self._state = action["value1"]
        self._name = action["name"]
        self._callbacks = set()
        self._loop = asyncio.get_event_loop()

    @property
    def name(self):
        """A Niko Action state."""
        return self._name

    @property
    def state(self):
        """A Niko Action state."""
        return self._state

    @property
    def action_id(self):
        """A Niko Action action_id."""
        return self._action_id

    @property
    def action_type(self):
        """The Niko Action type."""
        return self._state["type"]

    def is_cover(self) -> bool:
        """Is a cover."""
        return self.action_type == 4

    def is_light(self) -> bool:
        """Is a light."""
        return self.action_type == 1

    def is_dimmable(self) -> bool:
        """Is a dimmable light."""
        return self.action_type == 2

    def register_callback(self, callback) -> None:
        """Register callback, called when Roller changes state."""
        self._callbacks.add(callback)

    def remove_callback(self, callback) -> None:
        """Remove previously registered callback."""
        self._callbacks.discard(callback)

    async def publish_updates(self) -> None:
        """Schedule call all registered callbacks."""
        for callback in self._callbacks:
            callback()
