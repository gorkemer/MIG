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
                    monitor='T1', color='black', fullscr = False)
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
fileName = "MIG_May6_2" #+ expInfo['dateStr'] #"gorkemTestOnP7"

timerClock = core.Clock()
# Experiment Parameters #
refRate = 60  # 1 second
nTrials = 1 #400
second = refRate  # stimulus duration = 2 seconds
dotsN = 1000
screenSize = 15  # 3x3 square dot field
screenSizeX = 10
screenSizeY = 5
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

randDotsX = numpy.random.uniform(low=-5, high=5,size=(dotsN,))
randDotsY = numpy.random.uniform(low=-5, high=5,size=(dotsN,))

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

##Calculate the POSITIVE y value of a point on the edge of the ellipse given an x-value
def yValuePositive(x, shapeNo, verticalAxis, horizontalAxis, aperture_xy):
    totalX = []
    for i in x:
        xx = i - (aperture_xy[shapeNo][0]); #Bring it back to the (0,0) center to calculate accurately (ignore the y-coordinate because it is not necessary for calculation)
        workedX = verticalAxis * sqrt(1 - (math.pow(xx, 2) / math.pow(horizontalAxis, 2))) + aperture_xy[shapeNo][1]; #Calculated the positive y value and added apertureCenterY to recenter it on the screen 
        totalX.append(workedX)
    return totalX
##Calculate the NEGATIVE y value of a point on the edge of the ellipse given an x-value
def yValueNegative(x, shapeNo, verticalAxis, horizontalAxis, aperture_xy):
    totalX = []
    for i in x:
        xx = i - (aperture_xy[shapeNo][0]); #Bring it back to the (0,0) center to calculate accurately (ignore the y-coordinate because it is not necessary for calculation)
        workedX = -verticalAxis * sqrt(1 - (math.pow(xx, 2) / math.pow(horizontalAxis, 2))) + aperture_xy[shapeNo][1]; #Calculated the negative y value and added apertureCenterY to recenter it on the screen
        totalX.append(workedX)
    return totalX
##Calculate the POSITIVE x value of a point on the edge of the ellipse given a y-value
def xValuePositive(y, shapeNo, verticalAxis, horizontalAxis, aperture_xy):
    totalY = []
    for i in y:
        yy = i - (aperture_xy[shapeNo][1])
        workedY = horizontalAxis * sqrt(1 - (math.pow(yy, 2) / math.pow(verticalAxis, 2))) + aperture_xy[shapeNo][0]; #Calculated the positive x value and added apertureCenterX to recenter it on the screen
        
        totalY.append(workedY)
    return totalY

##Calculate the NEGATIVE x value of a point on the edge of the ellipse given a y-value
def xValueNegative(y, shapeNo, verticalAxis, horizontalAxis, aperture_xy):
    totalY = []
    for i in y:
        yy = i - (aperture_xy[shapeNo][1]); #Bring it back to the (0,0) center to calculate accurately (ignore the x-coordinate because it is not necessary for calculation)
        workedY =  -horizontalAxis * sqrt(1 - (math.pow(yy, 2) / math.pow(verticalAxis, 2))) + aperture_xy[shapeNo][0]; #Calculated the negative x value and added apertureCenterX to recenter it on the screen
        totalY.append(workedY)
    return totalY


##### FOR TARGET ##########
##Calculate the NEGATIVE y value of a point on the edge of the ellipse given an x-value

def yValuePositive_target(x, verticalAxis, horizontalAxis, targetLoc):
    totalX = []
    for i in x:
        xx = i - (targetLoc[0]); #Bring it back to the (0,0) center to calculate accurately (ignore the y-coordinate because it is not necessary for calculation)
        workedX = verticalAxis * sqrt(1 - (math.pow(xx, 2) / math.pow(horizontalAxis, 2))) + targetLoc[1]; #Calculated the positive y value and added apertureCenterY to recenter it on the screen 
        totalX.append(workedX)
    return totalX

def yValueNegative_target(x, verticalAxis, horizontalAxis, targetLoc):
    totalX = []
    for i in x:
        xx = i - (targetLoc[0]); #Bring it back to the (0,0) center to calculate accurately (ignore the y-coordinate because it is not necessary for calculation)
        workedX = -verticalAxis * sqrt(1 - (math.pow(xx, 2) / math.pow(horizontalAxis, 2))) + targetLoc[1]; #Calculated the negative y value and added apertureCenterY to recenter it on the screen
        totalX.append(workedX)
    return totalX

