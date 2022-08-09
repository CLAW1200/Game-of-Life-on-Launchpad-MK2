import random
import time
import mido
import re


#constants for epic gaming
GRIDSIZE = 8
SLEEPTIME = 0.1

print (mido.get_output_names())
print (mido.get_input_names())

#take note and return coord
def coordToNote(x,y):
    #0,0 > 81
    x = x + 1
    y = GRIDSIZE - y
    note = int(f"{y}{x}")
    return note

def noteToCoord(note):
    y = int(str(note)[0])
    x = int(str(note)[1])
    #the number 8 should become 0, the number 7 should become 1, etc.
    y = GRIDSIZE - y
    x = x - 1
    return x,y

def midiSend(note, state):
    if state == 1:
        velocity = 5
    else:
        velocity = 1
    
    if note >= 11 and note <= 88:
        msg = mido.Message('note_on', note=note, velocity=velocity)
        outPort.send(msg)


#set the grid to all 0s
def clearGrid():
    for i in range(GRIDSIZE):
        for j in range(GRIDSIZE):
            setCoord(i,j,0)
            midiSend(coordToNote(i,j), 0)

#set a given coordinate to a given value
def setCoord(x,y,val):
    grid[x][y] = val
    

#get the value of a given coordinate
def getCoord(x,y):
    return grid[x][y]


#game of life rules
def gameOfLife(x,y):
    
    #count the number of neighbours without counting cells outside the grid
    def check_neighbour(x,y):
        count = 0
        for i in range(x-1,x+2):
            for j in range(y-1,y+2):
                if i >= 0 and i < GRIDSIZE and j >= 0 and j < GRIDSIZE and not(i==x and j==y):
                    count += getCoord(i,j)
        return count



    neighbours = check_neighbour(x,y)

    #if the cell is alive and has 2 or 3 neighbours, it stays alive
    if getCoord(x,y) == 1 and neighbours == 2 or neighbours == 3:
        return 1
    #if the cell is alive and has less than 2 neighbours, it dies
    elif getCoord(x,y) == 1 and neighbours < 2:
        return 0
    #if the cell is alive and has more than 3 neighbours, it dies
    elif getCoord(x,y) == 1 and neighbours > 3:
        return 0
    #if the cell is dead and has 3 neighbours, it comes to life
    elif getCoord(x,y) == 0 and neighbours == 3:
        return 1
    #if the cell is dead and has less than 3 neighbours, it stays dead
    elif getCoord(x,y) == 0 and neighbours < 3:
        return 0
    #if the cell is dead and has more than 3 neighbours, it stays dead
    elif getCoord(x,y) == 0 and neighbours > 3:
        return 0
    else:
        return 0

#update the grid
def updateGrid():

    def setNewCoord(x,y,val):
        newGrid[x][y] = val

    def getNewCoord(x,y):
        return newGrid[x][y]

    newGrid = [[0 for x in range(GRIDSIZE)] for y in range(GRIDSIZE)]

    for i in range(GRIDSIZE):
        for j in range(GRIDSIZE):
            setNewCoord(i,j,gameOfLife(i,j))

    if newGrid == grid:
        print ("no change")
        return False
    
    if newGrid != grid:  
        for i in range(GRIDSIZE):
            for j in range(GRIDSIZE):
                setCoord(i,j,getNewCoord(i,j))
        return True


#print the grid
def printGrid():
    for j in range(GRIDSIZE):
        for i in range(GRIDSIZE):
            print(getCoord(i,j), end = " ")
        print()
    print()

def printLaunchpad():
    for i in range(GRIDSIZE):
        for j in range(GRIDSIZE):
            midiSend(coordToNote(i,j), getCoord(i,j))
        

def randomizeGrid():
    for i in range(GRIDSIZE):
        for j in range(GRIDSIZE):
            setCoord(i,j,random.randint(0,1))
        
#play the game
def play():
    while updateGrid():
        printGrid()
        printLaunchpad()
        time.sleep(SLEEPTIME)




#create an 8x8 grid

grid = [[0 for x in range(GRIDSIZE)] for y in range(GRIDSIZE)]

outPort = mido.open_output('6- Launchpad MK2 1')
inPort = mido.open_input('6- Launchpad MK2 0')

def extractNoteFromData(inputData):
    inputData = str(inputData)

    if (re.search(' velocity=0 ', inputData)) != None:
        return None

    else:
        m = re.search(' note=(.+?) ', inputData)
        if m:
            note = m.group(1)
            return note

def drawingMode():

    clearGrid()
    while True:
        inputData = inPort.receive()
        note = extractNoteFromData(inputData)
        if note == None:
            continue

        if note == "89":
            break

        if note == "79":
            randomizeGrid()
            break

        else:
            #print (getCoord(noteToCoord(note)[0], noteToCoord(note)[1]))
            if getCoord(noteToCoord(note)[0], noteToCoord(note)[1]) == 0:
                setCoord(noteToCoord(note)[0], noteToCoord(note)[1], 1)
                printGrid()
                printLaunchpad()

            else:
                setCoord(noteToCoord(note)[0], noteToCoord(note)[1], 0)
                printGrid()
                printLaunchpad()
    
    printLaunchpad()
    time.sleep(SLEEPTIME)
    play()


if __name__ == "__main__":
    while True:
        drawingMode()
