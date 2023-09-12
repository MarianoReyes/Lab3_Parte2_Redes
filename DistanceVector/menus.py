from utils import *

# estructura sugerida por chat gpt


def menu():
    print_cyan("\nXMPP CHAT: Qué desea hacer? (Ingresar número de opción)")
    print_cyan("1. Registrarse")
    print_cyan("2. Iniciar sesión")
    print_cyan("3. Eliminar cuenta")
    print_cyan("4. Salir")


def user_menu():
    print_cyan("\nQué desea hacer? (Ingresar número de opción)")
    print_cyan("1. Setear vecinos")
    print_cyan("2. Agregar vecino")
    print_cyan("3. Eliminar vecino")
    print_cyan("4. Mostrar detalles de vecinos")
    print_cyan("5. Enviar mensaje a un nodo")
    print_cyan("6. Enviar presencia a vecinos")
    print_cyan("7. Imprimir tabla de ruteo del nodo")
    print_cyan("8. Salir")
