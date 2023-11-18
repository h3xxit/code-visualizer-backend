from __future__ import annotations
from pydantic import BaseModel, field_serializer
from enum import Enum


class ConnectionType(Enum):
    DEFINES = 1
    CONTAINS = 2
    INHERITS_FROM = 3
    USES = 4


class NodeType(Enum):
    FILE = 1
    FUNCTION = 2
    CLASS = 3
    MODULE = 4


class Connection(BaseModel):
    next_node: Node
    connection_type: ConnectionType

    def __init__(self, next_node: Node, connection_type: ConnectionType):
        super().__init__(next_node=next_node, connection_type=connection_type)

    @field_serializer("next_node")
    def serialize_next_node(self, next_node: Node):
        return next_node.name


class Node(BaseModel):
    name: str
    node_type: str
    description: str
    node_type: NodeType
    connection: list[Connection]
    path: str
    #start_line: int = -1
    #end_line: int = -1

    def __init__(self, name: str, node_type: NodeType, path: str):
        super().__init__(name=name, description="", node_type=node_type, connection=[], path=path)
        self._parent_module = None

    @property
    def parent_module(self):
        return self._parent_module

    @parent_module.setter
    def parent_module(self, value):
        self._parent_module = value


class Graph(BaseModel):
    nodes: dict[str, Node]
    path_to_project: str

    def __init__(self, path_to_project):
        super().__init__(nodes=dict(), path_to_project=path_to_project)
