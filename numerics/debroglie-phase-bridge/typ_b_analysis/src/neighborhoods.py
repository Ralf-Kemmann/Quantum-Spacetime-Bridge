from __future__ import annotations

from dataclasses import dataclass
from statistics import median

from loader import PairUnit


@dataclass(slots=True)
class NeighborhoodGraph:
    node_ids: list[str]
    adjacency: dict[str, set[str]]
    connected_components: list[list[str]]

    @property
    def edge_count(self) -> int:
        seen: set[tuple[str, str]] = set()
        for src, nbrs in self.adjacency.items():
            for dst in nbrs:
                seen.add(tuple(sorted((src, dst))))
        return len(seen)

    @property
    def isolated_count(self) -> int:
        return sum(1 for node in self.node_ids if not self.adjacency.get(node))

    @property
    def mean_degree(self) -> float:
        if not self.node_ids:
            return 0.0
        return sum(len(self.adjacency.get(node, set())) for node in self.node_ids) / len(self.node_ids)

    @property
    def median_degree(self) -> float:
        if not self.node_ids:
            return 0.0
        values = sorted(len(self.adjacency.get(node, set())) for node in self.node_ids)
        return float(median(values))

    @property
    def max_degree(self) -> int:
        if not self.node_ids:
            return 0
        return max(len(self.adjacency.get(node, set())) for node in self.node_ids)

    @property
    def min_degree(self) -> int:
        if not self.node_ids:
            return 0
        return min(len(self.adjacency.get(node, set())) for node in self.node_ids)

    @property
    def largest_component_size(self) -> int:
        if not self.connected_components:
            return 0
        return max(len(comp) for comp in self.connected_components)


def connected_components(
    node_ids: list[str],
    adjacency: dict[str, set[str]],
) -> list[list[str]]:
    seen: set[str] = set()
    components: list[list[str]] = []

    for node in node_ids:
        if node in seen:
            continue

        stack = [node]
        comp: list[str] = []
        seen.add(node)

        while stack:
            cur = stack.pop()
            comp.append(cur)
            for nbr in adjacency.get(cur, set()):
                if nbr not in seen:
                    seen.add(nbr)
                    stack.append(nbr)

        components.append(sorted(comp))

    return components


def build_shared_endpoint_graph(pair_units: list[PairUnit]) -> NeighborhoodGraph:
    node_ids = [pu.pair_id for pu in pair_units]
    adjacency: dict[str, set[str]] = {pu.pair_id: set() for pu in pair_units}

    for i, left in enumerate(pair_units):
        left_endpoints = {left.endpoint_a, left.endpoint_b}
        for right in pair_units[i + 1:]:
            right_endpoints = {right.endpoint_a, right.endpoint_b}
            if left_endpoints & right_endpoints:
                adjacency[left.pair_id].add(right.pair_id)
                adjacency[right.pair_id].add(left.pair_id)

    return NeighborhoodGraph(
        node_ids=node_ids,
        adjacency=adjacency,
        connected_components=connected_components(node_ids, adjacency),
    )


def _build_endpoint_graph(pair_units: list[PairUnit]) -> dict[str, set[str]]:
    endpoint_graph: dict[str, set[str]] = {}
    for pu in pair_units:
        endpoint_graph.setdefault(pu.endpoint_a, set()).add(pu.endpoint_b)
        endpoint_graph.setdefault(pu.endpoint_b, set()).add(pu.endpoint_a)
    return endpoint_graph


def build_graph_distance_1_graph(pair_units: list[PairUnit]) -> NeighborhoodGraph:
    """
    Alternative neighborhood for N1-v1.

    Conservative operational reading:
    a pair-unit is connected to another if one of its endpoints lies within
    one endpoint-graph hop of an endpoint of the other pair-unit.

    This is still an operational choice, not a physically privileged rule.
    """
    node_ids = [pu.pair_id for pu in pair_units]
    adjacency: dict[str, set[str]] = {pu.pair_id: set() for pu in pair_units}

    endpoint_graph = _build_endpoint_graph(pair_units)
    endpoint_neighbors_1: dict[str, set[str]] = {
        ep: set(nbrs) for ep, nbrs in endpoint_graph.items()
    }

    for i, left in enumerate(pair_units):
        left_zone = {left.endpoint_a, left.endpoint_b}
        left_zone |= endpoint_neighbors_1.get(left.endpoint_a, set())
        left_zone |= endpoint_neighbors_1.get(left.endpoint_b, set())

        for right in pair_units[i + 1:]:
            right_zone = {right.endpoint_a, right.endpoint_b}
            if left_zone & right_zone:
                adjacency[left.pair_id].add(right.pair_id)
                adjacency[right.pair_id].add(left.pair_id)

    return NeighborhoodGraph(
        node_ids=node_ids,
        adjacency=adjacency,
        connected_components=connected_components(node_ids, adjacency),
    )


def build_neighborhood_graph(
    pair_units: list[PairUnit],
    mode: str,
) -> NeighborhoodGraph:
    if mode == "shared_endpoint":
        return build_shared_endpoint_graph(pair_units)
    if mode == "graph_distance_1":
        return build_graph_distance_1_graph(pair_units)
    raise ValueError(f"Unsupported neighborhood mode: {mode}")