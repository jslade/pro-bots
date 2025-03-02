from typing import Any, Callable, Hashable, Iterator, TypeAlias

OnGetCallback: TypeAlias = Callable[[str, Any], Any]
OnSetCallback: TypeAlias = Callable[[str, Any], None]
OnDeleteCallback: TypeAlias = Callable[[str], Any]
OnIterCallback: TypeAlias = Callable[[], Iterator[Hashable]]


class CallbackDict(dict):
    """Instrumented dictionary that calls a callback on get, set, and delete operations.
    It is specifically designed for working with string keys"""

    def __init__(
        self,
        *,
        on_get: OnGetCallback,
        on_set: OnSetCallback,
        on_delete: OnDeleteCallback,
        on_iter: OnIterCallback,
        **values,
    ):
        super().__init__()
        self.on_get = on_get
        self.on_set = on_set
        self.on_delete = on_delete
        self.on_iter = on_iter

        for key, value in values.items():
            self.set_(key, value)

    def get(self, key: str, default: Any = None) -> Any:
        return self.on_get(key, default)

    def get_(self, key: str) -> Any:
        """Get a value without calling the on_get callback"""
        return super().__getitem__(key)

    def __getitem__(self, key: str) -> Any:
        return self.on_get(key)

    def set_(self, key: str, value: Any) -> None:
        """Set a value without calling the on_set callback"""
        super().__setitem__(key, value)

    def __setitem__(self, key: str, value) -> None:
        self.on_set(key, value)

    def del_(self, key: str) -> None:
        """Delete a value without calling the on_delete callback"""
        super().__delitem__(key)

    def __delitem__(self, key) -> Any:
        return self.on_delete(key)

    def __iter__(self) -> Iterator[Hashable]:
        return self.on_iter()

    def items(self) -> Iterator[tuple[str, Any]]:
        for key in self.keys():
            yield key, self.get(key)

    def keys(self) -> Iterator[tuple[str, Any]]:
        return self.__iter__()

    def values(self) -> Iterator[Any]:
        for _, value in self.items():
            yield value
