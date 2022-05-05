import socket
from _thread import *
from sqlalchemy import null
from pymongo import MongoClient
import pymongo

CONNECTION_STRING = "mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false"
client = MongoClient(CONNECTION_STRING)
socketdb = client['SocketProgramming']

userdb = socketdb['User']
messagedb = socketdb['Message']

ServerSocket = socket.socket()
host = '127.0.0.1'
port = 1233
ThreadCount = 0

all_connection = []

try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waiting for a Connection..')
ServerSocket.listen(5)


def message_control(message, _client, _address):
    return_value = null
    if message.startswith('!'):
        username = message[1:]
        return_value = login_server(username, _client, _address)
    elif message.startswith('%'):
        username = message[1:]
        return_value = register_server(username)
    elif message.startswith('&'):
        message = message[1:]
        return_value = send_message(message, _client)
    elif message == '//onlineusers':
        return_value = online_users(_client)
    elif message == '//offlinemessage':
        return_value = offline_message_send(_client)

    return return_value


def online_users(_client):
    try:
        for i in all_connection:
            _client.sendall(str.encode(i['username'] + ' (online)'))
        return '1'
    except:
        return '0'


def login_server(username, _client, _address):
    myquery = {"username": username}
    mydoc = userdb.find_one(myquery)
    # print(mydoc)
    if mydoc is None:
        return "0"
    else:
        all_connection.append({'username': username, 'client': _client, 'address': _address})
        # print(all_connection)
        return "1"


def register_server(username):
    myquery = {"username": username}
    mydoc = userdb.find_one(myquery)
    # print(mydoc)
    if mydoc is None:
        insert_doc = {'username': username}
        userdb.insert_one(insert_doc)
        return "1"
    else:
        return "0"


def send_message(_message, _client):
    if _message.startswith('+'):  ## Server
        _message = _message[1:]
        send_message_to_server(_message, _client)
        return '1'
    elif _message.startswith('!'):  ## User
        _message = _message[1:]
        send_message_to_user(_message, _client)
        return '1'
    elif _message.startswith('*'):  ## group
        _message = _message[1:]
        send_message_to_group(_message, _client)
        return '1'
    else:
        return '0'

    pass


def send_message_to_server(_message, _client):
    username = None
    for client in all_connection:
        if client['client'] == _client:
            username = client['username']

    for client in all_connection:
        if client['client'] != _client:
            connection = client['client']
            _message = str(username) + ' (Server) : ' + _message
            try:
                connection.sendall(str.encode(_message))
            except Exception as e:
                print('Mesaj hatasi', _message, client['client'])

    pass


def send_message_to_user(_message, _client):
    username = None
    user, message = _message.split('+', 1)
    userClient = None
    for client in all_connection:
        if client['client'] == _client:
            username = client['username']
        elif client['username'] == user:
            userClient = client['client']
        else:
            return '0'
    if userClient:
        userClient.sendall(str.encode(username + '(user) : ' + message))
        insert_doc = {'from': username, 'to': user, 'message': message, 'fowarded': True}
        messagedb.insert_one(insert_doc)
    elif userClient is None:
        insert_doc = {'from': username, 'to': user, 'message': message, 'fowarded': False}
        messagedb.insert_one(insert_doc)

    return username + '(user) : ' + message
    pass


def send_message_to_group(_message, _client):
    username = None
    for client in all_connection:
        if client['client'] == _client:
            username = client['username']
    pass

    pass


def offline_message_send(_client):
    username = None
    for client in all_connection:
        if client['client'] == _client:
            username = client['username']

    myquery = {"to": username, 'forwarded': False}
    newvalues = {"$set": {"forwarded": True}}

    for i in messagedb.find(myquery):
        try:
            _from = i['from']
            message = i['message']
            _client.sendall(str.encode(_from + ' (offline mesaj) : ' + message))
        except Exception as e:
            print('Hata : ', e)
    messagedb.update_many(myquery, newvalues)

    return '1'
    pass


def disconnect_user_delete(_address):
    global all_connection
    all_connection = [i for i in all_connection if not (i['address'] == _address)]
    # print(all_connection)


def threaded_client(connection, _address):
    connection.send(str.encode('Welcome to the Server'))
    while True:
        try:
            data = connection.recv(2048)
            message = data.decode('utf-8')
            reply = message_control(message, connection, _address)
            if not data:
                break
            connection.sendall(str.encode(reply))
        except Exception as e:
            print(e)
            break
    disconnect_user_delete(address)
    connection.close()


if __name__ == '__main__':
    while True:
        try:
            Client, address = ServerSocket.accept()
            print('Connected to: ' + address[0] + ':' + str(address[1]))
            start_new_thread(threaded_client, (Client, address,))
            ThreadCount += 1
            print('Thread Number: ' + str(ThreadCount))
        except Exception as e:
            print(e)
            break

ServerSocket.close()
