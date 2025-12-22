import logging
from nova_act import NovaAct
from typing import Any

logger = logging.getLogger(__name__)


class InfiniteLoopException(Exception):
    """Exception raised when a step exceeds the maximum number of actions."""
    pass


class ActionCounter:
    """
    Track number of actions to detect infinite loops.

    Usage:
        counter = ActionCounter(max_actions=50)
        counter.safe_act(nova, "Click login button")
        counter.safe_act(nova, "Fill username field", schema=BOOL_SCHEMA)
    """

    def __init__(self, max_actions: int = 100, step_name: str = "Unknown"):
        """
        Initialize action counter.

        Args:
            max_actions: Maximum number of actions allowed
            step_name: Name of the step for logging
        """
        self.count = 0
        self.max_actions = max_actions
        self.step_name = step_name
        logger.debug(f"ActionCounter initialized for '{step_name}' (max: {max_actions})")

    def safe_act(self, nova: NovaAct, command: str, **kwargs) -> Any:
        """
        Wrapper for nova.act() with action counting to prevent infinite loops.

        Args:
            nova: NovaAct instance
            command: Command to execute
            **kwargs: Additional arguments for nova.act()

        Returns:
            Result from nova.act()

        Raises:
            InfiniteLoopException: If max actions exceeded
        """
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
            logger.warning(
                f"Action count for '{self.step_name}': {self.count}/{self.max_actions}"
            )
            print(f"⚠️ Action count: {self.count}/{self.max_actions}")

        # Execute the actual nova.act() command
        logger.debug(f"Action {self.count}: {command[:50]}...")
        return nova.act(command, **kwargs)

    def reset(self):
        """Reset the action counter."""
        logger.debug(f"Resetting action counter for '{self.step_name}' (was: {self.count})")
        self.count = 0

    def get_count(self) -> int:
        """Get current action count."""
        return self.count

    def get_remaining(self) -> int:
        """Get remaining actions before limit."""
        return self.max_actions - self.count

    def __str__(self) -> str:
        """String representation of counter state."""
        return f"ActionCounter({self.step_name}): {self.count}/{self.max_actions}"


class MultiStepActionCounter:
    """
    Manage action counters for multiple steps.

    Usage:
        counter_manager = MultiStepActionCounter()
        counter = counter_manager.get_counter("Login", max_actions=30)
        counter.safe_act(nova, "Click login")
    """

    def __init__(self, default_max_actions: int = 100):
        """
        Initialize multi-step counter manager.

        Args:
            default_max_actions: Default max actions per step
        """
        self.counters = {}
        self.default_max_actions = default_max_actions
        logger.debug(f"MultiStepActionCounter initialized (default max: {default_max_actions})")

    def get_counter(self, step_name: str, max_actions: int = None) -> ActionCounter:
        """
        Get or create action counter for a step.

        Args:
            step_name: Name of the step
            max_actions: Max actions for this step (uses default if None)

        Returns:
            ActionCounter instance
        """
        if step_name not in self.counters:
            max_actions = max_actions or self.default_max_actions
            self.counters[step_name] = ActionCounter(max_actions, step_name)
            logger.debug(f"Created new counter for step: {step_name}")
        return self.counters[step_name]

    def reset_counter(self, step_name: str):
        """Reset counter for a specific step."""
        if step_name in self.counters:
            self.counters[step_name].reset()

    def reset_all(self):
        """Reset all counters."""
        for counter in self.counters.values():
            counter.reset()
        logger.debug("All counters reset")

    def get_summary(self) -> dict:
        """Get summary of all counters."""
        return {
            name: {
                "count": counter.get_count(),
                "max": counter.max_actions,
                "remaining": counter.get_remaining()
            }
            for name, counter in self.counters.items()
        }