##Calculate the POSITIVE x value of a point on the edge of the ellipse given a y-value
def xValuePositive_target(y, verticalAxis, horizontalAxis, targetLoc):
    totalY = []
    for i in y:
        yy = i - (targetLoc[1])
        workedY = horizontalAxis * sqrt(1 - (math.pow(yy, 2) / math.pow(verticalAxis, 2))) + targetLoc[0]; #Calculated the positive x value and added apertureCenterX to recenter it on the screen
        
        totalY.append(workedY)
    return totalY

##Calculate the NEGATIVE x value of a point on the edge of the ellipse given a y-value
def xValueNegative_target(y, verticalAxis, horizontalAxis, targetLoc):
    totalY = []
    for i in y:
        yy = i - (targetLoc[1]); #Bring it back to the (0,0) center to calculate accurately (ignore the x-coordinate because it is not necessary for calculation)
        workedY =  -horizontalAxis * sqrt(1 - (math.pow(yy, 2) / math.pow(verticalAxis, 2))) + targetLoc[0]; #Calculated the negative x value and added apertureCenterX to recenter it on the screen
        totalY.append(workedY)
    return totalY

def remove_dots_leaving_screen(randDotsX, randDotsy, deathDots):
    ''' checks the location of X and Y - if extends the screen, kills and respawns'''
    outfieldDotsX = numpy.logical_or((randDotsX >= screenSizeX), (randDotsX <= -screenSizeX))
    outfieldDotsY = numpy.logical_or((randDotsY >= 5), (randDotsY <= -5))

    #randDotsX[outfieldDotsX] = numpy.random.uniform(low=-screenSizeX, high=screenSizeX,size=(sum(outfieldDotsX,)))
    randDotsY[outfieldDotsY] = numpy.random.uniform(low=-5, high=5,size=(sum(outfieldDotsY,)))
    #randDotsX[deathDots] = numpy.random.uniform(low=-screenSizeX, high=screenSizeX,size=(sum(deathDots,)))

