import logging
from nova_act import NovaAct
from typing import Any

logger = logging.getLogger(__name__)


class InfiniteLoopException(Exception):
    """Exception raised when a step exceeds the maximum number of actions."""
    pass


class ActionCounter:

    def __init__(self, max_actions: int = 100, step_name: str = "Unknown"):
        self.count = 0
        self.max_actions = max_actions
        self.step_name = step_name
        logger.debug(f"ActionCounter initialized for '{step_name}' (max: {max_actions})")

    def safe_act(self, nova: NovaAct, command: str, **kwargs) -> Any:
        self.count += 1

        if self.count > self.max_actions:
            error_msg = (
                f"Step '{self.step_name}' failed: Exceeded maximum actions limit ({self.max_actions}). "
                f"Possible infinite loop detected."
            )
            logger.error(error_msg)
            raise InfiniteLoopException(error_msg)

        # Log every 10 actions
        if self.count % 10 == 0:
            logger.warning(  f"Action count for '{self.step_name}': {self.count}/{self.max_actions}" )
            print(f"⚠️ Action count: {self.count}/{self.max_actions}")

        # Execute the actual nova.act() command
        logger.debug(f"Action {self.count}: {command[:50]}...")
        return nova.act(command, **kwargs)

    def reset(self):
        logger.debug(f"Resetting action counter for '{self.step_name}' (was: {self.count})")
        self.count = 0

    def get_count(self) -> int:
        return self.count

    def get_remaining(self) -> int:
        return self.max_actions - self.count

    def __str__(self) -> str:
        return f"ActionCounter({self.step_name}): {self.count}/{self.max_actions}"


class MultiStepActionCounter:

    def __init__(self, default_max_actions: int = 100):
        self.counters = {}
        self.default_max_actions = default_max_actions
        logger.debug(f"MultiStepActionCounter initialized (default max: {default_max_actions})")

    def get_counter(self, step_name: str, max_actions: int = None) -> ActionCounter:
        if step_name not in self.counters:
            max_actions = max_actions or self.default_max_actions
            self.counters[step_name] = ActionCounter(max_actions, step_name)
            logger.debug(f"Created new counter for step: {step_name}")
        return self.counters[step_name]

    def reset_counter(self, step_name: str):
        if step_name in self.counters:
            self.counters[step_name].reset()

    def reset_all(self):
        for counter in self.counters.values():
            counter.reset()
        logger.debug("All counters reset")

    def get_summary(self) -> dict:
        return {
            name: {
                "count": counter.get_count(),
                "max": counter.max_actions,
                "remaining": counter.get_remaining()
            }
            for name, counter in self.counters.items()
        }
