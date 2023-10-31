import socket 
import pygame
import numpy
import random


def gameloop():    
    pygame.mixer.init(44100, -16, 2, 512)
    sampleRate = 44100
    sounds = mKESOUNDS(sampleRate)
    soundINDEX = 10

    beatChannel = pygame.mixer.Channel(1)
    botChannel = pygame.mixer.Channel(2)

    sock = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)
    sock.sendto(str.encode("requestjoin:dvdbot"), ("localhost", 11000))

    x = 0.0
    y = 0.0
    lastX = 0.0
    lastY = 0.0
    rows = 256
    walls = [[0]* rows] * rows
    dir = "ne"
    beatcount = 0

    while True: 
        if beatcount == 5:
            beatChannel.play(sounds[0], -1, 150, 0)
            beatcount = 0
        beatcount+=1 

        lastX = x
        lastY = y
        msg = sock.recvfrom(1024)[0].decode("ascii")
        # playerupdate:x,y,health,ammo,hasKey
        if "playerupdate" in msg:
            pos = msg.split(":")[1]
            posParts = pos.split(",")
            x = float(posParts[0])
            y = float(posParts[1])

            dir, soundINDEX = newDirection(lastX, x, lastY, y, dir, soundINDEX, botChannel, sounds) 

        # playerjoined:class,name,x,y
        if "playerjoined" in msg:
            pos = msg.split(":")[1]
            posParts = pos.split(",")
            x = float(posParts[2])
            y = float(posParts[3])
        
        move2Dir(dir, x, y, sock)


def move2Dir(dir, x, y, sock):
    # LEZ GAUR
    if dir == "ne":
        y -= 10
        x += 10
    elif dir == "nw":
        y -= 10
        x -= 10
    elif dir == "se":
        y += 10
        x += 10
    elif dir == "sw":
        y += 10
        x -= 10
    msg = f"moveto:{x},{y}"
    sock.sendto(str.encode(msg), ("localhost", 11000))


def newDirection(lastX, x, lastY, y, oldDir, soundINDEX, botChannel, sounds):
    sensitivity = 0.25
    xUnchanged = lastX < (x + sensitivity) and lastX > (x - sensitivity)
    yUnchanged = lastY < (y + sensitivity) and lastY > (y - sensitivity)
    newDir = oldDir
    
    if xUnchanged:
        botChannel.play(sounds[soundINDEX], -1, 200, 0)
        soundINDEX = random.randrange(0, 20)
        if oldDir == "ne":
            newDir = "nw"
        elif oldDir == "nw":
            newDir = "ne"
        elif oldDir == "se":
            newDir = "sw"
        elif oldDir == "sw":
            newDir = "se"

    elif yUnchanged:
        botChannel.play(sounds[soundINDEX], -1, 200, 0)
        soundINDEX = random.randrange(0, 20)
        if oldDir == "ne":
            newDir = "se"
        elif oldDir == "nw":
            newDir = "sw"
        elif oldDir == "se":
            newDir = "ne"
        elif oldDir == "sw":
            newDir = "nw"

    return (newDir, soundINDEX)


def mKESOUNDS(sampleRate):
    sounds = []
    for i in range(20):
        freq = 400 + (i * 20)
        arr = numpy.array([4096 * numpy.sin(2.0 * numpy.pi * freq * x / sampleRate) for x in range(0, sampleRate)]).astype(numpy.int16)
        arr2 = numpy.c_[arr,arr]
        sound = pygame.sndarray.make_sound(arr2)
        sounds.append(sound)
    
    return sounds


if __name__ == "__main__":
    gameloop()