import sys
import random
from gamegrid import *
import json

# Konstanten
class CONS():
    GAME_W  = 1000 #Konstante Spiel Breite
    GAME_H  = 400 #Konstante Spiel Höhe
    SPEED   = 100
    OBJ_SPEED = 0.05
    DELAY   = 1
    JMP_KEY = 32
    JMP_MAX = 75
    DUK_KEY = 40
    BIRD_Y  = 260
    BIRD_Y_2 = 320
    BTN_W   = 200

# Wir haben hier unsere Main Klasse erstellt.
class Main():
    
    # Initialisierende Funktion
    def __init__(self):
        self.isInGame = False
        makeGameGrid(CONS.GAME_W,
                         CONS.GAME_H,
                         1,
                         Color.black,
                         None,
                         False,
                         keyPressed = self.keyPressed,
                         keyReleased = self.keyReleased)
                         
        setTitle("PyDino")
        show()
        self.welcome = Welcome()
        
    def keyPressed(self, e):
        if self.isInGame:
            if e.getKeyCode() == 32:
                game.dino.setIsJumping(True)
            
            elif e.getKeyCode() == 40:
                game.dino.setIsDucking(True)
                
        else:
            if e.getKeyCode() == 32:
                self.welcome.start()
            
    def keyReleased(self, e):
        if self.isInGame:
            game.dino.setIsDucking(False)

#welcome screen class
class Welcome():
    def __init__(self):
        self.txtWelcome = Text(0)
        addActor(self.txtWelcome, Location(int(CONS.GAME_W / 2), 80))
        
        self.dinoWelcome = DinoWelcome()
        addActor(self.dinoWelcome, Location(int(CONS.GAME_W / 2), 175))
        
        self.btnNew = Button(0)
        addActor(self.btnNew, Location(int(CONS.GAME_W / 2 - 110), 275))
        self.btnNew.addMouseTouchListener(self.start, GGMouse.lClick)
        
        self.btnScores = Button(1)
        addActor(self.btnScores, Location(int(CONS.GAME_W / 2 + 110), 275))
        self.btnScores.addMouseTouchListener(self.highscores, GGMouse.lClick)
        
        self.txtStart = Text(1)
        addActor(self.txtStart, Location(int(CONS.GAME_W / 2), 325))

        setSimulationPeriod(500)
        doRun()
        
    
    def start(self, *args):
        removeAllActors()
        doPause()
        game.initGame()
    
    def highscores(self, *args):
        print(args)

#game controller class
class Game():
    def initGame(self):
        main.isInGame = True #solve this shit with set/get
        self.score = 0
        self.count = 0
        registerAct(self.onAct)
  
        self.dino = Dino()
        addActor(self.dino, Location(175, 325))
        
        addActor(Score(), Location(60, 20))
        
        addActor(Floor(), Location(500, 375))
               
        setSimulationPeriod(CONS.SPEED)
        doRun()
        
    def newFloor(self):
        addActor(Floor(), Location(1450, 375))

    def onAct(self):
        ####CONS.OBJ_SPEED += 0.0001  
              
        if self.count == 40:
            
            if random.randint(1, 2) == 1:
                for i in range(0, random.randint(1, 6)):
                    cactus = Cactus()
                    addActor(cactus, Location(int(CONS.GAME_W + (i * 50)), 322))
                    self.dino.addColActor(cactus)
            
            else:
                bird = Bird()
                birdY = random.randint(0,1)
                
                if birdY == 0:
                    posY = CONS.BIRD_Y
                else:
                    posY = CONS.BIRD_Y_2
                    
                addActor(bird, Location(int(CONS.GAME_W + 20), posY))
                self.dino.addColActor(bird)  
        
            self.count = 0
        else:
            self.count += 1

# floor actor class, inherits functions from existing actor class
class Floor(Actor):
    def __init__(self):
        Actor.__init__(self, ["sprites/floor.png"])
        self.vx = 10
        self.floorOrdered = False
        self.show()

    def reset(self):
        self.px = self.getX()
        self.py = self.getY()   

    def act(self):
        self.movePhysically()
    
    def movePhysically(self):
        self.dt = CONS.OBJ_SPEED * getSimulationPeriod()
        self.px = self.px - self.vx * self.dt
        self.setLocation(Location(int(self.px), int(self.py)))
        self.destroy()
        
        if self.getX() <= 500 and not self.floorOrdered:
            self.floorOrdered = True
            game.newFloor()
    
    def destroy(self):
        if self.px == -500:
            self.removeSelf()

