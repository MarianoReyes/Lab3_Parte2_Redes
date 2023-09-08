import heapq

class Link_State():
    def __init__(self, nombre, roster):
        self.nombre = nombre
        self.vecinos_pesos = [(vecino, 1) for vecino in roster]
        print(f"Estos son los vecinos de {self.nombre}: ", self.vecinos_pesos)
        self.topologia = {self.nombre: self.vecinos_pesos}
        self.dijkstra()

    def dijkstra(self):
        self.distancias = {node: float("inf") for node in self.topologia}
        self.anterior = {node: None for node in self.topologia}
        self.distancias[self.nombre] = 0

        self.fila = [(0, self.nombre)]

        while self.fila:
            current_dist, u = heapq.heappop(self.fila)
            
            if current_dist > self.distancias[u]:
                continue

            for v, peso in self.topologia[u]:
                alt = self.distancias[u] + peso
                if alt < self.distancias[v]:
                    self.distancias[v] = alt
                    self.anterior[v] = u
                    heapq.heappush(self.fila, (alt, v))

        self.tabla_enrutamiento = {}
        for node, anterior_node in self.anterior.items():
            if anterior_node is not None:
                path = self.camino(node)
                self.tabla_enrutamiento[node] = (path, self.distancias[node])

    def camino(self, destination):
        path = [destination]
        while self.anterior[destination] is not None:
            destination = self.anterior[destination]
            path.insert(0, destination)
        return path

    def siguiente_nodo(self, destination):
        path = self.camino(destination)
        if len(path) > 1:
            return path[1]
        return path[0]

    def recibir_mensaje(self, emisor, receptor, mensaje):
        if self.nombre == receptor:
            print("Mensaje recibido: ", mensaje)
        else:
            print("De: ", emisor)
            print("Manda:", mensaje)
            print("El siguiente nodo en el camino es:", self.siguiente_nodo(receptor))

    def sincronizar_roster(self, roster):
        # Aquí debes agregar la lógica para sincronizar con el roster actualizado.
        # Por ahora solo actualiza la lista de vecinos y pesos.
        self.vecinos_pesos = [(vecino, 1) for vecino in roster]
        self.topologia[self.nombre] = self.vecinos_pesos
        self.dijkstra()
