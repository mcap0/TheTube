import mysql.connector
import rsa
import hashlib
import datetime
import time
import sys
import os

def connect_to_database():
    connection = mysql.connector.connect(
        host="localhost",
        user="TheTubeAPI",
        database="The_Tube",
        autocommit=True
    )
    return connection


def fetch_parameters(params):
    return ','.join(['"' + str(param) + '"' for param in params])

def call_stored_procedure(connection, procedure_name, parameters):
    try:
        cursor = connection.cursor()
    
    except:
        connection.close()
        connection = connect_to_database()
        cursor = connection.cursor()

    parameters = fetch_parameters(parameters)
    #print(f'\ncall The_Tube.{procedure_name}({parameters});')
    cursor.execute(f'\ncall The_Tube.{procedure_name}({parameters});', multi=True)
    result = cursor.fetchall()
    #print(result)
    return result

def register(connection, p_username):
    # connettiti, salva la chiave privata nel computer, crea l'hash della private key, crea l'encrypted username (public key) e passali alla stored procedure 

    private_key, public_key, private_pem, public_pem = generate_key_pairs()

    sha_private_key = Sha512(private_pem)

    encrypted_username = encrypt(p_username, public_key)
    encrypted_username = to_hex_string(encrypted_username)

    #print(encrypted_username)

    result = call_stored_procedure(connection, "add_user", (str(p_username),public_pem.decode(), encrypted_username, sha_private_key))
    
    return result

def delete_user(connection, username, private_pem):
    #implementare la cancellazione delle chat di un utente
    #cursor = connection.cursor()
    result = call_stored_procedure(connection,"delete_user", (username,Sha512(private_pem)))
    #print(cursor.rowcount, "record(s) deleted")

    return result


def generate_key_pairs():
    # genera un key pairs RSA. ritorna la versione file di entrambi
    public_key, private_key = rsa.newkeys(512)
    with open('keys/public_key.pem', 'wb') as p:
        p.write(public_key.save_pkcs1('PEM'))
    with open('keys/private_key.pem', 'wb') as p:
        p.write(private_key.save_pkcs1('PEM'))
    public_pem = public_key.save_pkcs1('PEM')
    private_pem = private_key.save_pkcs1('PEM')
    return private_key, public_key, private_pem, public_pem

def encrypt(message, key):
    block_size = 53 
    ciphertext = b''
    message_bytes = message.encode('utf-8')
    for i in range(0, len(message_bytes), block_size):
        block = message_bytes[i:i+block_size]
        if len(block) < block_size:
            block += b' ' * (block_size - len(block))
        ciphertext += rsa.encrypt(block, key)
    return ciphertext

