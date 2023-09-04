import asyncio
import menus
from cliente import *
import cliente

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

menus.menu()
opcion = input("\n>> ")

while opcion != "4":

    # registro
    if opcion == "1":
        jid = input('usuario: ')
        password = input('contraseña: ')

        if cliente.register(jid, password):
            print("Registro completado de manera correcta")
        else:
            print("Registro NO completado")

    # log in
    elif opcion == "2":
        jid = input('usuario: ')
        password = input('contraseña: ')

        client = Cliente(jid, password)
        client.connect(disable_starttls=True)
        client.process(forever=False)

    # eliminar cuenta
    elif opcion == "3":
        jid = input('usuario: ')
        password = input('contraseña: ')

        client = Borrar_Cliente(jid, password)
        client.connect(disable_starttls=True)
        client.process(forever=False)

    else:
        print("\nOpción NO válida, ingrese de nuevo porfavor.")

    menus.menu()
    opcion = input("\n>> ")
