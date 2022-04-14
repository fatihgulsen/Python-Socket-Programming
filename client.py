import socket

ClientSocket = socket.socket()
host = '127.0.0.1'
port = 1233

print('Waiting for connection')
try:
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))


def register(username):
    username = input('Register Username: ')
    ClientSocket.send(str.encode(username))
    Response = ClientSocket.recv(1024)
    Response.decode('utf-8')
    if Response == '1':
        print('Access')
        return True
    else:
        print('Denied')
        return False
    pass

def login(username):
    username = input('Login Username: ')
    ClientSocket.send(str.encode(username))
    Response = ClientSocket.recv(1024)
    Response.decode('utf-8')
    if Response == '1':
        print('Access')
        return True
    else:
        print('Denied')
        return False

def send_message():
    Input = input('Say Something: ')
    ClientSocket.send(str.encode(Input))
    Response = ClientSocket.recv(1024)
    print(Response.decode('utf-8'))
    pass


def menu():
    print('To Server')
    print('To User')
    print('to Group')
    pass

Response = ClientSocket.recv(1024)
while True:


def main():
    Input = input('Login or Username : (1,2)')
    if Input == 1:
        login()
    elif Input==0:
        register
    else:
        print('Wrong selection')
    while True:
        send_message()


ClientSocket.close()