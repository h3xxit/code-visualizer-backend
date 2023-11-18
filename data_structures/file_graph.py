class FileNode:
    def __init__(self, name):
        self.name = name
        self.description = ""
        self.connection: list[str] = []


class FileGraph:
    def __init__(self):
        self.nodes: list[FileNode] = []
