import os
import socket
from threading import Thread

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


def receive_message():
    """
    Sunucu tarafından gelen mesajları okur. Thread sayesinde kullanıcı mesaj bekleme satırına girmez
    :return:
    """
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
            break


def register():
    """
    Kullanıcı kayıt işlemleri yapılır. Sunucuya gönderirken prefix ekler
    :return:True veya False , kayıt işleminin başarısı
    """
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
    """
    Kullanıcı giriş işlemleri yapılır. Sunucuya gönderirken prefix ekler
    :return: True veya False (Bool) kullanıcı giriş başarısı
    """
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
    """
    Belirtilen kullanıcıya mesaj gönderir. Sunucuya gönderirken prefix ekler
    :return: None
    """
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
    """
    Sunucuya bağlı tüm kullancılara mesaj yollanmasını sağlar. Sunucuya gönderirken prefix ekler
    :return: None
    """
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
    """
    Belirtilen gruba mesaj yollanmasını sağlar. Sunucuya gönderirken prefix ekler
    :return: None
    """
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
    """
    Sunucuya bağlı kullanıcıları listeler. Sunucuya direkt mesaj yollar
    :return: None
    """
    ClientSocket.sendall(str.encode('//onlineusers'))


def all_users():
    """
    Sunucuya kayıtlı tüm kullanıcıları listeler. Sunucuya direkt mesaj yollar
    :return: None
    """
    ClientSocket.sendall(str.encode('//allusers'))


def group_members():
    """
    Girilen grup ismine göre üye tüm kullanıcıları listeler. Sunucuya gönderirken prefix ekler
    :return: None
    """
    groupname = input('Group Name : ')
    ClientSocket.sendall(str.encode('//group+' + groupname))


def user_group_members():
    """
    Kullanıcının üye olduğu tüm grupları listeler. Sunucuya gönderirken prefix ve username direkt yollanır
    :return: None
    """
    global username
    if username is not None:
        ClientSocket.sendall(str.encode('//usermember+' + username))


def create_group():
    """
    Girilen grup isminde grup kurmak için kullanılır. Sunucuya gönderirken prefix ekler
    :return: None
    """
    Input = input('Create Group name : ')
    if Input is not None:
        ClientSocket.sendall(str.encode("//create+"+Input))
    pass


def add_group():
    """
    Mevcut gruba üye eklemeyi sağlar. Sunucuya gönderirken prefix ekler
    :return: None
    """
    Input = input('Add group member (groupname+user+user..) : ')
    if Input is not None:
        ClientSocket.sendall(str.encode("//addgroup+"+Input))
    pass


def offline_message():
    """
    Giriş yapmış kullanıcının offline iken görmek istediği tüm mesajları görüntüler. Sunucuya direkt olarak yollar
    :return:
    """
    ClientSocket.sendall(str.encode('//offlinemessage'))


def menu():
    """
    Kullanıcı menusu
    :return: None
    """
    print('Username : ', username[1:])
    print('To Server(1)\nTo User(2)\nTo Group(3)\nUser Menu(9)\nOffline Messages(99)\nQuit(q)\nClear(c)\nMenu(m)')
    while True:
        Input = input('\nSelect menu (Q,1,2,3,9,99,c,m): ')
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
            group_menu()
            pass
        elif Input.capitalize() == '9':
            users_menu()
            pass
        elif Input.capitalize() == "99":
            offline_message()
            pass
        elif Input.capitalize() == 'C':
            os.system('cls')
            print('Username : ', username[1:])
            pass
        elif Input.capitalize() == 'M':
            print('Username : ', username[1:])
            print('To Server(1)\nTo User(2)\nTo Group(3)\nOnline Users(9)\nOffline Messages(99)\nQuit(q)\nClear\nMenu')
            pass
        else:
            print('Hatalı giriş')
    os.system('exit')
    pass


def register_login_menu():
    """
    Kullanıcı kayıt menusu
    :return: None
    """
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


def users_menu():
    """
    Kullanıcı işlem menusu
    :return: None
    """
    print('\nAll Users(1)\nOnline Users(2)\nGroup Members(3)\nGroup List(4)\n')
    Input = input('\nSelect menu (1,2,3,4): ')
    if Input == '1':
        all_users()
    elif Input == '2':
        online_users()
    elif Input == '3':
        group_members()
    elif Input == '4':
        user_group_members()


def group_menu():
    """
    Kullanıcı grup için işlem menusu
    :return: None
    """
    print("Group message(1)\nCreate Group(2)\nAdd member Group(3)")
    Input = input("Select menu (1,2,3): ")
    if Input == '1':
        send_message_to_group()
    elif Input == '2':
        create_group()
    elif Input == '3':
        add_group()


Response = ClientSocket.recv(1024)


def main():
    """
    main
    :return:
    """
    success = register_login_menu()
    os.system('cls')
    if success:
        receive_thread = Thread(target=receive_message)
        receive_thread.start()
        menu()


if __name__ == '__main__':
    main()

ClientSocket.close()
