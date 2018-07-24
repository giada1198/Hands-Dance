# Giada Sun, syuanchs
#################################################
# Term Project: Hands Dance 112
# Code Artifacts & Working Demo 05/04
#################################################

from pykinect2 import PyKinectV2, PyKinectRuntime
from pykinect2.PyKinectV2 import *

#################################################
# a) Build-In Module:
#    ctypes, copy, math, os, pickle, random, sys, datetime
# b) Third-Party Module:
#    PyGame, PyKinectV2, SoundFile, LibROSA
#################################################

import ctypes
import _ctypes
import pygame
import copy, math, os, pickle, random, sys, datetime

import soundfile as sf
import librosa

testMode = False
class RGBColorTable(object):
    def __init__(self):
        ##################################################
        # SOURCE | http://www.rapidtables.com/web/color/RGB_Color.htm
        # ------------------------------------------------
        self.black   = (0,0,0)
        self.white   = (255,255,255)
        self.red     = (255,0,0)
        self.lime    = (0,255,0)
        self.blue    = (0,0,255)
        self.yellow  = (255,255,0)
        self.cyan    = (0,255,255)
        self.megenta = (255,0,255)
        self.silver  = (192,192,192)
        self.gray    = (128,128,128)
        self.maroon  = (128,0,0)
        self.olive   = (128,128,0)
        self.green   = (0,128,0)
        self.purple  = (128,0,128)
        self.teal    = (0,128,128)
        self.navy    = (0,0,128)
        ##################################################
RGBColor = RGBColorTable()

#################################################
# Helper Functions
#################################################

def distance(x0, y0, x1, y1): return ((x0 - x1)**2 + (y0 - y1)**2)**0.5
def getMusicLength(path):
    ##################################################
    # MODULE | SoundFile 0.9.0.post1
    # SOURCE | https://pypi.python.org/pypi/SoundFile
    # ------------------------------------------------
    # Get and print information of the song
    file = sf.SoundFile(path)
    if testMode:
        print('music path       : %s' % path)
        print('music samples    : %d' % len(file))
        print('music sample rate: %d' % file.samplerate)
        print('music length     : %f sec' % (len(file) / file.samplerate))
    ##################################################
    return len(file)/file.samplerate
# ------------------------------------------------
def drawText(screen, position, textSetting, size, color=RGBColor.black, anchor='C', fontSetting=None):
    font = pygame.font.Font(fontSetting, size)
    text = font.render(textSetting, True, color)
    x0, y0 = position[0], position[1]
    width, height = text.get_width(), text.get_height()
    if   (anchor == 'NW'): x, y = x0         , y0
    elif (anchor == 'N' ): x, y = x0-width//2, y0
    elif (anchor == 'NE'): x, y = x0-width   , y0
    elif (anchor == 'W' ): x, y = x0         , y0-height//2
    elif (anchor == 'C' ): x, y = x0-width//2, y0-height//2
    elif (anchor == 'E' ): x, y = x0-width   , y0-height//2
    elif (anchor == 'SW'): x, y = x0         , y0-height
    elif (anchor == 'S' ): x, y = x0-width//2, y0-height
    elif (anchor == 'SE'): x, y = x0-width   , y0-height
    screen.blit(text, (int(x), int(y)))
    # return boundaries of the text
    return (x, y, x+width, y+height)
# ------------------------------------------------
def blitAlpha(screen, image, location, opacity):
        ##################################################
        # MODULE | Pygame
        # SOURCE | http://www.nerdparadise.com/programming/pygameblitopacity
        # ------------------------------------------------
        x = location[0]
        y = location[1]
        temp = pygame.Surface((image.get_width(), image.get_height())).convert()
        temp.blit(screen, (-x, -y))
        temp.blit(image, (0, 0))
        temp.set_alpha(opacity)
        ##################################################
        screen.blit(temp, location)
def blitImageCenter(screen, image, location, opacity=None, size=None):
    if size is None: x, y = location[0] - image.get_width()//2, location[1] - image.get_height()//2
    else:            x, y = location[0] - size[0]//2,           location[1] - size[1]//2
    if (opacity == None): screen.blit(image, (x,y))
    else: blitAlpha(screen, image, (x,y), opacity)
# ------------------------------------------------
def playSound(path, volume=1):
    ##################################################
    # MODULE | PyGame
    # SOURCE | http://www.nerdparadise.com/programming/pygame/part3
    # ------------------------------------------------
    try:    game.sound.stop()
    except: pass
    game.sound = pygame.mixer.Sound(path)
    game.sound.set_volume(volume)
    game.sound.play()
    ##################################################
    return game.sound.get_length() # return length of the song(second)
def playMusic(path, loops=0):
    try:    pygame.mixer.music.stop()
    except: pass
    pygame.mixer.music.load(path)
    pygame.mixer.music.play(loops)

#################################################
# TempoBall
#################################################

def createTempoBallList(beatList):
    tempoBallList = []
    order = 0
    for time in beatList:
        tempoBallList.append(TempoBall(time, order, 'Left'))
        tempoBallList.append(TempoBall(time, order, 'Right'))
        order += 1
    return tempoBallList
