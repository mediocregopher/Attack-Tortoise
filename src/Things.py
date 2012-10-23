'''
Created on Apr 4, 2009

@author: MediocreGopher
'''
import pygame
import os.path

class Character:
    
    def __init__(self,register):
        self.x = 0
        self.y = 0
        self.register = register
        self.nextSpawn = [0,0]
        
        self.img = pygame.image.load(os.path.join('images', 'Character', 'still.png'))
        
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.vx = 0
        self.vy = 0
        self.walkSpeed = 10
        self.jumpSpeed = -25
        self.state = {}
        self.__initStates()
        self.setRect()
        self.time = 1
        
        self.animationState = ["",0]
        self.animationLength = {'Jump':3,
                                'Walk':6,
                                'Unshelling':20,
                                'Die':0,
                                'Still':0,
                                'Airborne':0,
                                'Shelled':0}
        
        self.weapon = Weapons.LaserCannon(self.register,self)
        
    def spawn(self):
        [self.x,self.y] = self.nextSpawn
        self.__initStates()
        self.animationState = ["",0,0]
        self.vx = self.vy = 0
        
    def draw(self):
        screen = self.register.screen   
        currentAn = self.animationState[0]
        if currentAn and self.state['alive']:
            if self.animationState[1] < self.animationLength[currentAn] or not self.animationLength[currentAn]:
                tryFrame = self.animationState[1]
                while not (str(tryFrame) in self.register.tree['Character'][currentAn]) and tryFrame > 0:
                    tryFrame -= self.time
                    if not tryFrame % 1: tryFrame = int(tryFrame)
                if tryFrame < 0: tryFrame = 0
                self.img = self.register.tree['Character'][currentAn][str(tryFrame)]
                self.animationState[1] += self.time
            else:
                self.animationState = ["",0]
                if currentAn == "Jump":
                    self.vy = self.jumpSpeed
                    self.state['grounded'] = False   
                elif currentAn == "Unshelling":
                    self.state['unshelling'] = False
                self.img = self.register.tree['Character']['still']
        else:
            if not self.state['alive']:
                self.img = self.register.tree['Character']['dead']
            elif self.state['shelled']:
                self.img = self.register.tree['Character']['shelled']
            elif self.state['grounded']:
                self.img = self.register.tree['Character']['still']
            else:
                self.img = self.register.tree['Character']['airborne']
        screen.get().blit(self.img,(self.x - (self.img.get_width()/2) + screen.xOffset,self.y - (self.img.get_height()/2) + screen.yOffset))
        self.weapon.draw()
            
    def __initStates(self):
        self.state['grounded'] = False
        self.state['shelled'] = False
        self.state['unshelling'] = False
        self.state['alive'] = True
        
    def updateHW(self):
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        
    def newAnimation(self,animation):
        if self.animationState[0] is not animation:
            self.animationState = [animation,0,0]

    def updateWeapon(self):
        self.weapon.updatePos()
        
    def shoot(self):
        self.weapon.shoot()
        
    def incrFrame(self):
        if self.weapon.lastShot < 10000:
            self.weapon.lastShot += self.time
        
        if not self.state['alive'] and self.y + self.register.screen.yOffset > 1000:
            self.spawn()
            
    def physics(self,g):
        if not self.state['grounded'] or not self.state['alive']:
            self.vy += g
    
        self.x += self.vx
        self.y += self.vy
                   
    def setRect(self):
        self.rect = pygame.Rect(self.x - self.width / 2,
                    self.y - self.height / 2,
                    self.width,self.height)
                   
class Platform:
    
    def __init__(self,register,x,y,length,thickness,dual):
        self.register = register
        self.xone = x
        self.xtwo = x + length
        self.y = y
        self.thickness = thickness
        self.dual = dual
        self.activated = True
        self.rect = pygame.Rect(x,y,length,1)        
        
    def draw(self):
        screen = self.register.screen
        pygame.draw.line(screen.get(),(0, 0, 0),(self.xone + screen.xOffset, self.y + screen.yOffset),(self.xtwo + screen.xOffset, self.y + screen.yOffset),self.thickness)

    def testSupport(self,object):
        if object.x >= self.xone and object.x <= self.xtwo and self.activated:
            if object.y + (object.height/2) >= self.y and object.y + (object.height/2) - object.vy <= self.y and object.vy >= 0:   
                return "Top"
            elif self.dual and object.y + (object.height/2) > self.y and object.y - (object.height/2) <= self.y:
                return "Bottom"
        return False
    
