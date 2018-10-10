import os
import sys


# [START manipulate file path]
def add_path(new_path: str) -> None:
    __PATH__ = os.path.abspath(new_path)
    sys.path.insert(0, __PATH__)
    # [END manipulate file path]
