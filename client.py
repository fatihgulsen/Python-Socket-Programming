from ast import While
import socket
from time import sleep

from numba.cuda import In

Response = None
ClientSocket = socket.socket()
host = '127.0.0.1'
port = 1233

print('Waiting for connection')
try:
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))


def register():
    username = input('Register Username: ')
    username = '%' + username
    ClientSocket.sendall(str.encode(username))
    Response = ClientSocket.recv(1024)
    Response.decode()
    if Response == b'1':
        print('Success')
        return True
    elif Response == b'0':
        print('Denied')
        return False
    else:
        print(Response)
        print('!!Warning!!')
    pass


def login():
    username = input('Login Username: ')
    username = '!' + username
    ClientSocket.sendall(str.encode(username))
    Response = ClientSocket.recv(1024)
    Response.decode('utf-8')
    # print(Response.decode('utf-8'))
    if Response == b'1':
        print('Success')
        return True
    elif Response == b'0':
        print('Denied')
        return False
    else:
        print(Response)
        print('!!Warning!!')


def send_message_to_user():
    Input = input('Say Something: ')
    Input = '&!' + Input
    ClientSocket.sendall(str.encode(Input))
    Response = ClientSocket.recv(1024)
    print(Response.decode('utf-8'))
    pass


def send_message_to_server():
    Input = input('Server Message: ')
    Input = '&+' + Input
    ClientSocket.sendall(str.encode(Input))
    Response = ClientSocket.recv(1024)
    print(Response.decode('utf-8'))
    pass


def send_message_to_group():
    Input = input('Say Something: ')
    Input = '&*' + Input
    ClientSocket.sendall(str.encode(Input))
    Response = ClientSocket.recv(1024)
    print(Response.decode('utf-8'))

    # todo send messae olan bütün  fonsiyonları düzenle
    pass


def menu():
    while True:
        Input = input('To Server(1)\nTo User(2)\nTo Group(3)\nQuit(q)')
        if Input.capitalize() == 'Q':
            break
            pass
        elif Input.capitalize() == '1':
            send_message_to_server()
            pass
        elif Input.capitalize() == '2':
            send_message_to_user()
            pass
        elif Input.capitalize() == '3':
            send_message_to_group()
            pass

    # todo input ile veri la seçenekleri diz ona göre ilerle

    pass


def register_login_menu():
    Input = input('Register (1) \nLogin (2)\nQuit (q) ')
    if Input.capitalize() == 'Q':
        return False
        pass
    elif Input.capitalize() == '1':
        while True:
            success = register()
            if success:
                success = login()
                if success:
                    return True
            pass
    elif Input.capitalize() == '2':
        while True:
            success = login()
            if success:
                return True
        pass
    else:
        return False
    pass


Response = ClientSocket.recv(1024)


def main():
    while True:
        success = register_login_menu()
        if success is False:
            break
        else:
            menu()
            break


if __name__ == '__main__':
    main()

ClientSocket.close()