class Floor:
    
    def __init__(self,register,y,img):
        self.register = register
        self.y = y
        self.imgName = None
        self.thickness = None
        self.imgOffset = 0
        if type(img) == int:
            self.thickness = img
        else:
            self.imgName = img
        self.rect = pygame.Rect(0,0,1,1)
            
    def draw(self):
        screen = self.register.screen
        img = self.register.tree['World']['Floor'][self.imgName]
        if self.thickness >= 0:
            pygame.draw.line(screen.get(),(0, 0, 0),(0, self.y + screen.yOffset),(screen.width, self.y + screen.yOffset),self.thickness)
        else:
            number_needed = int(screen.width / img.get_width()) + 1
            for it in range(-1,number_needed):
                screen.get().blit(img,(it*img.get_width() + screen.xOffset % img.get_width(),self.y + screen.yOffset - self.imgOffset))
            
    def testSupport(self,object):
            if object.y + (object.height/2) >= self.y and object.y + (object.height/2) - object.vy <= self.y and object.vy >= 0:   
                return "Top"

class Wall:
    
    def __init__(self,register,x,y,height,thickness,dual):
        self.register = register
        self.yone = y
        self.ytwo = y + height
        self.x = x
        self.thickness = thickness
        self.dual = dual
        self.activated = True
        self.rect = pygame.Rect(x,y,1,height)
        
    def draw(self):
        screen = self.register.screen
        pygame.draw.line(screen.get(),(0, 0, 0),(self.x + screen.xOffset, self.yone + screen.yOffset),(self.x + screen.xOffset, self.ytwo + screen.yOffset),self.thickness)

    def isTouching(self,object):
        if object.y >= self.yone and object.y <= self.ytwo and self.activated:
            if object.x + (object.width/2) >= self.x and object.x - object.vx <= self.x:# and object.vx >= 0:
                return "Left"
            elif self.dual and object.x + (object.width/2) > self.x and object.x - (object.width/2) <= self.x:
                return "Right"
        return False

class Weapons:
    
    class LaserCannon:
        
        def __init__(self,register,char):
            self.register = register
            self.attachedTo = char
            self.xBuffer = 0
            self.yBuffer = 0
            self.updatePos()
            
            self.lastShot = 0
            
        def updatePos(self):
            char = self.attachedTo
            if char.animationState[0] is "Jump" and char.animationState[1] < 2:
                self.yBuffer = 5
                self.xBuffer = 0
            elif char.animationState[0] is "Unshelling":
                if char.animationState[1] < 8:
                    self.yBuffer = 3
                    self.xBuffer = 10
                elif 8 <= char.animationState[1]:
                    self.yBuffer = 1
                    self.xBuffer = 0
                
            elif char.state['shelled'] and not char.animationState[0]:
                self.yBuffer = 3
                self.xBuffer = 10
            elif not char.state['grounded'] and not char.animationState[0]:
                self.yBuffer = 4
                self.xBuffer = 0
            else:
                self.yBuffer = 1
                self.xBuffer = 0
            self.x = self.attachedTo.x + self.xBuffer + 17
            self.y = self.attachedTo.y + self.yBuffer - 21
            
        def draw(self):
            screen = self.register.screen
            if self.attachedTo.state['alive']:
                weapImg = self.register.tree['Weapons']['LaserCannon']['cannon']    
                screen.get().blit(weapImg,(self.x - (weapImg.get_width()/2) + screen.xOffset,self.y - (weapImg.get_height()/2) + screen.yOffset)) 
      
        def shoot(self):
            if self.lastShot >= 10:
                self.register.level.bullets.append(self.Bullet(self.register,self.x,self.y - 5))
                self.lastShot = 0
                if not self.attachedTo.state['grounded']:
                    self.attachedTo.vx -= 2
                    
        class Bullet:
            
            def __init__(self,register,x,y):
                self.register = register
                self.x = x
                self.y = y
                
                baseImg = pygame.image.load(os.path.join('images', 'Weapons', 'LaserCannon', 'Bullet', 'bullet.png'))
                
                self.width = baseImg.get_width()
                self.height = baseImg.get_height()
                self.setRect()
                self.vx = 20
                self.vy = 0
                
            def draw(self):
                screen = self.register.screen
                tempx = self.x - (self.width/2) + screen.xOffset
                tempy = self.y - (self.height/2) + screen.yOffset
                if (0 <= tempx <= screen.width) and (0 <= tempy <= screen.height):
                    bulletImg = pygame.image.load(os.path.join('images', 'Weapons', 'LaserCannon', 'Bullet', 'bullet.png'))
                    screen.get().blit(bulletImg,(tempx,tempy))
    
            def clean(self):
                if self.x - (self.width/2) + self.register.screen.xOffset > self.register.screen.width + 100:
                    self.removeThyself()
                    
            def removeThyself(self):
                self.register.level.bullets.remove(self)
            
            def updatePos(self):
                self.x += self.vx
                
            def setRect(self):
                self.rect = pygame.Rect(self.x - self.width / 2,
                            self.y - self.height / 2,
                            self.width,self.height)
     
    class MediationRay:
         
        def __init__(self,register,gandhi,target):
            self.target = target
            self.register = register
            self.attachedTo = gandhi
            
            self.xBuffer = -30
            self.yBuffer = -20
            
            self.img = register.tree['Weapons']['MediationRay']['ray']
            self.img2 = register.tree['Weapons']['MediationRay']['surround']
             
        def draw(self):
            target = self.target
            travelDir = 1 #1 -> going right
            if self.attachedTo.state['goingLeft']: travelDir = -1
            it = ((target.x - (target.width * 1.75)*travelDir) - (self.attachedTo.x + (self.attachedTo.width / 2)*travelDir*-1))*travelDir       
            #number of iterations is the same as the length because the picture is only 1px wide
            beginat = self.attachedTo.x + (self.attachedTo.width / 2)*travelDir
            screen = self.register.screen
            for i in range(1,int(it+5-self.xBuffer)):
                screen.get().blit(self.img,(beginat + (i * travelDir) + screen.xOffset + (self.xBuffer * travelDir),self.attachedTo.y + screen.yOffset + self.yBuffer))      
            screen.get().blit(self.img2,(int(target.x - target.width * 0.75 + screen.xOffset),target.y - target.height - 25 + screen.yOffset))
                   
