#!/usr/bin/python
# (c) 2016, Matthias Meier

import gi
#gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GObject

from pwmsysfs import PwmSysFs

SERVO_NAME = ("Middle", "Left", "Right", "Claw")
MIN_ANGLE  = (  0,  60,  40,  60)
MAX_ANGLE  = (180, 165, 180, 180)
INIT_POS = ( 90, 152,  90,  60)
#INIT_POS = ( 90, 90,  90,  25)

class MyArmHandsteuerung(Gtk.Window):

    def __init__(self, channels=xrange(4)):
        self.pwm = PwmSysFs(initpos=INIT_POS, channels=channels)
        self.channels=channels
        
        self.timeoutid = GLib.timeout_add(500, self.standby)

        Gtk.Window.__init__(self, title="Handsteuerung")
        self.set_border_width(10)

        grid = Gtk.Grid(row_spacing=10, column_spacing=10)
        self.add(grid)

        label = []
        self.spin = []
        self.coordinate = Gtk.Label(str(INIT_POS))
        
        for i in channels:
            label.append(0)
            self.spin.append(0)
            label[i] = Gtk.Label("Ch%d - %s:" % (i, SERVO_NAME[i]))
            adj = Gtk.Adjustment(INIT_POS[i], MIN_ANGLE[i], MAX_ANGLE[i], 1, 10, 0)
            self.spin[i] = Gtk.SpinButton()
            self.spin[i].set_adjustment(adj)
            adj.connect("value_changed", self.value_changed, self.spin[i], i)
            grid.attach(label[i], 0,i,1,1)
            grid.attach(self.spin[i], 1,i,1,1)

        grid.attach(Gtk.Label("All channels:"), 0, len(channels),1,1)
        grid.attach(self.coordinate, 1,len(channels),1,1)

        initbutton = Gtk.Button("Back to Init.Pos.")
        grid.attach(initbutton, 1,len(channels)+1,1,1)
        initbutton.connect("button-press-event", self.init_pos)

        self.connect("delete-event", self.quit)
        self.show_all()

    def value_changed(self, widget, spin, chan):
        if self.timeoutid != None:
            GObject.source_remove(self.timeoutid)
        pos = spin.get_value_as_int()
        print('value[%s] = %d' % (chan, pos))
        self.pwm.setServo(chan,pos)
        self.coordinate.set_text(str(map(lambda i: self.spin[i].get_value_as_int(), self.channels)))
        self.timeoutid = GLib.timeout_add(500, self.standby)

    def init_pos(self, wiget, event):
        if event.type == Gdk.EventType._2BUTTON_PRESS:
            self.pwm.reset()
        else:
            for i in xrange(0,len(self.spin)):
                self.spin[i].set_value(INIT_POS[i]-0.1)
                self.spin[i].set_value(INIT_POS[i])

    def on_button_toggled(self, button, name):
        if button.get_active():
            state = "on"
        else:
            state = "off"
        print("Button", name, "was turned", state)

    def quit(self,a,b):
        self.pwm.standby()
        Gtk.main_quit()

    def standby(self):
        self.pwm.standby()
        self.timeoutid = None
        return False


if __name__ == "__main__":
    #win = MyArmHandsteuerung()
    win = MyArmHandsteuerung(channels=xrange(4))
    Gtk.main()
