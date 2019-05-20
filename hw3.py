import fileinput


class Node:
    def __init__(self, node_id: int):
        self.id = node_id
        self.peers = list()
        self.peers_checked = list()
        self.customers = list()
        self.providers = list()


CUSTOMER_PROVIDER = "c"
PEER_TO_PEER = "p"
CUSTOMER_INDEX = 0
PROVIDER_INDEX = 1
CONNECTION_TYPE_INDEX = 2

# parse input
stripped_input = [line.rstrip() for line in fileinput.input()]

nodes = dict()  # type: {Node}

route = [int(i) for i in stripped_input[-1].strip('()').split(sep=',')]
# print(route)
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
# print("leaves")
# print([node.id for node in leaves])

possible_routes = list()


def add_path_steps(current_route: list, peer_step_happened: bool):
    node = current_route[-1]  # type: Node
    result = []
    if not peer_step_happened:
        for provider in node.providers:
            provider_node = nodes[provider]
            result += [add_path_steps(current_route + [provider_node], peer_step_happened)]

        for peer in node.peers:

            # do not go back to the peer we just came from
            if len(current_route) >= 2 and current_route[-2].id == peer:
                continue

            peer_index_in_node = node.peers.index(peer)
            if not node.peers_checked[peer_index_in_node]:
                node.peers_checked[peer_index_in_node] = True
                peer_node = nodes[peer]
                result += add_path_steps(current_route + [peer_node], False)
    if len(node.providers) == 0:
        return current_route
    else:
        return result


def clear_checks():
    for node in nodes.values():
        for i in range(len(node.peers_checked)):
            node.peers_checked[i] = False


for node in leaves:
    clear_checks()
    for list_list_node in add_path_steps([node], peer_step_happened=False):
        # print(list_node.id)
        for list_node in list_list_node:
            print([x.id for x in list_node])
            # print([x.id for x in list_node if isinstance(x, Node)])
            # print([x for x in list_node])
