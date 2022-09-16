#!/usr/bin/env python3
# -*- coding: utf-8 -*-

ROS_INTEGRATION = False

if ROS_INTEGRATION:
    import rospy
    from nav_msgs.msg import Odometry
    from std_msgs.msg import Bool

import os, sys
import matplotlib.pyplot as plt

import glob
import time
import os
from natsort import natsorted
from haversine import haversine
import xml.etree.ElementTree as et

from ott_utils.common import get_last_line
from ott_utils.point_increment import point_increment
from ott_utils.log import WKLogger
from ott_utils.osm_to_txt import osm_to_txt
from ott_utils.txt_to_osm import txt_to_osm
import sys

utm_x, utm_y = 0.0, 0.0
start, finish = False, False
cx, cy = [], []
close = False

pub = rospy.Publisher("/Local/close", Bool, queue_size=1)

narrow_map_path = '/home/' + os.getlogin() + '/catkin_ws/src/txt_saver/narrow map/1.txt'

fw = open(narrow_map_path, 'w')
fr = open(narrow_map_path, 'r')


def start_cb(msg):
    global start
    start = msg.data


def finish_cb(msg):
    global end
    end = msg.data


def odom_cb(msg):
    global start, end
    global utm_x, utm_y
    global fw
    global close
    utm_x = msg.pose.pose.position.x
    utm_y = msg.pose.pose.position.y
    print(start, end)

    if start and not end:  # first lap start
        rospy.loginfo("writing x,y for UTM")
        fw.write(str(utm_x))
        fw.write(',')
        fw.write(str(utm_y))
        fw.write('\n')
        pub.publish(close)

    elif start and end:  # first lap end
        rospy.loginfo("stop writing")
        fw.close()

        if pi_manager():
            close = True
            pub.publish(close)


def plotter():
    cx, cy = [], []
    while True:
        line = fr.readline()
        if not line:
            break
        if line.find('\n'):
            line = line[:line.find('\n')]
            cxy = (line.split(','))

        cx.append(float(cxy[0]))
        cy.append(float(cxy[1]))
    fr.close()

    plt.plot(cx, cy, ".r")

    plt.xlabel('x')
    plt.ylabel('y')
    plt.axis("equal")
    plt.grid(True)

    # plt.savefig('/home/'+os.getlogin()+'/catkin_ws/src/txt_saver/map_narrow/'+string+'.png',dpi=300)
    plt.show()


def pi_manager():
    # 미리 말씀드리는데, 이 코드는 사상누각입니다...!
    # 더 나은 방법이 머리속에 떠올랐지만, 돌이키기에는 너무 먼 길을 돌아왔기에 그냥 쓰는 것 뿐입니다.

    # osm 파일을 받아서 점 개수만 늘려줍니다.
    # 일단 파이썬 기본 recursion limit을 1000--->10000으로 조정합니다. recursion issue 발생할경우 다시 조정하세요.
    print(sys.setrecursionlimit(10000))

    input_dir = '/home/kroad/catkin_ws/src/kbub_planning_pkg/src/map'
    output_dir = '/home/kroad/catkin_ws/src/kbub_planning_pkg/src/map'

    source = glob.glob(input_dir + '/100.txt')
    # source = natsorted(source)
    get_filename = lambda n: n.split('/')[-1].replace('.osm', '').replace('.txt', '')

    for i, f in enumerate(source):
        point_increment(
            src_path=f,
            # src_array=utm_arr,
            path_smooth=False,
            dst=output_dir,
            save=True,
            diagnostic=True,
            node_interval=0.05,
            filename=get_filename(f))
        print('point_increment : {} / {} done. '.format(i + 1, len(source)))


def main():
    while not rospy.is_shutdown():
        rospy.init_node('kbub-local-narrow-gen-optimizer', anonymous=True)
        rospy.Subscriber("/odom", Odometry, odom_cb)
        rospy.Subscriber("/Local/start", Bool, start_cb)
        rospy.Subscriber("/Local/finish", Bool, finish_cb)
        rospy.spin()
    plotter()
    rospy.loginfo("Successfully exits")


if __name__ == '__main__':
    main()
