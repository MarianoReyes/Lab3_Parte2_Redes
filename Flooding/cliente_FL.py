import xmpp
import slixmpp
from slixmpp.exceptions import IqError, IqTimeout
from slixmpp.xmlstream.stanzabase import ET
from aioconsole import ainput
from aioconsole.stream import aprint
import asyncio
from asyncio import Future  # noqa
from typing import Optional, Union  # noqa
import tkinter as tk  # noqa
from tkinter import messagebox  # noqa
import menus
from slixmpp import Message  # noqa
import base64  # noqa
import math  # noqa
import os  # noqa
import re
from utils import *  # noqa

# implementacion modifica de registro simple extraido de repositorio https://github.com/xmpppy/xmpppy


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
    def __init__(self, jid, password, flooding):

        super().__init__(jid, password)
        self.flooding = flooding
        self.name = jid.split('@')[0]
        self.is_connected = False
        self.actual_chat = ''
        self.client_queue = asyncio.Queue()
        self.received_messages = []

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
                self.mostrar_notificacion("Solicitud de suscripción aceptada de " + str(
                    presence['from']).split('@')[0])  # se muestra una notificacion
            except IqError as e:
                print(
                    f"Error accepting subscription request: {e.iq['error']['text']}")
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

                if (node,mensaje) not in self.received_messages:
                    self.mostrar_notificacion(
                        f"Tienes una comunicación de {node}>> {mensaje}")
                    self.received_messages.append((node, mensaje))
                    
                    await self.enviar_mensaje_broadcast(mensaje)
                


            except:
                # si el mensaje es con el que chatea
                if user == self.actual_chat.split('@')[0]:
                    print_azul(f'{user}: {message["body"]}')
                # notificacion si es otro
                else:
                    self.mostrar_notificacion(
                        f"Tienes una comunicación de {node}>> {mensaje}")

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
                    pass
                    # Send the message to the contact
                    client.send_message(
                        mto=jid, mbody=message_body, mtype='chat')

            print("Message sent to all contacts except yourself.")
        except Exception as e:
            print("Error sending message:", e)

    def mostrar_presencia(self, presence, is_available):

        # verficaciones previas
        if str(presence['from']).split("/")[0] != self.boundjid.bare and "conference" not in str(presence['from']):

            # estado del usaurio
            if is_available:
                show = 'available'
            elif is_available == False:
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
            "Ingresa el JID del usuario que deseas agregar (Ejemplo: usuario@servidor.com): ")
        try:
            self.send_presence_subscription(pto=jid_to_add)
            print(f"Solicitud de suscripción enviada a {jid_to_add}")
            await self.get_roster()
        except IqError as e:
            print(
                f"Error al mandar suscrpcion: {e.iq['error']['text']}")
        except IqTimeout:
            print("Sin respuesta del servidor.")

    async def eliminar_contacto(self):
        try:
            jid_to_remove = input(
                "Ingresa el JID del contacto que deseas eliminar: ")
            await self.del_roster_item(jid_to_remove)
            print(
                f"El contacto {jid_to_remove} ha sido eliminado de tu lista de contactos.")
        except IqError as e:
            print(f"Error al eliminar el contacto: {e.iq['error']['text']}")
        except IqTimeout:
            print("No se recibió respuesta del servidor.")

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
            #print(f"Mensaje de estado: {c[2]}")
            print("")
        print("")

    async def add_neighbors(self):
        try:
            roster = self.client_roster

            for jid in roster.keys():
                # Check if the contact JID matches the pattern 'x_g9@alumchat.xyz'
                if re.match(r'^[a-zA-Z0-9]+_g9@alumchat\.xyz$', jid):
                    # Extract the 'x' value by splitting on '_' and taking the first part
                    node_name = jid.split('_')[0]

                    node = jid.split('@')[0]

                    if node != self.name:
                        # Add the 'x' value to the neighbor_costs dictionary with a value of 1
                        self.flooding.neighbors.append(node_name)

            print("Vecinos linkeados.")
        except Exception as e:
            print("Error al linkear con vecinos:", e)

    async def mostrar_detalles_vecinos(self, flooding):
        vecinos = flooding.neighbors

        if vecinos:
            print("Vecinos:")
            for vecino in vecinos:
                print(f"{vecino}")
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
            await self.add_neighbors()
            while self.is_connected:
                menus.user_menu()  # menu de cliente
                opcion = await ainput("\n>> ")

                # todos los contactios con estado
                if opcion == "1":
                    await self.mostrar_status_contacto()

                # agregar un nuevo usuario
                elif opcion == "2":
                    await self.anadir_contacto()

                # agregar un nuevo usuario
                elif opcion == "3":
                    await self.eliminar_contacto()

                # detalles de un usuario
                elif opcion == "4":
                    await self.mostrar_detalles_vecinos(self.flooding)

                # chatear con usuario
                elif opcion == "5":
                    await self.enviar_mensaje_contacto()

                # cerrar sesion
                elif opcion == "6":
                    self.disconnect()
                    self.is_connected = False

                # mensaje para todos
                elif opcion == "7":
                    mensaje = input('Ingresa el mensaje: ')
                    destino = input('Ingresa el destino: ')
                    await self.enviar_mensaje_broadcast(f'Fuente: {self.flooding.node_name} Para: {destino} dice: {mensaje}')

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
