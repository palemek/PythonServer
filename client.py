import os
import socket
import threading
import time
import random
import sys
import subprocess
import msvcrt
from ctypes import *

os.system('mode con: cols=78 lines=34')


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('207.180.226.77', 13333))

window = """/----------------------------------------------------------------------------\\
|#                                                                          #|
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|                                                                            |
|#                                                                          #|
\\----------------------------------------------------------------------------/"""
print(window)

class COORD(Structure):
    pass
 
COORD._fields_ = [("X", c_short), ("Y", c_short)]

OUTPUTSPACE = [5,3,71,23]
INPUTSPACE =  [5,30,71,1]
LOGINSPACE =  [33,14,18,1]
PASSWSPACE =  [33,20,18,1]
REGISTSPACE = [34,15,16,5]
ALLSPACE =    [4,8,73,23]

DRAWSTACK = []

INPUT = ""
OUTPUT = ""


def ATS(string, where, rest = [0,0]):
        DRAWSTACK.append([string,where,rest])
        draw()
def clearSpace(space):
        for i in range(space[1], space[1] + space[3]):
                sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (i, space[0]-2, " " * (space[2]+3)))
        
def printInSpace(string, space):
        tempText = string
        lineID = space[3] + space[1] - 1
        width = space[2]
        for i in range(space[1], space[1] + space[3]):
                sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (i, space[0], " " * width))
        
        while lineID >= space[1] and len(tempText) > 0:
                enterPlace = tempText.rfind('\n')
                lt = len(tempText)
                if not enterPlace == -1:
                        if lt - enterPlace > width:
                                if lt >= width:
                                        if len(tempText)%width == 0:
                                                toprint = tempText[lt - width:]
                                                tempText = tempText[:lt - width]
                                        else:
                                                toprint = tempText[lt - (lt%width):]
                                                tempText = tempText[:lt - (lt%width)]
                                else:
                                        toprint = tempText
                                        tempText = ""
                        else:
                                toprint = tempText[enterPlace + 1:]
                                tempText = tempText[:enterPlace]
                else:
                        if lt >= width:
                                if lt%width == 0:
                                        toprint = tempText[lt - width:]
                                        tempText = tempText[:lt - width]
                                else:
                                        toprint = tempText[lt - (lt%width):]
                                        tempText = tempText[:lt - (lt%width)]
                        else:
                                toprint = tempText
                                tempText = ""
                
                sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (lineID, space[0], toprint))
                sys.stdout.flush()
                lineID -= 1
        sys.stdout.write("\x1b[%d;%df" % (INPUTSPACE[1], INPUTSPACE[0]))
        
def printchar(toprint, pos):
        sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (pos[1], pos[0], toprint))
        sys.stdout.flush()
def draw():
        global MODE
        if len(DRAWSTACK) > 0:
                first = DRAWSTACK.pop(0)
                if first[1] == "input":
                        if MODE == 'N':
                                if first[0] == '':
                                        clearSpace(INPUTSPACE)
                                else:
                                        printInSpace(first[0],INPUTSPACE)
                        elif MODE == 'L':
                                if first[0] == '':
                                        clearSpace(LOGINSPACE)
                                else:
                                        printInSpace(first[0],LOGINSPACE)
                        elif MODE == 'P':
                                if first[0] == '':
                                        clearSpace(PASSWSPACE)
                                else:
                                        printInSpace(len(first[0])*"*",PASSWSPACE)
                        elif MODE == 'W':
                                printInSpace(first[0],REGISTSPACE)
                elif first[1] == "output":
                        printInSpace(first[0],OUTPUTSPACE)
                elif first[1] == "char":
                        printchar(first[0], first[2])
                elif first[1] == "clear":
                        clearSpace(first[2])

