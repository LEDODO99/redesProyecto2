# -*- coding: utf-8 -*-

"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2011  Nathanael C. Fritz
    This file is part of SleekXMPP.
    See the file LICENSE for copying permission.
"""

import sys
import logging
import getpass
import threading
from optparse import OptionParser

import sleekxmpp
from sleekxmpp.exceptions import IqError, IqTimeout


# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input

#bot para registrar un nuevo usuario 
#Estraido de https://searchcode.com/file/58168360/examples/register_account.py/
class RegisterBot(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.start, threaded=True)
        self.add_event_handler("register", self.register, threaded=True)

    def start(self, event):
        self.send_presence()
        self.get_roster()

        # We're only concerned about registering, so nothing more to do here.
        self.disconnect()

    def register(self, iq):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password

        try:
            resp.send(now=True)
            print("Se creo la cuenta para:",self.boundjid.user, ".\n En dominio:",self.boundjid.domain)
        except IqError as e:
            logging.error("Could not register account: %s" %
                    e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            logging.error("No response from server.")
            self.disconnect()
#Extraido de https://github.com/fritzy/SleekXMPP/blob/develop/examples/roster_browser.py
#Lo extraido fue la capacidad de imprimir el roster
class RosterBrowser(sleekxmpp.ClientXMPP):

    """
    A basic script for dumping a client's roster to
    the command line.
    """

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster. We need threaded=True so that the
        # session_start handler doesn't block event processing
        # while we wait for presence stanzas to arrive.
        self.add_event_handler("session_start", self.start, threaded=True)
        self.add_event_handler("changed_status", self.wait_for_presences, threaded=True)
        self.add_event_handler("message", self.message, threaded=True)
        self.add_event_handler("groupchat_message", self.muc_message)

        self.received = set()
        self.presences_received = threading.Event()

    def start(self, event):
        """
        Process the session_start event.
        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.
        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        try:
            self.get_roster()
        except IqError as err:
            print('Error: %s' % err.iq['error']['condition'])
        except IqTimeout:
            print('Error: Request timed out')
        self.send_presence()
        # Inicia el thread para manejar el cliente
        t=threading.Thread(target=self.client_mannager,daemon=True)
        t.run()
    def send_message_to_group(self,jid,body):
        m=self.Message()
        m['to']=jid
        m['type']='groupchat'
        m['body']=body
        m.send()
    #Funcion de borrar cuenta actual
    def delete_account(self):
        a="""
            <iq type='set' id='unreg1'>
                <query xmlns='jabber:iq:register'>
                    <remove/>
                </query>
            </iq>
        """
        self.send_raw(a)
        print("Se eliminó la cuenta")
        
    #Funcion para manejar el cliente
    def client_mannager(self):
        while (1):
            a=input("Ingrese la opcion que desee:\n1. imprimir Roster.\n2. Agregar un usuario a tu lista\n3. Enviar Mensaje directo\n"+
            "4. Crear chat grupal\n5. Unirse a un chat grupal\n6. Enviar mensaje a grupo\n7. Eliminar Cuenta\n8. Cerrar Sesion\n")
            if (a=="1"):
                self.print_contacts()
            if (a=="2"):
                nombre=input("Ingrese el JID de el contacto a agregar")
                self.send_presence_subscription(pto=nombre)
            if (a=="3"):
                recipient=input("Ingrese el usuario del receptor: ")
                body=input("Ingrese el mensaje: ")
                self.send_dm(recipient,body)
            if (a=="4"):
                self.create_room(input("Ingrese el nombre del grupo: "))
            if (a=="5"):
                self.create_room(input("Ingrese el nombre del grupo: "))
            if (a=="6"):
                group=input("ingrese el nombre del grupo: ")
                body=input("Ingrese el mensaje: ")
                self.send_message_to_group(group,body)
            if (a=="7"):
                self.delete_account()
                break
            if (a=="8"):
                break
        self.disconnect()
    #Funcion para recibir mensajes de grupos
    def muc_message(self, msg):
        if msg['mucnick'] != self.boundjid.username:
            print("[Groupchat: ",msg['from'].bare,"]","\n\t[%(mucnick)s]: %(body)s"%msg)
    #Funcion para crear/unirse a un chat grupal
    def create_room(self, room):
        try:
            self.add_event_handler("muc::%s::got_online" % room,self.muc_online)
            self.plugin['xep_0045'].joinMUC(room,self.boundjid.username,wait=True)
        except IqError as err:
            print('Error: %s' % err.iq['error']['condition'])
        except IqTimeout:
            print('Error: Request timed out')
    def muc_online(self, presence):
        if presence['muc']['nick'] != self.boundjid.username:
            self.send_message(mto=presence['from'].bare,mbody="Hello, %s %s" % (presence['muc']['role'],presence['muc']['nick']),mtype='groupchat')
    #Funcion para recibir mensajes directos
    def message(self, msg):
        """
        Process incoming message stanzas. Be aware that this also
        includes MUC messages and error messages. It is usually
        a good idea to check the messages's type before processing
        or sending replies.

        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.
        """
        if (msg["type"]in ('normal','chat')):
            print("[%(from)s]: %(body)s"%msg)
    #Enviar mensaje a persona en específico
    def send_dm(self, recipient, body):
        self.send_message(mto=recipient,mbody=body,mtype='chat')

    def wait_for_presences(self, pres):
        """
        Track how many roster entries have received presence updates.
        """
        self.received.add(pres['from'].bare)
        if len(self.received) >= len(self.client_roster.keys()):
            self.presences_received.set()
        else:
            self.presences_received.clear()

    #Imprime los contactos del roster
    #Extraido de https://github.com/fritzy/SleekXMPP/blob/develop/examples/roster_browser.py
    def print_contacts(self):
        try:
            self.get_roster()
        except IqError as err:
            print('Error: %s' % err.iq['error']['condition'])
        except IqTimeout:
            print('Error: Request timed out')
        
        print('Waiting for presence updates...\n')
        self.presences_received.wait(5)
        print('Roster for %s' % self.boundjid.bare)
        groups = self.client_roster.groups()
        for group in groups:
            print('\n%s' % group)
            print('-' * 72)
            for jid in groups[group]:
                sub = self.client_roster[jid]['subscription']
                name = self.client_roster[jid]['name']
                if self.client_roster[jid]['name']:
                    print(' %s (%s) [%s]' % (name, jid, sub))
                else:
                    print(' %s [%s]' % (jid, sub))

                connections = self.client_roster.presence(jid)
                for res, pres in connections.items():
                    show = 'available'
                    if pres['show']:
                        show = pres['show']
                    print('   - %s (%s)' % (res, show))
                    if pres['status']:
                        print('       %s' % pres['status'])

