class Flooding:
    def __init__(self, node_name=None):
        self.node_name = node_name
        self.neighbors = []

    def set_neighbors(self, neighbors):
        # Establecer vecinos
        self.neighbors = neighbors

    def send_message(self, sender, receiver, message):
        # En flooding, simplemente enviamos el mensaje a todos los vecinos, 
        # independientemente de si es el destinatario final o no.
        for neighbor in self.neighbors:
            if neighbor != sender:  # No reenviar al emisor original
                print(f"Reenviar mensaje de {sender} a {receiver} a través de {neighbor}")

    def receive_message(self, sender, receiver, message):
        # Simular la recepción de un mensaje
        if receiver == self.node_name:
            print(f"Mensaje recibido de {sender}: {message}")
        else:
            # En caso de que este nodo no sea el destinatario final, reenviamos el mensaje.
            self.send_message(sender, receiver, message)
