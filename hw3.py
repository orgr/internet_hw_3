import fileinput

import itertools


class Node:
    def __init__(self, node_id: int):
        self.id = node_id
        self.peers = list()
        self.peers_checked = list()
        self.customers = list()
        self.providers = list()

    def __repr__(self):
        return str(self.id)


class Route:
    def __init__(self, node_list: [Node], ends_with_peer_connection: bool):
        self.ends_with_peer_connection = ends_with_peer_connection
        self.node_list = node_list  # type: [Node]

    def __repr__(self):
        return self.node_list.__repr__()

    def union(self, other: 'Route') -> []:
        if self.node_list[-1] == other.node_list[-1] \
                and self.ends_with_peer_connection != other.ends_with_peer_connection \
                and len(set(self.node_list[:-1]).intersection(set(other.node_list))) == 0:
            return self.node_list[:-1] + other.node_list[::-1]
        return None


CUSTOMER_PROVIDER = "c"
PEER_TO_PEER = "p"
CUSTOMER_INDEX = 0
PROVIDER_INDEX = 1
CONNECTION_TYPE_INDEX = 2

if __name__ == '__main__':

    # parse input
    stripped_input = [line.rstrip() for line in fileinput.input()]

    nodes = dict()  # type: {Node}

    route = [int(i) for i in stripped_input[-1].strip('()').split(sep=',')]

    for line in stripped_input[:-1]:  # type: str
        line_parsed = line.split(sep=",")
        customer = int(line_parsed[CUSTOMER_INDEX])
        provider = int(line_parsed[PROVIDER_INDEX])
        connection_type = line_parsed[CONNECTION_TYPE_INDEX]
        if connection_type == CUSTOMER_PROVIDER:
            if not customer in nodes:
                nodes[customer] = Node(customer)
            nodes[customer].providers.append(provider)

            if not provider in nodes:
                nodes[provider] = Node(provider)
            nodes[provider].customers.append(customer)

        elif connection_type == PEER_TO_PEER:
            if customer not in nodes:
                nodes[customer] = Node(customer)
            nodes[customer].peers.append(provider)
            nodes[customer].peers_checked.append(False)
            if provider not in nodes:
                nodes[provider] = Node(provider)
            nodes[provider].peers.append(customer)
            nodes[provider].peers_checked.append(False)

    # create all paths according to export policies

    # find customer-only nodes
    leaves = [node for node in nodes.values() if len(node.customers) == 0]
    possible_half_routes = list()


    def fill_half_routes(current_route: list, peer_step_happened: bool):
        """
        fills possible _half_routes. half route is a route from a leave through
        customer-provider links until the first peer connection
        :param current_route:
        :param peer_step_happened:
        :return:
        """
        node = current_route[-1]  # type: Node
        result = []
        if peer_step_happened:
            possible_half_routes.append(Route(current_route, peer_step_happened))
            return
        else:
            # peer_step_happened = False
            for provider in node.providers:
                provider_node = nodes[provider]
                fill_half_routes(current_route + [provider_node], peer_step_happened)

            for peer in node.peers:

                # do not go back to the peer we just came from
                if len(current_route) >= 2 and current_route[-2].id == peer:
                    continue

                peer_index_in_node = node.peers.index(peer)
                if not node.peers_checked[peer_index_in_node]:
                    node.peers_checked[peer_index_in_node] = True
                    peer_node = nodes[peer]
                    fill_half_routes(current_route + [peer_node], True)
        if len(current_route) > 1:
            possible_half_routes.append(Route(current_route, peer_step_happened))


    """ use fill_half_routes on all leaves """
    # for node in leaves:
    #     fill_half_routes([node], peer_step_happened=False)
    def uncheck_all():
        for node in nodes.values():
            for i, _ in enumerate(node.peers_checked):
                node.peers_checked[i] = False
    for node in nodes.values():
        uncheck_all()
        fill_half_routes([node], peer_step_happened=False)

    """ for all half_route permutations, try to union(failure will be None) """
    full_routes = [route_tuple[0].union(route_tuple[1]) for route_tuple in
                   list(itertools.permutations(possible_half_routes, 2)) if route_tuple[0].union(route_tuple[1])]

    all_routes = [route.node_list for route in possible_half_routes] + [ [node.id for node in node_list] for node_list in full_routes]
    for possible_route in all_routes:
        if possible_route == route:
            print("0")
            exit()
    print("1")
