import sys
import random
from gamegrid import * #from gamegrid import everything

#Constants
class CONS():
    GAME_W       = 1000 #window width
    GAME_H       = 400  #window height
    SPEED        = 100  #game speed
    SPACE_KEY    = 32   #keycode for space
    UP_KEY       = 38   #keycode for up
    DOWN_KEY     = 40   #keycode for down
    GRAVITY      = 2.3  #gravity
    BIRD_Y_HIGH  = 260  #bird position Y (high)
    BIRD_Y_LOW   = 320  #bird position Y (low)
    VEL_X        = 50   #default velocity X

#Main class
class Main():
    def __init__(self):
        self.highscore = 0
        self.score = 0
        self.gridPosition = Point(10, 10)
        self.buildGameGrid()
        self.welcome = Welcome()
    
    #builds our game window
    def buildGameGrid(self):
        self.game = Game() 
        self.isInGame = False
        
        #create game window and set background
        makeGameGrid(CONS.GAME_W,
                     CONS.GAME_H,
                     1,
                     Color.black,
                     None,
                     False,
                     keyPressed = self.keyPressed, #any key pressed -> bind to keyPressed function
                     keyReleased = self.keyReleased) #any key released -> bind to keyReleased function
        
        setPosition(int(self.gridPosition.getX()), int(self.gridPosition.getY()))
        setTitle("PyDino")
        show()
        

    #key pressed down
    def keyPressed(self, e):
        #in game
        if self.isInGame:
            #space or key up pressed
            if e.getKeyCode() == CONS.SPACE_KEY or e.getKeyCode() == CONS.UP_KEY:
                self.game.dino.setIsJumping(True) #set dino jumping
            
            #key down pressed
            elif e.getKeyCode() == CONS.DOWN_KEY:
                self.game.dino.setIsDucking(True) #set dino ducking
        
        #not in game   
        else:
            #if space is pressed
            if e.getKeyCode() == CONS.SPACE_KEY:
                self.welcome.start()
                    
    #key was released
    def keyReleased(self, e):
        #key down released and in game
        if self.isInGame and e.getKeyCode() == CONS.DOWN_KEY:
            self.game.dino.setIsDucking(False) #set dino not ducking


#Welcome screen class
class Welcome():
    def __init__(self):
        #add welcome text to game grid
        addActor(Text(0), Location(int(CONS.GAME_W / 2), 80))
        
        #add welcome dino to game grid
        addActor(DinoWelcome(), Location(int(CONS.GAME_W / 2), 175))

        #add "new game" button to game grid
        self.btnNew = Button(0)
        addActor(self.btnNew, Location(int(CONS.GAME_W / 2), 275))
        self.btnNew.addMouseTouchListener(self.start, GGMouse.lClick) #add mouse touch listener to "new game" button

        #add blinking start text to game grid
        addActor(Text(1), Location(int(CONS.GAME_W / 2), 325))

        #start welcome screen simulation
        setSimulationPeriod(500)
        doRun()

    #game started
    def start(self, *args):
        main.game.initGame()

class Game():        
    def initGame(self):
        removeAllActors()
        registerAct(self.onAct)
        main.isInGame = True
        self.spaceCount = 0
        self.objSpace = 40
  
        self.dino = Dino() #init new dino
        addActor(self.dino, Location(175, 325)) #add dino to scene       
        addActor(Floor(), Location(500, 375)) #add initial floor
        addActor(Score(), Location(60, 20)) #add score count
        addActor(Highscore(), Location(800, 24)) #add highscore count
               
        setSimulationPeriod(CONS.SPEED) #set simulation speed
        doRun() #start simulation
    
    #order a new floor for game grid
    def newFloor(self):
        addActor(Floor(), Location(1450, 375))
    
    #on act function, callback for act function
    def onAct(self):    
        #if object should be made
        if self.spaceCount == self.objSpace:
            
            #if random == 1 -> make new cactus
            if random.randint(1, 2) == 1:
                
                #create between 1 and 3 new cactus
                for i in range(0, random.randint(1, 3)):
                    cactus = Cactus() #init new cactus
                    addActor(cactus, Location(int(CONS.GAME_W + (i * 50)), 322)) #add cactus to scene
                    self.dino.addColActor(cactus) #add cactus as collision partner to dino
            
            #else make new bird
            else:
                bird = Bird() #init new bird
                
                #if random == 1 --> make bird in air
                if random.randint(1, 2) == 1:
                    addActor(bird, Location(int(CONS.GAME_W + 20), CONS.BIRD_Y_HIGH)) #add bird to scene
                
                #else make bird on floor
                else:                                                                                                       
                    addActor(bird, Location(int(CONS.GAME_W + 20), CONS.BIRD_Y_LOW)) #add bird to scene
                
                self.dino.addColActor(bird) #add bird as collision partner to dino  
            
            #reset space count
            self.spaceCount = 0
            
            #if space between objects > 20, remove 1 from object space
            if self.objSpace > 20:
                self.objSpace -= 1
                
        #no new item should be created -> add 1 to space counter
        else:
            self.spaceCount += 1

