######################################################################
# Author: David Newswanger
# username: newswangerd
#
# Assignment: Final Project
# Purpose: This program is a server that relays messages from the enigma chat client
#
# Acknowledgements: https://wiki.python.org/moin/TcpCommunication
#                   http://stackoverflow.com/questions/2957116/make-2-functions-run-at-the-same-time
#
######################################################################

import socket

def main():
    IP = '104.131.187.248' # Change to 127.0.0.1 to run the server locally.
    #IP = '127.0.0.1'
    port = 5005
    buffer = 2048

    # all_messages = [recipient: {sender: [message1, message2...]}}
    all_messages = {}

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((IP, port))

    print "Starting up server. IP: %s. Port: %s" % (IP, port)

    while True:
        s.listen(5)

        # Waits for new connections.
        conn, addr = s.accept()
        m = []
        data = conn.recv(buffer)

        # When connection recieved, message split into new array m
        m = data.split("\n")

        # m[0] contains the server command (send, check or receive)
        if m[0] == "send":
            send(all_messages, m, conn)
        elif m[0] == "receive":
            receive(all_messages, m, conn)
        elif m[0] == "check":
            check_messages(all_messages,m,conn)
        else:
            conn.sendall("202")
        conn.close()

# m = cmd, dest user, sender, messge
def send(all_messages, m, conn):
    '''
    Takes the encrypted messages sent by client and stores them in dictionairy

    :param all_messages: dictionairy with all messages
    :param m: list with new messages from client
    :param conn: connection object
    :return: Nont
    '''

    # If the recipient is not in the message dictionairy, a new entry is added.
    # If the recipient is in the entry dictionairy, a new list of messages is added
    if m[1] in all_messages.keys():

        # If the sender is already in the dictionairy of senders, the message is appended to the list for
        # that sender. Else, a new sender is added to the recipient dictionairy.
        if m[2] in all_messages[m[1]].keys():
            all_messages[m[1]][m[2]].append(m[3])
        else:
            all_messages[m[1]][m[2]] = [m[3]]
    else:
        all_messages[m[1]] = {m[2]: [m[3]]}
    conn.sendall("100")
    if all_messages != {}: print all_messages

# m = cmd, dest user, sender
def receive(all_messages, m, conn):
    '''
    Downloads unread messages from server.

    :param all_messages: dictionairy with all messages
    :param m: messages from client
    :param conn: connection object
    :return: None
    '''
    to_send = "201"

    # Pulls the messages for the user and dest user from the dictionairy.
    # If the user has no more mail, deletes the dictionairy entry.
    if m[1] in all_messages.keys():
        if m[2] in all_messages[m[1]]:
            to_send = "200\n"
            for x in all_messages[m[1]][m[2]]:
                to_send += x + '\n'
            del all_messages[m[1]][m[2]]
        if all_messages[m[1]] == {}:
            del all_messages[m[1]]
    conn.sendall(to_send)

# m = cmd, current user
def check_messages(all_messages, m, conn):
    '''
    Checks to see if the current user has any new messages from users they aren't actively chatting with

    :param all_messages: dictionairy with all messages
    :param m: messages from client
    :param conn: connection object
    :return: None
    '''
    to_send = ""

    # If the current user is in the dictionairy with all the messages, returns the names of the users
    # who have sent the current user a message.
    if m[1] in all_messages.keys():
        if all_messages[m[1]] != {}:
            to_send += '200\n'
            for x in all_messages[m[1]].keys():
                to_send += x + '\n'
        else:
            to_send = '201'
    else:
        to_send = '201'

    conn.sendall(to_send)

main()
