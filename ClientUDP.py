'''
Created on 12 Feb 2015

@author: shutebt01
'''
#!/bin/env/python3
'''
Packet formating:
    [type, src-name, src-group, data]
'''

#Normal imports
import socket, threading, json, platform, ctypes, timer

#GUI Imports
import tkinter, operator

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

"""
--BEGIN-FLASH--

Flash the console when a message is recieved
"""
isFlashing = False

def __win_unflash():
    global isFlashing
    ctypes.windll.user32.FlashWindow(ctypes.windll.kernel32.GetConsoleWindow(), False)
    isFlashing=False

def flashIcon():
    global isFlashing
    if platform.system() == "Windows" and not isFlashing:
        ctypes.windll.user32.FlashWindow(ctypes.windll.kernel32.GetConsoleWindow(), True)
        isFlashing = True
        threading.Timer(2, __win_unflash).start()
"""
--END-FLASH--
"""

"""
---BEGIN-PRINTOUT---

Allows redifining of input and output code
"""
def writeout(out):
    print(str(out))
    flashIcon()

def readin():
    return input()
"""
--END-PRINTOUT--
"""

"""
--BEGIN-GUI--
"""
inputList = []

def guireadin():
    while len(inputList) == 0:
        pass
    return inputList.pop()

def guiwriteout(out):
    Gui.addMessage(str(out))

class GuiThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, target=self.gui, name="")
        self.guisetup()
    
    def guisetup(self):
        global name, port, room, inputList
        self.root = tkinter.Tk()
        self.root.title("CliUDP - GUI")
        self.frame = tkinter.Frame(self.root)
        self.frame.pack()

        #Info Frame; where general info is put#
        #######################################
        self.infoframe = tkinter.Frame(self.frame)
        self.infoframe.pack()
        #Uname Label
        tkinter.Label(self.infoframe, text="Name:").grid(row=0, column=0)
        self.uname = tkinter.Label(self.infoframe, text=str(name))
        self.uname.grid(row=0, column=1)
        #Port Label
        tkinter.Label(self.infoframe, text="Port:").grid(row=1, column=0)
        self.port = tkinter.Label(self.infoframe, text=str(port))
        self.port.grid(row=1, column=1)
        #Room Label
        tkinter.Label(self.infoframe, text="Room:").grid(row=2, column=0)
        self.room = tkinter.Label(self.infoframe, text=str(room))
        self.room.grid(row=2, column=1)

        def updateRoom(self=self):
            self.room.config(text=str(room))
            self.root.after(100, updateRoom)    

        updateRoom()

        #Canvas; where messages go#
        ###########################
        self.canvasframe = tkinter.Frame(self.frame)
        self.canvasframe.pack()
        self.canvas = tkinter.Canvas(self.canvasframe, width=400, height=500)
        self.canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
        #Setup Y scrollbar
        self.canvasyscroll = tkinter.Scrollbar(self.canvasframe, command=self.canvas.yview)
        self.canvas.config(yscrollcommand = self.canvasyscroll.set)
        self.canvasyscroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        #Generate message area
        self.canvasiframe = tkinter.Frame(self.canvas, width=395)
        self.canvas.create_window(0, 0, window=self.canvasiframe, anchor='nw')
        self.addMessage("Messages appear here")

        #INPUT ZONE; Where you type stuff#
        ##################################
        eventLambda = lambda event=None, self=self, inputList=inputList: (inputList.append(self.inputentry.get()), self.inputentry.delete(0, tkinter.END))
        
        self.inputframe = tkinter.Frame(self.frame)
        self.inputframe.pack(fill=tkinter.X)
        self.inputentry = tkinter.Entry(self.inputframe)
        self.inputentry.grid(row=0, column=0, columnspan=6)
        self.inputentry.bind("<Return>", eventLambda)
        self.inputbutton = tkinter.Button(self.inputframe, text="Send", command=eventLambda)
        self.inputbutton.grid(row=0, column=6)

        #Hide self until ready
        self.root.withdraw()
        
    #Define message add function
    def addMessage(self, message):
        tkinter.Label(self.canvasiframe, text=message, relief=tkinter.RIDGE, borderwidth=1, justify=tkinter.LEFT,anchor="w").pack(fill=tkinter.X)
        region = (0,0,0,0)
        try:
            region=tuple(map(operator.add, self.canvas.bbox("all"), (0,0,0,40)))
        except e:
            print(e)
        self.canvas.config(scrollregion=region)
        #self.canvasyscroll.scroll(region[3])

    def gui(self):
        while True:
            self.root.mainloop()

    def show(self):
        self.root.deiconify()

    def hide(self):
        self.root.withdraw()
"""
--END-GUI--
"""

class InputThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, target=self.input, name="Thread-Input")

    def input(self):
        global room
        while True:
            inp = readin()
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
                    writeout("You changed to room:" + room)
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
                    writeout(array[1] + " (" + array[2] + "):" + array[3])
            elif array[0] == "Event":
                if array[3] == "pm" and array[4] == name:
                    writeout(array[1] + " (" + array[2] + ") -> You: " + array[5])
                elif array[3] == "bcast":
                    writeout(array[1] + " (" + "*" + "):" + array[4])


#Comment out to not use GUI
Gui = GuiThread()
Gui.start()
Gui.show()
writeout = guiwriteout
readin = guireadin

Inp = InputThread()
Inp.start()
Out = OutputThread()
Out.start()
#Here for debugging in idle
while True:
    pass