# floor actor class, inherits functions from existing actor class
class Floor(Actor):
    def __init__(self):
        Actor.__init__(self, ["sprites/floor.png"])
        self.floorOrdered = False
        self.show()

    #get initial position of floor
    def reset(self):
        self.px = self.getX()
        self.py = self.getY()

    #calculate and set new position
    def act(self):
        self.px = self.px - CONS.VEL_X
        self.setLocation(Location(int(self.px), int(self.py)))
        self.destroy()
        
        #if floor about to move off screen
        if self.getX() <= 500 and not self.floorOrdered:
            self.floorOrdered = True #prevent from ordering more than one floor
            main.game.newFloor() #order a new floor on main game function
    
    #destroy floor if moved off screen
    def destroy(self):
        if self.px == -500:
            self.removeSelf()

#dino actor class, inherits functions from existing actor class
class Dino(Actor):
    def __init__(self):
        self.isJumping = False
        self.isDucking = False
        self.vy = -25
        
        #sprites for animation
        Actor.__init__(self, ["sprites/dino_w_1.png",
                              "sprites/dino_w_2.png",
                              "sprites/dino_d_1.png",
                              "sprites/dino_d_2.png",
                              "sprites/dino_j.png"])

    #set initial position
    def reset(self):
        self.px = self.getX()
        self.py = self.getY()
        
    #dino collided with other actor --> game over                          
    def collide(self, *args):
        main.gridPosition = getPosition()
        dispose() #dispose game window
        GameOver() #show game over screen
        return 0
    
    #dino act class
    def act(self):
        #if dino is jumping
        if self.isJumping:
            self.py += self.vy #add velocity Y to position Y
            
            #if position Y greater than 325
            if self.py > 325:
                self.py = 325 #reset position Y
                self.vy = -25 #reset velocity Y
                self.isJumping = False #set jumping to false
                self.show(0) #set default running sprite
            else:
                self.show(4) #set jumping sprite

            self.setLocation(Location(int(self.px), int(self.py))) #set new dino location
            self.vy += CONS.GRAVITY #add gravity to velocity Y
        
        #if dino is ducking                                   
        elif self.isDucking:
            self.setLocation(Location(175, 343)) #set ducking location
            
            #ducking running animation
            if self.getIdVisible() != 2:
                self.show(2)
            else:
                self.show(3)
        
        #dino neither jumping nor ducking
        else:
            self.setLocation(Location(175, 325)) #set default location
            
            #running animation
            if self.getIdVisible() != 1:
                self.show(1)
            else:
                self.show(0)

    #set if dino is jumping or not
    def setIsJumping(self, isJumping):
        self.isJumping = isJumping
    
    #set if dino is ducking or not
    def setIsDucking(self, isDucking):
        self.isDucking = isDucking

    #add a new collision actor to dino
    def addColActor(self, actor):
        self.addCollisionActor(actor)

#cactus actor class, iherits functions from existing actor class
class Cactus(Actor):
    def __init__(self):
        
        #sprites
        Actor.__init__(self, ["sprites/cactus_1.png",
                              "sprites/cactus_2.png",
                              "sprites/cactus_3.png",
                              "sprites/cactus_4.png"])
        img = random.randint(0,3)
        self.show(img)

    #set initial position of cactus
    def reset(self):
        self.px = self.getX()
        
        if self.getIdVisible() == 2:
            self.py = 335
        else:
            self.py = self.getY()
    
    #calculate and set new position
    def act(self):
        self.px = self.px - CONS.VEL_X
        self.setLocation(Location(int(self.px), int(self.py)))
        self.destroy()
    
    def destroy(self):
        #if cactus is off screen --> remove from game
        if self.getX() <= 900 and not self.isInGrid():
            self.removeSelf()

