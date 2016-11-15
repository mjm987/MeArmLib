#!/usr/bin/python

# set PWM via SysFs and i2c PWM-chip PCA9685a
# (c) 2016, Matthias Meier

# Prerequisites:
#
# * Connect PWM chip PCA9685 with I2C addr 0x40 (e.g. FeatherWing 8ch PWM board) to the Raspi
#    --> connect it on Raspi to GPIO connector: Pin3=SDA0, Pin5=SCL0, Pin6=GND, (Pin1:3.3V)
#
# * Uses Raspberry Pi device tree (overlay) for this PWM chip
#    --> will be added automatically on first run by appending '/boot/config.txt' by line 'dtoverlay=i2c-pwm-pca9685a'
#    -->  if it does not work after reboot, if this dtoverlay was loaded by 'vcdbg log msg'
#
# * the kernel module 'pwm-pca9685' should be loaded automatically when the dtoverlay is loaded
#
# Remarks:
# - PWM time at SysFs is in nanoseconds
# - Standard analog servo parameters are: period=20ms (50Hz), 0 degree = 544us, 180 degree = 2.4ms (see default init-parameters)

import os
import sys

class PwmSysFs(object):
    def __init__(self, channels=xrange(4), period=20000000, initpos=None, servomap=(0, 180, 544000, 2400000), pwmchip='pwmchip0' ):
        self.channels = channels
        self.period = period
        self.initpos = initpos
        self.pwmchip = '/sys/class/pwm/' + pwmchip
        self.servoM = (servomap[3]-servomap[2]) / (servomap[1]-servomap[0])
        self.servoB = servomap[2]-servomap[0]*self.servoM
        # if sysfs path not exisiting try first to load kernel module module and if this is unsuccessful add dto to /boot/config.txt
        if not os.path.isdir(self.pwmchip):
            os.system('sudo modprobe pwm-pca9685')
            if not os.path.isdir(self.pwmchip):
                print("DTO entry added in '/boot/config.txt'. Please reboot and try again!")
                os.system('sudo /bin/sh -c \'if [ -e /boot/config.txt -a -z "`egrep ^dtoverlay=i2c-pwm-pca9685a /boot/config.txt`" ]; then echo "dtoverlay=i2c-pwm-pca9685a" >>/boot/config.txt; sync; fi \'')
                os._exit(1)
        if channels != None:
            for ch in channels:
                self.export(ch, period, initpos)

    def reset(self):
        if self.channels != None:
            for ch in self.channels:
                os.system("sudo /bin/sh -c 'echo {0} | tee {1}/unexport'".format(ch, self.pwmchip))
        if self.channels != None:
            os.system('sudo modprobe -r pwm-pca9685; sudo modprobe pwm-pca9685')
        if self.channels != None:
            for ch in self.channels:
                self.export(ch, self.period, self.initpos)

    def fileWrite(self, filename, data):
        f = open(filename,"a")
        f.write(data)
        f.close()
        
    def export(self, chan, period=None, initpos=None):
        # after exporting the pwm channel change its permissions by 'sudo chown' so we have access to the pwm entries without sudo (same does not work by UDEV rule)
        path = '{1}/pwm{0}'.format(chan, self.pwmchip)
        if not (os.path.isdir(path) and os.stat(path).st_uid==os.geteuid()):
            os.system("sudo /bin/sh -c 'echo {0} | tee {1}/export ; sleep 0.5; chown -R {2} {1}/pwm{0}'".format(chan, self.pwmchip, os.geteuid()))
        self.fileWrite(path + '/enable', '1')
        if period != None:
            self.setPeriod(chan, period)     # 50Hz --> 20ms --> 20000000ns
        if initpos != None:
            self.setServo(chan, initpos[chan])      

    def setPeriod(self, chan, val):
        self.fileWrite("{0}/pwm{1}/period".format(self.pwmchip, chan), str(val))

    def setPw(self, chan, val):
        self.fileWrite("{0}/pwm{1}/duty_cycle".format(self.pwmchip, chan), str(val))

    def setServo(self, chan, setangle):
        self.setPw(chan, self.servoB + setangle * self.servoM)

    def standby(self):
        print("Set channels to standby")
        for i in self.channels:
            self.setPw(i,0)
        

if __name__ == '__main__':
    from time import sleep
    SERVO_NAME = ("Middle", "Left", "Right", "Claw", "Test")
    INIT_POS = (90, 152,  90,  60, 90)
    pwm = PwmSysFs(channels=xrange(5))
    for chan in xrange(len(INIT_POS)):
        print("Set pwm%d (%s) to %d deg" % (chan, SERVO_NAME[chan], INIT_POS[chan]))
        pwm.setServo(chan, INIT_POS[chan]-30)
        sleep(0.25)
        pwm.setServo(chan, INIT_POS[chan]+30)
        sleep(0.25)
        pwm.setServo(chan, INIT_POS[chan])
        sleep(0.5)
    pwm.standby()
