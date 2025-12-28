from typing import Any, Callable, Dict

class IoCContainer:
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}

    def register_singleton(self, key: str, instance: Any) -> None:
        self._services[key] = instance

    def register_factory(self, key: str, factory: Callable[[], Any]) -> None:
        self._factories[key] = factory

    def resolve(self, key: str) -> Any:
        if key in self._services:
            return self._services[key]
        
        if key in self._factories:
            return self._factories[key]()
            
        raise KeyError(f"Service {key} not registered in IoC container")

