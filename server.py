import socket
import random
import threading
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind(('0.0.0.0',10000))

sock.listen(1)

connections = {}
names = []
#TODO#0#errorhandle
#we should implement some error sending and receiving them on client side

#TODO#1#namecheck
#there should be namechecking on server side, for proper names
#we should check here if name is valid, and send error if its not
#it can contain everything but spaces, and first letter cannot be anything but letters
#its length must be shortrer than 10

#TODO#2#Server:log&pass
#there should be file on server side enabling to login to your account
#also error checking and so on

#TODO#3#privateChat
#i thnik it should be next big thing these private connections
#we can start it by smth like !private [name1] [name2] [name3]
#then we send invitations for all parties interested, and if they agree to participate than their all
#conversations go to this private channel
#it has to have option to quit, if all people quit it closes, and it has to have option to invite new people

def SendTo(person, data):
    global connections
    connections[person].send(bytes(data, 'utf-8'))

fileName = "chat_info"

codedLength = 40
#czytanie info
#all of it should be done on server side
#maximum password/login length is 18

def encode(string):
        coded = ""
        for i in range(0,codedLength):
                char = chr(random.randint(33,122))
                if char == '\\':
                    char = 'x'
                coded += char

        magic = int(codedLength/len(string))
        for i in range(0,len(string)):
                coded = coded[:i*magic] + string[i] + coded[(magic*i)+1:]

        strlen = str(len(string))
        strlen = "0"*(2-len(strlen)) + strlen

        coded = coded[:codedLength-2] + strlen
        checksum = 0
        for s in string:
                checksum += ord(s)

        checksumstr = str(checksum)
        checksumstr = "0"*(4 - len(checksumstr)) + checksumstr
        
        coded += checksumstr
        return coded

def decode(string):
        #maybe we should check string length first

        checksum = int(string[codedLength:])
        string = string[:codedLength]
        strlen = int(string[codedLength-2:])
        magic = int(codedLength/strlen)
        string = string[:codedLength-2]
        decoded = ""
        for i in range(0,codedLength, magic):
                decoded += string[i]
        decoded = decoded[:strlen]
        localchecksum = 0
        for s in decoded:
                localchecksum += ord(s)
        if localchecksum == checksum:
                #great! all things are OK
                return [True, decoded]
        else:
                #upsi its not that
                print("local: "+str(localchecksum))
                print("written: "+str(checksum))
                return [False, decoded]



def validAuthInput(string):
    if len(string) > 18:
        return "#ERROR value is too long"
    elif haveForbiddenChars(string):
        return "#ERROR value has forbidden chars"
    else:
        return ""
    
def haveForbiddenChars(string):
    for s in string:
        if ord(s) < 48 or ord(s) in range(58,65) or ord(s) in range(91,97) or ord(s) > 122:
            return True
    return False

def handler(c, a):
    global connections
    
    myGuy = c
    ###############login
        
    myGuy.send(bytes("#LOGIN", 'utf-8'))
    login = str(myGuy.recv(1024), 'utf-8')
    REGISTER = False
    if login == "register":
        REGISTER = True

    if REGISTER:
        myGuy.send(bytes("#LOGIN", 'utf-8'))
        while True:
            login = str(myGuy.recv(1024), 'utf-8')
            err = validAuthInput(login)
            if err == "":
                break
            else:
                myGuy.send(bytes(err, 'utf-8'))
                continue
    else:
        err = validAuthInput(login)
        if err != "":
            myGuy.send(bytes(err, 'utf-8'))
            myGuy.close()
            return
            
    myGuy.send(bytes("#PASSW", 'utf-8'))
    if REGISTER:
        while True:
            password = str(myGuy.recv(1024), 'utf-8')
            err = validAuthInput(password)
            if err == "":
                break
            else:
                myGuy.send(bytes(err, 'utf-8'))
                continue
            
    else:
        password = str(myGuy.recv(1024), 'utf-8')
        err = validAuthInput(password)
        if err != "":
            myGuy.send(bytes(err, 'utf-8'))
            myGuy.close()
            return


    if not REGISTER:
        localBool = False
        f = open(fileName, 'r')
        for line in f:
            params = line.split(" ")
            if len(params)>= 3:
                if decode(params[1])[1] == login and decode(params[2])[1] == password:
                    localBool = True
                    break
        f.close()
        if not localBool:
            myGuy.send(bytes("you cannot login, sorry...", 'utf-8'))
            myGuy.close()
            return
        else:
            myGuy.send(bytes("#HELLO", 'utf-8'))
    else:
        myGuy.send(bytes("#REGISTERING", 'utf-8'))
        print("do we want to accept this person?")
        print(login)
        print(password)
        answer = input("y/n")
        if answer =='y':
            f = open(fileName, 'a')
            f.write("\nn: " + encode(login) + " " + encode(password))
            f.close()
            #myGuy.send(bytes("you've been accepted, welcome!", 'utf-8'))
            time.sleep(1)
            myGuy.send(bytes("#HELLO", 'utf-8'))
        else:
            myGuy.send(bytes("#ERROR your request for registration was declined", 'utf-8'))
            myGuy.close()
            return
            
    


    myGuyName = login

    if myGuyName in connections.keys():
        myGuy.send(bytes("your account is already logged in, sorry", 'utf-8'))
        return
    
    connections[myGuyName] = myGuy

    for person in connections:
        if person != myGuyName:
            data = ("Dolaczyl do nas: " + myGuyName)
            SendTo(person, data)
    
    print("new connection from: " + myGuyName)
    print(str(a))
    while True:
        try:
            data = str(c.recv(1024), 'utf-8')
            spaceplace = data.find(' ')
            private = False
            special = False
            if data[0:1] == "?":
                if data[1:] == "people":
                    allList = "\n"
                    for person in connections:
                        allList += person + "\n"
                    SendTo(myGuyName, "List of all logged users: " + allList)
                if data[1:] == "":
                    helpInfo = "help should be written here, but i dont know if it should be on the server side ... "
                    print(helpInfo)
                    SendTo(myGuyName, helpInfo)
                continue
            if data[0:1] == '!': #privatemessage to
                if spaceplace != -1:
                    if data[1:spaceplace] in connections.keys():
                        private = True
                        otherGuy = data[1:spaceplace]
                        print(myGuyName + " to " + otherGuy + ": " + data)
                        SendTo(myGuyName, myGuyName + " to " + otherGuy + ": " + data[spaceplace:])
                        SendTo(otherGuy, myGuyName + " to " + otherGuy + ": " + data[spaceplace:])
                        continue
            
            print(myGuyName + ": " + data)
            for person in connections:
                SendTo(person, myGuyName + ": " + data)
            continue
        except:
            
            print("koniec polaczenia z " + myGuyName)
            connections.pop(myGuyName)
            myGuy.close()
            
            for person in connections:
                data = ("Polaczenie zakonczyl: " + myGuyName)
                SendTo(person, data)
            return

print("""
========================================================

                      Server started

========================================================
""")
print()

while True:
    c, a = sock.accept()
    print(sock.getsockname()[0])
    cThread = threading.Thread(target=handler, args=(c,a))
    cThread.daemon = True
    cThread.start()
    print(connections)