class Enemies:
    
    class Enemy:
        
        def __init__(self,register,x,y):
            self.register = register
            self.animationLength = {}
            self.state = {}
            self.init2()
            if not hasattr(self,'init2'): #Abstract Method
                raise NotImplementedError, "Must provide init2()"
            self.x = x
            self.y = y
            self.vx = 0
            self.vy = 0
            
            self.img = pygame.image.load(os.path.join('images', 'Enemies', self.name, 'base.png'))
            
            self.height = self.img.get_height()
            self.width = self.img.get_width()
            self.setRect()

            self.animationState = ["",0,0]
            self.reactTo = []
            self.initStates()
            self.time = 1
        
        def ai(self):
            None
            
        def clean(self):
            if self.y - (self.img.get_height()/2) + self.register.screen.yOffset > 1000 and not self.state['alive']:
                self.register.level.deadEnemies.remove(self)
        
        def collision(self,object):
            return self.rect.colliderect(object.rect)
        
        def die(self):
            self.register.level.enemies.remove(self)
            self.register.level.deadEnemies.append(self)
            self.state['alive'] = False
            self.vy = -20
        
        def draw(self):
            screen = self.register.screen
            if screen.isOnScreen(self):
                if self.state['alive']:
                    self.animationState[0] = "Walk"
                    self.animationState[2] = self.animationLength[self.animationState[0]]
                    if not self.animationState[1] < self.animationState[2]:
                        self.animationState[1] = 0
                    tryFrame = self.animationState[1]
                    while not str(tryFrame) in self.register.tree['Enemies'][self.name][self.animationState[0]] and tryFrame > 0:
                        tryFrame -= self.time
                        if not tryFrame % 1: tryFrame = int(tryFrame)
                    if tryFrame < 0: tryFrame = 0
                    self.img = self.register.tree['Enemies'][self.name][self.animationState[0]][str(tryFrame)]
                    self.animationState[1] += self.time
                else:
                    self.img = self.register.tree['Enemies'][self.name]['dead']
                if not self.state['goingLeft']:
                    self.img = pygame.transform.flip(self.img,True,False)
                screen.get().blit(self.img,(self.x - (self.img.get_width()/2) + screen.xOffset,self.y - (self.img.get_height()/2) + screen.yOffset))         
        
        def setRect(self):
            screen = self.register.screen
            self.rect = pygame.Rect(self.x - self.width / 2,
                        self.y - self.height / 2,
                        self.width,self.height)
        
        def move(self):
            if "touchingWall" in self.reactTo:
                self.state['goingLeft'] = not self.state['goingLeft']
                self.reacted("touchingWall")
            if "falling" in self.reactTo:
                self.state['goingLeft'] = not self.state['goingLeft']
                self.reacted("falling")
            if self.state['goingLeft']:
                self.x -= self.walkSpeed * self.time
            else:
                self.x += self.walkSpeed * self.time
        
        def physics(self,g):
            if not self.state['grounded'] or not self.state['alive']:
                self.vy += g
        
            self.x += self.vx
            self.y += self.vy
        
        def react(self,new):
            self.reactTo.append(new)
        
        def reacted(self,remove):
            self.reactTo.remove(remove)
        
        def initStates(self):
            self.state['grounded'] = False
            self.state['alive'] = True
            self.state['goingLeft'] = True  
            
    class Blob(Enemy):
        
        def init2(self):
            self.name = "Blob"
            self.walkSpeed = 7
            self.weapon = None
            self.animationLength["Walk"] = 1
                
    class Pacman(Enemy):
        
        def init2(self):
            self.name = "Pacman"
            self.walkSpeed = 10
            self.weapon = None
            self.animationLength["Walk"] = 6
            
    class Gandhi(Enemy):
        
        def init2(self):
            self.name = "Gandhi"
            self.walkSpeed = 12
            self.weapon = Weapons.MediationRay(self.register,self,self.register.character)
            self.animationLength["Walk"] = 6
            self.state['time_till_turn'] = 10

        def ai(self):
            char = self.register.character
            charTop = char.y - char.height / 2
            charBottom = char.y + char.height / 2
            selfTop = self.y - self.height / 2 + 55
            selfBottom = self.y + self.height / 2
            
            if (charBottom > selfTop and charBottom < selfBottom) or (charTop > selfTop and charTop < selfBottom):
                left = True
                if char.x - self.x > 0: left = False
                if (left and not self.state['goingLeft']) or (not left and self.state['goingLeft']):
                    if self.state['time_till_turn'] <= 0:
                        self.state['goingLeft'] = not self.state['goingLeft']
                        self.state['time_till_turn'] = 10
                    else: self.state['time_till_turn'] -= self.time
                else:
                    self.register.level.toDraw.append(self.weapon.draw)
                    char.time = 0.5
            else: self.state['time_till_turn'] = 10
        
