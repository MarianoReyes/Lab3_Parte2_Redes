import asyncio
from cliente_DV import Cliente, Borrar_Cliente
import cliente_DV
from DistanceVector import DistanceVector  # Importa la clase DistanceVector
import menus

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


menus.menu()
opcion = input("\n>> ")

while opcion != "4":

    # Registro
    if opcion == "1":
        jid = input('Usuario: ')
        password = input('Contraseña: ')

        if cliente_DV.register(jid, password):
            print("Registro completado de manera correcta")
        else:
            print("Registro NO completado")

    # Inicio de sesión
    elif opcion == "2":
        jid = input('Usuario: ')
        password = input('Contraseña: ')

        # Obtener el nombre de usuario (node_name) del JID (por ejemplo, "usuario@servidor.com" se convierte en "usuario")
        node_name = jid.split('@')[0]

        # Crear una instancia de DistanceVector con el node_name obtenido
        distance_vector = DistanceVector(node_name)
        distance_vector.load_neighbor_costs_from_file(
            'topo_DistanceVector.json')

        # Pasa la instancia del algoritmo Distance Vector
        client = Cliente(jid, password, distance_vector)
        client.connect(disable_starttls=True)
        client.process(forever=False)

    # Eliminar cuenta
    elif opcion == "3":
        jid = input('Usuario: ')
        password = input('Contraseña: ')

        client = Borrar_Cliente(jid, password)
        client.connect(disable_starttls=True)
        client.process(forever=False)

    else:
        print("\nOpción NO válida, ingrese de nuevo por favor.")

    menus.menu()
    opcion = input("\n>> ")
