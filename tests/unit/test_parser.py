import pytest
from pathlib import Path
from khops.pipelines.models import PipelineConfig, Node, Edge, NodeType
from khops.pipelines.parser import PipelineParser, PipelineParseError, PipelineValidationError
from khops.pipelines.dag import DAG, DAGCycleError, DAGValidationError


class TestPipelineModels:
    """Test pipeline data models"""

    def test_node_creation_valid(self):
        """Test creating a valid node"""
        node = Node(id="test_node", type=NodeType.DATA, params={"key": "value"})
        assert node.id == "test_node"
        assert node.type == NodeType.DATA
        assert node.params == {"key": "value"}

    def test_node_invalid_id(self):
        """Test node with invalid ID"""
        with pytest.raises(ValueError, match="Node ID must contain only"):
            Node(id="test@node", type=NodeType.DATA)

    def test_edge_creation(self):
        """Test creating a valid edge"""
        edge = Edge(from_node="node1", to_node="node2")
        assert edge.from_node == "node1"
        assert edge.to_node == "node2"

    def test_pipeline_config_valid(self):
        """Test creating a valid pipeline config"""
        nodes = [Node(id="node1", type=NodeType.DATA), Node(id="node2", type=NodeType.TRAINING)]
        edges = [Edge(from_node="node1", to_node="node2")]
        config = PipelineConfig(
            name="test_pipeline",
            version="1.0",
            description="Test pipeline",
            nodes=nodes,
            edges=edges,
        )
        assert config.name == "test_pipeline"
        assert config.version == "1.0"
        assert len(config.nodes) == 2
        assert len(config.edges) == 1

    def test_pipeline_config_duplicate_nodes(self):
        """Test pipeline config with duplicate node IDs"""
        nodes = [
            Node(id="node1", type=NodeType.DATA),
            Node(id="node1", type=NodeType.TRAINING),  # Duplicate ID
        ]
        with pytest.raises(ValueError, match="Duplicate node IDs found"):
            PipelineConfig(name="test", version="1.0", nodes=nodes)

    def test_pipeline_config_invalid_edge_reference(self):
        """Test pipeline config with edge referencing unknown node"""
        nodes = [Node(id="node1", type=NodeType.DATA)]
        edges = [Edge(from_node="node1", to_node="unknown")]
        with pytest.raises(ValueError, match="Edge references unknown to_node"):
            PipelineConfig(name="test", version="1.0", nodes=nodes, edges=edges)

    def test_pipeline_config_methods(self):
        """Test pipeline config helper methods"""
        nodes = [
            Node(id="node1", type=NodeType.DATA),
            Node(id="node2", type=NodeType.TRAINING),
            Node(id="node3", type=NodeType.EVALUATION),
        ]
        edges = [Edge(from_node="node1", to_node="node2"), Edge(from_node="node2", to_node="node3")]
        config = PipelineConfig(name="test", version="1.0", nodes=nodes, edges=edges)

        # Test get_node_by_id
        node = config.get_node_by_id("node2")
        assert node.type == NodeType.TRAINING

        # Test predecessors/successors
        assert config.get_predecessors("node1") == []
        assert config.get_predecessors("node2") == ["node1"]
        assert config.get_successors("node2") == ["node3"]
        assert config.get_successors("node3") == []