def write():
        global INPUT
        while True:
                INPUT = ""
                while True:
                        c = str(msvcrt.getch(),'utf-8')
                        if MODE == 'W':
                                continue
                        if ord(c) <= 127:
                                if c == '\r':
                                        break
                                if c == '\b':
                                        INPUT = INPUT[:-1]
                                        ATS(INPUT, "input")
                                        continue
                                INPUT += c
                                ATS(INPUT, "input")
                sock.send(bytes(INPUT, 'utf-8'))
                INPUT = ""
                ATS(INPUT, "input")
                time.sleep(0.1)


MODE = 'N'#'NORMAL'
#'L'#'LOGIN'
#'P'#'PASSWORD'
#'W'#'WAIT'
#'R'#'REGISTRATION'

def read():
        global OUTPUT
        global INPUT
        global MODE
        while True:
                try:
                        data = str(sock.recv(1024), 'utf-8')
                        if not data: sys.exit(0)
                        #depending on data type we should determine what to do with that:
                        #for example if message begins with '#' it has smth to do with server messages
                        if data == '#LOGIN':
                                ATS("","clear", ALLSPACE)
                                createBorderAroundSpace(LOGINSPACE,"login")
                                MODE = 'L'
                                INPUT = ''
                                continue
                        elif data == '#PASSW':
                                createBorderAroundSpace(PASSWSPACE,"password")
                                MODE = 'P'
                                INPUT = ''
                                continue
                        elif data == '#HELLO':
                                ATS("","clear", ALLSPACE)
                                createBorderAroundSpace(OUTPUTSPACE,"chat")
                                createBorderAroundSpace(INPUTSPACE, "input")
                                MODE = 'N'
                                INPUT = ''
                                continue
                        elif data[:6] == '#ERROR':
                                #TODO
                                print(data[6:])
                                continue
                        elif data == '#REGISTERING':
                                ATS("","clear", REGISTSPACE)
                                createBorderAroundSpace(REGISTSPACE,"Registering")
                                MODE = 'W'
                                ATS("Please wait...", "input")
                                continue
                                
                                
                        OUTPUT += "\n" + data
                        ATS(OUTPUT, "output")
                        #print(data)
                except:
                        data = "SERVER WAS CLOSED, CONTACT ADMIN(its kuba of course)"
                        OUTPUT += "\n" + data
                        ATS(OUTPUT, "output")
                        return

        
def createBorderAroundSpace(space,name):
        global MODE
        tempMODE = MODE
        MODE = 'W'
        tb = space[1]-1
        bb = space[1] + space[3]
        lb = space[0] - 3
        rb = space[0] + space[2] + 1
        for i in range(lb + 1, rb):
                ATS('-','char',[i,tb])
                time.sleep(0.01)
        ATS('\\','char',[rb, tb])
        for i in range(tb + 1, bb):
                ATS('|','char',[rb,i])
                time.sleep(0.02)
        ATS('/','char',[rb, bb])
        for i in reversed(range(lb + 1, rb)):
                ATS('-','char',[i,bb])
                time.sleep(0.01)
        ATS('\\','char',[lb, bb])
        for i in reversed(range(tb + 1, bb)):
                ATS('|','char',[lb,i])
                time.sleep(0.02)
        ATS('/','char',[lb, tb])
            
        for i in range(0,len(name)):
                ATS(name[i],'char',[lb + 2 + i, tb])
                time.sleep(0.15)
        
        #arr = """_`.'-~^,!:;*></\|()}{?+71"][i=jotvclr0C&uILzJVe432y5YsZ98nT$6awfSGhdFOUbx%kPqgpDXAmREQH#KB@NMW"""
        #for j in range(0,60):
        #        for i in range(0,len(arr)):
        #                for g in range(0,len(arr)):
        #                        for h in range(0,24):
        #                                ATS(arr[(i+g+h)%len(arr)],'char',[1+g, tb - 2+h])
        #                                time.sleep(0.000)
        MODE = tempMODE
        
ATS("","clear", ALLSPACE)
#startowanie thread'u czytajacego
readThread = threading.Thread(target=read)
readThread.daemon = True
readThread.start()
#start pisania
write()
