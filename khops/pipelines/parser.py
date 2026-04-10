import yaml
from pathlib import Path
from typing import Union, Dict, Any
from .models import PipelineConfig, Node, Edge, NodeType


class PipelineParseError(Exception):
    """Raised when pipeline YAML cannot be parsed"""
    pass


class PipelineValidationError(Exception):
    """Raised when pipeline configuration is invalid"""
    pass


class PipelineParser:
    """Parses and validates pipeline YAML configurations"""

    @staticmethod
    def parse_yaml_file(file_path: Union[str, Path]) -> PipelineConfig:
        """
        Parse a pipeline YAML file and return a validated PipelineConfig.

        Args:
            file_path: Path to the YAML file

        Returns:
            PipelineConfig: Validated pipeline configuration

        Raises:
            PipelineParseError: If YAML cannot be parsed
            PipelineValidationError: If pipeline configuration is invalid
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise PipelineParseError(f"Pipeline file not found: {file_path}")

        if not file_path.is_file():
            raise PipelineParseError(f"Path is not a file: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise PipelineParseError(f"Invalid YAML syntax in {file_path}: {e}")
        except Exception as e:
            raise PipelineParseError(f"Error reading file {file_path}: {e}")

        if data is None:
            raise PipelineParseError(f"Empty or null YAML file: {file_path}")

        return PipelineParser.parse_dict(data)

    @staticmethod
    def parse_yaml_string(yaml_content: str) -> PipelineConfig:
        """
        Parse YAML content from a string.

        Args:
            yaml_content: YAML content as string

        Returns:
            PipelineConfig: Validated pipeline configuration

        Raises:
            PipelineParseError: If YAML cannot be parsed
            PipelineValidationError: If pipeline configuration is invalid
        """
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise PipelineParseError(f"Invalid YAML syntax: {e}")

        if data is None:
            raise PipelineParseError("Empty or null YAML content")

        return PipelineParser.parse_dict(data)

    @staticmethod
    def parse_dict(data: Dict[str, Any]) -> PipelineConfig:
        """
        Parse a dictionary containing pipeline configuration.

        Args:
            data: Dictionary with pipeline configuration

        Returns:
            PipelineConfig: Validated pipeline configuration

        Raises:
            PipelineValidationError: If pipeline configuration is invalid
        """
        try:
            # Validate required fields
            if 'name' not in data:
                raise PipelineValidationError("Pipeline must have a 'name' field")
            if 'version' not in data:
                raise PipelineValidationError("Pipeline must have a 'version' field")
            if 'nodes' not in data:
                raise PipelineValidationError("Pipeline must have a 'nodes' field")

            # Ensure nodes is a list
            if not isinstance(data['nodes'], list):
                raise PipelineValidationError("'nodes' must be a list")

            # Ensure edges is a list if present
            if 'edges' in data and not isinstance(data['edges'], list):
                raise PipelineValidationError("'edges' must be a list")

            # Validate node structure
            PipelineParser._validate_nodes(data['nodes'])

            # Validate edge structure if present
            if 'edges' in data:
                PipelineParser._validate_edges(data['edges'], data['nodes'])

            # Create PipelineConfig (Pydantic will handle final validation)
            return PipelineConfig(**data)

        except Exception as e:
            if isinstance(e, (PipelineParseError, PipelineValidationError)):
                raise
            raise PipelineValidationError(f"Invalid pipeline configuration: {e}")

    @staticmethod
    def _validate_nodes(nodes_data: list) -> None:
        """Validate the structure of nodes"""
        if not nodes_data:
            raise PipelineValidationError("Pipeline must have at least one node")

        for i, node_data in enumerate(nodes_data):
            if not isinstance(node_data, dict):
                raise PipelineValidationError(f"Node {i} must be a dictionary")

            if 'id' not in node_data:
                raise PipelineValidationError(f"Node {i} must have an 'id' field")
            if 'type' not in node_data:
                raise PipelineValidationError(f"Node {i} must have a 'type' field")

            # Validate node type
            try:
                NodeType(node_data['type'])
            except ValueError:
                valid_types = [t.value for t in NodeType]
                raise PipelineValidationError(
                    f"Node {node_data['id']} has invalid type '{node_data['type']}'. "
                    f"Valid types: {valid_types}"
                )

    @staticmethod
    def _validate_edges(edges_data: list, nodes_data: list) -> None:
        """Validate the structure of edges"""
        node_ids = {node['id'] for node in nodes_data}

        for i, edge_data in enumerate(edges_data):
            if not isinstance(edge_data, dict):
                raise PipelineValidationError(f"Edge {i} must be a dictionary")

            if 'from' not in edge_data:
                raise PipelineValidationError(f"Edge {i} must have a 'from' field")
            if 'to' not in edge_data:
                raise PipelineValidationError(f"Edge {i} must have a 'to' field")

            from_node = edge_data['from']
            to_node = edge_data['to']

            if from_node not in node_ids:
                raise PipelineValidationError(f"Edge {i} references unknown from_node: {from_node}")
            if to_node not in node_ids:
                raise PipelineValidationError(f"Edge {i} references unknown to_node: {to_node}")

            if from_node == to_node:
                raise PipelineValidationError(f"Edge {i} cannot connect node to itself: {from_node}")

    @staticmethod
    def validate_pipeline_file(file_path: Union[str, Path]) -> bool:
        """
        Validate a pipeline YAML file without returning the config.

        Args:
            file_path: Path to the YAML file

        Returns:
            bool: True if valid, raises exception if invalid
        """
        PipelineParser.parse_yaml_file(file_path)
        return True

    @staticmethod
    def get_pipeline_info(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get basic information about a pipeline without full parsing.

        Args:
            file_path: Path to the YAML file

        Returns:
            Dict with basic pipeline info (name, version, node count, etc.)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            return {
                'name': data.get('name', 'unknown'),
                'version': data.get('version', 'unknown'),
                'description': data.get('description', ''),
                'node_count': len(data.get('nodes', [])),
                'edge_count': len(data.get('edges', [])),
                'valid': True
            }
        except Exception as e:
            return {
                'name': 'unknown',
                'version': 'unknown',
                'description': '',
                'node_count': 0,
                'edge_count': 0,
                'valid': False,
                'error': str(e)
            }