class TempoBall(object):
    def __init__(self, time, order, side='Left'):
        self.time = time
        self.order = order
        self.side = side
        self.L = None
        self.degree = None
        if   (self.side == 'Left'):  self.color = RGBColor.blue
        elif (self.side == 'Right'): self.color = RGBColor.red
        self.speed = 30
        # ------------------------------------------------
        self.isRecorded = False
        self.isBeated   = False
    def getX(self):
        if (self.side == 'Left') and (game.DCRadiusLeft != None) and (game.DCPositionXLeft != None):
            d = (game.DCRadiusLeft*self.L)*(math.cos(math.radians(self.degree)))
            d = int(d) + game.DCPositionXLeft
            return d
        elif (self.side == 'Right') and (game.DCRadiusRight != None) and (game.DCPositionXRight != None):
            d = (game.DCRadiusRight*self.L)*(math.cos(math.radians(self.degree)))
            d = int(d) + game.DCPositionXRight
            return d
        return None
    def getY(self):
        if (self.side == 'Left') and (game.DCRadiusLeft != None) and (game.DCPositionYLeft != None):
            d = (game.DCRadiusLeft*self.L)*(math.sin(math.radians(self.degree)))
            d = int(d) + game.DCPositionYLeft
            return d
        elif (self.side == 'Right') and (game.DCRadiusRight != None) and (game.DCPositionYRight != None):
            d = (game.DCRadiusRight*self.L)*(math.sin(math.radians(self.degree)))
            d = int(d) + game.DCPositionYRight
            return d
        return None
    def record(self, screen):
        # record the position of this ball
        if (not self.isRecorded) and (self.time//0.1 == game.time//0.1):
            self.isRecorded = True
            if   (self.side == 'Left'):
                x0, y0 = game.handPositionXLeft, game.handPositionYLeft
                x1, y1, r = game.DCPositionXLeft, game.DCPositionYLeft, game.DCRadiusLeft
            elif (self.side == 'Right'):
                x0, y0 = game.handPositionXRight, game.handPositionYRight
                x1, y1, r = game.DCPositionXRight, game.DCPositionYRight, game.DCRadiusRight
            if (x0 != None) and (y0 != None) and (x1 != None) and (y1 != None) and (r != None):
                self.L = distance(x0, y0, x1, y1)/r
                if (self.L > 1): self.L = 1 
                self.degree = math.degrees(math.atan2(y0-y1, x0-x1)%(2*math.pi))
                if testMode: print('Tempoball Record: L=%f, degree=%f' % (self.L, self.degree))
                game.tempoBallEffectList.append(TempoBallEffect('record', None, (x0, y0)))
                pygame.draw.circle(screen, RGBColor.red, (x0, y0), 80, 15)
        # when this ball needs to appear on screen, draw the ball
        elif (self.time < game.time) and ((game.time - self.time) <= 0.2):
            if   (self.side == 'Left'):  x0, y0 = game.handPositionXLeft, game.handPositionYLeft
            elif (self.side == 'Right'): x0, y0 = game.handPositionXRight, game.handPositionYRight
            if (x0 != None) and (y0 != None): pygame.draw.circle(screen, RGBColor.red, (x0, y0), 80, 15)
        else: pass
    def draw(self, screen):
        if (not self.isBeated):
            x0, y0 = self.getX(), self.getY()
            if (x0 != None) and (y0 != None):
                if   (self.side == 'Left' ): x1 = int(x0 - (self.time - game.time)*game.fps*self.speed)
                elif (self.side == 'Right'): x1 = int(x0 + (self.time - game.time)*game.fps*self.speed)
                if   (self.time < game.time):
                    if   (self.side == 'Left' ):
                        self.isBeated = True
                        game.tempoBallEffectList.append(TempoBallEffect('miss', 'Left', (x0, y0)))
                        # Scroe
                        game.scoreMiss()
                    elif (self.side == 'Right'):
                        self.isBeated = True
                        game.tempoBallEffectList.append(TempoBallEffect('miss', 'Right', (x0, y0)))
                        # Scroe
                        game.scoreMiss()
                elif (self.time - game.time) <= 0.1:
                    if   (self.side == 'Left'):
                        if (game.handPositionXLeft != None) and (game.handPositionYLeft != None) and\
                           (distance(x1, y0, game.handPositionXLeft, game.handPositionYLeft) <= 125):
                            self.isBeated = True
                            game.tempoBallEffectList.append(TempoBallEffect('beat', 'Left', (x0, y0)))
                            # Scroe
                            game.scoreBeat()
                        else: blitImageCenter(screen, game.imgTempoBallLeftNormal, (x1, y0))
                    elif (self.side == 'Right'):
                        if (game.handPositionXRight != None) and (game.handPositionYRight != None) and\
                           (distance(x1, y0, game.handPositionXRight, game.handPositionYRight) <= 125):
                            self.isBeated = True
                            game.tempoBallEffectList.append(TempoBallEffect('beat', 'Right', (x0, y0)))
                            # Scroe
                            game.scoreBeat()
                        else: blitImageCenter(screen, game.imgTempoBallRightNormal, (x1, y0))
                elif (self.time - game.time) <= 2:
                    if   (self.side == 'Left' ): blitImageCenter(screen, game.imgTempoBallLeftNormal,  (x1, y0))
                    elif (self.side == 'Right'): blitImageCenter(screen, game.imgTempoBallRightNormal, (x1, y0))
    def drawHint(self, screen):
            if (self.isBeated == False) and (self.time > game.time) and ((self.time - game.time) <= 1):
                x0, y0 = self.getX(), self.getY()
                if (x0 != None) and (y0 != None):
                    if   (self.side == 'Left' ): image = game.imgTempoBallLeftHint
                    elif (self.side == 'Right'): image = game.imgTempoBallRightHint
                    if ((self.time - game.time) >= 0.5): opacity = int((1-((self.time-game.time)-0.5)/0.5)*255)
                    else: opacity = 255
                    blitImageCenter(screen, image, (x0,y0), opacity)
class TempoBallEffect(object):
    def __init__(self, type, side, location):
        self.type = type
        self.side = side
        self.x = location[0]
        self.y = location[1]
        self.frame = 0
        self.opacity = 255
        if   (self.type == 'record'):
            self.textX = self.x
            self.textY = self.y - 100
        elif (self.type == 'beat'):
            self.textX = self.x
            self.textY = self.y - 100
            self.size = 160
        elif (self.type == 'miss'):
            self.textX = self.x
            self.textY = self.y - 100
        self.done = False
    def draw(self, screen):
        if (not self.done):
            # RECORD Effect Text
            if   (self.type == 'record'):
                blitImageCenter(screen, game.imgTextRecord, (self.textX, self.textY))
                # for next frame
                self.frame += 1
                self.textY -= 3
                if (self.frame == 21): self.done = True
            # BEAT Effect Text
            if   (self.type == 'beat'):
                if (int(self.opacity) >= 0):
                    if   (self.side == 'Left' ): blitImageCenter(screen, game.imgTempoBallLeftBeat,  (self.x, self.y), int(self.opacity))
                    elif (self.side == 'Right'): blitImageCenter(screen, game.imgTempoBallRightBeat, (self.x, self.y), int(self.opacity))
                pygame.draw.circle(screen, RGBColor.red, (self.x, self.y), self.size//2, 10)
                #blitImageCenter(screen, game.imgTextBeat, (self.textX, self.textY))
                # for next frame
                self.frame += 1
                self.opacity -= 25.5
                #self.textY   -= 3
                self.size    += 8
                if (self.frame == 11): self.done = True
            # MISS Effect Text
            elif (self.type == 'miss'):
                #if (int(self.opacity) >= 0):
                #    if   (self.side == 'Left' ): blitImageCenter(screen, game.imgTempoBallLeftNormal,  (self.x, self.y), int(self.opacity))
                #    elif (self.side == 'Right'): blitImageCenter(screen, game.imgTempoBallRightNormal, (self.x, self.y), int(self.opacity))
                blitImageCenter(screen, game.imgTextMiss, (self.x, self.textY))
                # for next frame
                self.frame += 1
                self.opacity -= 50
                self.textY   -= 3
                if (self.frame == 16): self.done = True

#################################################
# Game Runtime
#################################################

class GameRuntime(object):

    def __init__(self):
        pygame.init()
        self.done = False
        self.clock = pygame.time.Clock()
        self.mode = 'intro'
        # ------------------------------------------------
        self.displayInfo = pygame.display.Info()
        self.width  = 1920
        self.height = 1080
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.HWSURFACE|pygame.DOUBLEBUF, 32)
        self.fps = 30
        # ------------------------------------------------
        pygame.mixer.init()
        pygame.font.init()
        self.font = pygame.font.Font(None, 100)
        # ------------------------------------------------
        self.loadImageFile()
        self.loadSoundFile()
        self.levelName = ['EASY', 'BASIC', 'EXPERT']
        # ------------------------------------------------
        self.introModeInit()
        
        ##################################################
        # MODULE | PyKinect 2
        # SOURCE | Microsoft Kinect 2 Workshop Sample
        #          https://drive.google.com/file/d/0B034f0-ld_3wcVZUSTNXUndWQXM/view?usp=sharing
        # ------------------------------------------------
        self.kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color|PyKinectV2.FrameSourceTypes_Body)
        self.bodies = None
        self._frame_surface = pygame.Surface((self.kinect.color_frame_desc.Width, self.kinect.color_frame_desc.Height), 0, 32)
        ##################################################
        self.handPositionXLeft  = None
        self.handPositionYLeft  = None
        self.handPositionXRight = None
        self.handPositionYRight = None
        # ------------------------------------------------
        self.DCPositionXLeft = None
        self.DCPositionYLeft = None
        self.DCPositionXRight = None
        self.DCPositionYRight = None
        self.DCRadiusLeft = None
        self.DCRadiusRight = None
    
    #################################################
    # Load Files
    #################################################

    def loadImageFile(self):
        # [Interface] Intro Mode
        self.imgInterfaceIntro       = pygame.image.load('Images/Interface_Intro.png')
        # [Interface] Setting Mode
        self.imgInterfaceSetting     = []
        for i in range(2):
            path = 'Images/Interface_Setting_' + str(i) + '.png'
            self.imgInterfaceSetting.append(pygame.image.load(path))
        # [Interface] Level Mode
        self.imgInterfaceLevel       = []
        for i in range(3):
            path = 'Images/Interface_Level_' + str(i) + '.png'
            self.imgInterfaceLevel.append(pygame.image.load(path))
        # [Interface] Init Mode
        self.imgInterfaceInitNone    = pygame.image.load('Images/Interface_Init_0.png')
        self.imgInterfaceInit        = pygame.image.load('Images/Interface_Init_1.png')
        self.imgInterfaceInitSave    = pygame.image.load('Images/Icon_Save.png')
        self.imgInterfaceInitRedo    = pygame.image.load('Images/Icon_Redo.png')
        self.imgInterfaceInitPlay    = pygame.image.load('Images/Icon_Play.png')
        # [Interface] Record Mode
        self.imgInterfaceRecord      = pygame.image.load('Images/Interface_Record.png')
        self.imgTextRecord           = pygame.image.load('Images/Text_Record.png')
        # [Interface] Play Mode
        self.imgInterface            = pygame.image.load('Images/Interface.png')
        # [Interface] Play Mode Text
        self.imgTextBeat             = pygame.image.load('Images/Text_Beat.png')
        self.imgTextMiss             = pygame.image.load('Images/Text_Miss.png')
        self.imgTextCombo            = pygame.image.load('Images/Combo_C.png')
        self.imgTextComboDigit       = []
        for i in range(10):
            path = 'Images/Combo_' + str(i) + '.png'
            self.imgTextComboDigit.append(pygame.image.load(path))
        # [Interface] Record End Mode
        self.imgInterfaceRecordEnd   = pygame.image.load('Images/Interface_Record_End.png')
        # [Interface] Play End Mode
        self.imgInterfacePlayEnd     = pygame.image.load('Images/Interface_Play_End.png')
        # ------------------------------------------------
        self.tempoBallSize = (160,160)
        # TempoBall Images
        self.imgTempoBallLeftNormal  = pygame.image.load('Images/TempoBall_Left_1.png')
        self.imgTempoBallLeftNormal  = pygame.transform.scale(self.imgTempoBallLeftNormal,  self.tempoBallSize)
        self.imgTempoBallLeftBeat    = pygame.image.load('Images/TempoBall_Left_2.png')
        self.imgTempoBallLeftBeat    = pygame.transform.scale(self.imgTempoBallLeftBeat,    self.tempoBallSize)
        self.imgTempoBallLeftHint    = pygame.image.load('Images/Hint_Left.png')
        self.imgTempoBallLeftHint    = pygame.transform.scale(self.imgTempoBallLeftHint, (200,200))
        self.imgTempoBallRightNormal = pygame.image.load('Images/TempoBall_Right_1.png')
        self.imgTempoBallRightNormal = pygame.transform.scale(self.imgTempoBallRightNormal, self.tempoBallSize)
        self.imgTempoBallRightBeat   = pygame.image.load('Images/TempoBall_Right_2.png')
        self.imgTempoBallRightBeat   = pygame.transform.scale(self.imgTempoBallRightBeat,   self.tempoBallSize)
        self.imgTempoBallRightHint   = pygame.image.load('Images/Hint_Right.png')
        self.imgTempoBallRightHint   = pygame.transform.scale(self.imgTempoBallRightHint, (200,200))
        # Hand Icons Images
        self.imgHandIconLeft         = pygame.image.load('Images/Hand_Left_Normal.png')
        self.imgHandIconRight        = pygame.image.load('Images/Hand_Right_Normal.png')
    def loadSoundFile(self):
        self.soundOpening = 'Sounds/Bike_Rides.wav'
        self.soundClick   = 'Sounds/Click.wav'
        self.soundEnter   = 'Sounds/Enter.wav'
        self.soundBeat1   = 'Sounds/Beat_StyleB_1.wav'
        self.soundBeat2   = 'Sounds/Beat_StyleB_2.wav'
        self.soundBeat3   = 'Sounds/Beat_StyleB_3.wav'
    def loadMusicFile(self):
        self.musicFilePath = []
        self.musicFileName = []
        for filename in os.listdir('Database'):
            if (filename[-4:] == '.wav') or (filename[-4:] == '.WAV'):
                self.musicFilePath.append('Database/' + filename)
                self.musicFileName.append(filename)
        if testMode: print('musicFilePath:', self.musicFilePath)
        self.musicFileAmount = len(self.musicFilePath)
        self.musicFileSelect = 0
        self.path = self.musicFilePath[self.musicFileSelect]
    def loadBinFile(self):
        self.binFilePath = []
        self.binFileName = []
        for filename in os.listdir('Database'):
            if (filename[-4:] == '.bin') or (filename[-4:] == '.BIN'):
                self.binFilePath.append('Database/' + filename)
                self.binFileName.append(filename)
        if testMode: print('binFilePath:', self.binFilePath)
        self.binFileAmount = len(self.binFilePath)
        self.binFileSelect = 0
        if (self.binFileAmount > 0): self.bin = self.binFilePath[self.binFileSelect]
        else: self.bin = None

    #################################################
    # Mode Init
    #################################################

    def introModeInit(self): playMusic(self.soundOpening, -1)
    def settingModeInit(self):
        self.settingModeSelection = 1
        self.loadMusicFile()
        self.loadBinFile()
    def levelModeInit(self): self.level = 0
    # ------------------------------------------------
    def recordInitModeInit(self):
        self.musicLength = getMusicLength(self.path)
        self.loadMusic()
        self.isDetectiveCircleSaved = False
    def playInitModeInit(self): self.isDetectiveCircleSaved = False
    # ------------------------------------------------
    def recordModeInit(self):
        self.time = -10
        self.frame = 0
        self.isMusicPlayed = False
        self.tempoBallListStart = 0
        self.tempoBallEffectList = []

        ##################################################
        # MODULE | Datetime
        # SOURCE | https://docs.python.org/2/library/datetime.html
        # ------------------------------------------------
        date = datetime.datetime.now()
        ##################################################
        if (len(str(date.month)) == 1): fileName = str(date.year) + '0' + str(date.month)
        else: fileName = str(date.year) + str(date.month)
        if (len(str(date.day)) == 1): fileName = fileName + '0' + str(date.day) + '_'
        else: fileName = fileName + str(date.day) + '_'
        if (len(str(date.hour)) == 1): fileName = fileName + '0' + str(date.hour)
        else: fileName = fileName + str(date.hour)
        if (len(str(date.minute)) == 1): fileName = fileName + '0' + str(date.minute)
        else: fileName = fileName + str(date.minute)
        self.binFileName = self.path[:-4] + '_' + fileName
        self.bin = self.binFileName + '.bin'
        if not os.path.exists(self.binFileName): os.makedirs(self.binFileName)
        pass
    def playModeInit(self):
        self.time = -10
        self.frame = 0
        self.isMusicPlayed = False
        self.tempoBallListStart = 0
        self.tempoBallEffectList = []
        second = str(int(self.musicLength%60))
        if (len(second) == 1): second = '0' + second
        self.musicLengthText = str(int(self.musicLength//60)) + ':' + second
        #
        self.importBinFileVideo()
        # score
        self.combo       = 0
        self.comboHeight = 180
        self.score       = 0
        self.scorePlus   = 100
    # ------------------------------------------------
    def playEndModeInit(self):
        if (self.score > self.tempoBallList[0].bestScore): self.bestScore = self.score
        self.updateBinFile()

    #################################################
    # Main Loop
    #################################################

    def run(self):
        while not self.done:
            ##############################
            # 1) Intro Mode
            if   (self.mode == 'intro'):
                for event in pygame.event.get():
                    if   (event.type is pygame.QUIT): self.done = True
                    elif (event.type == pygame.KEYDOWN):
                        if (event.key == pygame.K_w):
                            if self.screen.get_flags() & pygame.FULLSCREEN: pygame.display.set_mode((self.width, self.height))
                            else: pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
                        else:
                            playSound(self.soundEnter)
                            self.drawLoading()
                            self.settingModeInit()
                            self.mode = 'setting'
                self.drawIntroModeInterface()
                pygame.display.flip()
            ##############################
            # 2) Setting Mode
            elif (self.mode == 'setting'):
                for event in pygame.event.get():
                    if   (event.type is pygame.QUIT): self.done = True
                    elif (event.type == pygame.KEYDOWN):
                        if   (event.key == pygame.K_w):
                            if self.screen.get_flags() & pygame.FULLSCREEN: pygame.display.set_mode((self.width, self.height))
                            else: pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
                        elif (event.key == pygame.K_SPACE):
                            playSound(self.soundEnter)
                            pygame.mixer.music.stop()
                            if (self.settingModeSelection == 0): # RECORD
                                # Loading Screen
                                self.drawLoading()
                                self.recordInitModeInit()
                                self.mode = 'record_init'
                            elif (self.settingModeSelection == 1) and (self.binFilePath != []): # LOAD
                                self.drawLoading()
                                self.importBinFile()
                                self.levelModeInit()
                                self.mode = 'level'
                        elif (event.key == pygame.K_RIGHT):
                            playSound(self.soundClick)
                            if (self.settingModeSelection == 0): # RECORD
                                self.musicFileSelect = (self.musicFileSelect + 1)%self.musicFileAmount
                                self.path = self.musicFilePath[self.musicFileSelect]
                                playMusic(self.musicFilePath[self.musicFileSelect], -1)
                            elif (self.settingModeSelection == 1) and (self.binFilePath != []): # LOAD
                                self.binFileSelect = (self.binFileSelect + 1)%self.binFileAmount
                                self.bin = self.binFilePath[self.binFileSelect]
                        elif (event.key == pygame.K_LEFT):
                            playSound(self.soundClick)
                            if (self.settingModeSelection == 0): # RECORD
                                self.musicFileSelect = (self.musicFileSelect - 1)%self.musicFileAmount
                                self.path = self.musicFilePath[self.musicFileSelect]
                                playMusic(self.musicFilePath[self.musicFileSelect], -1)
                            elif (self.settingModeSelection == 1) and (self.binFilePath != []): # LOAD
                                self.binFileSelect = (self.binFileSelect - 1)%self.binFileAmount
                                self.bin = self.binFilePath[self.binFileSelect]
                        elif (event.key == pygame.K_UP):
                            playSound(self.soundClick)
                            self.settingModeSelection = (self.settingModeSelection - 1)%2
                            if (self.settingModeSelection == 0): playMusic(self.musicFilePath[self.musicFileSelect], -1)
                            else: playMusic(self.soundOpening, -1)
                        elif (event.key == pygame.K_DOWN):
                            playSound(self.soundClick)
                            self.settingModeSelection = (self.settingModeSelection + 1)%2
                            if (self.settingModeSelection == 0): playMusic(self.musicFilePath[self.musicFileSelect], -1)
                            else: playMusic(self.soundOpening, -1)
                self.drawSettingModeInterface()
                pygame.display.flip()
            ##############################
            # 3) Level Mode
            elif (self.mode == 'level'):
                for event in pygame.event.get():
                    if   (event.type is pygame.QUIT): self.done = True
                    elif (event.type == pygame.KEYDOWN):
                        if   (event.key == pygame.K_w):
                            if self.screen.get_flags() & pygame.FULLSCREEN: pygame.display.set_mode((self.width, self.height))
                            else: pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
                        elif (event.key == pygame.K_SPACE):
                            playSound(self.soundEnter)
                            self.drawLoading()
                            self.playInitModeInit()
                            self.mode = 'play_init'
                        elif (event.key == pygame.K_RIGHT):
                            playSound(self.soundClick)
                            self.level = (self.level + 1)%3
                        elif (event.key == pygame.K_LEFT):
                            playSound(self.soundClick)
                            self.level = (self.level - 1)%3
                self.drawLevelModeInterface()
                pygame.display.flip()
            ##############################
            # 4) Record/Play Init Model
            elif (self.mode == 'record_init') or (self.mode == 'play_init'):
                for event in pygame.event.get():
                    if   (event.type is pygame.QUIT): self.done = True
                    elif (event.type == pygame.KEYDOWN) and (event.key == pygame.K_w):
                        if self.screen.get_flags() & pygame.FULLSCREEN: pygame.display.set_mode((self.width, self.height))
                        else: pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
                self.screen.fill((RGBColor.black))
                ##################################################
                # MODULE | PyKinect 2
                # SOURCE | Microsoft Kinect 2 Workshop Sample
                #          https://drive.google.com/file/d/0B034f0-ld_3wcVZUSTNXUndWQXM/view?usp=sharing
                # ------------------------------------------------
                if self.kinect.has_new_body_frame():
                    self.bodies = self.kinect.get_last_body_frame()
                    if self.bodies is not None:
                        noBody = True
                        for i in range(0, self.kinect.max_body_count):
                            # Detection Part
                            body = self.bodies.bodies[i]
                            if body.is_tracked:
                                noBody = False
                                # Draw Background and Touch Icons
                                self.screen.blit(self.imgInterfaceInit, (0,0))
                                if (self.isDetectiveCircleSaved == False):
                                    self.screen.blit(self.imgInterfaceInitSave, (45,205))
                                else:
                                    self.screen.blit(self.imgInterfaceInitRedo, (1575,15))
                                    self.screen.blit(self.imgInterfaceInitPlay, (1575,395))
                                joints = body.joints
                                # convert joint coordinates to color space
                                jointPoints = self.kinect.body_joints_to_color_space(joints)
                                if (self.getHandsPosition(joints, jointPoints) != False):
                                    if (self.isDetectiveCircleSaved == False):
                                        if (self.getDetectiveCircleRadius(joints,jointPoints) != False):
                                            ### Layer 1 (SAVE icon)
                                            if (self.handPositionXLeft >  45) and (self.handPositionXLeft < 345) and\
                                               (self.handPositionYLeft > 205) and (self.handPositionYLeft < 505) and\
                                               (isinstance(self.DCRadiusLeft, int)) and (isinstance(self.DCRadiusRight, int)):
                                                playSound(self.soundClick)
                                                self.isDetectiveCircleSaved = True
                                            ### Layer 2 (Detective Circles)
                                            self.drawDetectiveCircles(joints, jointPoints)
                                    else:
                                        ### Layer 1 (REDO icon)
                                        if   (self.handPositionXRight > 1575) and (self.handPositionXRight < 1875) and\
                                           (self.handPositionYRight >   15) and (self.handPositionYRight <  315):
                                            playSound(self.soundClick)
                                            self.isDetectiveCircleSaved = False
                                        ### Layer 1 (PLAY icon)
                                        elif (self.handPositionXRight > 1575) and (self.handPositionXRight < 1875) and\
                                           (self.handPositionYRight >  395) and (self.handPositionYRight <  695):
                                            self.isDetectiveCircleSaved = False
                                            self.drawLoading()
                                            if (self.mode == 'record_init'):
                                                playSound(self.soundEnter)
                                                self.recordModeInit()
                                                self.mode = 'record'
                                            elif (self.mode == 'play_init'):
                                                playSound(self.soundEnter)
                                                self.playModeInit()
                                                self.mode = 'play'
                                        ### Layer 2 (Detective Circles)
                                        self.drawDetectiveCircles(joints, jointPoints)
                                    ### Layer 3 (Hands)
                                    self.drawHandsPosition()
                                break
                        if (noBody == True):
                                self.screen.blit(self.imgInterfaceInitNone, (0,0))
                                ### Please Stand in Front of the Kinect Sensor...
                                x, y = self.width//2, self.height//2
                                text = 'Detecting... Please Stand in Front of the Sensor...'
                                drawText(self.screen, (x,y), text, 70, RGBColor.white)
                ##################################################
                    else:
                        self.screen.blit(self.imgInterfaceInitNone, (0,0))
                        ### Please Stand in Front of the Kinect Sensor...
                        x, y = self.width//2, self.height//2
                        text = 'Detecting... Please Stand in Front of the Sensor...'
                        drawText(self.screen, (x,y), text, 70, RGBColor.white)
                else:
                    self.screen.blit(self.imgInterfaceInitNone, (0,0))
                    ### Cannot Find Any Kinect Device... Please Check Connection...
                    x, y = self.width//2, self.height//2
                    text = 'Cannot Find Any Kinect Device... Please Check Connection...'
                    drawText(self.screen, (x,y), text, 70, RGBColor.white)
                pygame.display.flip()
                self.clock.tick(10) # High Frame Rate in this mode might cause lag
            ##############################
            # 5) Record/Play Mode
            elif (self.mode == 'record') or (self.mode == 'play'):
                for event in pygame.event.get():
                    if (event.type == pygame.QUIT): self.done = True
                    elif (event.type == pygame.KEYDOWN) and (event.key == pygame.K_w):
                        if self.screen.get_flags() & pygame.FULLSCREEN: pygame.display.set_mode((self.width, self.height))
                        else: pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)                
                ##################################################
                # MODULE | PyKinect 2
                # SOURCE | Microsoft Kinect 2 Workshop Sample
                #          https://drive.google.com/file/d/0B034f0-ld_3wcVZUSTNXUndWQXM/view?usp=sharing
                # ------------------------------------------------
                # Dectect color frame from kinect and draw the color frame
                if self.kinect.has_new_color_frame():
                    frame = self.kinect.get_last_color_frame()
                    self.drawKinectColorFrame(frame, self._frame_surface)
                    frame = None
                if (self.mode == 'record') and (self.frame%2 == 0):
                    time = (str(int(((self.time+10)*100)//1+1000000)))[1:]
                    path = self.binFileName + '/' + time + '.jpg'
                    pygame.image.save(pygame.transform.scale(self._frame_surface, (490, 276)), path)
                surfaceToDraw = pygame.transform.scale(self._frame_surface, (1920, 1080))
                self.screen.blit(surfaceToDraw, (0,0))
                surfaceToDraw = None
                ##################################################
                if self.kinect.has_new_body_frame():
                    self.bodies = self.kinect.get_last_body_frame()
                    for i in range(0, self.kinect.max_body_count):
                        # Detection Part
                        body = self.bodies.bodies[i]
                        if body.is_tracked:
                            joints = body.joints
                            # convert joint coordinates to color space
                            jointPoints = self.kinect.body_joints_to_color_space(joints)
                            self.getHandsPosition(joints, jointPoints)
                            ### Layer 1 (Detective Circles)
                            self.drawDetectiveCircles(joints, jointPoints)
                            break
                if (self.tempoBallList != []):
                    # Layer 2 (Record Circles and Hint Circles)
                    for ball in self.tempoBallList[self.tempoBallListStart:]:
                        if (self.time > ball.time) and (self.time - ball.time > 2): self.tempoBallListStart += 1
                        elif (self.time < ball.time) and (ball.time - self.time > 1): break
                        else:
                            if (self.mode == 'record'): ball.record(self.screen)
                            elif (self.mode == 'play'):
                                if   (self.level == 0):
                                    if   (ball.side == 'Left')  and (ball.order%4 == 0): ball.drawHint(self.screen)
                                    elif (ball.side == 'Right') and (ball.order%4 == 0): ball.drawHint(self.screen)
                                elif (self.level == 1):
                                    if (ball.order%2 == 0): ball.drawHint(self.screen)
                                elif (self.level == 2):
                                    if   (ball.side == 'Left')  and (ball.order%2 == 0): ball.drawHint(self.screen)
                                    elif (ball.side == 'Right') and (ball.order%2 == 1): ball.drawHint(self.screen)
                    # Layer 3 (TempoBall Effects)
                    if (self.tempoBallEffectList != None):
                        i = 0
                        for effect in self.tempoBallEffectList:
                            if (effect.done == True): i += 1
                            effect.draw(self.screen)
                        self.tempoBallEffectList = self.tempoBallEffectList[i:]
                    # Layer 4 (TempoBall)
                    if (self.mode == 'play'):
                        for ball in self.tempoBallList[self.tempoBallListStart:]:
                            if (self.time < ball.time) and (ball.time - self.time > 1): break
                            else:
                                if   (self.level == 0):
                                    if   (ball.side == 'Left')  and (ball.order%4 == 0): ball.draw(self.screen)
                                    elif (ball.side == 'Right') and (ball.order%4 == 0): ball.draw(self.screen)
                                elif (self.level == 1):
                                    if (ball.order%2 == 0): ball.draw(self.screen)
                                elif (self.level == 2):
                                    if   (ball.side == 'Left')  and (ball.order%2 == 0): ball.draw(self.screen)
                                    elif (ball.side == 'Right') and (ball.order%2 == 1): ball.draw(self.screen)
                # Layer 5 (Hands)
                self.drawHandsPosition()
                # Layer 6 (Interface)
                if (self.mode == 'play'):
                    self.drawPlayModeInterface()
                    self.drawBinFileVideo()
                elif (self.mode == 'record'):
                    self.drawRecordModeInterface()
                # ------------------------------------------------
                if (self.time >= self.musicLength):
                    if (self.mode == 'record'):
                        self.drawLoading()
                        self.createBinFile()
                        self.mode = 'record_end'
                        playMusic(self.soundOpening, -1)
                    elif (self.mode == 'play'):
                        self.drawLoading()
                        self.playEndModeInit()
                        self.mode = 'play_end'
                        playMusic(self.soundOpening, -1)
                # enhance the frame and time
                self.frame += 1
                self.time  += self.clock.get_time()/1000
                # Count Down
                if (self.time < 0):
                    x, y = self.width//2, self.height//2
                    drawText(self.screen, (x,y), str(int(abs(self.time))), 500, RGBColor.red)
                # Play Music
                elif (self.time >= 0) and (not self.isMusicPlayed):
                    self.isMusicPlayed = True
                    playMusic(self.path)
                # ------------------------------------------------
                pygame.display.flip()
                self.clock.tick(self.fps)
            ##############################
            # 6) Record End Mode
            elif (self.mode == 'record_end'):
                for event in pygame.event.get():
                    if   (event.type is pygame.QUIT): self.done = True
                    elif (event.type == pygame.KEYDOWN):
                        if (event.key == pygame.K_w):
                            if self.screen.get_flags() & pygame.FULLSCREEN: pygame.display.set_mode((self.width, self.height))
                            else: pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
                        else:
                            playSound(self.soundEnter)
                            self.drawLoading()
                            self.settingModeInit()
                            self.mode = 'setting'
                self.drawRecordEndModeInterface()
                pygame.display.flip()
                self.clock.tick(self.fps)
            ##############################
            # Play End Mode
            elif   (self.mode == 'play_end'):
                for event in pygame.event.get():
                    if (event.type is pygame.QUIT): self.done = True
                    elif (event.type == pygame.KEYDOWN):
                        if (event.key == pygame.K_w):
                            if self.screen.get_flags() & pygame.FULLSCREEN: pygame.display.set_mode((self.width, self.height))
                            else: pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
                        else:
                            playSound(self.soundEnter)
                            self.drawLoading()
                            self.settingModeInit()
                            self.mode = 'setting'
                self.drawPlayEndModeInterface()
                pygame.display.flip()
        self.kinect.close()
        pygame.quit()

    #################################################
    # Score Caculation
    #################################################

    def scoreBeat(self):
        self.combo += 1
        self.comboHeight = 240
        self.score += self.scorePlus
        n = self.scorePlus + random.randint(50,100)
        if (n >= 1000): self.scorePlus = 999
        else: self.scorePlus = n
        if   (game.combo < 15): playSound(game.soundBeat1)
        elif (game.combo < 30): playSound(game.soundBeat2)
        else:                   playSound(game.soundBeat3)
    def scoreMiss(self):
        self.combo = 0
        self.scorePlus = 100

    #################################################
    # Draw Interface
    #################################################

    def drawIntroModeInterface(self):
        ### Hands Dance Title and Background
        self.screen.blit(self.imgInterfaceIntro, (0,0))
        ### PRESS W TO ENTER/LEAVE FULL SCREEN MODE, OR ANY OTHER KEYS TO START
        x, y = self.width//2, self.height*0.98
        text = 'PRESS W TO ENTER/LEAVE FULL SCREEN MODE, OR ANY OTHER KEYS TO START'
        drawText(self.screen, (x,y), text, 60, RGBColor.white, 'S')
    def drawSettingModeInterface(self):
        self.screen.blit(self.imgInterfaceSetting[self.settingModeSelection], (0,0))
        ### FileName.wav
        x, y = self.width//2, 340
        text = self.musicFileName[self.musicFileSelect]
        drawText(self.screen, (x,y), text, 125, RGBColor.white, 'S')
        ### FileName.bin
        x, y = self.width//2, 735
        ### No Recorded Dance Piece is Found
        if (self.binFileName == []): text = 'No Recorded Dance Piece is Found'
        else: text = self.binFileName[self.binFileSelect]
        drawText(self.screen, (x,y), text, 125, RGBColor.white, 'S')
    def drawLevelModeInterface(self): self.screen.blit(self.imgInterfaceLevel[self.level], (0,0))
    # ------------------------------------------------
    def drawRecordModeInterface(self): self.screen.blit(self.imgInterfaceRecord, (0,703))
    def drawPlayModeInterface(self):
        self.screen.blit(self.imgInterface, (0,703))
        drawText(self.screen, (285,900), self.path[9:-4], 90, RGBColor.white, 'S')
        tempText = self.levelName[self.level] + ' / ' + self.musicLengthText
        drawText(self.screen, (285,1015), tempText, 90, RGBColor.white, 'S')
        tempText = (str(1000000 + self.score))[1:] + '   +' + (str(1000 + self.scorePlus))[1:]
        drawText(self.screen, (960,1040), tempText, 135, RGBColor.white, 'S')
        n = str(1000 + self.combo)[1:]
        if (self.comboHeight > 180): self.comboHeight -= 5
        for i in range(3):
            img = pygame.transform.scale(self.imgTextComboDigit[int(n[i])], (100, self.comboHeight))
            self.screen.blit(img, (555+100*i, 687-(self.comboHeight-180)))
        img = pygame.transform.scale(self.imgTextCombo, (500, self.comboHeight))
        self.screen.blit(img, (860, 687-(self.comboHeight-180)))
    # ------------------------------------------------
    def drawRecordEndModeInterface(self):
        self.screen.blit(self.imgInterfaceRecordEnd, (0,0))
        ### PRESS ANY KEY TO RETURN MENU
        x, y = self.width//2, self.height*0.9
        text = 'PRESS ANY KEY TO RETURN MENU'
        drawText(self.screen, (x,y), text, 70, RGBColor.white, 'S')
    def drawPlayEndModeInterface(self):
        self.screen.blit(self.imgInterfacePlayEnd, (0,0))
        ### Your Score
        x, y = self.width//2, 340
        drawText(self.screen, (x,y), str(self.score), 125, RGBColor.red, 'S')
        ### Best Score
        x, y = self.width//2, 735
        drawText(self.screen, (x,y), str(self.bestScore), 125, RGBColor.red, 'S')
        ### PRESS ANY KEY TO RETURN MENU
        x, y = self.width//2, self.height*0.9
        text = 'PRESS ANY KEY TO RETURN MENU'
        drawText(self.screen, (x,y), text, 70, RGBColor.white, 'S')

    #################################################
    # Other Draw Fuctions
    #################################################

    def drawBinFileVideo(self):
        for i in range(self.currentBinFileVideoNumber, len(self.binFileVideoTime)):
            if (self.binFileVideoTime[i] > game.time):
                self.currentBinFileVideoNumber = i-1
                break
        try:    self.screen.blit(self.binFileVideo[self.currentBinFileVideoNumber+1], (1410, 760))
        except: self.screen.blit(self.binFileVideo[self.currentBinFileVideoNumber],   (1410, 760))
    def drawLoading(self):
        self.screen.fill(RGBColor.black)
        ### Loading... Please Wait...
        x, y = self.width//2, self.height//2
        text = 'Loading... Please Wait...'
        drawText(self.screen, (x,y), text, 125, RGBColor.white)
        pygame.display.flip()
    def drawKinectColorFrame(self, frame, target_surface):
        ##################################################
        # MODULE | PyKinect 2
        # SOURCE | Microsoft Kinect 2 Workshop Sample
        #          https://drive.google.com/file/d/0B034f0-ld_3wcVZUSTNXUndWQXM/view?usp=sharing
        # ------------------------------------------------
        target_surface.lock()
        address = self.kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        target_surface.unlock()
        ##################################################
        pass
    # ------------------------------------------------
    def getHandsPosition(self, joints, jointPoints):
        notTracked = PyKinectV2.TrackingState_NotTracked
        if (joints[PyKinectV2.JointType_HandLeft].TrackingState  != notTracked) and\
           (joints[PyKinectV2.JointType_HandRight].TrackingState != notTracked):
            try:
                self.handPositionXLeft  = int(jointPoints[PyKinectV2.JointType_HandLeft].x)
                self.handPositionYLeft  = int(jointPoints[PyKinectV2.JointType_HandLeft].y)
                self.handPositionXRight = int(jointPoints[PyKinectV2.JointType_HandRight].x)
                self.handPositionYRight = int(jointPoints[PyKinectV2.JointType_HandRight].y)
            except:
                self.handPositionXLeft,  self.handPositionYLeft  = None, None
                self.handPositionXRight, self.handPositionYRight = None, None
        else:
            self.handPositionXLeft,  self.handPositionYLeft  = None, None
            self.handPositionXRight, self.handPositionYRight = None, None
            return False
    def getDetectiveCircleRadius(self, joints, jointPoints):
        notTracked = PyKinectV2.TrackingState_NotTracked
        if (joints[PyKinectV2.JointType_HandTipLeft].TrackingState   != notTracked) and\
           (joints[PyKinectV2.JointType_HandTipRight].TrackingState  != notTracked) and\
           (joints[PyKinectV2.JointType_HandLeft].TrackingState      != notTracked) and\
           (joints[PyKinectV2.JointType_HandRight].TrackingState     != notTracked) and\
           (joints[PyKinectV2.JointType_WristLeft].TrackingState     != notTracked) and\
           (joints[PyKinectV2.JointType_WristRight].TrackingState    != notTracked) and\
           (joints[PyKinectV2.JointType_ElbowLeft].TrackingState     != notTracked) and\
           (joints[PyKinectV2.JointType_ElbowRight].TrackingState    != notTracked) and\
           (joints[PyKinectV2.JointType_ShoulderLeft].TrackingState  != notTracked) and\
           (joints[PyKinectV2.JointType_ShoulderRight].TrackingState != notTracked):
            # Left Hand
            leftLength = 0
            x0 = jointPoints[PyKinectV2.JointType_HandTipLeft].x
            y0 = jointPoints[PyKinectV2.JointType_HandTipLeft].y
            x1 = jointPoints[PyKinectV2.JointType_HandLeft].x
            y1 = jointPoints[PyKinectV2.JointType_HandLeft].y
            leftLength += distance(x0, y0, x1, y1)
            x0 = jointPoints[PyKinectV2.JointType_WristLeft].x
            y0 = jointPoints[PyKinectV2.JointType_WristLeft].y
            leftLength += distance(x0, y0, x1, y1)
            x1 = jointPoints[PyKinectV2.JointType_ElbowLeft].x
            y1 = jointPoints[PyKinectV2.JointType_ElbowLeft].y
            leftLength += distance(x0, y0, x1, y1)
            x0 = jointPoints[PyKinectV2.JointType_ShoulderLeft].x
            y0 = jointPoints[PyKinectV2.JointType_ShoulderLeft].y
            leftLength += distance(x0, y0, x1, y1)
            # Right Hand
            rightLength = 0
            x0 = jointPoints[PyKinectV2.JointType_HandTipRight].x
            y0 = jointPoints[PyKinectV2.JointType_HandTipRight].y
            x1 = jointPoints[PyKinectV2.JointType_HandRight].x
            y1 = jointPoints[PyKinectV2.JointType_HandRight].y
            rightLength += distance(x0, y0, x1, y1)
            x0 = jointPoints[PyKinectV2.JointType_WristRight].x
            y0 = jointPoints[PyKinectV2.JointType_WristRight].y
            rightLength += distance(x0, y0, x1, y1)
            x1 = jointPoints[PyKinectV2.JointType_ElbowRight].x
            y1 = jointPoints[PyKinectV2.JointType_ElbowRight].y
            rightLength += distance(x0, y0, x1, y1)
            x0 = jointPoints[PyKinectV2.JointType_ShoulderRight].x
            y0 = jointPoints[PyKinectV2.JointType_ShoulderRight].y
            rightLength += distance(x0, y0, x1, y1)
            # ------------------------------------------------
            try:
                result = int((leftLength+rightLength)/2)
                self.DCRadiusLeft, self.DCRadiusRight = result, result
            except: return False
        else: return False
    # ------------------------------------------------
    def drawDetectiveCircles(self, joints, jointPoints):
        notTracked = PyKinectV2.TrackingState_NotTracked
        if (joints[PyKinectV2.JointType_ShoulderLeft].TrackingState != notTracked):
            self.DCPositionXLeft = int(jointPoints[PyKinectV2.JointType_ShoulderLeft].x)
            self.DCPositionYLeft = int(jointPoints[PyKinectV2.JointType_ShoulderLeft].y)
            pygame.draw.circle(self.screen, RGBColor.white, (self.DCPositionXLeft, self.DCPositionYLeft), self.DCRadiusLeft, 5)
            pygame.draw.circle(self.screen, RGBColor.white, (self.DCPositionXLeft, self.DCPositionYLeft), 15)
        if (joints[PyKinectV2.JointType_ShoulderRight].TrackingState != notTracked):
            self.DCPositionXRight = int(jointPoints[PyKinectV2.JointType_ShoulderRight].x)
            self.DCPositionYRight = int(jointPoints[PyKinectV2.JointType_ShoulderRight].y)
            pygame.draw.circle(self.screen, RGBColor.white, (self.DCPositionXRight, self.DCPositionYRight), self.DCRadiusRight, 5)
            pygame.draw.circle(self.screen, RGBColor.white, (self.DCPositionXRight, self.DCPositionYRight), 15)
    def drawHandsPosition(self):
        if (self.handPositionXLeft  != None) and (self.handPositionYLeft  != None) and\
           (self.handPositionXRight != None) and (self.handPositionYRight != None):
            blitImageCenter(self.screen, self.imgHandIconLeft,  (self.handPositionXLeft, self.handPositionYLeft))
            blitImageCenter(self.screen, self.imgHandIconRight, (self.handPositionXRight, self.handPositionYRight))

    #################################################
    # Music & Bin Files Fuctions
    #################################################

    def loadMusic(self):
        ##################################################
        # MODULE | LibROSA 0.5
        # SOURCE | http://librosa.github.io/librosa/tutorial.html#quickstart
        # ------------------------------------------------
        # Detect and create a list of beats in the song
        y, sr = librosa.load(self.path)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        self.tempoBallList = createTempoBallList(list(librosa.frames_to_time(beat_frames, sr=sr)))
        ##################################################
        return
    # ------------------------------------------------
    def createBinFile(self):
        binPath = self.binFileName + '.bin'
        if testMode: print(binPath)
        self.tempoBallList[0].path = self.path
        self.tempoBallList[0].bestScore = 0
        ##################################################
        # MODULE | Pickle
        # SOURCE | http://stackoverflow.com/questions/20716812/saving-and-loading-multiple-objects-in-pickle-file
        # ------------------------------------------------
        with open(binPath, 'wb') as file:
           pickle.dump(self.tempoBallList, file)
        ##################################################
        return binPath
    def importBinFile(self):
        ##################################################
        # MODULE | Pickle
        # SOURCE | http://stackoverflow.com/questions/20716812/saving-and-loading-multiple-objects-in-pickle-file
        # ------------------------------------------------
        try:
            with open(self.bin, 'rb') as file:
                self.tempoBallList = pickle.load(file)
                self.path          = self.tempoBallList[0].path
                self.bestScore     = self.tempoBallList[0].bestScore
                self.musicLength   = getMusicLength(self.path)
                if testMode: print('Loading Dance Piece Successed!')
        except:
            if testMode:print('Loading Dance Piece Failed!')
        ##################################################
        return
    def updateBinFile(self):
        ##################################################
        # MODULE | Pickle
        # SOURCE | http://stackoverflow.com/questions/20716812/saving-and-loading-multiple-objects-in-pickle-file
        # ------------------------------------------------
        try:
            with open(self.bin, 'rb') as file:
                self.tempoBallList = pickle.load(file)
                self.tempoBallList[0].bestScore = self.bestScore
            with open(self.bin, 'wb') as file:
                pickle.dump(self.tempoBallList, file)
            if testMode: print('Updating Dance Piece Successed!')
        except:
            if testMode: print('Updating Dance Piece Failed!')
        ##################################################
        return
    # ------------------------------------------------
    def importBinFileVideo(self):
        self.binFileVideo = []
        self.binFileVideoTime = []
        for filename in os.listdir(self.bin[:-4]):
            if (filename[-4:] == '.jpg'):
                path = self.bin[:-4] + '/' + filename
                self.binFileVideo.append(pygame.image.load(path))
                n = (int(filename[:-4]))/100-10
                self.binFileVideoTime.append(n)
        self.currentBinFileVideoNumber = 0

game = GameRuntime()
game.run()