#bird actor class, inherits functions from existing actor class
class Bird(Actor):
    def __init__(self):
        #sprites for animation
        Actor.__init__(self, ["sprites/bird_1.png",
                              "sprites/bird_2.png"])
        self.show(0)

    #set initial position
    def reset(self):
        self.px = self.getX()
        self.py = self.getY()

    #calculate and set new position
    def act(self):
        self.px = self.px - CONS.VEL_X
        self.setLocation(Location(int(self.px), int(self.py)))
        self.destroy()
        
        #switch sprites for bird animation
        if self.getIdVisible() == 0:
            self.show(1)
        else:
            self.show(0)
            
    def destroy(self):
        #if cactus is off screen --> remove from game
        if self.getX() <= 900 and not self.isInGrid():
            self.removeSelf()

#score actor class
class Score(Actor):
    def __init__(self):
        self.score = 0
        
        Actor.__init__(self, "sprites/score.png")
        self.show()
    
    def act(self):
        getBg().setPaintColor(Color.white)
        getBg().drawText(str(int(round(self.score / 10, 0))), Point(115, 31)) #draw score count
        main.score = int(round(self.score / 10, 0))
        self.score += 1 #add one to score
        
class Highscore(Actor):
    def __init__(self):
        Actor.__init__(self, "sprites/highscore.png")
        self.show()
    
    def act(self):
        getBg().clear() #clear background to prevent overwriting
        getBg().setPaintColor(Color.white)
        
        #if highscore greater than score -> display highscore
        if main.highscore > main.score:
            getBg().drawText(str(int(main.highscore)), Point(883, 31))
            
        #else display current score
        else:
            getBg().drawText(str(int(main.score)), Point(883, 31))

#dino on welcome screen
class DinoWelcome(Actor):
    def __init__(self):
        Actor.__init__(self, ["sprites/dino_s_r.png",
                              "sprites/dino_s_c.png",
                              "sprites/dino_s_r.png",
                              "sprites/dino_s_l.png"])
        self.show()
    
    #dino start screen animation
    def act(self):
        self.showNextSprite() #loops through sprites

#dino on over screen
class DinoOver(Actor):
    def __init__(self):
        Actor.__init__(self, ["sprites/dino_over.png"])
        self.show()


#button component
class Button(Actor):
    def __init__(self, sprite):
        Actor.__init__(self, ["sprites/new.png"])
        self.show(sprite)

#text component (sprites as text)
class Text(Actor):
    def __init__(self, sprite):
        Actor.__init__(self, ["sprites/welcome.png",
                              "sprites/start.png",
                              "sprites/start_b.png",
                              "sprites/game_over.png",
                              "sprites/new_highscore.png",
                              "sprites/new_highscore_b.png",
                              "sprites/your_score.png",
                              "sprites/highest_score.png"])
        self.show(sprite)
    
    #blinking start text animation
    def act(self):
        if self.getIdVisible() == 1:
            self.show(2)
        elif self.getIdVisible() == 2:
            self.show(1)
            
        if self.getIdVisible() == 4:
            self.show(5)
        elif self.getIdVisible() == 5:
            self.show(4)

#Game over screen
class GameOver():
    def __init__(self):
        #build new window
        main.buildGameGrid()
                
        addActor(DinoOver(), Location(130, 85))
        addActor(Text(3), Location(int(CONS.GAME_W / 2), 50))
        
        #if is new highscore
        if main.highscore < main.score:
            main.highscore = main.score
            addActor(Text(4), Location(int(CONS.GAME_W / 2), 95))
            
        addActor(Text(6), Location(int(CONS.GAME_W / 2), 150))
        getBg().setPaintColor(Color.white)
        getBg().drawText(str(int(main.score)), Point(int(CONS.GAME_W / 2), 200))
        
        addActor(Text(7), Location(int(CONS.GAME_W / 2), 230))
        getBg().drawText(str(int(main.highscore)), Point(int(CONS.GAME_W / 2), 280))

        self.btnNew = Button(0)
        addActor(self.btnNew, Location(int(CONS.GAME_W / 2), 330))
        self.btnNew.addMouseTouchListener(self.start, GGMouse.lClick) #add mouse touch listener to "new game" button

        addActor(Text(1), Location(int(CONS.GAME_W / 2), 375))
        
        setSimulationPeriod(500)
        doRun()
    
    #game started
    def start(self, *args):
        getBg().clear()
        main.game.initGame()

#init main class
if __name__ == '__main__':
    main = Main()