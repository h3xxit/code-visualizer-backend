from __future__ import annotations
from pydantic import BaseModel, field_serializer


class Connection(BaseModel):
    next_node: Node
    connection_type: str

    def __init__(self, next_node: Node, connection_type: str):
        super().__init__(next_node=next_node, connection_type=connection_type)

    @field_serializer("next_node")
    def serialize_next_node(self, next_node: Node):
        return next_node.name


class Node(BaseModel):
    name: str
    node_type: str
    description: str
    connection: list[Connection]
    path: str

    def __init__(self, name: str, node_type: str, path: str):
        super().__init__(name=name, node_type=node_type, description="", connection=[], path=path)


class Graph(BaseModel):
    nodes: dict[str, Node]

    def __init__(self):
        super().__init__(nodes=dict())
