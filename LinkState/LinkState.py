import heapq

class LinkState():
    def __init__(self, nombre, roster):
        self.nombre = nombre.lower()
        self.roster = roster
        self.vecinos = roster[self.nombre]
        print(f"Estos son los vecinos de {self.nombre}: ", self.vecinos)
        
        self.topologia = {self.nombre: self.vecinos}
        for vecino, vecinos_vecino in roster.items():
            if vecino != self.nombre:
                self.topologia[vecino] = vecinos_vecino
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

            for v in self.topologia.get(u, []):
                alt = self.distancias[u] + 1  # El peso es siempre 1
                if alt < self.distancias.get(v, float("inf")):
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
            return None
        else:
            print("De: ", emisor)
            print("Manda:", mensaje)
            next = self.siguiente_nodo(receptor)
            print("El siguiente nodo en el camino es:", next)
            return next

    def sincronizar_roster(self, roster):
        self.roster = roster
        self.vecinos = roster[self.nombre]
        self.topologia[self.nombre] = self.vecinos
        
        for vecino, vecinos_vecino in roster.items():
            if vecino != self.nombre:
                self.topologia[vecino] = vecinos_vecino
        self.dijkstra()


# A continuación, el código para probar la clase
if __name__ == "__main__":
    nuevoLink = LinkState("A", {"A": ["B"]})
    vecinosB = ["A", "C"]
    vecinosC = ["B"]
    print(nuevoLink.topologia)
    nuevoLink.sincronizar_roster({"A": ["B"], "B": vecinosB, "C": vecinosC})
    print("TABLA ", nuevoLink.topologia)
    print(nuevoLink.siguiente_nodo("B"))
    print(nuevoLink.siguiente_nodo("C"))
    print(nuevoLink.recibir_mensaje("A", "C", "Hola"))