class TestPipelineParser:
    """Test pipeline YAML parser"""

    def test_parse_valid_yaml_string(self):
        """Test parsing valid YAML string"""
        yaml_content = """
        name: test_pipeline
        version: "1.0"
        description: "Test pipeline"
        nodes:
          - id: data_node
            type: data
            params:
              source: "s3://bucket/data.csv"
          - id: train_node
            type: training
            params:
              algorithm: "random_forest"
        edges:
          - from: data_node
            to: train_node
        """

        config = PipelineParser.parse_yaml_string(yaml_content)
        assert config.name == "test_pipeline"
        assert config.version == "1.0"
        assert len(config.nodes) == 2
        assert len(config.edges) == 1
        assert config.nodes[0].type == NodeType.DATA
        assert config.nodes[1].type == NodeType.TRAINING

    def test_parse_invalid_yaml(self):
        """Test parsing invalid YAML"""
        with pytest.raises(PipelineParseError, match="Invalid YAML syntax"):
            PipelineParser.parse_yaml_string("invalid: yaml: content: [")

    def test_parse_missing_required_fields(self):
        """Test parsing YAML with missing required fields"""
        yaml_content = """
        name: test_pipeline
        # missing version and nodes
        """

        with pytest.raises(PipelineValidationError, match="must have a 'version' field"):
            PipelineParser.parse_yaml_string(yaml_content)

    def test_parse_invalid_node_type(self):
        """Test parsing YAML with invalid node type"""
        yaml_content = """
        name: test_pipeline
        version: "1.0"
        nodes:
          - id: invalid_node
            type: invalid_type
        """

        with pytest.raises(PipelineValidationError, match="invalid type 'invalid_type'"):
            PipelineParser.parse_yaml_string(yaml_content)

    def test_parse_duplicate_node_ids(self):
        """Test parsing YAML with duplicate node IDs"""
        yaml_content = """
        name: test_pipeline
        version: "1.0"
        nodes:
          - id: duplicate
            type: data
          - id: duplicate
            type: training
        """

        with pytest.raises(PipelineValidationError, match="Duplicate node IDs found"):
            PipelineParser.parse_yaml_string(yaml_content)

    def test_parse_edge_invalid_reference(self):
        """Test parsing YAML with edge referencing unknown node"""
        yaml_content = """
        name: test_pipeline
        version: "1.0"
        nodes:
          - id: node1
            type: data
        edges:
          - from: node1
            to: unknown_node
        """

        with pytest.raises(PipelineValidationError, match="references unknown to_node"):
            PipelineParser.parse_yaml_string(yaml_content)

    def test_parse_file_not_found(self):
        """Test parsing non-existent file"""
        with pytest.raises(PipelineParseError, match="Pipeline file not found"):
            PipelineParser.parse_yaml_file("/non/existent/file.yaml")

    def test_validate_pipeline_file(self):
        """Test pipeline file validation"""
        # Create a temporary valid YAML file
        import tempfile
        import os

        yaml_content = """
        name: test_pipeline
        version: "1.0"
        nodes:
          - id: node1
            type: data
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            result = PipelineParser.validate_pipeline_file(temp_path)
            assert result is True
        finally:
            os.unlink(temp_path)

    def test_get_pipeline_info(self):
        """Test getting pipeline info without full parsing"""
        import tempfile
        import os

        yaml_content = """
        name: test_pipeline
        version: "1.0"
        description: "Test description"
        nodes:
          - id: node1
            type: data
          - id: node2
            type: training
        edges:
          - from_node: node1
            to_node: node2
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            info = PipelineParser.get_pipeline_info(temp_path)
            assert info["name"] == "test_pipeline"
            assert info["version"] == "1.0"
            assert info["description"] == "Test description"
            assert info["node_count"] == 2
            assert info["edge_count"] == 1
            assert info["valid"] is True
        finally:
            os.unlink(temp_path)


