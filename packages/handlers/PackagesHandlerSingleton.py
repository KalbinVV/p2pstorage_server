from typing import Optional

from packages.handlers.PackagesHandler import PackagesHandler


class PackagesHandlerSingleton:
    __packages_handlers: Optional[PackagesHandler] = None

    @classmethod
    def instance(cls) -> PackagesHandler:
        if not cls.__packages_handlers:
            cls.__packages_handlers = PackagesHandler()

        return cls.__packages_handlers

    def __init__(self):
        raise Exception('You should use instance()!')
