'''
Created on Mar 22, 2009

@author: God
'''
import time
import pygame
from Things import *
import Interface
import Levels
from Registry import Register
import os
from pygame.locals import *

pygame.init()

screen_w = 1000
screen_h = 800

Register = Register()

def makeTree(path):
    subTree = {}
    for item in os.listdir(path):
        newPath = os.path.join(path,item)
        if os.path.isdir(newPath):
            subTree[item] = makeTree(newPath)
        elif item[0] is not '~' and item.split('.')[1] == 'png':
            subTree[item.split('.')[0]] = pygame.image.load(newPath)
    return subTree

Tree = makeTree('images')

Screen = Interface.Screen(Register,screen_w,screen_h)

Register.screen = Screen

Pause = Interface.MenuItems.Pause_Menu(Register)

secondsPerFrame = 1.0 / 30
g = 2
loopTo = 'gameloop'

Character = Character(Register)
Level = Levels.TestLevel(Register)

Register.level = Level
Register.tree = Tree
Register.pause = Pause
Register.character = Character

Level.begin()

def game():
    global loopTo
    Level.pause = False
    while loopTo is 'gameloop':
        delayTime = time.clock()

        #handle input
        for event in pygame.event.get():
            if event.type == KEYUP and event.key == K_RETURN:
                loopTo = "pause"
            if event.type == KEYDOWN and event.key == K_DOWN and Character.state['grounded'] and not Character.state['unshelling']:
                Character.vy = -5
                Character.vx = 3
            if event.type == QUIT:
                loopTo = "exit"
                
        
        pressedKeys = pygame.key.get_pressed()
        if pressedKeys[K_DOWN] and Character.state['alive'] and not Character.state['unshelling']:
            Character.state['shelled'] = True
            if pressedKeys[K_LEFT] and not Character.state['grounded']:
                Character.x -= Character.walkSpeed * Character.time
            if pressedKeys[K_RIGHT] and not Character.state['grounded']:
                Character.x += Character.walkSpeed * Character.time
        elif Character.state['shelled'] and not pressedKeys[K_DOWN] and Character.state['alive']:
                Character.state["shelled"] = False
                Character.state["unshelling"] = True
                Character.newAnimation("Unshelling")           
        elif not Character.state['unshelling'] and Character.state['alive']:
            Character.state['shelled'] = False
            if pressedKeys[K_LEFT]:
                Character.x -= Character.walkSpeed * Character.time
                if not Character.animationState[0] and Character.state['grounded']:
                    Character.newAnimation("Walk")
            if pressedKeys[K_RIGHT]:
                Character.x += Character.walkSpeed * Character.time
                if not Character.animationState[0] and Character.state['grounded']:
                    Character.newAnimation("Walk")
            if pressedKeys[K_UP] and Character.state['grounded']:
                Character.newAnimation("Jump")
            if pressedKeys[K_SPACE]:
                Character.shoot()
        if pressedKeys[K_ESCAPE]:
            loopTo = "exit"
        
        Level.moveEnemies()
        Level.setTimeAll(1)
        #physics
        Level.physics(g)
        
        Character.state['grounded'] = False
        Level.makeRect()
        Level.testCollisions()

        Level.ai()
        Character.incrFrame()
        Character.updateWeapon()
        drawMain()
        

              
        pygame.display.flip()
        if secondsPerFrame - (time.clock() - delayTime) > 0:
            time.sleep(secondsPerFrame - (time.clock() - delayTime))
        else: print 'lag'

def drawMain():
    if not Level.background:   
        Screen.get().fill((255,255,255))
    if Character.state['alive']:
        Screen.drawPrep()     
    Level.draw()
          
def pause():
    global loopTo
    Pause.animationState = "To"
    Pause.x = 0
    Level.pause = True
    while loopTo is 'pause':
        delayTime = time.clock()
        
        #handle input
        for event in pygame.event.get():
            if event.type == KEYUP and event.key == K_DOWN:
                Pause.select("Down")
            elif event.type == KEYUP and event.key == K_UP:
                Pause.select("Up")
            if event.type == KEYUP and event.key == K_RETURN:
                command = Pause.cmd()
                if command == "Back to 'The Game'":
                    Pause.animationState = "From"
                elif command == "Restart Level":
                    Level.reset()
                    loopTo = "gameloop"
                elif command == "Exit":
                    loopTo = "exit"
        
        if Pause.animationState == "From" and Pause.x <= 0:
            loopTo = "gameloop"
        
        pressedKeys = pygame.key.get_pressed()
        if pressedKeys[K_ESCAPE]:
            loopTo = "exit"
            
        drawMain()
        Pause.draw()
        
        pygame.display.flip()
        if secondsPerFrame - (time.clock() - delayTime) > 0:
            time.sleep(secondsPerFrame - (time.clock() - delayTime))

while loopTo is not "exit":
    if loopTo is "gameloop":
        game()
    elif loopTo is "pause":
        pause()