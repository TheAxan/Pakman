import queue


def neighbors(center_node: tuple[int], array: list[list[int]], excluded_values: tuple[int]) -> set:
    """Returns the neighbors of a node in a an array.

    Args:
        center_node (tuple[int]): The node whose neighbors are to be returned.
        array (list[list[int]]): The array in which the nodes are.
        excluded_values (tuple): Values which exclude a node from being a neighbor.

    Returns:
        set: The immediate neighbors of allowed values.
    """
    x, y = center_node
    neighbors_set = set()
    for i, j in ((x-1, y), (x, y-1), (x+1, y), (x, y+1)):
        try:
            if array[j][i] not in excluded_values:
                neighbors_set.add((i, j))
        except:
            pass
    return neighbors_set

def neighbor_values(center_node: tuple[int], array: list[list[int]], diagonal: bool = False) -> dict:
    """Identify walls around a node.

    Args:
        center_node (tuple[int]): The node whose neighbors are to be returned.
        array (list[list[int]]): The array in which the nodes are.

    Returns:
        dict: A dict indicating whether a direction has a wall.
    """
    x, y = center_node
    neighbors_dict = dict()
    if diagonal:
        nodes_to_identify = ((x-1, y-1, 'up left'), (x+1, y-1, 'up right'), (x+1, y+1, 'down right'), (x-1, y+1, 'down left'))
    else:
        nodes_to_identify = ((x-1, y, 'left'), (x, y-1, 'up'), (x+1, y, 'right'), (x, y+1, 'down'))
    
    for i, j, d in nodes_to_identify:
        try:
            neighbors_dict[d] = (array[j][i] in (1, 4))
        except:
            neighbors_dict[d] = 1

    return neighbors_dict


def heuristic_cost(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


coordinates = tuple[int, int]
def A_star(start_node: coordinates, end_node: coordinates, 
           array: list[list[int]], wall_values: tuple[int] = 1) -> list[coordinates]:
    """A* pathfinding from start_node to end_node in an array.

    Args:
        start_node (tuple of int): starting coordinates.
        end_node (tuple of int): goal coordinates.
        array (list of lists): array to pathfind through
        wall_values (tuple of int) : node values in the array that can't be navigated.

    Returns:
        list: list of node coordinates from (including) start_node to (including) end_node.
    """
    nodes_to_explore = queue.PriorityQueue()
    origin_node = dict()
    g_cost = dict()  # g cost: # of moves from the start_node
    nodes_to_explore.put((0, start_node))
    origin_node[start_node] = None
    g_cost[start_node] = 0

    while not nodes_to_explore.empty():
        current_node = nodes_to_explore.get()
        for new_node in neighbors(current_node[1], array, wall_values):
            new_g_cost = g_cost[current_node[1]] + 1
            if new_node not in g_cost or new_g_cost < g_cost[new_node]:
                g_cost[new_node] = new_g_cost
                nodes_to_explore.put((new_g_cost + heuristic_cost(end_node, new_node), new_node))
                origin_node[new_node] = current_node[1]
        if current_node[1] == end_node:
            break
    
    active_node = end_node
    path = [active_node]
    while active_node != start_node:
        active_node = origin_node[active_node]
        path.append(active_node)
    path.reverse()
    return path


def breadth_first_map(array, start_node, wall_values: tuple[int] = (1,)):
    """Explores an array

    Args:
        array (list[list[int]]): Array to explore.
        start_node ([type]): A reachable node.
        wall_values (tuple[int], optional): Values which exclude a node from being a neighbor. Defaults to 1.

    Returns:
        set: Reachable nodes.
    """
    nodes_to_explore = queue.Queue()
    explored_nodes = set()
    nodes_to_explore.put(start_node)

    while not nodes_to_explore.empty():
        current_node = nodes_to_explore.get()
        for new_node in neighbors(current_node, array, wall_values):
            if new_node not in explored_nodes:
                nodes_to_explore.put(new_node)
            explored_nodes.add(current_node)
    
    return explored_nodes


def triangulation(start_node: coordinates, end_node: coordinates, 
                  array: list[list[int]], wall_values: tuple[int] = 1):
    """Find the next best move by triangulation

    Args:
        start_node (coordinates)
        end_node (coordinates): The target.
        array (list[list[int]]): Array in which the nodes are located.
        wall_values (tuple[int], optional): Values which exclude a node from being a neighbor. Defaults to 1.

    Returns:
        coordinates: The coordinates of the start_node neighbor closest to the end_node.
    """
    distance_of_node = {}
    for (x, y) in neighbors(start_node, array, wall_values):
        distance_of_node[(x - end_node[0]) ** 2 + (y - end_node[1]) ** 2] = (x, y)
    return distance_of_node[min(distance_of_node)]