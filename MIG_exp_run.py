"""
19 Nisan 2022

S22 project script. 
Design TBD
    
"""

from __future__ import division  # so that 1/3=0.333 instead of 1/3=0
from psychopy import visual, core, data, event, logging, sound, gui
from psychopy.constants import *  # things like STARTED, FINISHED
import numpy  # whole numpy lib is available, prepend 'np.'
from numpy import sin, cos, tan, log, log10, pi, average, sqrt, std, deg2rad, rad2deg, linspace, asarray
from numpy.random import random, randint, normal, shuffle
import os  # handy system and path functions
import random as rd
from random import choice, randrange, shuffle, uniform
#from psychopy.tools.coordinatetools import pol2cart, cart2pol
import time
from psychopy.tools.filetools import fromFile, toFile
import csv
import os
import pylab
from psychopy.tools.coordinatetools import pol2cart, cart2pol
import math

# assign window #
win = visual.Window([1920, 1080], units='deg',
                    monitor='T1', color='black', fullscr = True)
win.setRecordFrameIntervals(True)
win._refreshThreshold=1/60

rt_clock = core.Clock()
rt_clock.reset()  # set rt clock to 0

expInfo = {'observer':'' } #add more if you want # 'practice': 1 # 'InitialPosition':0
expInfo['dateStr']= data.getDateStr() #add the current time
#present a dialogue to change params
# dlg = gui.DlgFromDict(expInfo, title='Gabor', fixed=['dateStr'])
# if dlg.OK == False: #quiting if the user pressed 'cancel'
#     core.quit()

#make a text file to save data
fileName = "MIG_GE_600Trials_1700dots" #+ expInfo['dateStr'] #"gorkemTestOnP7"


timerClock = core.Clock()
# Experiment Parameters #
refRate = 60  # 1 second
nTrials = 600 #400
second = refRate  # stimulus duration = 2 seconds
dotsN = 1700
screenSize = 15  # 3x3 square dot field
screenSizeX = 15
screenSizeY = 12
transFieldSize = 3
shapeFieldSize = 3
elemSize = 0.2 #0.25
speed =  1/60 #13/60 # 7 degree/seconds
posX = 9.06
posY = 0
centerDissappearence = 3#0.2
deathBorder = screenSizeX - elemSize
trialDur = refRate * 3
cookDur = refRate * 1

nonCookDur = trialDur - cookDur

restDur = refRate * 2
fixSize = 0.3
fixOpa = 1
posX = -4

# wind :D 
winds = [4,2]
targetAnglePlus = 30 # targetAngle plus this angle
targetDuration = 60/5# 200 ms

# stim list to store frames of motion
transVertiStims = []
transVertiFrameList= []
randomFrameList = []
randomFrameList_cook = []
randomFrameList_trial = [None] * nTrials

responses = [] #.append(key_ID) #key[1] is the timestamp
responseTime = [] #.append(key[1])

# initial dot location assignments
transDotsX = numpy.random.uniform(low=-transFieldSize, high=transFieldSize, size=(dotsN,))  # array of random float numbers between fieldSize range
transDotsY = numpy.random.uniform(low=-transFieldSize, high=transFieldSize, size=(dotsN,))

randDotsX = numpy.random.uniform(low=-screenSizeX, high=screenSizeX,size=(dotsN,))
randDotsY = numpy.random.uniform(low=-screenSizeY, high=screenSizeY,size=(dotsN,))

dotsTheta = numpy.random.rand(dotsN) * 360  # array with shape (500,)
dotsRadius = numpy.random.rand(dotsN) * screenSizeX

# speed and direction 
alpha= numpy.random.uniform(low=0, high=2*pi,size=(dotsN,))
veloX = speed * cos(alpha)
veloY = speed * sin(alpha)

# death-border assignment
screenBorder_y = numpy.logical_or((randDotsY >= screenSizeX), (randDotsY <= -screenSizeX))
screenBorder_x = numpy.logical_or((randDotsY >= screenSizeY), (randDotsY <= -screenSizeY))

# initializing experiment stimuli
fixation = visual.GratingStim(win, size=fixSize, pos=[0,0], sf=0,color = 'gray', opacity = fixOpa)

