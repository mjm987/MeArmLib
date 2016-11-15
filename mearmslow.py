# -*- coding: utf-8 -*-

from __future__ import print_function
from pwmsysfs import PwmSysFs
from time import sleep

DREHE=0
HOEHE=1
WEITE=2
GREIFER=3
SERVO=("DREHE", "HOEHE", "WEITE", "GREIFER")
WAIT_BETWEEN_STEPS=0
WAIT_BETWEEN_TICS=0.02


def sign(x):  return 1 if x>0 else -1

#def sum(vecta, vectb): return map(lambda x,y: x+y, vecta, vectb) 
def sum(vecta, vectb): return map(lambda x,y: x+y, vecta, list(vectb)+[0,]*(len(vecta)-len(vectb))) 

class Pos(list):
    def __add__(vecta, vectb):
        #return map(lambda x,y: x+y, vecta, vectb) 
        return map(lambda x,y: x+y, vecta, list(vectb)+[0,]*(len(vecta)-len(vectb))) 
class MeArm():

    def __init__(self, initpos=None, offset=(0,0,0,0)):
        self.position = list(initpos)
        self.offset = offset
        self.pwm = PwmSysFs()
        self.n = 0
        sleep(2)

    def standby(self): self.pwm.standby()

    def gotoPos(self, endpos):
        curr = self.position[0:len(endpos)]
        print("%d: gotoPos from " % self.n , curr, " to ", endpos)
        self.n += 1
        while curr != list(endpos):
            for i in xrange(0,len(endpos)):
                if curr[i] != endpos[i]:
                    #print(curr, endpos)
                    curr[i] = curr[i]+sign(endpos[i]- curr[i])
                    self.pwm.setServo(i, curr[i]+self.offset[i])
            sleep(WAIT_BETWEEN_TICS)
        for i in xrange(0, len(endpos)):
            self.position[i] = endpos[i]
        sleep(WAIT_BETWEEN_STEPS)

    def deltaPos(self, delta):
        print("%d: deltaPos by " % self.n, delta, '--->')
        self.gotoPos(sum(self.position, delta))

    def setServo(self, servo, endpos):
        curr = self.position[servo]
        print("%d: setServo %s from %d to %d" % (self.n, SERVO[servo], curr, endpos))
        self.n += 1
        direction=sign(endpos-curr)
        while curr != endpos:
            curr += direction
            self.pwm.setServo(servo, curr+self.offset[servo])
            sleep(WAIT_BETWEEN_TICS)
        self.position[servo] = endpos
        sleep(WAIT_BETWEEN_STEPS)


    def deltaServo(self, servo, delta):
        curr = self.position[servo]
        endpos = curr+delta
        print("%d: deltaServo %s by %d to %d" % (self.n, SERVO[servo], delta, endpos))
        self.n += 1
        direction=sign(endpos-curr)
        while curr != endpos:
            curr += direction
            self.pwm.setServo(servo, curr+self.offset[servo])
            sleep(WAIT_BETWEEN_TICS)
        self.position[servo] = endpos
        sleep(WAIT_BETWEEN_STEPS)

