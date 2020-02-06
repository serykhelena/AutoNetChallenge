#!/usr/bin/env python
import rospy
from std_msgs.msg import UInt8
from nav_msgs.msg import OccupancyGrid
from map_msgs.msg import OccupancyGridUpdate
from geometry_msgs.msg import Polygon
from geometry_msgs.msg import Point
from car_parking.msg import Point2D
from car_parking.msg import Points2D
from car_parking.msg import Polygons
from car_parking.msg import Statuses

NODE_NAME = 'parking_test_pub_sub_node'
POLY_PUB_TOPIC = "/parking_polygones"
STATUS_SUB_TOPIC = "/parking_status"
CMD_TOPIC = "/parking_cmd"

def status_callback(msg):
    rospy.loginfo("I heard statuses with length {}".format(len(msg.statuses)))
    for s in msg.statuses:
        if ord(s) == 0:
            print "NO_INFO ",
        elif ord(s) == 1:
            print "EMPTY ",
        elif ord(s) == 2:
            print "FILLED ",
        elif ord(s) == 3:
            print "OUT_OF_RANGE ",
        elif ord(s) == 4:
            print "BAD_POLYGON ",
        else:
            print "UNKNOWN_STATUS ",
    print("")

rospy.init_node(NODE_NAME)
sub = rospy.Subscriber(STATUS_SUB_TOPIC, Statuses, status_callback, queue_size=10)
pub = rospy.Publisher(POLY_PUB_TOPIC, Polygons, queue_size=10)
rate = rospy.Rate(0.2)
#rospy.spin()

def create_little_squares():
    p1 = Point2D(); p1.x = 0.0; p1.y = 0
    p2 = Point2D(); p2.x = 0.0; p2.y = 0.5
    p3 = Point2D(); p3.x = 0.5; p3.y = 0.5
    p4 = Point2D(); p4.x = 0.5; p4.y = 0
    poly1 = Points2D()
    poly1.points = tuple((p1, p2, p3, p4))

    p1 = Point2D(); p1.x = 1.0; p1.y = 0
    p2 = Point2D(); p2.x = 1.0; p2.y = 0.5
    p3 = Point2D(); p3.x = 1.5; p3.y = 0.5
    p4 = Point2D(); p4.x = 1.5; p4.y = 0
    poly2 = Points2D()
    poly2.points = tuple((p1, p2, p3, p4))

    p1 = Point2D(); p1.x = 2.0; p1.y = 0.5
    p2 = Point2D(); p2.x = 2.0; p2.y = 0.9
    p3 = Point2D(); p3.x = 2.5; p3.y = 0.9
    p4 = Point2D(); p4.x = 2.5; p4.y = 0.5
    poly3 = Points2D()
    poly3.points = tuple((p1, p2, p3, p4))

    p1 = Point2D(); p1.x = 2.0; p1.y = -0.5
    p2 = Point2D(); p2.x = 2.0; p2.y = -0.9
    p3 = Point2D(); p3.x = 2.5; p3.y = -0.9
    p4 = Point2D(); p4.x = 2.5; p4.y = -0.5
    poly4 = Points2D()
    poly4.points = tuple((p1, p2, p3, p4))

    polygons = Polygons()
    polygons.polygons = tuple((poly1, poly2, poly3, poly4))

    return polygons 

def create_squares():
    p1 = Point2D(); p1.x = 0.5; p1.y = 0
    p2 = Point2D(); p2.x = 0.5; p2.y = -2
    p3 = Point2D(); p3.x = 2.5; p3.y = -2
    p4 = Point2D(); p4.x = 2.5; p4.y = 0
    poly1 = Points2D()
    poly1.points = tuple((p1, p2, p3, p4))

    p1 = Point2D(); p1.x = -0.5; p1.y = 0
    p2 = Point2D(); p2.x = -2.5; p2.y = 2
    p3 = Point2D(); p3.x = -2.5; p3.y = 2
    p4 = Point2D(); p4.x = -0.5; p4.y = 0
    poly2 = Points2D()
    poly2.points = tuple((p1, p2, p3, p4))

    p1 = Point2D(); p1.x = 0.5; p1.y = 0
    p2 = Point2D(); p2.x = 0.5; p2.y = 2
    p3 = Point2D(); p3.x = 2.5; p3.y = 2
    p4 = Point2D(); p4.x = 2.5; p4.y = 0
    poly3 = Points2D()
    poly3.points = tuple((p1, p2, p3, p4))

    polygons = Polygons()
    polygons.polygons = tuple((poly1, poly2, poly3))

    return polygons

def create_big_square():
    p1 = Point2D(); p1.x = -3; p1.y = -3
    p2 = Point2D(); p2.x = -3; p2.y = +3
    p3 = Point2D(); p3.x = +3; p3.y = +3
    p4 = Point2D(); p4.x = +3; p4.y = -3
    poly1 = Points2D()
    poly1.points = tuple((p1, p2, p3, p4))

    p1 = Point2D(); p1.x = 0; p1.y = 0
    p2 = Point2D(); p2.x = 0; p2.y = 0
    p3 = Point2D(); p3.x = 0; p3.y = 0
    p4 = Point2D(); p4.x = 0; p4.y = 0
    poly2 = Points2D()
    poly2.points = tuple((p1, p2, p3, p4))
    polygons = Polygons()
    polygons.polygons = tuple((poly1, poly2))

    return polygons

def create_trapezoid():
    p1 = Point2D(); p1.x = 0.5; p1.y = 0
    p2 = Point2D(); p2.x = 2.5; p2.y = 2
    p3 = Point2D(); p3.x = 2.5; p3.y = 4
    p4 = Point2D(); p4.x = 0.5; p4.y = 2
    poly1 = Points2D()
    poly1.points = tuple((p1, p2, p3, p4))

    p1 = Point2D(); p1.x = 0.5; p1.y = 2
    p2 = Point2D(); p2.x = 2.5; p2.y = 4
    p3 = Point2D(); p3.x = 2.5; p3.y = 6
    p4 = Point2D(); p4.x = 0.5; p4.y = 4
    poly2 = Points2D()
    poly2.points = tuple((p1, p2, p3, p4))

    p1 = Point2D(); p1.x = 0.5; p1.y = 4
    p2 = Point2D(); p2.x = 2.5; p2.y = 6
    p3 = Point2D(); p3.x = 2.5; p3.y = 8
    p4 = Point2D(); p4.x = 0.5; p4.y = 6
    poly3 = Points2D()
    poly3.points = tuple((p1, p2, p3, p4))

    polygons = Polygons()
    polygons.polygons = tuple((poly1, poly2, poly3))

    return polygons

def talker():
    #polygons = create_squares()
    #polygons = create_trapezoid()
    polygons = create_little_squares()
    #polygons = create_big_square()
    while not rospy.is_shutdown():
        rospy.loginfo("I published poly.")
        pub.publish(polygons)
        #rospy.spin()
        rate.sleep()

try:
    talker()
except (rospy.ROSInterruptException, KeyboardInterrupt):
    rospy.logerr('Exception catched')