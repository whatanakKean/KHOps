from typing import Dict, List, Any, Literal
from pydantic import BaseModel, Field, validator
from enum import Enum


class NodeType(str, Enum):
    """Supported node types in pipelines"""
    DATA = "data"
    TRAINING = "training"
    EVALUATION = "evaluation"


class Node(BaseModel):
    """Represents a single node in the pipeline"""
    id: str = Field(..., min_length=1, max_length=100, description="Unique node identifier")
    type: NodeType = Field(..., description="Type of node (data, training, evaluation)")
    params: Dict[str, Any] = Field(default_factory=dict, description="Node-specific parameters")

    @validator('id')
    def validate_node_id(cls, v):
        """Validate node ID format"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Node ID must contain only alphanumeric characters, underscores, and hyphens')
        return v


class Edge(BaseModel):
    """Represents a connection between nodes"""
    from_node: str = Field(..., alias="from", description="Source node ID")
    to_node: str = Field(..., alias="to", description="Target node ID")

    class Config:
        validate_by_name = True


class PipelineConfig(BaseModel):
    """Complete pipeline configuration loaded from YAML"""
    name: str = Field(..., min_length=1, max_length=255, description="Pipeline name")
    version: str = Field(..., pattern=r'^\d+\.\d+$', description="Pipeline version (e.g., '1.0')")
    description: str = Field(default="", max_length=1000, description="Pipeline description")
    nodes: List[Node] = Field(..., min_items=1, description="List of pipeline nodes")
    edges: List[Edge] = Field(default_factory=list, description="List of node connections")

    @validator('nodes')
    def validate_unique_node_ids(cls, v):
        """Ensure all node IDs are unique"""
        ids = [node.id for node in v]
        if len(ids) != len(set(ids)):
            duplicates = [id for id in ids if ids.count(id) > 1]
            raise ValueError(f'Duplicate node IDs found: {duplicates}')
        return v

    @validator('edges')
    def validate_edge_references(cls, v, values):
        """Ensure all edge references point to valid nodes"""
        if 'nodes' not in values:
            return v

        node_ids = {node.id for node in values['nodes']}

        for edge in v:
            if edge.from_node not in node_ids:
                raise ValueError(f'Edge references unknown from_node: {edge.from_node}')
            if edge.to_node not in node_ids:
                raise ValueError(f'Edge references unknown to_node: {edge.to_node}')

        return v

    def get_node_by_id(self, node_id: str) -> Node:
        """Get a node by its ID"""
        for node in self.nodes:
            if node.id == node_id:
                return node
        raise ValueError(f'Node with ID {node_id} not found')

    def get_incoming_edges(self, node_id: str) -> List[Edge]:
        """Get all edges pointing to a node"""
        return [edge for edge in self.edges if edge.to_node == node_id]

    def get_outgoing_edges(self, node_id: str) -> List[Edge]:
        """Get all edges originating from a node"""
        return [edge for edge in self.edges if edge.from_node == node_id]

    def get_predecessors(self, node_id: str) -> List[str]:
        """Get IDs of all nodes that have edges to this node"""
        return [edge.from_node for edge in self.get_incoming_edges(node_id)]

    def get_successors(self, node_id: str) -> List[str]:
        """Get IDs of all nodes that this node has edges to"""
        return [edge.to_node for edge in self.get_outgoing_edges(node_id)]