def inShapeTransDots(randDotsY, randDotsX, groupElementShape, groupingElementsSpeed, aperture_xy, diffGroupingDirections, sharedMotion):

    verticalAxis = groupElementShape[0]
    horizontalAxis = groupElementShape[1]
    #dot.x > xValueNegative_foreground(dot.y) && dot.x < xValuePositive_foreground(dot.y) && dot.y > yValueNegative_foreground(dot.x) && dot.y < yValuePositive_foreground(dot.x)) {
    #if (dot.x < xValueNegative(dot.y) || dot.x > xValuePositive(dot.y) || dot.y < yValueNegative(dot.x) || dot.y > yValuePositive(dot.x)) {
    shapeNo = 0
    xIn = numpy.logical_and((randDotsX > xValueNegative(randDotsY, shapeNo, verticalAxis, horizontalAxis, aperture_xy)), (randDotsX < xValuePositive(randDotsY, shapeNo, verticalAxis, horizontalAxis, aperture_xy)))
    yIn = numpy.logical_and((randDotsY > yValueNegative(randDotsX, shapeNo, verticalAxis, horizontalAxis, aperture_xy)), (randDotsY < yValuePositive(randDotsX, shapeNo, verticalAxis, horizontalAxis, aperture_xy)))
    shapeNo = 1
    xIn_2 = numpy.logical_and((randDotsX > xValueNegative(randDotsY, shapeNo, verticalAxis, horizontalAxis, aperture_xy)), (randDotsX < xValuePositive(randDotsY, shapeNo, verticalAxis, horizontalAxis, aperture_xy)))
    yIn_2 = numpy.logical_and((randDotsY > yValueNegative(randDotsX, shapeNo, verticalAxis, horizontalAxis, aperture_xy)), (randDotsY < yValuePositive(randDotsX, shapeNo, verticalAxis, horizontalAxis, aperture_xy)))
    shapeNo = 2
    xIn_3 = numpy.logical_and((randDotsX > xValueNegative(randDotsY, shapeNo, verticalAxis, horizontalAxis, aperture_xy)), (randDotsX < xValuePositive(randDotsY, shapeNo, verticalAxis, horizontalAxis, aperture_xy)))
    yIn_3 = numpy.logical_and((randDotsY > yValueNegative(randDotsX, shapeNo, verticalAxis, horizontalAxis, aperture_xy)), (randDotsY < yValuePositive(randDotsX, shapeNo, verticalAxis, horizontalAxis, aperture_xy)))
    shapeNo = 3
    xIn_4 = numpy.logical_and((randDotsX > xValueNegative(randDotsY, shapeNo, verticalAxis, horizontalAxis, aperture_xy)), (randDotsX < xValuePositive(randDotsY, shapeNo, verticalAxis, horizontalAxis, aperture_xy)))
    yIn_4 = numpy.logical_and((randDotsY > yValueNegative(randDotsX, shapeNo, verticalAxis, horizontalAxis, aperture_xy)), (randDotsY < yValuePositive(randDotsX, shapeNo, verticalAxis, horizontalAxis, aperture_xy)))
    

    inside = numpy.logical_and(xIn, yIn)
    inside_2 = numpy.logical_and(xIn_2, yIn_2)
    inside_3 = numpy.logical_and(xIn_3, yIn_3)
    inside_4 = numpy.logical_and(xIn_4, yIn_4)

    #outside = [not elem for elem in inside]

    #anyInside = numpy.logical_or(inside, inside_2)
    # move randomly but faster

    moveDir1 = diffGroupingDirections[0]
    moveDir2 = diffGroupingDirections[1]
    moveDir3 = diffGroupingDirections[2]
    moveDir4 = diffGroupingDirections[3]

    if sharedMotion==0:
        randDotsX[inside] += speed * groupingElementsSpeed * moveDir1[0]   #* cos(alpha[inside])#* sin(alpha2)
        randDotsX[inside_2] += speed * groupingElementsSpeed * moveDir2[0]  #* cos(alpha[inside_2])#* sin(alpha2)
        randDotsX[inside_3] += speed * groupingElementsSpeed * moveDir3[0] #* cos(alpha[inside_3])#* sin(alpha2)
        randDotsX[inside_4] += speed * groupingElementsSpeed * moveDir4[0] #* cos(alpha[inside_4])
        
        randDotsY[inside] += speed* groupingElementsSpeed *moveDir1[1] #*sin(alpha[inside])  #sin(alpha[inside])
        randDotsY[inside_2] += speed* groupingElementsSpeed *moveDir2[1] #*sin(alpha[inside_2])
        randDotsY[inside_3] += speed* groupingElementsSpeed *moveDir3[1] #*sin(alpha[inside_3])
        randDotsY[inside_4] += speed* groupingElementsSpeed *moveDir4[1] #*sin(alpha[inside_4])

    else:
        if (hori==1):
            randDotsX[inside] += speed * groupingElementsSpeed * moveDir   #* cos(alpha[inside])#* sin(alpha2)
            randDotsX[inside_2] += speed * groupingElementsSpeed * moveDir  #* cos(alpha[inside_2])#* sin(alpha2)
            randDotsX[inside_3] += speed * groupingElementsSpeed * moveDir #* cos(alpha[inside_3])#* sin(alpha2)
            randDotsX[inside_4] += speed * groupingElementsSpeed * moveDir #* cos(alpha[inside_4])
        else:
            randDotsY[inside] += speed*groupingElementsSpeed *moveDir #*sin(alpha[inside])  #sin(alpha[inside])
            randDotsY[inside_2] += speed*groupingElementsSpeed *moveDir #*sin(alpha[inside_2])
            randDotsY[inside_3] += speed*groupingElementsSpeed *moveDir #*sin(alpha[inside_3])
            randDotsY[inside_4] += speed*groupingElementsSpeed *moveDir #*sin(alpha[inside_4])

