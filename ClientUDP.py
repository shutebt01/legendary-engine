'''
Created on 12 Feb 2015

@author: shutebt01
'''
#!/bin/env/python3
'''
Packet formating:
    [type, src-name, src-group, data]
'''

import socket, threading, json

name = input("Enter User Name: ")
port = 16500
#host = input("Enter host: ")
room = "Global"

showall = False

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) 
s.bind(('', port)) 
#s.connect((host, port))

class InputThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, target=self.input, name="Thread-Input")
    
    def input(self):
        global room
        while True:
            inp = input()
            data = None
            if not(inp.startswith('!')):
                #assumes its a message if not a command
                data = json.dumps(["Message", name, room, inp])
            else:
                # Creates initial packet with data for tracking
                packet = ["Event", name, room]
                split = inp.split(' ', 1)
                if split[0] == "!pm":
                    pmsplit = split[1].split(' ', 1)
                    #TODO implement better validation
                    if (len(split) == 2):
                        #Adds data to packet
                        packet.append("pm")
                        packet.append(pmsplit[0])
                        packet.append(pmsplit[1])
                    data = json.dumps(packet)
                if split[0] == "!room":
                    room = split[1]
                    print("You changed to room:" + room)
                if split[0] == "!broadcast" or split[0] == "!bcast":
                    msg = split[1]
                    packet.append("bcast")
                    packet.append(msg)
                    data = json.dumps(packet)
            if data:
                s.sendto(data.encode("ascii"), ("<broadcast>", port))

class OutputThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, target=self.output, name="Thread-Output")
        
    def output(self):
        while True:
            data = s.recv(2048).decode("ascii")
            array = json.loads(data)
            if array[0] == "Message":
                if array[2] == room:
                    print(array[1] + " (" + array[2] + "):" + array[3])
            elif array[0] == "Event":
                if array[3] == "pm" and array[4] == name:
                    print(array[1] + " (" + array[2] + ") -> You: " + array[5])
                elif array[3] == "bcast":
                    print(array[1] + " (" + "*" + "):" + array[4])

Inp = InputThread()
Inp.start()
Out = OutputThread()
Out.start()
