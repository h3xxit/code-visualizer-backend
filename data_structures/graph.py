from __future__ import annotations


class Connection:
    def __init__(self, nextNode: Node, connectionType: str):
        self.nextNode: Node = nextNode
        self.connectionType: str = connectionType


class Node:
    def __init__(self, name):
        self.name = name
        self.description = ""
        self.connection: list[Connection] = []


class Graph:
    def __init__(self):
        self.nodes: list[Node] = []