def inShapeDotsPolar():
    # handle structure-from-motion 
    shapeXBorders =  numpy.logical_and((dotsRadius <= 8), (dotsRadius > 6)) #numpy.where(numpy.logical_or((randDotsX <= shapeFieldSize), (randDotsX >= -shapeFieldSize))) #numpy.logical_or((randDotsX >= shapeFieldSize), (randDotsX <= -shapeFieldSize))
    shapeYBorders_1 = numpy.logical_and((dotsTheta <= 90), (dotsTheta >= 0))
    shapeYBorders_2 = numpy.logical_and((dotsTheta <= 180), (dotsTheta >= 90))
    shapeYBorders_3 = numpy.logical_and((dotsTheta <= 270), (dotsTheta >= 180))
    shapeYBorders_4 = numpy.logical_and((dotsTheta <= 360), (dotsTheta >= 270))
    shapeYBorders_1 = numpy.logical_or(shapeYBorders_1, shapeYBorders_2)
    shapeYBorders_2 = numpy.logical_or(shapeYBorders_3, shapeYBorders_4)
    shapeIn_1 = numpy.logical_and(shapeXBorders, shapeYBorders_1)
    shapeIn_2 = numpy.logical_and(shapeXBorders, shapeYBorders_2)
    dotsRadius[shapeIn_1] += (speed*winds[0]) * cos(numpy.random.uniform(low=0, high=2*pi)) #cos(alpha[shapeIn]) 
    dotsRadius[shapeIn_2] += (speed*winds[1]) * cos(numpy.random.uniform(low=0, high=2*pi)) #cos(alpha[shapeIn]) 
    #dotsTheta[shapeIn] += speed/dotsRadius[shapeIn] #*  sin(numpy.random.uniform(low=0, high=2*pi)) #sin(alpha[shapeIn])
    #        dotsTheta += speed/dotsRadius * moveSign

def targetShapeDetermine(targetAngle):
    # handle structure-from-motion 
    targetRadiusRange =  numpy.logical_and((dotsRadius <= 8), (dotsRadius > 6)) #numpy.where(numpy.logical_or((randDotsX <= shapeFieldSize), (randDotsX >= -shapeFieldSize))) #numpy.logical_or((randDotsX >= shapeFieldSize), (randDotsX <= -shapeFieldSize))
    targetAngleRange = numpy.logical_and((dotsTheta <= targetAngle + targetAnglePlus), (dotsTheta >= targetAngle))

    targetIn = numpy.logical_and(targetRadiusRange, targetAngleRange)
    dotsRadius[targetIn] += (speed*winds[0] * 2) * cos(numpy.random.uniform(low=0, high=2*pi)) #cos(alpha[shapeIn]) 

def inShapeTargetTransDots(targetLoc, targetShape, targetSpeed):
    # handle structure-from-motion 
    verticalAxis = targetShape[0]
    horizontalAxis = targetShape[1]
    xIn = numpy.logical_and((randDotsX > xValueNegative_target(randDotsY, verticalAxis, horizontalAxis, targetLoc)), (randDotsX < xValuePositive_target(randDotsY, verticalAxis, horizontalAxis, targetLoc)))
    yIn = numpy.logical_and((randDotsY > yValueNegative_target(randDotsX, verticalAxis, horizontalAxis, targetLoc)), (randDotsY < yValuePositive_target(randDotsX, verticalAxis, horizontalAxis, targetLoc)))
   
    targetIn = numpy.logical_and(xIn, yIn)
    if targetHori:
        randDotsY[targetIn] += speed * targetSpeed * targetMoveDir
    else:
        randDotsX[targetIn] += speed * targetSpeed * targetMoveDir


def transVertiDotMove(transDotsX, transDotsY, speed,transMoveSign, deathDots):
    transDotsX += speed * transMoveSign #moves right-left
    remove_dots_leaving_screen(transDotsX, transDotsY, deathDots)

    return (transDotsX, transDotsY)

def randomDotMove(randDotsX, randDotsY, randDots, veloX, veloY, deathDots, cookGroup, moveDir, hori, targetLoc, groupElementShape, targetShape, groupingElementsSpeed, aperture_xy, targetExists, diffGroupingDirections, sharedMotion, targetSpeed):

    # np.invert or [not elem for elem in mylist]
    if cookGroup:
        inShapeTransDots(randDotsY, randDotsX, groupElementShape, groupingElementsSpeed, aperture_xy, diffGroupingDirections, sharedMotion)

    if target:
        if targetExists==1:
            inShapeTargetTransDots(targetLoc, targetShape, targetSpeed)
        else:
            pass

    randDotsX += veloX * moveDir
    randDotsY += veloY * moveDir
    #remove_dots_leaving_screen(randDotsX, randDotsX, deathDots) # remove dots leaving the screen

    outfieldDotsX = numpy.logical_or((randDotsX >= 5), (randDotsX <= -5))
    outfieldDotsY = numpy.logical_or((randDotsY >= 5), (randDotsY <= -5))

    randDotsX[outfieldDotsX] = numpy.random.uniform(low=-5, high=5,size=(sum(outfieldDotsX,)))
    randDotsY[outfieldDotsY] = numpy.random.uniform(low=-5, high=5,size=(sum(outfieldDotsY,)))
    #randDotsX[deathDots] = numpy.random.uniform(low=-screenSizeX, high=screenSizeX,size=(sum(deathDots,)))
    

    # move the dots to different places
    

    return (randDotsX, randDotsY)

