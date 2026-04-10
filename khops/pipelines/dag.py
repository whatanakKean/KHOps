from typing import List, Dict, Set, Optional
from collections import defaultdict, deque
from .models import PipelineConfig, Node


class DAGCycleError(Exception):
    """Raised when a cycle is detected in the pipeline DAG"""
    pass


class DAGValidationError(Exception):
    """Raised when DAG structure is invalid"""
    pass


class DAG:
    """
    Directed Acyclic Graph representation of a pipeline.

    Handles topological sorting, cycle detection, and execution order generation.
    """

    def __init__(self, config: PipelineConfig):
        """
        Initialize DAG from pipeline configuration.

        Args:
            config: Validated PipelineConfig

        Raises:
            DAGValidationError: If DAG structure is invalid
            DAGCycleError: If cycles are detected
        """
        self.config = config
        self.nodes = {node.id: node for node in config.nodes}
        self.edges = config.edges

        # Build adjacency lists
        self._build_adjacency_lists()

        # Validate DAG structure
        self._validate_dag()

        # Check for cycles
        if self.has_cycles():
            cycle = self._find_cycle()
            raise DAGCycleError(f"Cycle detected in pipeline: {' -> '.join(cycle)}")

    def _build_adjacency_lists(self) -> None:
        """Build adjacency lists for efficient traversal"""
        self.adj_list = defaultdict(list)  # node -> list of nodes it points to
        self.rev_adj_list = defaultdict(list)  # node -> list of nodes pointing to it

        for edge in self.edges:
            self.adj_list[edge.from_node].append(edge.to_node)
            self.rev_adj_list[edge.to_node].append(edge.from_node)

    def _validate_dag(self) -> None:
        """Validate basic DAG structure"""
        # Check that all referenced nodes exist
        all_node_ids = set(self.nodes.keys())

        for edge in self.edges:
            if edge.from_node not in all_node_ids:
                raise DAGValidationError(f"Edge references unknown node: {edge.from_node}")
            if edge.to_node not in all_node_ids:
                raise DAGValidationError(f"Edge references unknown node: {edge.to_node}")

    def has_cycles(self) -> bool:
        """
        Check if the DAG contains cycles using topological sort.

        Returns:
            bool: True if cycles exist, False otherwise
        """
        # Kahn's algorithm for cycle detection
        in_degree = {node_id: 0 for node_id in self.nodes}
        for neighbors in self.adj_list.values():
            for neighbor in neighbors:
                in_degree[neighbor] += 1

        # Queue of nodes with no incoming edges
        queue = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
        processed_count = 0

        while queue:
            current = queue.popleft()
            processed_count += 1

            for neighbor in self.adj_list[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return processed_count != len(self.nodes)

    def _find_cycle(self) -> List[str]:
        """
        Find and return a cycle in the DAG.

        Returns:
            List[str]: List of node IDs forming a cycle

        Note: This is a simplified cycle detection that may not find all cycles
        """
        # Use DFS to find cycles
        visited = set()
        rec_stack = set()
        cycle_path = []

        def dfs(node_id: str) -> Optional[List[str]]:
            visited.add(node_id)
            rec_stack.add(node_id)
            cycle_path.append(node_id)

            for neighbor in self.adj_list[node_id]:
                if neighbor not in visited:
                    cycle = dfs(neighbor)
                    if cycle:
                        return cycle
                elif neighbor in rec_stack:
                    # Found cycle
                    start_idx = cycle_path.index(neighbor)
                    return cycle_path[start_idx:] + [neighbor]

            rec_stack.remove(node_id)
            cycle_path.pop()
            return None

        for node_id in self.nodes:
            if node_id not in visited:
                cycle = dfs(node_id)
                if cycle:
                    return cycle

        return []

    def get_execution_order(self) -> List[List[str]]:
        """
        Get the execution order using topological sort.

        Returns:
            List[List[str]]: List of lists, where each inner list contains
                           node IDs that can be executed in parallel

        Raises:
            DAGCycleError: If cycles exist (shouldn't happen due to validation)
        """
        if self.has_cycles():
            raise DAGCycleError("Cannot generate execution order for cyclic graph")

        # Kahn's algorithm for topological sort
        in_degree = {node_id: 0 for node_id in self.nodes}
        for neighbors in self.adj_list.values():
            for neighbor in neighbors:
                in_degree[neighbor] += 1

        # Queue of nodes with no incoming edges
        queue = deque([node_id for node_id, degree in in_degree.items() if degree == 0])

        execution_levels = []

        while queue:
            level_size = len(queue)
            current_level = []

            for _ in range(level_size):
                current = queue.popleft()
                current_level.append(current)

                for neighbor in self.adj_list[current]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)

            execution_levels.append(current_level)

        # Check if all nodes were processed
        total_processed = sum(len(level) for level in execution_levels)
        if total_processed != len(self.nodes):
            raise DAGCycleError("Not all nodes could be processed - possible cycle")

        return execution_levels

    def get_node_dependencies(self, node_id: str) -> List[str]:
        """
        Get all nodes that must execute before this node.

        Args:
            node_id: Node ID to check

        Returns:
            List[str]: List of prerequisite node IDs
        """
        if node_id not in self.nodes:
            raise ValueError(f"Unknown node: {node_id}")

        return self.rev_adj_list[node_id]

    def get_node_dependents(self, node_id: str) -> List[str]:
        """
        Get all nodes that depend on this node.

        Args:
            node_id: Node ID to check

        Returns:
            List[str]: List of dependent node IDs
        """
        if node_id not in self.nodes:
            raise ValueError(f"Unknown node: {node_id}")

        return self.adj_list[node_id]

    def is_reachable(self, from_node: str, to_node: str) -> bool:
        """
        Check if there's a path from from_node to to_node.

        Args:
            from_node: Starting node ID
            to_node: Target node ID

        Returns:
            bool: True if path exists
        """
        if from_node not in self.nodes or to_node not in self.nodes:
            return False

        visited = set()
        stack = [from_node]

        while stack:
            current = stack.pop()
            if current == to_node:
                return True

            if current not in visited:
                visited.add(current)
                stack.extend(self.adj_list[current])

        return False

    def get_longest_path_length(self) -> int:
        """
        Get the length of the longest path in the DAG.

        Returns:
            int: Length of longest path (number of edges)
        """
        # Use dynamic programming to find longest path
        memo = {}

        def longest_path_from(node_id: str) -> int:
            if node_id in memo:
                return memo[node_id]

            max_length = 0
            for neighbor in self.adj_list[node_id]:
                max_length = max(max_length, longest_path_from(neighbor) + 1)

            memo[node_id] = max_length
            return max_length

        max_path = 0
        for node_id in self.nodes:
            max_path = max(max_path, longest_path_from(node_id))

        return max_path

    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about the DAG.

        Returns:
            Dict with various statistics
        """
        return {
            'node_count': len(self.nodes),
            'edge_count': len(self.edges),
            'max_parallelism': max(len(level) for level in self.get_execution_order()),
            'longest_path': self.get_longest_path_length(),
            'has_cycles': self.has_cycles()
        }