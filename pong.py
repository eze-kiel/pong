# -*- coding:utf-8 -*-
import SH1106
import time
import config
import traceback

import RPi.GPIO as GPIO

import time
import subprocess

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

#GPIO define
RST_PIN        = 25
CS_PIN         = 8
DC_PIN         = 24

KEY_UP_PIN     = 6 
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13

KEY1_PIN       = 21
KEY2_PIN       = 20
KEY3_PIN       = 16


# 240x240 display with hardware SPI:
disp = SH1106.SH1106()
disp.Init()

# Clear display.
disp.clear()
# time.sleep(1)

#init GPIO
# for P4:
# sudo vi /boot/config.txt
# gpio=6,19,5,26,13,21,20,16=pu
GPIO.setmode(GPIO.BCM) 
GPIO.setup(KEY_UP_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_DOWN_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_LEFT_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_RIGHT_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_PRESS_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY1_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY2_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY3_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)

## GAME SETUP
DIFFICULTY = 5 # this is the number of pixel the ball will move each tick
END_OF_GAME = False # set to True when a player loses a point
WINNER = "none"

# player 1
P1_X = 15

P1_TOP_Y = 30
P1_BOTTOM_Y = 45

# player 2
P2_X = 113

P2_TOP_Y = 30
P2_BOTTOM_Y = 45

# ball
GO_TO_LEFT = True
BALL_X = 61
BALL_Y = 30

# create the initial line
def mainPanelStartup(draw):
    # player 1
    draw.line([(P1_X,P1_TOP_Y),(P1_X,P1_BOTTOM_Y)])
    # player 2
    draw.line([(P2_X,P2_TOP_Y),(P2_X,P2_BOTTOM_Y)])

def welcomePanelStartup(draw):
    draw.text((30,30), "hello !")

def endPanelStartup(draw, winner):
    draw.rectangle([(0, 0), (127, 63)], fill="#ffffff")

    if winner == "player1":
        draw.text((2,30), "player 1 won ! GG WP")
    else:
        draw.text((2,30), "player 2 won ! GG WP")

def checkPoint(currentY, YTop, YBottom):
    if YTop <= currentY <= YBottom:
        return False
    else:
        return True


# updatePlayer adjust the position of the player line depending of the movement
def updatePlayer(player, movement, draw):
    if player == "player1":
        global P1_TOP_Y, P1_BOTTOM_Y

        if movement == "up":
            # if we are at the top of the screen, we simply ignore the movement instruction
            if P1_TOP_Y <= 0:
                pass

            else:
                P1_TOP_Y -= 5
                P1_BOTTOM_Y -= 5

        else:
            if P1_BOTTOM_Y >= 64:
                pass

            else:
                P1_TOP_Y += 5
                P1_BOTTOM_Y += 5

        # the screen is cleared
        draw.rectangle([(0, 0), (15, 127)], fill="#ffffff")

        # the new line is drew
        draw.line([(P1_X,P1_TOP_Y),(P1_X,P1_BOTTOM_Y)])
    else:
        global P2_TOP_Y, P2_BOTTOM_Y

        if movement == "up":
            # if we are at the top of the screen, we simply ignore the movement instruction
            if P2_TOP_Y <= 0:
                pass

            else:
                P2_TOP_Y -= 5
                P2_BOTTOM_Y -= 5

        else:
            if P2_BOTTOM_Y >= 64:
                pass

            else:
                P2_TOP_Y += 5
                P2_BOTTOM_Y += 5

        # the screen is cleared
        draw.rectangle([(112, 0), (117, 127)], fill="#ffffff")

        # the new line is drew
        draw.line([(P2_X,P2_TOP_Y),(P2_X,P2_BOTTOM_Y)])

def ballMovement(draw):
    global GO_TO_LEFT, BALL_X, BALL_Y, END_OF_GAME, WINNER
    if GO_TO_LEFT:
        # the screen is cleared
        draw.rectangle([(16, 0), (110, 127)], fill="#ffffff")

        # draw the ball
        BALL_X -= DIFFICULTY
        draw.point((BALL_X, BALL_Y))

        if BALL_X <= 16:
            GO_TO_LEFT = False
            if checkPoint(BALL_Y, P1_TOP_Y, P1_BOTTOM_Y):
                END_OF_GAME = True
                WINNER = "player2"
            
    else:
        # the screen is cleared
        draw.rectangle([(16, 0), (110, 127)], fill="#ffffff")

        # draw the ball
        BALL_X += DIFFICULTY
        draw.point((BALL_X, BALL_Y))

        if BALL_X >= 110:
            GO_TO_LEFT = True
            if checkPoint(BALL_Y, P2_TOP_Y, P2_BOTTOM_Y):
                END_OF_GAME = True
                WINNER = "player1"



# create images for drawing.
welcomePanel = Image.new('1', (disp.width, disp.height), "WHITE")
mainPanel = Image.new('1', (disp.width, disp.height), "WHITE")
endPanel = Image.new('1', (disp.width, disp.height), "WHITE")

# create drawers
drawWelcomePanel = ImageDraw.Draw(welcomePanel)
drawMainPanel = ImageDraw.Draw(mainPanel)
drawEndPanel = ImageDraw.Draw(endPanel)

welcomePanelStartup(drawWelcomePanel)
mainPanelStartup(drawMainPanel)

disp.ShowImage(disp.getbuffer(welcomePanel))
time.sleep(3)

while 1:

    # player 1 controls
    if not GPIO.input(KEY_UP_PIN):
        updatePlayer("player1", "up", drawMainPanel)
    
    if not GPIO.input(KEY_DOWN_PIN):
        updatePlayer("player1", "down", drawMainPanel)

    # player 2 controls
    if not GPIO.input(KEY1_PIN):
        updatePlayer("player2", "up", drawMainPanel)
    
    if not GPIO.input(KEY3_PIN):
        updatePlayer("player2", "down", drawMainPanel)

    ballMovement(drawMainPanel)

    if END_OF_GAME:
        endPanelStartup(drawEndPanel, WINNER)
        disp.ShowImage(disp.getbuffer(endPanel))
        time.sleep(10)
        exit(0)

    # refresh main image
    disp.ShowImage(disp.getbuffer(mainPanel))