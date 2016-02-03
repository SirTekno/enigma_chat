######################################################################
# Author: David Newswanger
# username: newswangerd
#
# Assignment: Final Project
# Purpose: This program encrypts messages using Enigma and relays them to a server.
#
# Acknowledgements: https://wiki.python.org/moin/TcpCommunication
#                   http://stackoverflow.com/questions/2957116/make-2-functions-run-at-the-same-time
#
######################################################################

import socket
from enigma import Enigma
import sys
from threading import Thread
import time

# Server Codes:
# Command (0-9), Response(00-99)
# 1 - send
# 100- Message sent
# 101- Message not sent
# 2- receive
# 200 messages received
# 201 no messages to receive
# 202 error

class Client():
    ''' The Client object handles sending and receiving messages from the server '''

    def __init__(self, user, key, dest_user, port=5005, ip="127.0.0.1", buffer=2048):
        ''' Initializes the client with a username, key, and all the  necesary connection variables. '''
        self.port = port
        self.ip = ip
        self.buffer = buffer
        self.messages = []
        self.user = user
        self.key = key
        self.dest_user = dest_user
        self.active = True

        self.server_responses = {
            '100': 'Message Sent',
            '101': 'Error Sending Message',
            '200': 'Message(s) received',
            '201': 'No new messages',
            '202': 'Error receiving messages'
        }

        # List of commands the user can enter in the client.
        self.commands = {
            '/get': ['get_messages', 'Receives your messages.'],
            '/display': ['display_messages', 'Displays all the messages that you have received.'],
            '/decrypt': ['decrypt_message', 'Decrypts a specific message and displays the plain text.'],
            '/help': ['show_commands', 'Shows a list of all the available commands.'],
            '/history': ['chat_history', 'Shows the plaintext for all the messages in this session.'],
            '/set_key': ['change_key', 'Changes the conversation key for the session.'],
            '/change_recipient': ['change_recipient', 'Changes the username of the person you are talking to.'],
            '/exit': ['exit', 'Closes the application.'],
            '/check': ['check_messages', 'Checks to see if any new messages have been recieved from anyone other than the person you are talking to.']
        }

    def send(self, message):
        ''' Sends a message to the server using sockets. '''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, self.port))
        s.send(message)
        response = s.recv(self.buffer)
        s.close()

        return response

    def send_message(self, message):
        ''' Encrypts a message and sends it to a specified user. '''

        cipher = Enigma(message, self.key, True)

        to_send = "%s\n%s\n%s\n%s" % ("send", self.dest_user, self.user, cipher.cipher_text)
        response = self.send(to_send)

    def get_messages(self):
        ''' Downloads and displays all of the messages that have recently been recieved by the current user. '''
        to_send = "%s\n%s\n%s" % ("receive", self.user, self.dest_user)
        response = self.send(to_send)

        response = response.split('\n')

        # If new messages have been recieved, prints out the sender and the message
        if response[0] == '200':
            messages = response[1:]
            messages.pop()
            for x in messages:
                cipher = Enigma(x, self.key, False)
                self.messages.append({'sender': self.dest_user, 'cipher_text': x, 'plain_text': cipher.plain_text})

                print "%s: %s" % (self.dest_user, cipher.plain_text)

    def display_messages(self):
        ''' Displays all of the messages along with the sender, the message number, the plain text and cipher text '''
        print '\n'
        for (i, val) in enumerate(self.messages):
            print "Message number: " + str(i)
            print "Sender: " + val['sender']
            print "Cipher text: " + val['cipher_text']
            print "Plain  text: " + val['plain_text'] + "\n"

        if len(self.messages) == 0:
            print "No messages to display."

    def decrypt_message(self):
        ''' Allows the user to decrypt a specific message number if the master key  isn't right. '''
        while True:
            try:
                message_no = int(raw_input("Enter the message number: "))
                break
            except ValueError:
                print "Please enter a number."

        key = raw_input("Enter the secret key: ")

        try:
            message = self.messages[message_no]
            cipher = Enigma(message['cipher_text'], key, False)
            self.messages[message_no]['plain_text'] = cipher.plain_text

            print cipher.plain_text
        except IndexError:
            print "That message does not exist."

    def show_commands(self):
        ''' Displays a list of all the commands that the client includes. '''
        print "+-----------------------------------------------------------------------------------+"
        for x in self.commands:
            print "%s: %s" % (x, self.commands[x][1])
        print "+-----------------------------------------------------------------------------------+"

    def change_key(self):
        ''' Prompts the user to change the current conversation key '''
        self.key = raw_input('Enter a new conversation key: ')

    def chat_history(self):
        ''' Displays all the messages that have been recieved this session '''
        for x in self.messages:
            print "%s: %s" % (x['sender'], x['plain_text'])

    def change_recipient(self):
        ''' Change the username of the person you are talking to '''
        self.change_key(self)
        self.dest_user = raw_input('Enter the username of the person you want to talk to: ')

        print "You are now messaging: " + self.dest_user

    def exit(self):
        ''' Exits the program. '''
        self.active = False
        print 'Goodbye!'

        sys.exit(0)

    def ping(self):
        ''' Periodically pings the server to recieve messages from it. '''
        while self.active:
            self.get_messages()
            time.sleep(5)

    def check_messages(self):
        ''' Checks to see if any new messages have come in from any other users. '''
        response = self.send('%s\n%s' % ('check', self.user))
        response = response.split('\n')
        if response[0] == "200":
            response = response[1:]
            response.pop()
            new = ""
            for x in response:
                new += x + ', '
            print "New Messages from: " + new
        elif response[0] == "201":
            print self.server_responses[response[0]]
        else:
            print "Error"

def main():
    user = raw_input('Enter your username: ')
    dest_user = raw_input('Enter the name of the user you would like to talk to: ')
    key = raw_input('Enter conversation key: ')
    client = Client(user, key, dest_user, ip="104.131.187.248")

    # Starts pinging the server ever few seconds for a new message
    Thread(target = client.ping).start()
    print "You are now talking to %s. Type a message or '/help' for a list of options." % client.dest_user

    while True:

        # Wait for user input. If user input is a command, execute command. Else, send user input
        # to current destination user.
        command = raw_input("")
        if len(command) > 0 and command[0] == '/':
            if command in client.commands.keys():
                to_execute = getattr(client, client.commands[command][0])
                to_execute()
            else: print "That is not a valid command."
        elif command == "":
            pass
        else: client.send_message(command)

main()
