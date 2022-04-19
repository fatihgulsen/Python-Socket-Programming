from ast import While
import socket
from time import sleep

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
    ClientSocket.send(str.encode(username))
    Response = ClientSocket.recv(1024)
    Response.decode('utf-8')
    if Response == '1':
        print('Success')
        return True
    elif Response == '0':
        print('Denied')
        return False
    else:
        print(Response)
        print('!!Warning!!')
    pass

def login():
    username = input('Login Username: ')
    username = '!' + username
    ClientSocket.send(str.encode(username))
    Response = ClientSocket.recv(1024)
    Response.decode('utf-8')
    #print(Response.decode('utf-8'))
    if Response == '1':
        print('Success')
        return True
    elif Response == '0':
        print('Denied')
        return False
    else:
        print(Response)
        print('!!Warning!!')


def send_message():
    Input = input('Say Something: ')
    Input = '&' + Input
    ClientSocket.send(str.encode(Input))
    Response = ClientSocket.recv(1024)
    print(Response.decode('utf-8'))
    pass


def menu():
    print('To Server(1)\nTo User(2)\nTo Group(3)\nQuit(q)')
    pass

Response = ClientSocket.recv(1024)

def main():
    while True:
        success = register()
        
        
if __name__ == '__main__':
    main()

ClientSocket.close()