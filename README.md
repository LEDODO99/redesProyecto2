How to execute:
Make sure you have the next python libraries and versions:
-pyasn1 v0.3.6
-pyasn1-modules v0.1.5
-sleekxmpp v1.3.3

If you are unsure of your version you can run the next command to install the propper libraries.
pip install pyasn1==0.3.6 pyasn1-modules==0.1.5 sleekxmpp==1.3.3

After making sure your libraries and version are in order run the command
python LuisDelgadoXMPPClient.py
or
python3 LuisDelgadoXMPPClient.py
Make sure you are running it in python 3.

You'll be met with the next menu.
1. Login
2. Signup
3. Salir
Please enter the coresponding number to the action you are trying to achieve. 1 to log in, 2 to sign up (register new account), 3 quit the program.

Whichever you chose you'll be asked the username and pasword of the account. Please include both the username and domain-name. (ej. username@example.com). Afterwards if you chose signup you'll recieve a a message that sais if your account creation was successful or not and will be returned to the previous menu. If you chose Login and the username and password were correct you'll be taken to the next menu.

Ingrese la opcion que desee:
1. imprimir Roster.
2. Agregar un usuario a tu lista
3. Enviar Mensaje directo
4. Crear chat grupal
5. Unirse a un chat grupal
6. Enviar mensaje a grupo
7. Eliminar Cuenta
8. Cerrar Sesion

-Option 1 will print you contact list
-Option 2 will ask you for the username of a contact you'd like to add. Again, please enter the Username and domain-name (ej. username@example.com). afterwards the user will be added to you contact list and will apear whenever you print it.
-Option 3 will ask you for the username of the contact to send the direct message. Again please enter the username and domain-name (ej. username@example.com). Afterwards it will ask for the message you'd like to send.
-Option 4 will ask you for the name of the room you'd like to create. Please enter roomname followed by @ and then conference.domain (ej. groupchatName@conference.example.com).
-Option 5 will ask you for the name of the room you'd like to join. Again, please enter roomname followed by @ and then conference.domain (ej. groupchatName@conference.example.com).
-Option 6 will ask you for the name of the room you'd like to send a message to. Again, please enter roomname followed by @ and then conference.domain (ej. groupchatName@conference.example.com). Afterwards it will ask for the message you'd like to send.
-Option 7 will delete the account you are currently on from the domain/server and disconect you. Afterwards you'll be sent to the login menu. if you try to login to the now deleted account you won't be able to.
-Option 8 will log you out and return you to the login menu.