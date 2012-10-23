'''
Created on Apr 4, 2009

@author: God
'''
import os
import pygame

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

tryFrame = 7
#while not tryFrame in Tree['Character']["Jump"]:
print bool(Tree['Character']["Jump"][str(0)])