if __name__ == '__main__':
    while (1):
        a=input("Seleccione lo que desea hacer\n1. Login\n2. Signup\n3. Salir\n")
        if (a=="1"):
            jid = raw_input("Username: ")
            password = getpass.getpass("Password: ")
            xmpp = RosterBrowser(jid, password)
            xmpp.register_plugin('xep_0030') # Service Discovery
            xmpp.register_plugin('xep_0045') # Multi-User Chat
            xmpp.register_plugin('xep_0199') # XMPP Ping
            if xmpp.connect():
                xmpp.process(block=True)
            else:
                print("Unable to connect.")
                exit()
        if (a=="2"):
            jid = raw_input("Username: ")
            password = getpass.getpass("Password: ")
            xmpp = RegisterBot(jid,password)
            xmpp.register_plugin('xep_0030') # Service Discovery
            xmpp.register_plugin('xep_0004') # Data forms
            xmpp.register_plugin('xep_0066') # Out-of-band Data
            xmpp.register_plugin('xep_0077') # In-band Registration
            xmpp['xep_0077'].force_registration = True
            if xmpp.connect():
                # If you do not have the dnspython library installed, you will need
                # to manually specify the name of the server if it does not match
                # the one in the JID. For example, to use Google Talk you would
                # need to use:
                #
                # if xmpp.connect(('talk.google.com', 5222)):
                #     ...
                xmpp.process(block=True)
        if (a=="3"):
            exit()