def polarDotMove(dotsRadius, dotsTheta, rotDots, speed, deathDots, moveSign, motion, cookGroup, targetAngle, rest, winds):

    if motion == ['radial']:
        dotsRadius += speed * moveSign
        if moveSign == 1:
            outFieldRadius = (dotsRadius >= deathBorder)
        else:
            outFieldRadius = (dotsRadius <= centerDissappearence)
        dotsRadius[outFieldRadius] = numpy.random.rand(sum(outFieldRadius)) * screenSizeX
        #dotsRadius[deathDots] = numpy.random.rand(sum(deathDots)) * fieldSize
    else: #elif motion == ['angular']
        #dotsTheta += speed * moveSign #speed/dotsRadius * moveSign
        dotsTheta[deathDots] = numpy.random.rand(sum(deathDots)) * 360
        outFieldRadius = (dotsRadius <= centerDissappearence)
        dotsRadius[outFieldRadius] = numpy.random.rand(sum(outFieldRadius)) * screenSizeX
        #dotsRadius += veloX
        dotsTheta += speed/dotsRadius * moveSign #* sin(numpy.random.uniform(low=0, high=2*pi))
        #randDotsX += veloX
        #randDotsY += veloY
    # if (cookGroup):
    #     inShapeDotsPolar()
    # elif (not(rest)):
    #     targetShapeDetermine(targetAngle)
    thetaX, radiusY = pol2cart(dotsTheta, dotsRadius)
    rotDots.setXYs(numpy.array([thetaX, radiusY]).transpose())


def my_shuffle(array):
    rd.shuffle(array)
    return array

#############################################################################
###############################################################
# ####### initializing dot locations before the experiment loop # #######
######################################################################
######################################################################

tall = [2.5,1]
circle = [2,2]
flat = [1,2.5]
displacement = 6 # from fixation

# grouping elements
sharedMotionList = numpy.random.choice([0, 1], size=nTrials, p=[.5, .5]) #p=[.1, .9] # 1 is all have the same direction, all have different direction
moveDirList = numpy.random.choice([-1, 1], size=nTrials, p=[.5, .5])
groupingHoriList = numpy.random.choice([0, 1], size=nTrials, p=[.5, .5])
groupElementsShapePossible = [circle]
groupElementsShapeList = []
aperture_xy_possible = [[[0,-displacement], [-displacement,0], [displacement,0], [0,displacement]], [[displacement,displacement], [-displacement,displacement], [-displacement,-displacement], [displacement,-displacement]]]
groupElementsSpeedPossible = [2, 2, 2]
groupingElementsSpeedList = []

# cardinal or non cardinal
cardinalChangeList = numpy.random.choice([0, 1], size=nTrials, p=[.5, .5]) # 0 means stay = grouping at cardinals & target at non-cardinal, 1 means the opposite

immediateDelay = second/10 # 60 seconds 60 frames
delayTimePossible = [second/10, 4*second/10, 8*second/10]

# gorkem
xleft = [-1, 0]
xright = [1, 0]
ytop = [0,1]
ybot = [0,-1]
diffGroupingDirectionPossible = [xleft, xright, ytop, ybot] 

# target
targetShapeLocPossible = [[displacement,displacement], [-displacement,displacement], [-displacement,-displacement], [displacement,-displacement], [0,-displacement], [-displacement,0], [displacement,0], [0,displacement]]
targetShapeLocList = []
targetHoriList = numpy.random.choice([0, 1], size=nTrials, p=[.5, .5])
targetMoveDirList= numpy.random.choice([-1, 1], size=nTrials, p=[.5, .5])
targetExistenceList = numpy.random.choice([0, 1], size=nTrials, p=[.5, .5])
targetShapeList = []
groupingDirectionsList = []
targetSpeedPossible = [2, 3, 4]
targetSpeedList = []
delayTimeList = []