class Effects:
    
    class Effect:
    
        def __init__(self,register,x,y):
            self.register = register            
            self.x = x
            self.y = y
            
            self.aliveCount = 0
            
            if not hasattr(self,'init2'): #Abstract Method
                raise NotImplementedError, "Must provide init2()"
            elif not hasattr(self,'draw'): #Abstract Method
                raise NotImplementedError, "Must provide draw()"
            
            self.init2()
            self.height = self.img.get_height()
            self.width = self.img.get_width()
            self.setRect()
            
        def removeThyself(self):
            self.register.level.effects.remove(self)
            
        def setRect(self):
            self.rect = pygame.Rect(self.x - self.width / 2,
                        self.y - self.height / 2,
                        self.width,self.height)
            
    class ShellHit(Effect):
        
        def init2(self):
            self.name = 'ShellHit'
            self.img = pygame.image.load(os.path.join('images', 'Effects', self.name, 'base.png'))
            
        def draw(self):
            screen = self.register.screen
            if screen.isOnScreen(self) and self.aliveCount < 10:
                self.img = self.register.tree['Effects'][self.name]['base']
                screen.get().blit(self.img,(self.x - (self.img.get_width()/2) + screen.xOffset,self.y - (self.img.get_height()/2) + screen.yOffset))
                self.aliveCount += 1
            else:
                self.removeThyself()

class Background:
    
    def __init__(self,register,color):
        self.register = register
        self.color = color
        
    def draw(self):
        self.register.screen.get().fill(self.color)
        
class BackgroundObjects:
    
    class BackgroundObject:
    
        def __init__(self,register,x,y,img):
            self.register = register
            self.x = x
            self.y = y
            self.img = self.register.tree['World']['BackgroundObject'][img]
            self.height = self.img.get_height()
            self.width = self.img.get_width()
            self.setRect()
            
        def setRect(self):
            self.rect = pygame.Rect(self.x - self.width / 2,
                                    self.y - self.height / 2,
                                    self.width,self.height)
            
        def draw(self):
            screen = self.register.screen
            screen.get().blit(self.img,(self.x - (self.img.get_width()/2) + screen.xOffset,self.y - (self.img.get_height()/2) + screen.yOffset))
            
    class Sign(BackgroundObject):
        
        def __init__(self,register,x,y,text):
            self.register = register
            self.x = x
            self.y = y
            self.text = text
            self.color = (255,255,255)
            self.font = None
            self.font_size = 25
            self.make_sign()
            self.setRect()
            
        def make_sign(self):
            total_plank_height = 48*len(self.text)-10
            self.img = pygame.Surface((251,62+total_plank_height),pygame.SRCALPHA,32)
            self.img.blit(self.register.tree['World']['BackgroundObject']['Sign']['post'],
                          (113,total_plank_height))
            
            font = pygame.font.Font(self.font, self.font_size)
            for i in range(0,len(self.text)):
                self.img.blit(self.register.tree['World']['BackgroundObject']['Sign']['plank'],
                          (0,i*46))
                text = font.render(self.text[i], True, self.color)
                self.img.blit(text,(20,i*46+15))
                
            self.height = 62 + total_plank_height
            self.width = 251