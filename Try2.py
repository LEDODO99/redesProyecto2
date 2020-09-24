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

class RegisterBot(sleekxmpp.ClientXMPP):

    """
    A basic bot that will attempt to register an account
    with an XMPP server.

    NOTE: This follows the very basic registration workflow
          from XEP-0077. More advanced server registration
          workflows will need to check for data forms, etc.
    """

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start, threaded=True)

        # The register event provides an Iq result stanza with
        # a registration form from the server. This may include
        # the basic registration fields, a data form, an
        # out-of-band URL, or any combination. For more advanced
        # cases, you will need to examine the fields provided
        # and respond accordingly. SleekXMPP provides plugins
        # for data forms and OOB links that will make that easier.
        self.add_event_handler("register", self.register, threaded=True)

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
        self.send_presence()
        self.get_roster()

        # We're only concerned about registering, so nothing more to do here.
        self.disconnect()

    def register(self, iq):
        """
        Fill out and submit a registration form.

        The form may be composed of basic registration fields, a data form,
        an out-of-band link, or any combination thereof. Data forms and OOB
        links can be checked for as so:

        if iq.match('iq/register/form'):
            # do stuff with data form
            # iq['register']['form']['fields']
        if iq.match('iq/register/oob'):
            # do stuff with OOB URL
            # iq['register']['oob']['url']

        To get the list of basic registration fields, you can use:
            iq['register']['fields']
        """
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
        t=threading.Thread(target=self.client_mannager,daemon=True)
        t.run()
        
    def client_mannager(self):
        while (1):
            a=input("Ingrese la opcion que desee:\n1. imprimir Roster.\n2. Agregar un usuario a tu lista\n3. Enviar Mensaje directo\n4. Salir\n")
            if (a=="1"):
                xmpp.print_contacts()
            if (a=="2"):
                nombre=input("Ingrese el JID de el contacto a agregar")
                self.send_presence_subscription(pto=nombre)
            if(a=="3"):
                recipient=input("Ingrese el usuario del receptor: ")
                body=input("Ingrese el mensaje: ")
                self.send_dm(recipient,body)
            if (a=="4"):
                break
        self.disconnect()

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
        print("[%(from)s]: %(body)s"%msg)

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
            if xmpp.connect():
                # If you do not have the dnspython library installed, you will need
                # to manually specify the name of the server if it does not match
                # the one in the JID. For example, to use Google Talk you would
                # need to use:
                #
                # if xmpp.connect(('talk.google.com', 5222)):
                #     ...
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


    # If you are working with an OpenFire server, you may need
    # to adjust the SSL version used:
    # xmpp.ssl_version = ssl.PROTOCOL_SSLv3

    # If you want to verify the SSL certificates offered by a server:
    # xmpp.ca_certs = "path/to/ca/cert"

    # Connect to the XMPP server and start processing XMPP stanzas.
    
    
#als=Jabber("LuisDelgadoTry2","1234","redes2020.xyz")