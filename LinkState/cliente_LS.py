import menus
import xmpp
import slixmpp
import asyncio
from aioconsole import ainput
from aioconsole.stream import aprint
from utils import print_azul, print_rojo
from LinkState import Link_State
from slixmpp.xmlstream.stanzabase import ET
from slixmpp.exceptions import IqError, IqTimeout


def register(client, password):

    jid = xmpp.JID(client)
    account = xmpp.Client(jid.getDomain(), debug=[])
    account.connect()
    return bool(
        xmpp.features.register(account, jid.getDomain(), {
            'username': jid.getNode(),
            'password': password
        }))


class Cliente(slixmpp.ClientXMPP):
    def __init__(self, jid, password):

        super().__init__(jid, password)
        
        self.name = jid.split('@')[0]
        self.link_state = Link_State(self.name, {'misvecinos': []})
        self.is_connected = False
        self.actual_chat = ''
        self.client_queue = asyncio.Queue()

        # generado por IA para los diferentes plugins que se usaran
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0199')  # Ping
        self.register_plugin('xep_0045')  # MUC
        self.register_plugin('xep_0085')  # Notifications
        self.register_plugin('xep_0004')  # Data Forms
        self.register_plugin('xep_0060')  # PubSub
        self.register_plugin('xep_0066')  # Out of Band Data
        self.register_plugin('xep_0363')  # HTTP File Upload

        # eventos
        self.add_event_handler('session_start', self.start)
        self.add_event_handler('subscription_request',
                               self.handler_presencia)
        self.add_event_handler('message', self.chat)

    # FUNCIONES DE CONTACTOS Y CHATS

    # aceptar mensajes entrantes

    async def handler_presencia(self, presence):

        # si se tiene solicitud
        if presence['type'] == 'subscribe':
            try:
                self.send_presence_subscription(
                    pto=presence['from'], ptype='subscribed')
                await self.get_roster()
                self.mostrar_notificacion("Solicitud de suscripción"
                                          + " aceptada de "
                                          + str(presence['from']).split('@')[0]
                                          )
            except IqError as e:
                print(
                    f"Error accepting subscription request:\
                        {e.iq['error']['text']}")
            except IqTimeout:
                print("No response from server.")

        # si hay presencia
        else:
            # notificacion si esta logeado
            if self.is_connected:
                if presence['type'] == 'available':
                    self.mostrar_presencia(presence, True)
                elif presence['type'] == 'unavailable':
                    self.mostrar_presencia(presence, False)
                else:
                    self.mostrar_presencia(presence, None)

    async def chat(self, message):

        # chat normal
        if message['type'] == 'chat':
            # solo user
            user = str(message['from']).split('@')[0]

            node = user.split("_")[0].upper()

            mensaje = message["body"]

            try:
                neighbors = mensaje.split(':')[1].split(',')

                # si el mensaje es con el que chatea
                if user == self.actual_chat.split('@')[0]:
                    print_azul(f'{user}: {message["body"]}')
                    self.distance_vector.update(neighbors)
                    print(self.distance_vector.routing_table)

                # notificacion si es otro
                else:
                    self.distance_vector.update(neighbors)
                    self.mostrar_notificacion(
                        f"Tienes una comunicación de {node}>> {mensaje}")
                    print(self.distance_vector.routing_table)
            except IndexError:
                # si el mensaje es con el que chatea
                if user == self.actual_chat.split('@')[0]:
                    print_azul(f'{user}: {message["body"]}')
                # notificacion si es otro
                else:
                    self.mostrar_notificacion(
                        f"Tienes una comunicación de {node}>> {mensaje}")
            except Exception as e:
                print("An error occurred:", e)

    # funcion generada por chat gpt para imprimir con colores
    def mostrar_notificacion(self, mensaje):
        print_rojo(mensaje)
        print("v")

    async def enviar_mensaje_broadcast(client, message_body):
        try:
            # Get the roster (list of contacts)
            roster = client.client_roster

            for jid in roster.keys():
                # Check if the contact JID is not the same as your own JID
                if jid != client.boundjid.bare:
                    # Send the message to the contact
                    client.send_message(
                        mto=jid, mbody=message_body, mtype='chat')

            print("Message sent to all contacts except yourself.")
        except Exception as e:
            print("Error sending message:", e)

    def mostrar_presencia(self, presence, is_available):

        # verficaciones previas
        if str(presence['from']).split("/")[0] \
                != self.boundjid.bare and "conference" \
                not in str(presence['from']):

            # estado del usaurio
            if is_available:
                show = 'available'
            elif is_available is False:
                show = 'offline'
            else:
                show = presence['show']

            # obtener mensaje de usaurio
            user = (str(presence['from']).split('/')[0])
            # presencia de contactos
            status = presence['status']

            if status != '':
                notification_message = f'{user} esta {show} - {status}'
            else:
                notification_message = f'{user} esta {show}'

            # se muestra la notificacion
            self.mostrar_notificacion(notification_message)

    async def anadir_contacto(self):  # funcion para anadir contacto
        jid_to_add = input(
            "Ingresa el JID del usuario que deseas agregar",
            " (Ejemplo: usuario@servidor.com): ")
        try:
            self.send_presence_subscription(pto=jid_to_add)
            print(f"Solicitud de suscripción enviada a {jid_to_add}")
            await self.get_roster()
        except IqError as e:
            print(
                f"Error al mandar suscrpcion: {e.iq['error']['text']}")
        except IqTimeout:
            print("Sin respuesta del servidor.")

    async def mostrar_status_contacto(self):  # mostrar status de los contactos
        # Extract roster items and their presence status
        roster = self.client_roster
        contacts = roster.keys()
        contact_list = []

        if not contacts:
            print("Sin contactos.")
            return

        for jid in contacts:
            user = jid

            # obtener presencia de cada contacto
            connection = roster.presence(jid)
            show = 'available'
            status = ''

            for answer, presence in connection.items():
                if presence['show']:
                    show = presence['show']
                if presence['status']:
                    status = presence['status']

            contact_list.append((user, show, status))

        print("\nLista de contactos:")
        for c in contact_list:
            print(f"Contacto: {c[0]}")
            print(f"Estado: {c[1]}")
            print(f"Mensaje de estado: {c[2]}")
            print("")
        print("")

    async def mostrar_detalles_contacto(self):  # mostrar detalles del contacto
        jid_to_find = input(
            "Ingresa el JID del usuario/contacto que deseas buscar: ")
        roster = self.client_roster
        contacts = roster._jids.keys()

        if jid_to_find not in contacts:
            print("El usuario/contacto no se encuentra",
                  " en la lista de contactos.")
            return

        # Obtener presencia del contacto
        connection = roster.presence(jid_to_find)
        # show = 'available'
        status = ''

        for answer, presence in connection.items():

            if presence['status']:
                status = presence['status']

        print("\nDetalles del contacto:")
        print(f"Usuario: {jid_to_find}")
        print(f"Mensaje de estado/status: {status}")
        print("")

    async def mostrar_detalles_vecinos(self, distance_vector):
        vecinos = distance_vector.neighbor_costs

        if vecinos:
            print("Vecinos:")
            for vecino in vecinos:
                peso = distance_vector.neighbor_costs[vecino]
                print(f"{vecino}: Peso = {peso}")
        else:
            print("No hay vecinos disponibles.")

    async def enviar_mensaje_contacto(self):  # enviar mensaje a algun contacto

        jid = await ainput('Ingrasa el JID del usuario\n')
        self.actual_chat = jid
        await aprint('\nPresiona x y luego enter para salir\n')
        chatting = True
        while chatting:
            message = await ainput('')
            if message == 'x':
                chatting = False
                self.actual_chat = ''
            else:
                self.send_message(mto=jid, mbody=message, mtype='chat')

    # FUNCION QUE CORRE TODO

    async def start(self, event):
        try:
            self.send_presence()
            await self.get_roster()
            print("Roster: ", self.client_roster)
            myRoster = list(self.client_roster.keys())
            print("Mis contactos: ", {"misvecinos": myRoster})
            self.link_state.sincronizar_roster({"misvecinos": myRoster})
            self.is_connected = True
            print('Logged in')

            asyncio.create_task(self.instancia_usuario())

        # errores en log in
        except IqError as err:
            self.is_connected = False
            print(f"Error: {err.iq['error']['text']}")
            self.disconnect()
        except IqTimeout:
            self.is_connected = False
            print('Error de Time out')
            self.disconnect()

    async def instancia_usuario(self):  # funcion para menu de user
        try:
            while self.is_connected:

                menus.user_menu()  # menu de cliente
                opcion = await ainput("\n>> ")

                # todos los contactios con estado
                if opcion == "1":
                    await self.mostrar_status_contacto()

                # agregar un nuevo usuario
                elif opcion == "2":
                    await self.anadir_contacto()

                # detalles de un usuario
                elif opcion == "3":
                    await self.mostrar_detalles_vecinos(self.distance_vector)

                # chatear con usuario
                elif opcion == "4":
                    await self.enviar_mensaje_contacto()

                # cerrar sesion
                elif opcion == "5":
                    self.disconnect()
                    self.is_connected = False

                # mensaje para todos
                elif opcion == "6":
                    mensaje = str(self.distance_vector.node_name) + ":" + \
                        ",".join(self.distance_vector.neighbor_costs.keys())
                    await self.enviar_mensaje_broadcast(mensaje)

                else:
                    print("\nOpción NO válida, ingrese de nuevo porfavor.")

                await asyncio.sleep(0.1)
        except Exception as e:
            print("An error occurred:", e)


class Borrar_Cliente(slixmpp.ClientXMPP):  # funcion para borrar un cliente
    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.user = jid
        self.add_event_handler("session_start", self.start)

    async def start(self, event):
        self.send_presence()
        await self.get_roster()

        response = self.Iq()
        response['type'] = 'set'
        response['from'] = self.boundjid.user
        fragment = ET.fromstring(
            "<query xmlns='jabber:iq:register'><remove/></query>")
        response.append(fragment)

        try:
            await response.send()
            print(f"Cuenta borrada correctamente: {self.boundjid.jid}!")
        except IqError as e:
            print(f"Error al borrar la cuenta: {e.iq['error']['text']}")
            self.disconnect()
        except IqTimeout:
            print("Sin respuesta del servidor.")
            self.disconnect()

        self.disconnect()

