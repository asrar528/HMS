"""
Dependency Injection Container for HMS Application.

Provides a lightweight, loosely-coupled IoC container that resolves
and injects dependencies throughout the application lifecycle.
"""

from __future__ import annotations
from typing import Any, Callable, Dict, Optional, Type, TypeVar

T = TypeVar("T")


class DIContainer:
    """
    A simple, thread-safe Dependency Injection container.

    Supports:
    - Singleton registrations (one instance per container lifetime)
    - Factory registrations (new instance on every resolve)
    - Instance registrations (pre-built objects)
    """

    def __init__(self) -> None:
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._singleton_flags: Dict[str, bool] = {}

    # ------------------------------------------------------------------
    # Registration API
    # ------------------------------------------------------------------

    def register_singleton(self, interface: str, factory: Callable[[], T]) -> None:
        """Register a factory that is resolved only once (singleton)."""
        self._factories[interface] = factory
        self._singleton_flags[interface] = True

    def register_factory(self, interface: str, factory: Callable[[], T]) -> None:
        """Register a factory that creates a new instance on each resolve."""
        self._factories[interface] = factory
        self._singleton_flags[interface] = False

    def register_instance(self, interface: str, instance: Any) -> None:
        """Register a pre-created object as a singleton."""
        self._singletons[interface] = instance
        self._singleton_flags[interface] = True

    # ------------------------------------------------------------------
    # Resolution API
    # ------------------------------------------------------------------

    def resolve(self, interface: str) -> Any:
        """
        Resolve a registered dependency by its interface name.

        Raises:
            KeyError: If the interface has not been registered.
        """
        # Return cached singleton
        if interface in self._singletons:
            return self._singletons[interface]

        if interface not in self._factories:
            raise KeyError(
                f"[DIContainer] Dependency '{interface}' is not registered."
            )

        instance = self._factories[interface]()

        # Cache if singleton
        if self._singleton_flags.get(interface, False):
            self._singletons[interface] = instance

        return instance

    def is_registered(self, interface: str) -> bool:
        """Check whether an interface is registered in the container."""
        return interface in self._factories or interface in self._singletons


# ---------------------------------------------------------------------------
# Module-level singleton container instance
# ---------------------------------------------------------------------------
container = DIContainer()
