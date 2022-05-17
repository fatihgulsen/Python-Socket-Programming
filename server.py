import socket
from _thread import *
from pymongo import MongoClient

CONNECTION_STRING = "mongodb://localhost:27017"
client = MongoClient(CONNECTION_STRING)
socketdb = client['SocketProgramming']

userdb = socketdb['User']
messagedb = socketdb['Message']
groupdb = socketdb['Group']

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
    """
    Gelen mesajları kontrol eder. Alt fonksiyonlara ayrıştırır.
    :param message: Gelen mesaj (str)
    :param _client: Gönderen client (socket.client)
    :param _address: Gönderen adres (socket.address)
    :return:  1 veya 0 (str)
    """
    return_value = None
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
    elif message == '//allusers':
        return_value = all_users(_client)
    elif message.startswith('//group+'):
        return_value = group_member(_client, message)
    elif message.startswith('//usermember+'):
        return_value = user_group_member(_client, message)
    elif message.startswith('//create+'):
        return_value = create_group(_client, message)
    elif message.startswith('//addgroup+'):
        return_value = add_group(_client, message)

    return return_value


def online_users(_client):
    """
    Sokete bağlı tüm clientlerin giriş yapıldıktan sonra kullanıcı adını
    hedef cliente yollar
    :param _client: Gönderen client (socket.client)
    :return: 1 veya 0 (str)
    """
    try:
        res = [ele['username'] for ele in all_connection]
        users = ", ".join(res)
        # print(users)
        _client.sendall(str.encode('Online users : ' + users))
        return '1'
    except:
        return '0'


def login_server(username, _client, _address):
    """
    Clientlerin login olmasını sağlar
    :param username: Giriş yapılmak istenen kullanıcı adı (str)
    :param _client: Giriş yapmak isteyen client (socket.client)
    :param _address: Giriş yapmak isteyen adres (socket.address)
    :return: 1 veya 0 (str) , 1 onay 0 red
    """
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
    """
    Clientlerin kullanıcı kayıt etmelerini sağlar
    :param username: Kayıt edilmek istenen kullanıcı adı (str)
    :return: 1 veya 0 (str) 1 onay 0 red
    """
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
    """
    Gelen mesajları prefixlerine göre ayırmayı sağlar
    :param _message: Gelen mesaj (str)
    :param _client: Gönderen client (socket.client)
    :return: 1 veya 0 (str)
    """
    if _message.startswith('+'):  # Server
        _message = _message[1:]
        send_message_to_server(_message, _client)
        return '1'
    elif _message.startswith('!'):  # User
        _message = _message[1:]
        send_message_to_user(_message, _client)
        return '1'
    elif _message.startswith('*'):  # Group
        _message = _message[1:]
        send_message_to_group(_message, _client)
        return '1'
    else:
        return '0'

    pass


def send_message_to_server(_message, _client):
    """
    Server a bağlı tüm clientlere mesajı iletir.
    :param _message: Gönderilmek istenen mesaj (str)
    :param _client: Gönderen client (socket.client)
    :return: None
    """
    username = client_to_username(_client)
    for client in all_connection:
        if client['client'] != _client:
            connection = client['client']
            _message = str(username) + ' (Server) : ' + _message
            try:
                connection.sendall(str.encode(_message))
            except Exception as e:
                print('Message Error', _message, client['client'])

    pass


def send_message_to_user(_message, _client):
    """
    Belirlenen kullanıcı adına mesaj yollar
    :param _message: Gönderilmek istenen  mesaj (str) exp = (username+message)
    :param _client: Gönderen client (socket.client)
    :return: client.username + (user) + message (str)
    """
    fromUsername = None
    user, message = _message.split('+', 1)
    toUserClient = None

    for client in all_connection:
        if client['client'] == _client:
            fromUsername = client['username']
        elif client['username'] == user:
            toUserClient = client['client']
        else:
            return '0'
    if toUserClient:
        toUserClient.sendall(str.encode(fromUsername + '(user) : ' + message))
        insert_doc = {'from': fromUsername, 'to': user, 'message': message, 'forwarded': True}
        messagedb.insert_one(insert_doc)
    elif toUserClient is None:
        insert_doc = {'from': fromUsername, 'to': user, 'message': message, 'forwarded': False}
        messagedb.insert_one(insert_doc)

    return fromUsername + '(user) : ' + message
    pass


def send_message_to_group(_message, _client):
    """
    Belirlenen gruba mesaj yollar
    :param _message: önderilmek istenen  mesaj (str) exp = (groupname+message)
    :param _client: Gönderen client (socket.client)
    :return: 1 veya 0 (str)
    """
    group, message = _message.split('+', 1)
    myquery = {"groupname": group}
    mydoc = groupdb.find_one(myquery)
    if mydoc is None:
        _client.sendall(str.encode('not created ' + group))
        return '0'

    groupMembers = mydoc['members']

    fromUsername = client_to_username(_client)
    if fromUsername in groupMembers:
        for toUsername in groupMembers:
            if fromUsername == toUsername:
                continue
            else:
                toUserClient = username_to_client(toUsername)
                if toUserClient:
                    toUserClient.sendall(str.encode(fromUsername + ' (' + group + ') : ' + message))
                    insert_doc = {'from': fromUsername, 'to': toUsername, 'message': message, 'forwarded': True,
                                  'groupname': group
                                  }
                    messagedb.insert_one(insert_doc)
                else:
                    insert_doc = {'from': fromUsername, 'to': toUsername, 'message': message, 'forwarded': False,
                                  'groupname': group
                                  }
                    messagedb.insert_one(insert_doc)
                    pass
        return '1'
    else:
        _client.sendall(str.encode('not in ' + group))
        return '0'
    pass

    pass


