class DistanceVector:
    def __init__(self, node_name=None, node_weight=None):
        self.node_name = node_name
        self.node_weight = node_weight
        self.routing_table = {}
        self.neighbor_costs = {}
        self.next_hops = {}
        self.converged = False

    def set_routing_table(self, topology_nodes):
        # Inicializa la tabla de enrutamiento
        for node in topology_nodes:
            if node != self.node_name:
                if node in self.neighbor_costs:
                    # Si es un vecino, usa el costo proporcionado en neighbor_costs
                    self.routing_table[node] = self.neighbor_costs[node]
                    self.next_hops[node] = node
                else:
                    # Si no es un vecino, establece el costo a infinito
                    self.routing_table[node] = float('inf')
                    self.next_hops[node] = None
            else:
                self.routing_table[node] = 0

    def update(self, neighbors, sending_node_name):
        for neighbor in neighbors:
            if neighbor != self.node_name:
                if neighbor not in self.neighbor_costs and sending_node_name in self.neighbor_costs and self.routing_table[neighbor] == float('inf'):
                    actual_cost = self.routing_table.get(
                        neighbor, float('inf'))
                    new_cost = self.routing_table[sending_node_name] + 1
                    self.routing_table[neighbor] = min(actual_cost, new_cost)
                    self.next_hops[neighbor] = sending_node_name

    def receive_message(self, sender, receiver, message):
        # Simular la recepción de un mensaje
        if receiver == self.node_name:
            print(f"Mensaje recibido de {sender}: {message}")
        else:
            next_hop = self.next_hops[receiver]
            print(
                f"Reenviar >> {message} >> de: {sender} -> {receiver} a través de {next_hop}")

    def is_converged(self):
        # Verificar si la tabla de enrutamiento ha convergido
        return self.routing_table == self.next_hops