#dino actor class, inherits functions from existing actor class
class Dino(Actor):
    def __init__(self):
        self.isJumping = False
        self.doubleJump = False
        self.isDucking = False
        self.vy = -25
        self.gravity = 2.3
        
        Actor.__init__(self, ["sprites/dino_w_1.png",
                              "sprites/dino_w_2.png",
                              "sprites/dino_d_1.png",
                              "sprites/dino_d_2.png",
                              "sprites/dino_j.png"])

    def reset(self):
        self.px = self.getX()
        self.py = self.getY()
        
                              
    def collide(self, a1, a2):
        getBg().clear()
        removeAllActors()
        doPause()
        GameOver()
        return 0
    
    def act(self):
        if self.isJumping:
            self.py += self.vy
            
            if self.py > 325:
                self.py = 325
                self.vy = -25
                self.isJumping = False
                self.doubleJump = False
                self.show(0)
            else:
                self.show(4)
            
            self.setLocation(Location(int(self.px), int(self.py)))
            self.vy += self.gravity
                                            
        elif self.isDucking:
            self.setLocation(Location(175, 343))
            if self.getIdVisible() != 2:
                self.show(2)
            else:
                self.show(3)
    
        else:
            self.setLocation(Location(175, 325))
            #playTone([("c'e'g'f''g'e'c'", 50)])
            if self.getIdVisible() != 1:
                self.show(1)
            else:
                self.show(0)

    def setIsJumping(self, isJumping):
        if self.isJumping == True and self.doubleJump == False:
            self.doubleJump = True
            self.vy -= 10
        else:
            self.isJumping = isJumping
            
    def setIsDucking(self, isDucking):
        self.isDucking = isDucking

    def addColActor(self, actor):
        self.addCollisionActor(actor)

#cactus actor class, iherits functions from existing actor class
class Cactus(Actor):
    def __init__(self):
        Actor.__init__(self, ["sprites/cactus_1.png",
                              "sprites/cactus_2.png",
                              "sprites/cactus_3.png",
                              "sprites/cactus_4.png"])
        self.vx = 10
        img = random.randint(0, 3)
        self.show(img)

    def reset(self):
        self.px = self.getX()
        
        if self.getIdVisible() == 2:
            print("small called")
            self.py = 335
        else:
            self.py = self.getY()
        
    def act(self):
        self.movePhysically()
    
    def movePhysically(self):
        self.dt = CONS.OBJ_SPEED * getSimulationPeriod()
        self.px = self.px - self.vx * self.dt
        self.setLocation(Location(int(self.px), int(self.py)))
        self.destroy()

    def destroy(self):
        if self.getX() <= 900 and not self.isInGrid():
            self.removeSelf()

#bird actor class, inherits functions from existing actor class
class Bird(Actor):
    def __init__(self):
        Actor.__init__(self, ["sprites/bird_1.png",
                              "sprites/bird_2.png"])
        self.vx = 10
        self.show(0)

    def reset(self):
        self.px = self.getX()
        self.py = self.getY()

    def act(self):    
        self.movePhysically()
        
        if self.getIdVisible() == 0:
            self.show(1)
        else:
            self.show(0)
    
    def movePhysically(self):
        self.dt = CONS.OBJ_SPEED * getSimulationPeriod()
        self.px = self.px - self.vx * self.dt
        self.setLocation(Location(int(self.px), int(self.py)))
        self.destroy()

    def destroy(self):
        if self.getX() <= 900 and not self.isInGrid():
            self.removeSelf()

class Score(Actor):
    def __init__(self):
        self.score = 0
        
        Actor.__init__(self, "sprites/score.png")
        self.show()
    
    def act(self):
        getBg().clear()
        getBg().setPaintColor(Color.white)
        getBg().drawText(str(int(round(self.score / 10, 0))), Point(115, 31))
        self.score += 1

#dino on welcome screen
class DinoWelcome(Actor):
    def __init__(self):
        Actor.__init__(self, ["sprites/dino_s_r.png",
                              "sprites/dino_s_c.png",
                              "sprites/dino_s_r.png",
                              "sprites/dino_s_l.png"])
        self.show()
    
    def act(self):
        self.showNextSprite()

#button component
class Button(Actor):
    def __init__(self, sprite):
        Actor.__init__(self, ["sprites/new.png",
                              "sprites/scores.png",
                              "sprites/save.png",
                              "sprites/cancel.png"])
        self.show(sprite)

#text component (sprites as text)
class Text(Actor):
    def __init__(self, sprite):
        Actor.__init__(self, ["sprites/welcome.png",
                              "sprites/start.png",
                              "sprites/start_b.png"])
        self.show(sprite)
        
    def act(self):
        if self.getIdVisible() == 1:
            self.show(2)
        elif self.getIdVisible() == 2:
            self.show(1)

#Game over screen
class GameOver():
    def __init__(self):
        global game
        print("game over")
        del game

#Highscores screen
class Highscores():
    def __init__(self):
        return 0
        
if __name__ == '__main__':
    main = Main()
    game = Game()