def exist_group(group_name):
    """
    Grubun veri tabanında kaydını sorgular
    :param group_name: Sorgulanacak grup ismi (str)
    :return: 0 veya 1 (int)
    """
    myquery = {"groupname": group_name}
    mydoc = groupdb.find_one(myquery)
    if mydoc is None:
        return 0
    else:
        return 1


def offline_message_send(_client):
    """
    Kullanıcılara offline iken gelen mesajları veri tabanından isteyerek kullanıcıya iletir
    :param _client: Görüntülemek isteyen client (socket.client)
    :return: 1 (str)
    """
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
            try:
                group = i['groupname']
            except:
                group = None

            if group:
                _client.sendall(str.encode(_from + ' (offline ' + group + ' message) : ' + message))
            else:
                _client.sendall(str.encode(_from + ' (offline user message) : ' + message))

        except Exception as e:
            print('Hata : ', e)
    messagedb.update_many(myquery, newvalues)

    return '1'
    pass


def all_users(_client):
    """
    Tüm kayıtlı kullanıcıları veri tabanından alır
    :param _client: Görüntülemek isteyen client (socket.client)
    :return: 1 veya 0 (str)
    """
    try:
        res = [ele['username'] for ele in userdb.find()]
        users = ", ".join(res)
        _client.sendall(str.encode('All users : ' + users))
        return '1'
    except:
        return '0'
    pass


def group_member(_client, _message):
    """
    Grup da olan kullanıcaları veri tabanından alır
    :param _client: Görüntülemek isteyen client (socket.client)
    :param _message: Görüntülenmesi için grup ismi (str) exp = (prefix+groupname)
    :return: 1 veya 0 (str)
    """
    iter, group = _message.split('+', 1)
    myquery = {"groupname": group}
    try:
        res = groupdb.find_one(myquery)
        users = ", ".join(res['members'])
        _client.sendall(str.encode(group + ' users : ' + users))
        return '1'
    except:
        return '0'


def user_group_member(_client, _message):
    """
    Kullanıcının içerisinde bulunduğu grupları listeler.
    :param _client: Görüntülemek isteyen client (socket.client)
    :param _message: Görüntülemek isteyen kullanıcı ismi (str) exp = (prefix+username)
    :return: 1 veya 0 (str)
    """
    iter, user = _message.split('+', 1)
    user = user[1:]
    try:
        userGroup = [group['groupname'] for group in groupdb.find() if user in group['members']]
        userGroup = ", ".join(userGroup)
        _client.sendall(str.encode(user + ' groups : ' + userGroup))
        return '1'
    except:
        return '0'


def create_group(_client, _message):
    """
    Grup kurulmasını sağlar
    :param _client: Kurmak isteyen client (socket.client)
    :param _message: Kurulmak istenen gruop ismi (str) exp = (prefix+groupname)
    :return: 0 veya 1 (str) Grup mevcut ise 0 kuruluş başarılı ise 1
    """
    iter, groupname = _message.split('+', 1)
    createrUsername = [client_to_username(_client)]
    if exist_group(groupname) == 1:
        _client.sendall(str.encode('Exist group '+groupname))
        return '0'
    try:
        myquery = {"groupname": groupname, 'members': createrUsername}
        groupdb.insert_one(myquery)
        return '1'
    except:
        return '0'
    pass


def add_group(_client, _message):
    """
    Mevcut gruba kullanıcı eklenmesini sağlar
    :param _client: Eklemek isteyen client (socket.client)
    :param _message: Girilen isme birden fazla kullanıcı ismi barındıran mesaj(str)
    exp =(prefix+groupname+username+username+...)
    :return: 1 veya 0 (str)
    """
    messageSplit = _message.split('+')
    iter, groupname, users = messageSplit[0], messageSplit[1], messageSplit[2:]
    myquery = {"groupname": groupname}
    if exist_group(groupname) == 0:
        _client.sendall(str.encode('Not exist group '+groupname))
        return '0'
    try:
        res = groupdb.find_one(myquery)
        members = res['members']
        users.extend(members)
        users = list(set(users))
        newvalues = {"$set": {'members': users}}
        groupdb.update_one(myquery, newvalues)
        return '1'
    except:
        return '0'
    pass


def disconnect_user_delete(_address):
    """
    Kullanıcının server ile bağlantısında bağlantı listesinden silinmesi
    :param _address: Bağlantısı kesilen adres
    :return: None
    """
    global all_connection
    all_connection = [i for i in all_connection if not (i['address'] == _address)]
    # print(all_connection)


def threaded_client(connection, _address):
    """
    Clientlerin threadler sayesinde birden fazla bağlantı oluşturulması
    :param connection: Bağlantı clienti (socket.client)
    :param _address: Bağlantı adres (socket.address)
    :return: None
    """
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


def client_to_username(_client):
    """
    Girilen client ile username verisini almak
    :param _client: Kullanıcı adı isteyen client (socket.client)
    :return: username (str) Kullanıcı adı
    """
    username = None
    for client in all_connection:
        if client['client'] == _client:
            username = client['username']
    return username


def username_to_client(username: str):
    """
    Girilen Kullanıcı adından clienti almak
    :param username: Girilen kullanıcı adı  (str)
    :return: client (socket.client) Kullanıcının bağlı olduğu client
    """
    userClient = None
    for client in all_connection:
        if client['username'] == username:
            userClient = client['client']
    return userClient


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
