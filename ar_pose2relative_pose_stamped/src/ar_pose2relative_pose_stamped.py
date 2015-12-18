#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from nityc.msg import RelativePoseStamped
from ar_pose.msg import ARMarker, ARMarkers

# for test
# from kaken_msg.msg import ARMarker, ARMarkers, RelativePoseStamped

REMAPPABLE_DEFAULT_NODE_NAME = 'ar_pose2relative_pose_stamped'
REMAPPABLE_RELATIVEPOSESTAMPED_TOPIC = 'position_topic'
REMAPPABLE_ARMARKER_TOPIC = 'ar_pose_marker_topic'

PARAM_NAME_LOOP_RATE = '~loop_rate_hz'
PARAM_NAME_TARGET_ID_FRONT = '~ar_marker_target_id_front'
PARAM_NAME_TARGET_ID_LEFT = '~ar_marker_target_id_left'
PARAM_NAME_TARGET_ID_RIGHT = '~ar_marker_target_id_right'
PARAM_NAME_TARGET_ID_BACK = '~ar_marker_target_id_back'
PARAM_NAME_TARGET_NAME = '~relative_pose_stamped_target_name'


class ARPose2RelativePoseStamped(object):
    def __init__(self):
        target_name = rospy.get_param(PARAM_NAME_TARGET_NAME)
        self._ar_pose_id2name = {
            rospy.get_param(PARAM_NAME_TARGET_ID_FRONT): target_name + '_Front',
            rospy.get_param(PARAM_NAME_TARGET_ID_LEFT): target_name + '_Left',
            rospy.get_param(PARAM_NAME_TARGET_ID_RIGHT): target_name + '_Right',
            rospy.get_param(PARAM_NAME_TARGET_ID_BACK): target_name + '_Back'
        }
        self._sub = rospy.Subscriber(REMAPPABLE_ARMARKER_TOPIC,
                                     ARMarkers,
                                     self._callback)
        self._pub = rospy.Publisher(REMAPPABLE_RELATIVEPOSESTAMPED_TOPIC,
                                    RelativePoseStamped,
                                    queue_size=5)
        self._relative_pose_stamped = RelativePoseStamped()

    def activate(self):
        self._relative_pose_stamped.header.stamp = rospy.Time.now()
        self._relative_pose_stamped.pose.orientation.w = 1.0
        return self

    def _callback(self, ar_markers):
        for marker in ar_markers.markers:
            if marker.id in self._ar_pose_id2name:
                self._relative_pose_stamped.target = self._ar_pose_id2name[marker.id]
                self._relative_pose_stamped.pose.position.x = marker.pose.pose.position.x
                self._relative_pose_stamped.pose.position.y = marker.pose.pose.position.y
                self._relative_pose_stamped.pose.position.z = marker.pose.pose.position.z


    def publish_data(self):
        self._relative_pose_stamped.header.stamp = rospy.Time.now()
        self._pub.publish(self._relative_pose_stamped)


# --------------------------------------------
if __name__ == '__main__':
    rospy.init_node(REMAPPABLE_DEFAULT_NODE_NAME, anonymous=True)
    rate_mgr = rospy.Rate(rospy.get_param(PARAM_NAME_LOOP_RATE,
                                          default=100))  # Hz

    ar_pose2relative_pose_stamped = ARPose2RelativePoseStamped().activate()

    while not rospy.is_shutdown():
        ar_pose2relative_pose_stamped.publish_data()
        rate_mgr.sleep()
