'''
Created on Apr 4, 2009

@author: MediocreGopher
'''
import pygame
import os

class Screen:
    def __init__(self,register,width,height):
        self.width = width
        self.height = height
        self.register = register
        
        self.screen = pygame.display.set_mode((width, height))
        
    def get(self):
        return self.screen
    
    def drawPrep(self):
        self.xOffset = self.width / 2 - self.register.character.x
        if self.register.character.y < self.register.level.floor.y - self.height / 2 + 50:
            self.yOffset = self.height / 2 - self.register.character.y
        else:
            self.yOffset = -50
            
        #print 'xOffset:' + str(self.xOffset)
        #print 'yOffset:' + str(self.yOffset)
        
    def isOnScreen(self,object):
        #pygame.draw.rect(self.get(),(255,0,0),pygame.Rect(0,0,self.width,self.height),5)
        return pygame.Rect(0,
                           0,
                           self.width,self.height).colliderect(object.rect)

class MenuItems:     
            
    class Item:
        def __init__(self,register,text):
            self.register = register
            self.text = text
            self.selected = False
            
        def draw(self,x,y):
                font = pygame.font.Font(None, 30)
                text = font.render(self.text, True, (196,249,175))
                textRect = text.get_rect()
                textRect.topleft = (x,y)
                self.register.screen.get().blit(text, textRect)
                
                if self.selected:
                    arrow = pygame.image.load(os.path.join('images', 'MenuItems', 'Item', 'arrow.png'))
                    self.register.screen.get().blit(arrow,( textRect.right + 10,y))

    class Pause_Menu():
    
        def __init__(self,register):
            self.register = register
            self.screen = self.register.screen
            self.width = self.screen.width - (self.screen.width * 3 / 5)
            self.height = self.screen.height - (self.screen.height / 2)
            self.img = pygame.image.load(os.path.join('images', 'MenuItems', 'pausemenu.png'))       
            self.topx = (self.screen.width / 2) - (self.width / 2)
            self.topy = (self.screen.height / 2) - (self.height / 2)
            self.destx = self.screen.width / 2
            self.x = 0
            self.y = self.screen.height / 2
            
            self.list = [MenuItems.Item(self.register,"Back to 'The Game'"), MenuItems.Item(self.register,"Restart Level"), MenuItems.Item(self.register,"Exit")]
        
            self.animationState = "To"
            self.selection = 0
            self.list[self.selection].selected = True  
             
        def draw(self):
            if self.animationState == "To" and self.x < self.destx:
                self.x += 80
            elif self.animationState == "From":
                self.x -= 80
            
                   
            self.register.screen.get().blit(self.img,(self.x - (self.img.get_width()/2),self.y - (self.img.get_height()/2)))
            next = 0
            for item in self.list:
                item.draw(self.x - (self.width / 4),self.topy + 50 + next)
                next += 40
                
        def select(self,dir):
              
            self.list[self.selection].selected = False
            if dir is "Down" and self.selection + 1 < len(self.list):
                self.selection += 1
            elif dir is "Up" and self.selection > 0:
                self.selection -= 1
            self.list[self.selection].selected = True
            
        def cmd(self):
            return self.list[self.selection].text
        
        
        