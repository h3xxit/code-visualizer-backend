from typing import Union


class File:
    def __init__(self, name: str, relative_path: str):
        self.name: str = name
        self.relative_path: str = relative_path


class Module:
    def __init__(self, name: str, relative_path: str):
        self.name: str = name
        self.relative_path: str = relative_path
        self.remapping: dict[str, str] = dict()


class Project:
    def __init__(self):
        self.files = dict[str, Union[File, Module]]()