for t in range(nTrials):
    ''' determining feature lists'''
    targetLocSelected = rd.choice(targetShapeLocPossible)
    groupElementsShape = rd.choice(groupElementsShapePossible)
    targetShape = rd.choice(groupElementsShapePossible)
    groupingElementsSpeed = 3                      #rd.choice(groupElementsSpeedPossible)
    groupingDirections = my_shuffle(diffGroupingDirectionPossible)
    targetSpeed = rd.choice(targetSpeedPossible)
    delayTime = rd.choice(delayTimePossible)
    # add to lists
    targetShapeLocList.append(targetLocSelected) #append it to our feature list
    groupElementsShapeList.append(groupElementsShape)
    targetShapeList.append(targetShape)
    groupingElementsSpeedList.append(groupingElementsSpeed)
    groupingDirectionsList.append(groupingDirections[:])
    targetSpeedList.append(targetSpeed)
    delayTimeList.append(delayTime)



###############################################################
######### TRIAL LOOP ##########################################
######################################################################
######################################################################

welcomeText = visual.TextStim(win, text = "press a key to start the experiment.")
welcomeText.draw()
win.flip()
event.waitKeys()

responses = numpy.random.choice(["y", "n"], size=nTrials, p=[.5, .5])
responseTime = numpy.random.choice([0.0, 1.0], size=nTrials, p=[.5, .5])

for times in range(nTrials):
    responseGiven = False
    delayTime = 60/10#delayTimeList[times]
    t0 = time.time()
    print(times)
    #trialFrameDeets = randomFrameList_trial[trials]
    #define_target_info(trials)

    p0 = time.time()
    moveDir = moveDirList[times] #1 means right/top, #2 means bot/top
    hori = groupingHoriList[times]
    targetLoc = targetShapeLocList[times]
    targetHori = targetHoriList[times]
    targetMoveDir = targetMoveDirList[times]
    groupElementShape = groupElementsShapeList[times]
    cardinalChangeStatus = cardinalChangeList[times]
    aperture_xy = aperture_xy_possible[cardinalChangeStatus]
    groupingElementsSpeed = groupingElementsSpeedList[times]
    targetShape = targetShapeList[times]
    targetExists = targetExistenceList[times]
    diffGroupingDirections = groupingDirectionsList[times]
    targetSpeed = targetSpeedList[times]
    sharedMotion = sharedMotionList[times]
    delayTime = delayTimeList[times]

    fixation.color = "gray"
    rest = False
    #winds = [numpy.random.uniform(low=2, high=4), numpy.random.uniform(low=2, high=4)]

    for frameN in range(trialDur):
        c0 = time.time()


        dieScoreArray = numpy.random.rand(dotsN)  # generating array of float numbers
        deathDots = (dieScoreArray < 0.005) #each dot have maximum of 10 frames life
        target = False

        if (1*second/2 < frameN < 1*second):
            cookGroup = True
            #target = True
        elif (1*second + delayTime <= frameN < 1*second + delayTime + targetDuration):
            cookGroup = False
            target = True
        else:
            cookGroup = False

        randomDotMove(randDotsX, randDotsY, randDots, veloX, veloY, deathDots, cookGroup, moveDir, hori, targetLoc, groupElementShape, targetShape, groupingElementsSpeed, aperture_xy, targetExists, diffGroupingDirections, sharedMotion, targetSpeed)
        randXY = numpy.array([randDotsX, randDotsY]).transpose()
        randDots.setXYs(randXY)
        
        randDots.draw()
        #rotDots.draw()
        #transDots.draw()
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
            responses[times] = keys[0]#key_ID #key[1] is the timestamp
            responseTime[times] = keys[1]
            responseGiven = True

            # if ( (keys[0] == "y" and targetExists == 1 ) or (keys[0] == 'o' and targetExists == 0 )):
            #     #colorPresented = choice(['yellow'])
            #     fixation.color = "green"
            if keys[0] == 'escape':
                win.close()
                core.quit()

    t1 = time.time()
    trialDuration = t1-t0
    print("trialDuration:", trialDuration)
    # rest block ###
    # rest = True
    # cookGroup = False
    # fixation.color = "yellow"
    # for frameN in range(restDur):
    #     polarDotMove(dotsRadius, dotsTheta, rotDots, speed, deathDots, moveSign, motion, cookGroup, targetAngle, rest, winds)
    #     rotDots.draw()
    #     fixation.draw()
    #     win.flip()
    # end of rest block ###


saveData()
win.close()