def decrypt(ciphertext, key):
    if ciphertext is None:
        return ciphertext
    key_size = 512
    plaintext = b''
    ciphertext_blocks = [ciphertext[i:i+key_size//8] for i in range(0, len(ciphertext), key_size//8)]

    for i, block in enumerate(ciphertext_blocks):
        try:
            block_plaintext = rsa.decrypt(block, key)
            plaintext += block_plaintext
        except:
            plaintext += bytes(block)
            if i == len(ciphertext_blocks) - 1 and len(block) < key_size // 8:
                plaintext = plaintext[:-key_size // 8 + len(block)]
    return plaintext

def load_keys():
    if not os.path.exists('keys/public_key.pem'):
        return
    with open('keys/public_key.pem', 'rb') as p:
        public_key = rsa.PublicKey.load_pkcs1(p.read())
    with open('keys/private_key.pem', 'rb') as p:
        private_key = rsa.PrivateKey.load_pkcs1(p.read())

    public_pem = public_key.save_pkcs1('PEM')
    private_pem = private_key.save_pkcs1('PEM')
    return private_key, public_key, private_pem, public_pem

def getkey(connection, username):
    key = call_stored_procedure(connection, "get_key", (username,))
    key = key[0][0]
    key = rsa.PublicKey.load_pkcs1(key)
    return key

def get_texts_byID(connection, chatid, p_key):
    texts = call_stored_procedure(connection, "get_texts_byID", (chatid,))
    chats = []
    for text in texts:
        text = text[0]
        try:
            text.decode()
        except:
            pass

        try:
            text = from_hex_string(text.decode())
        except:
            pass

        text = decrypt(text, p_key)
        chats.append(text.strip())

    return chats


def get_texts(connection, username, p_key):
    texts = call_stored_procedure(connection, "get_texts", (username,))
    chats = []
    for text in texts:
        text = text[0]
        try:
            text.decode()
        except:
            pass

        try:
            text = from_hex_string(text.decode())
        except:
            pass
        #print(text)
        text = decrypt(text, p_key)
        #print(decrypt(from_hex_string(text[1].decode()), private_key))
        chats.append(text)


    return chats


def get_requests(connection, username, pk):
    result = call_stored_procedure(connection, "get_chats", (username,))
    chats = []
    for chat in result:
        header = chat[0]
        chatid = chat[1]
        if header is None:
            continue
        header = from_hex_string(header.decode())
        header = decrypt(header,pk)
        chat_number = header.strip().split(b"-")[1].decode()
        if is_request(connection, int(chat_number)) == 0:
            chats.append([header,chatid])
        
    return chats

def get_chats(connection, username, p_key):
    result = call_stored_procedure(connection, "get_chats", (username,))
    chats = []
    for chat in result:
        header = chat[0]
        chatid = chat[1]
        if header is None:
            continue
        header = from_hex_string(header.decode())
        header = decrypt(header,p_key)
        chat_number = header.strip().split(b"-")[1].decode()
        if is_request(connection, int(chat_number)) == 0:
            continue        
        chats.append([header,chatid])
        #print(decrypt(from_hex_string(header.decode()), p_key))

    return chats

def is_request(connection, chatid):
    res = call_stored_procedure(connection, "is_request", (chatid,))
    #print(res)
    if res:
        if res[0][0] is None:
            return 0
        else:
            return 1
    else:
        return 1



def print_chat_list(chat_list):
    for i, chat in enumerate(chat_list):
        header, chatid = chat
        header = header.strip()
        if header:
            print(f"{i+1}) {header.strip().decode()} (chat:{chatid})")

    selected = None
    while not selected:
        selection = input("Seleziona una chat (1-{}): ".format(len(chat_list)))
        if selection.isdigit():
            selection = int(selection)
            if 1 <= selection <= len(chat_list):
                selected = chat_list[selection - 1]
        else:
            break

    if selected:
        return selected[1], selected[0]
    else:
        return 0, 0

def check_username(connection, username):
    result = call_stored_procedure(connection, "exists_user", (username,))
    if len(result) >= 1:
        return result[0][0]
    else:
        return 0

def login(connection, username, key):
    result = call_stored_procedure(connection, "login", (username, key))
    if len(result) >= 1:
        return result[0][0]
    else:
        return 0

def Sha512(key):
    if isinstance(key,bytes):
        Hashedkey=hashlib.sha512(key).hexdigest()
    else:
        Hashedkey=hashlib.sha512(key.encode('utf-8')).hexdigest()
    #print(Hashedkey)
    return Hashedkey

def to_hex_string(ciphertext):
    hex_list = [b for b in bytearray(ciphertext)]
    return '0x' + ''.join(f'{b:02x}' for b in hex_list)

def from_hex_string(hex_string):
    try:
        if hex_string.startswith('0x'):
            hex_string = hex_string[2:]

    except:
        return hex_string

    return bytes.fromhex(hex_string)

def newchat(connection, username1, username2, p_key):
# per creare una chat bisogna -> avere l'username del destinatario
# ottenere la public key del destinatario
# inserire nel header (criptato) in ordine:
# destinatario, chatid del destinatario
    date_time = datetime.datetime.now()

    key = getkey(connection, username2)
    header2 = encrypt(f"{username1}", key)
    message2 = encrypt(f"Chat initiated by {username1} on {date_time}", key)

    key = getkey(connection, username1)
    header1 = encrypt(f"{username2}", key)
    message1 = encrypt(f"Chat initiated by {username1} on {date_time}", key)

    message1 = to_hex_string(message1)
    message2 = to_hex_string(message2)
    header1 = to_hex_string(header1)
    header2 = to_hex_string(header2)

    htest_plain = f"{Sha512(p_key.save_pkcs1('PEM'))}{username2}"
    htest = Sha512(htest_plain)

    pk = Sha512(p_key.save_pkcs1('PEM'))

    result = call_stored_procedure(connection, "new_chat", (username1, username2, message1, message2, header1, header2, htest ,pk))
    #print(result)
    return sign_chat(connection, username1, username2, result[0][0], htest, pk)

def sign_chat(connection, username1, username2, chatid, htest,pk):
    chatid1 = chatid - 1
    chatid2 = chatid
    key = getkey(connection, username1)
    new_header1 = encrypt(f"{username2}-{chatid2}", key)
    new_header1 = to_hex_string(new_header1)
    key = getkey(connection, username2)
    new_header2 = encrypt(f"{username1}-{chatid1}", key)
    new_header2 = to_hex_string(new_header2)
    
    result = call_stored_procedure(connection, "sign_chats", (username1, pk,  new_header1, new_header2, htest, chatid1, chatid2))
    

    return result

def live_chat(connection, chatid1, chatid2, pk, username2, username1):

    while True:
        chat = get_texts_byID(connection, chatid1, pk)
        for text in chat:
            print(text.decode().strip())
        message = input("> ")
        if message == "exit":
            break
        elif message:
            message = f"[{datetime.datetime.now()}]{username1}: {message}"
            #print(message)
            
            htest_plain = f"{Sha512(pk.save_pkcs1('PEM'))}{username2}"
            print(f'{username2}')
            htest = Sha512(htest_plain)
            new_text(connection, username1, username2, chatid1, chatid2,htest, message, pk)
        else:
            continue


def new_text(connection, username1, username2, chatid1, chatid2, htest, message, pk):
    chat = get_texts_byID(connection, chatid1, pk)
    chat = chat[0].decode().strip()
    if not chat.endswith("\n"):
        chat += "\n" + message
    else:
        chat += message
    
    #print(chat)
    key = getkey(connection, username1)
    message1 = encrypt(chat, key)
    message1 = to_hex_string(message1)

    key = getkey(connection, username2)
    message2 = encrypt(chat, key)
    message2 = to_hex_string(message2) 


    res = call_stored_procedure(connection, "new_text", (message1, message2, chatid1, chatid2, htest))
    return res

def delete_chat(connection, username, p_key, chatid):
    print(f"Deleting chat: {chatid}...")
    call_stored_procedure(connection, "erase_chat", (username, chatid, p_key))

def accept_request(connection,user,username,chatid1, chatid2, pk):
    print(f"Accepting chat: {chatid1}...")
    htest_plain = pk + user
    #print(htest_plain)
    htest = Sha512(htest_plain)
    call_stored_procedure(connection, "accept_request", (username, chatid1, chatid2, pk, htest))

def banner():
    banner = ("""████████╗██╗  ██╗███████╗    ████████╗██╗   ██╗██████╗ ███████╗
╚══██╔══╝██║  ██║██╔════╝    ╚══██╔══╝██║   ██║██╔══██╗██╔════╝
   ██║   ███████║█████╗         ██║   ██║   ██║██████╔╝█████╗  
   ██║   ██╔══██║██╔══╝         ██║   ██║   ██║██╔══██╗██╔══╝  
   ██║   ██║  ██║███████╗       ██║   ╚██████╔╝██████╔╝███████╗
   ╚═╝   ╚═╝  ╚═╝╚══════╝       ╚═╝    ╚═════╝ ╚═════╝ ╚══════╝""")
    print(banner)

def main():
    # Esegui il login richiedendo un nome utente
    banner()
    username = input("Insert Your Username: ")

    try:
        connection = connect_to_database()
        if(connection):
            print("Successfully Connected")
        else:
            print("Connection failed")
            exit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit()

    if load_keys():
        private_key, public_key, private_pem, public_pem = load_keys()
    
    try:
        check_result = check_username(connection, username)
        if check_result:
            login_result = login(connection, username, Sha512(private_pem))
            if login_result:
                print(f"Welcome {username}!")
            else:
                print("Sorry! Private_Key not found...")
                exit()



        else:
            choice = input(f'Account for "{username}" does not exist yet.\nYou want to register with that username? (Y/N)\n')
            if choice == "Y" or choice == "y":
                register(connection, username)
                private_key, public_key, private_pem, public_pem = load_keys()
            else:
                print("Login failed")
                
            
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        

    while True:
        try:
            check = login(connection,username,Sha512(private_pem))
        except:
            break

        if(check):
            choice = input("\n0) Exit\n1) Conversations\n2) Incoming Requests\n3) New Chat Request\n4) Delete Chat\n5) Delete Account\n")

        if choice and choice == '0':
            break

        if choice == '1':
            chats = get_chats(connection, username, private_key)
            chatid1, user = print_chat_list(chats)
            if user == 0:
                continue
            user = user.decode().strip().split("-")
            if len(user) > 1:
                live_chat(connection, chatid1, user[1], private_key, user[0], username)
            else:
                print("There was a problem with the chat. Please create a new one.")

        if choice == '2':
            requests = get_requests(connection, username, private_key)
            chatid1, user = print_chat_list(requests)
            if user == 0:
                continue
            user = user.decode().strip().split("-")
            if len(user) > 1:
                request = input("Insert '1' to accept and '2' to decline the chat request.")
                if request == '1':

                    accept_request(connection, user[0], username, chatid1, user[1], Sha512(private_pem))
                if request == '2':
                    delete_chat(connection, username, Sha512(private_pem), chatid1)
                else:
                    continue

        if choice == '3':
            user = input("Insert the recipient's Username: ")
            check = check_username(connection,user)
            if check == 0:
                print("User not Found.")
                continue
            ret = newchat(connection, username, user, private_key)
            #print(ret)
            chats = get_chats(connection, username, private_key)
            chatid1, user = print_chat_list(chats)
            user = user.decode().strip().split("-")
            if len(user) > 1:
                live_chat(connection, chatid1, user[1], private_key, user[0], username)
            else:
                print("There was a problem with the chat. Please delete it and create a new one.")

        if choice == '4':
            print("Select a chat to delete. Changes are irreversible.")
            chats = get_chats(connection, username, private_key)
            chatid1, user = print_chat_list(chats)
            delete_chat(connection, username, Sha512(private_pem), chatid1)

        if choice == '5':
            delete_user(connection, username, private_pem)

        choice = '0'
       
    print("Program Ended.")

main()