transDots = visual.ElementArrayStim(win,
                                    nElements=dotsN, sizes=elemSize, elementTex=None,
                                    colors=(1.0, 1.0, 1.0), xys=random([dotsN, 2]) * transFieldSize,
                                    colorSpace='rgb', elementMask='circle',
                                    fieldSize=transFieldSize)                                    
randDots = visual.ElementArrayStim(win,
                                   nElements=dotsN, sizes=elemSize, elementTex=None,
                                   colors=(1.0, 1.0, 1.0), xys=numpy.array([randDotsX, randDotsY]).transpose(),
                                   colorSpace='rgb', elementMask='circle',
                                   fieldSize=screenSizeX)
rotDots = visual.ElementArrayStim(win,
                                  nElements=dotsN, units = 'deg', sizes=elemSize, elementTex=None,
                                  colors=(1.0, 1.0, 1.0), xys=random([dotsN, 2]),
                                  colorSpace='rgb', elementMask='circle', texRes=128,
                                  fieldSize=screenSizeX, fieldShape = 'sqr')

rotDots.setFieldPos([0, 0])
transDots.setFieldPos([0, 0])

#AR_list = [ [verticalAxis, horizontalAxis], [1, 4], [5, 3]]

def saveData():
    #===========================================
    # Save Data
    #===========================================
    header = [ "responses", "responseTime" ]
    rows = zip(responses, responseTime)
    with open(fileName+'motionGrouping.csv', 'w') as f:
        #create the csv writer
        writer = csv.writer(f)
        # write the header
        writer.writerow(header)
        # write the data
        #print(rows)
        for row in rows:
            print(row)
            writer.writerow(row)



# paul
randomFrameList_trial = numpy.load('600_trials_2kDots.npy')

print(len(randomFrameList_trial))

###############################################################
######### TRIAL LOOP ##########################################
######################################################################
######################################################################

breakText = visual.TextStim(win, text = "Nice! 1/3 of the experiment is now over. You can have a rest for a few minutes. Press a key to continue!")

welcomeText = visual.TextStim(win, text = "press a key to start the experiment.")
welcomeText.draw()
win.flip()
event.waitKeys()

responses = numpy.random.choice(["y", "n"], size=nTrials, p=[.5, .5])
responseTime = numpy.random.choice([0.0, 1.0], size=nTrials, p=[.5, .5])

for trials in range(nTrials):
    responseGiven = False
    delayTime = 60/10#delayTimeList[times]
    t0 = time.time()
    print(trials)
    trialFrameDeets = randomFrameList_trial[trials]


    fixation.color = "gray"
    rest = False
    #winds = [numpy.random.uniform(low=2, high=4), numpy.random.uniform(low=2, high=4)]

    if (trials == nTrials/3) or (trials == 2*nTrials/3):
        breakText.draw()
        win.flip()
        event.waitKeys()

    for frameN in range(trialDur):
        c0 = time.time()
        responseWindow = 0
        if (frameN > 1*second + delayTime):
            rt_clock.reset() # target is shown!!
        if (frameN >= 3*second - second/5): # test-time
            colorPresented = choice(['yellow'])
            fixation.color = colorPresented

        # set XY from frame list
        randDots.setXYs(trialFrameDeets[frameN])

        #transDots.setXYs(transVertiFrameList[frameN])
        # draw stim #
        randDots.draw()

        fixation.draw()



        win.flip()
        c1 = time.time()

        keys = event.getKeys(keyList=["escape", 'y', 'o'], timeStamped=rt_clock ) #keyList=["escape", "y"]
        if frameN == trialDur-2 and (not responseGiven):
            keys = event.waitKeys(keyList=["escape", 'y', 'o'], timeStamped=rt_clock ) #keyList=["escape", "y"]
        for keys in keys:
            print(keys)
            if keys[0]=="y":
                key_ID = 1 #could be 1 
            else:
                key_ID = 0 # 2
            responses[trials] = keys[0]#key_ID #key[1] is the timestamp
            responseTime[trials] = keys[1]
            responseGiven = True

            if keys[0] == 'escape':
                win.close()
                core.quit()

    t1 = time.time()
    trialDuration = t1-t0
    print("trialDuration:", trialDuration)



saveData()

endText = visual.TextStim(win, text = "Experiment is over! Pleae notify the researcher. Press a key to end the experiment.")
endText.draw()
win.flip()
event.waitKeys()

win.close()

