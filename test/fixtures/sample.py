"""Sample Python module for parser snapshot test."""

import os
from pathlib import Path
from .utils import helper, another_helper


class Base:
    """Base class docstring"""
    pass


class MyClass(Base):
    """MyClass docstring"""

    def method(self, x, y=2):
        """Method docstring"""
        return x + y

    async def async_method(self, data):
        """Async method docstring"""
        return data

    def _private_method(self):
        return None

    @staticmethod
    def static_method(a, b):
        return a + b


# Back-to-back class with no docstring - regression check for docstring leak
class NoDocClass(Base):
    def method_no_doc(self):
        return None


def top_function(a, b=2, *args, **kwargs):
    """Top function docstring"""
    return a + b


async def top_async_function(x):
    return x


def _private_top_function():
    return None


if __name__ == "__main__":
    print('run')