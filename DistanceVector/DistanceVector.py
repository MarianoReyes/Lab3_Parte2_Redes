import json


class DistanceVector:
    def __init__(self, node_name=None, node_weight=None):
        self.node_name = node_name
        self.node_weight = node_weight
        self.routing_table = {}
        self.neighbor_costs = {}
        self.next_hops = {}
        self.converged = False

    def load_neighbor_costs_from_file(self, filename):
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                if 'type' in data and data['type'] == 'topo' and 'config' in data:
                    config = data['config']
                    if self.node_name in config:
                        neighbors_and_weights = config[self.node_name]
                        for neighbor, weight in neighbors_and_weights:
                            self.neighbor_costs[neighbor] = weight
        except FileNotFoundError:
            print(f"El archivo {filename} no se encontró.")

    def update(self):
        # Actualizar la tabla de enrutamiento utilizando el algoritmo de vector de distancia
        for node in self.neighbor_costs:
            if node != self.node_name:
                min_cost = min(
                    [self.neighbor_costs[n] + self.routing_table[n] for n in self.neighbor_costs])
                if min_cost < self.routing_table[node]:
                    self.routing_table[node] = min_cost
                    self.next_hops[node] = [
                        n for n in self.neighbor_costs if self.routing_table[node] == self.neighbor_costs[n]][0]

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