class TestDAG:
    """Test DAG construction and operations"""

    def test_dag_creation_valid(self):
        """Test creating a valid DAG"""
        nodes = [
            Node(id="node1", type=NodeType.DATA),
            Node(id="node2", type=NodeType.TRAINING),
            Node(id="node3", type=NodeType.EVALUATION),
        ]
        edges = [Edge(from_node="node1", to_node="node2"), Edge(from_node="node2", to_node="node3")]
        config = PipelineConfig(name="test", version="1.0", nodes=nodes, edges=edges)

        dag = DAG(config)
        assert len(dag.nodes) == 3
        assert len(dag.edges) == 2

    def test_dag_cycle_detection(self):
        """Test cycle detection in DAG"""
        nodes = [Node(id="node1", type=NodeType.DATA), Node(id="node2", type=NodeType.TRAINING)]
        edges = [
            Edge(from_node="node1", to_node="node2"),
            Edge(from_node="node2", to_node="node1"),  # Creates cycle
        ]
        config = PipelineConfig(name="test", version="1.0", nodes=nodes, edges=edges)

        with pytest.raises(DAGCycleError, match="Cycle detected"):
            DAG(config)

    def test_dag_execution_order(self):
        """Test topological sort execution order"""
        nodes = [
            Node(id="data", type=NodeType.DATA),
            Node(id="preprocess", type=NodeType.DATA),
            Node(id="train", type=NodeType.TRAINING),
            Node(id="eval", type=NodeType.EVALUATION),
        ]
        edges = [
            Edge(from_node="data", to_node="preprocess"),
            Edge(from_node="preprocess", to_node="train"),
            Edge(from_node="train", to_node="eval"),
        ]
        config = PipelineConfig(name="test", version="1.0", nodes=nodes, edges=edges)

        dag = DAG(config)
        execution_order = dag.get_execution_order()

        # Should have 4 levels (no parallelism in this case)
        assert len(execution_order) == 4
        assert execution_order[0] == ["data"]
        assert execution_order[1] == ["preprocess"]
        assert execution_order[2] == ["train"]
        assert execution_order[3] == ["eval"]

    def test_dag_parallel_execution(self):
        """Test parallel execution levels"""
        nodes = [
            Node(id="data1", type=NodeType.DATA),
            Node(id="data2", type=NodeType.DATA),
            Node(id="merge", type=NodeType.DATA),
            Node(id="train", type=NodeType.TRAINING),
        ]
        edges = [
            Edge(from_node="data1", to_node="merge"),
            Edge(from_node="data2", to_node="merge"),
            Edge(from_node="merge", to_node="train"),
        ]
        config = PipelineConfig(name="test", version="1.0", nodes=nodes, edges=edges)

        dag = DAG(config)
        execution_order = dag.get_execution_order()

        # data1 and data2 can run in parallel
        assert len(execution_order) == 3
        assert set(execution_order[0]) == {"data1", "data2"}
        assert execution_order[1] == ["merge"]
        assert execution_order[2] == ["train"]

    def test_dag_dependencies(self):
        """Test dependency queries"""
        nodes = [
            Node(id="a", type=NodeType.DATA),
            Node(id="b", type=NodeType.DATA),
            Node(id="c", type=NodeType.TRAINING),
        ]
        edges = [Edge(from_node="a", to_node="c"), Edge(from_node="b", to_node="c")]
        config = PipelineConfig(name="test", version="1.0", nodes=nodes, edges=edges)

        dag = DAG(config)

        assert dag.get_node_dependencies("a") == []
        assert dag.get_node_dependencies("c") == ["a", "b"]
        assert dag.get_node_dependents("a") == ["c"]
        assert dag.get_node_dependents("c") == []

    def test_dag_reachability(self):
        """Test path reachability"""
        nodes = [
            Node(id="a", type=NodeType.DATA),
            Node(id="b", type=NodeType.DATA),
            Node(id="c", type=NodeType.TRAINING),
        ]
        edges = [Edge(from_node="a", to_node="b"), Edge(from_node="b", to_node="c")]
        config = PipelineConfig(name="test", version="1.0", nodes=nodes, edges=edges)

        dag = DAG(config)

        assert dag.is_reachable("a", "c") is True
        assert dag.is_reachable("c", "a") is False
        assert dag.is_reachable("a", "b") is True

    def test_dag_stats(self):
        """Test DAG statistics"""
        nodes = [
            Node(id="a", type=NodeType.DATA),
            Node(id="b", type=NodeType.DATA),
            Node(id="c", type=NodeType.TRAINING),
        ]
        edges = [Edge(from_node="a", to_node="b"), Edge(from_node="b", to_node="c")]
        config = PipelineConfig(name="test", version="1.0", nodes=nodes, edges=edges)

        dag = DAG(config)
        stats = dag.get_stats()

        assert stats["node_count"] == 3
        assert stats["edge_count"] == 2
        assert stats["has_cycles"] is False
        assert stats["longest_path"] == 2  # a -> b -> c
