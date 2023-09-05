class DistanceVector:
    def __init__(self, node_name=None, node_weight=None):
        self.node_name = node_name
        self.node_weight = node_weight
        self.routing_table = {}
        self.neighbor_costs = {}
        self.next_hops = {}
        self.converged = False

    def set_neighbor_costs(self, neighbors):
        # Establecer costos de vecinos y asignarles un peso de 1
        for neighbor in neighbors:
            self.neighbor_costs[neighbor] = 1

    def update(self, neighbors):
        # Actualizar la tabla de enrutamiento utilizando el algoritmo de vector de distancia
        for node in neighbors:
            if node != self.node_name:
                min_cost = min(
                    [self.neighbor_costs[n] + self.routing_table[n] for n in neighbors])
                if min_cost < self.routing_table[node]:
                    self.routing_table[node] = min_cost
                    self.next_hops[node] = [
                        n for n in neighbors if self.routing_table[node] == self.neighbor_costs[n]][0]

    def receive_message(self, sender, receiver, message):
        # Simular la recepción de un mensaje
        if receiver == self.node_name:
            print(f"Mensaje recibido de {sender}: {message}")
        else:
            next_hop = self.next_hops[receiver]
            print(
                f"Reenviar mensaje de {sender} a {receiver} a través de {next_hop}")

    def is_converged(self):
        # Verificar si la tabla de enrutamiento ha convergido
        return self.routing_table == self.next_hops
