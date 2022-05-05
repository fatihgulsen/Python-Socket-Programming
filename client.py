import os
import socket
from threading import Thread
from time import sleep

Response = None
ClientSocket = socket.socket()
host = '127.0.0.1'
port = 1233
username = None
print('Waiting for connection')
try:
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))


def recive_message():
    while True:
        try:
            Response = ClientSocket.recv(1024)
            print('\n')
            if Response.decode('utf-8') == '1':
                # print('Mesaj Gönderildi')
                continue
            elif Response.decode('utf-8') == '0':
                # print('Mesaj Gönderilemedi')
                continue
            # else:

            print(Response.decode())
        except Exception as e:
            print('Hata : ', e)


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
    global username
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
    Input = input('Say Something (user+message): ')
    Input = '&!' + Input
    ClientSocket.sendall(str.encode(Input))
    # Response = ClientSocket.recv(1024)
    # # print(Response.decode('utf-8'))
    # if Response.decode('utf-8') == b'1':
    #     print('Mesaj Gönderildi')
    # elif Response.decode('utf-8') == b'0':
    #     print('Mesaj Gönderilemedi')
    pass


def send_message_to_server():
    Input = input('Server Message (only online user): ')
    Input = '&+' + Input
    ClientSocket.sendall(str.encode(Input))
    # Response = ClientSocket.recv(1024)
    # # print(Response.decode('utf-8'))
    # if Response.decode('utf-8') == b'1':
    #     print('Mesaj Gönderildi')
    # elif Response.decode('utf-8') == b'0':
    #     print('Mesaj Gönderilemedi')
    pass


def send_message_to_group():
    Input = input('Say Something (groupname+message): ')
    Input = '&*' + Input
    ClientSocket.sendall(str.encode(Input))
    # Response = ClientSocket.recv(1024)
    # # print(Response.decode('utf-8'))
    # if Response.decode('utf-8') == b'1':
    #     print('Mesaj Gönderildi')
    # elif Response.decode('utf-8') == b'0':
    #     print('Mesaj Gönderilemedi')
    pass


def online_users():
    ClientSocket.sendall(str.encode('//onlineusers'))


def offline_message():
    ClientSocket.sendall(str.encode('//offlinemessage'))


def menu():
    print('Username : ', username[1:])
    print('To Server(1)\nTo User(2)\nTo Group(3)\nOnline Users(9)\nOffline Messages(99)\nQuit(q)\nClear\nMenu')
    while True:
        Input = input('\nSelect menu (Q,1,2,3,9,99,cls,menu): ')
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
        elif Input.capitalize() == '9':
            online_users()
            pass
        elif Input.capitalize() == "99":
            offline_message()
            pass
        elif Input.capitalize() == "CLS":
            os.system('cls')
        elif Input.capitalize() == "MENU":
            print('To Server(1)\nTo User(2)\nTo Group(3)\nOnline Users(9)\nOffline Messages(99)\nQuit(q)\nClear\nMenu')
        else:
            print('Hatalı giriş')
    os.system('exit')
    pass


def register_login_menu():
    Input = input('Register (1)\nLogin (2)\nQuit (q)\nSelect (Q,1,2):  ')
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
        print('Hatali Giriş')
        return False
    pass


Response = ClientSocket.recv(1024)


def main():
    success = register_login_menu()
    os.system('cls')
    if success:
        receive_thread = Thread(target=recive_message)
        receive_thread.start()
        menu()


if __name__ == '__main__':
    main()

ClientSocket.close()
