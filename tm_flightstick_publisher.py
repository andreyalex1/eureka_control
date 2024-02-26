#!/usr/bin/env python3
import hid
import time
import threading
import rospy
from geometry_msgs.msg import Twist
#print(hid.enumerate())
#fs = hid.device()
#fs.open(1103, 45320)
#while True:
    #print(fs.read(64))
    #time.sleep(0.1)

class tm_flight_stick:
    def __init__(self): 
        self.roll = 0       #an
        self.pitch = 0      #an
        self.yaw = 0        #an
        self.throttle = 0   #an
        self.jsx = 0        #btn, 3 states
        self.jsy = 0        #btn, 3 states
        self.R1 = 0         #btn
        self.R3 = 0         #btn
        self.L1 = 0         #btn
        self.L3 = 0         #btn
        self.tri = 0        #btn
        self.sq = 0         #btn
        self.circ = 0       #btn
        self.x = 0          #btn
        self.fs = hid.device()
        self.fs.open(1103, 45320)
        self.stop_flag = 0

    def start(self):
        self.thread_1 = threading.Thread(name='background', target=self.read_fs, daemon = True)
        self.thread_1.start()
        print("Thread started!")
        time.sleep(1)
    def stop (self):
        self.stop_flag = 1
    def read_fs(self):
        while (self.stop_flag == 0):
            arr = self.fs.read(64)
            self.roll = (arr[4] * 255 + arr[3]) / (255 * 2) - 1
            self.pitch = -(arr[6] * 255 + arr[5]) / (255 * 2) + 1
            self.yaw = arr[8] / 128 - 1
            self.throttle = abs(1 - arr[7]/255)
           # print(self.roll, self.pitch, self.yaw)
            if(arr[2] == 255): self.jsx = 0; self. jsy = 0
            if(arr[2] == 0): self.jsx = 1; self.jsy = 0
            if(arr[2] == 4): self.jsx = -1; self.jsy = 0
            if(arr[2] == 6): self.jsx = 0; self.jsy = 1
            if(arr[2] == 2): self.jsx = 0; self.jsy = -1
            self.R1 = arr[0] % 2
            arr[0] -=self.R1
            self.L1 = (arr[0] % 4) / 2
            arr[0] -=self.L1 * 2
            self.R3 = (arr[0] % 8) / 4
            arr[0] -=self.R3 * 4
            self.L3 = (arr[0] % 16) / 8
            arr[0] -=self.L3 * 8
            self.sq = (arr[0] % 32) / 16
            arr[0] -=self.sq * 16
            self.x = (arr[0] % 64) / 32
            arr[0] -=self.x * 32
            self.circ = (arr[0] % 128) / 64
            arr[0] -=self.circ * 64
            self.tri = (arr[0] % 256) / 128
         #   print("123")
    def print_fs(self):
        print("roll\t:" + str(self.roll))
        print("pitch\t:" + str(self.pitch))
        print("yaw\t:" + str(self.yaw))
        print("throttle:" + str(self.throttle))
        print("jsx\t:" + str(self.jsx))
        print("jsy\t:" + str(self.jsy))
        print("R1\t:" + str(self.R1))
        print("R3\t:" + str(self.R3))
        print("L1\t:" + str(self.L1))
        print("L3\t:" + str(self.L3))
        print("sq\t:" + str(self.sq))
        print("circ\t:" + str(self.circ))
        print("tri\t:" + str(self.tri))
        print("x\t:" + str(self.x))
        print("----------------------------------")


if (__name__ == "__main__"):
    fs = tm_flight_stick()
    rospy.init_node('FS_Pub')
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1000)
    fs.start()
    while True:
        twist = Twist()
        if (float(fs.throttle > 0)):
           # fs.print_fs()
            twist.linear.x = float(fs.pitch * fs.throttle)
            twist.angular.z = float(fs.roll)
            print(twist)
            pub.publish(twist) 
        time.sleep(0.1)
