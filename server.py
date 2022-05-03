import socket
import os
from _thread import *

from sqlalchemy import null
from pymongo import MongoClient
import pymongo

CONNECTION_STRING = "mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false"
client = MongoClient(CONNECTION_STRING)
socketdb = client['SocketProgramming']

userdb = socketdb['User']
userlogindb = socketdb['User_Login']
messagedb = socketdb['Message']

ServerSocket = socket.socket()
host = '127.0.0.1'
port = 1233
ThreadCount = 0

all_connection = {}
# todo ip ve username sakla ona göre iletim sağlanacak

try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waitiing for a Connection..')
ServerSocket.listen(5)

def message_control(message):
    return_value = null
    if message.startswith('!'):
        username = message[1:]
        return_value = login_server(username)
    elif message.startswith('%'):
        username = message[1:]
        return_value = register_server(username)
    elif message.startswith('&'):
        message = message[1:]

    return return_value
    
def login_server(username):
    return '1'
    #todo login yap register benzer ancak her girişte mesaj kontrolü sağlanacak
    # ileti ysapıldığına dair
    pass

def register_server(username):
    myquery = { "username": username }
    mydoc = userdb.find_one(myquery)
    print(mydoc)
    if mydoc is None:
        return "1"
    else:
        return "0"

def threaded_client(connection):
    connection.send(str.encode('Welcome to the Server'))
    while True:
        try:
            data = connection.recv(2048)
            message = data.decode('utf-8')
            reply = message_control(message)
            if not data:
                break
            connection.sendall(str.encode(reply))
        except Exception as e:
            break
    connection.close()

while True:
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, ))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))
    
ServerSocket.close()