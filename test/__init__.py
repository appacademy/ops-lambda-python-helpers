from os import path
import sys

__PATH__ = path.abspath(
    path.join(
        path.dirname(__file__),
        '..'
    )
)
sys.path.insert(0, __PATH__)
