'''
Created on Apr 7, 2009

@author: God
'''
from Things import *

class Level:
    
    def __init__(self,register):
        self.register = register
        self.register.state = {}
        self.platforms = []
        self.floor = None
        self.background = None
        self.walls = []
        self.bullets = []
        self.enemies = []
        self.deadEnemies = []
        self.backgroundObjects = []
        self.effects = []
        self.images = {}
        self.pause = False
        self.toDraw = []
        
        if not hasattr(self,'begin'): #Abstract Method
            raise NotImplementedError, "Must provide begin()"
    
    def ai(self):
        self.ai2()
        for enemy in self.enemies:
            enemy.ai()
            
    def ai2(self):
        None
    
    def draw(self):
        
        screen = self.register.screen
        
        if self.background:
            self.background.draw()
        for object in self.backgroundObjects:
            if screen.isOnScreen(object): object.draw()
        for platform in self.platforms:
            if screen.isOnScreen(platform): platform.draw()
        for wall in self.walls:
            if screen.isOnScreen(wall): wall.draw()
        if not self.pause:
            for bullet in self.bullets:
                if screen.isOnScreen(bullet): bullet.draw()
            for enemy in self.enemies:
                if screen.isOnScreen(enemy): enemy.draw()
                #pygame.draw.rect(screen.get(),(255,0,0),enemy.rect,5)
            for enemy in self.deadEnemies:
                if screen.isOnScreen(enemy): enemy.draw()
            for effect in self.effects:
                if screen.isOnScreen(effect): effect.draw()
            for func in self.toDraw: func()
            self.register.character.draw()
        if self.floor:
            self.floor.draw()
            
        self.toDraw = []
        
    def makeRect(self):
        for enemy in self.enemies:
            enemy.setRect()
        for bullet in self.bullets:
            bullet.setRect()
        for effect in self.effects:
            effect.setRect()
        self.register.character.setRect()
            
    def moveEnemies(self):
        for enemy in self.enemies:
            enemy.move()
    
    def physics(self,g):
        self.register.character.physics(g)        
        for enemy in self.enemies:
            enemy.physics(g)
        for enemy in self.deadEnemies:
            enemy.physics(g)
            enemy.clean()
        for bullet in self.bullets:
            bullet.clean()
        for bullet in self.bullets:
            bullet.updatePos()      
            
    def reset(self):
        self.__init__(self.register)
        self.begin() 
        
    def setTimeAll(self,time):
        self.register.character.time = time
        for enemy in self.enemies:
            enemy.time = time
    
    def testPlatforms(self,object):
        for platform in self.platforms:
            answer = platform.testSupport(object)
            if answer is "Top":
                object.vy = 0
                object.y = platform.y - (object.height/2)
                object.state['grounded'] = True
                if abs(object.vx) > 1:
                    object.vx /= 2
                else:
                    object.vx = 0
                return answer
            elif answer is "Bottom":
                object.vy = 0
                object.y = platform.y + (object.height/2)
                return answer
                
    def testWalls(self,object):
        for wall in self.walls:
            answer = wall.isTouching(object)
            if answer is "Left":
                object.vx = 0
                object.x = wall.x - (object.width/2)
                return answer
            elif answer is "Right":
                object.vx = 0
                object.x = wall.x + (object.width/2)
                return answer
                
    def testCollisions(self):
        Character = self.register.character
        if Character.state['alive']:
            self.testWalls(Character)
            self.testPlatforms(Character)
        for enemy in self.enemies:
            if self.testWalls(enemy):
                enemy.react("touchingWall")
            enemy.state['grounded'] = False
            if not self.testPlatforms(enemy):
                enemy.react("falling")
            if enemy.collision(Character) and Character.state['alive']:
                if not Character.state['shelled']:
                    Character.state['alive'] = False
                    Character.vx = 0
                    Character.vy = -20
                elif Character.vy >= 27:
                    enemy.die()
                    self.effects.append(Effects.ShellHit(self.register,Character.x,Character.y))
                    Character.vy = -15
            for bullet in self.bullets:
                if enemy.collision(bullet):
                    enemy.die()
                    bullet.removeThyself()
        for wall in self.walls:
            for bullet in self.bullets:
                if wall.isTouching(bullet):
                        bullet.removeThyself()
             
class TestLevel(Level):
    
    def begin(self):
        self.floor = Floor(self.register,800,'grass')
        self.floor.imgOffset = 44
        self.background = Background(self.register,(157,210,255))
        
        self.backgroundObjects.append(BackgroundObjects.Sign(self.register,650,450,['   Watch out for Gandhi.',
                                                                                   'He\'ll slow you down with',
                                                                                   'his mediation ray, then',
                                                                                   'run your dumb ass over']))
        self.backgroundObjects[-1].y = 450 - self.backgroundObjects[-1].height / 2
        
        self.platforms.extend([self.floor,Platform(self.register,600,450,300,2,False)])
        self.walls.extend([Wall(self.register,0,0,800,5,True),Wall(self.register,1000,0,800,5,False)])
        self.enemies.append(Enemies.Gandhi(self.register,150,600))

        self.register.character.nextSpawn = [700,0]
        self.register.character.spawn()
