#!/usr/bin/env python3

import rospy
import math
import tf2_ros
from geometry_msgs.msg import Twist, PointStamped
from ur5e_control.msg import Plan
import tf2_geometry_msgs
from robot_vision_lectures.msg import SphereParams
from std_msgs.msg import UInt8, Bool

tool_twist = Twist()
can_move = False
plan_printed = False
params_received = False
ball_position = PointStamped()

def calculate_distance():
    try:
        # Get the transform from the camera frame to the base frame
        trans = tf_buffer.lookup_transform("camera_color_optical_frame", "base", rospy.Time())
        
        # Extract the translation components (x, y, z)
        distance_x = trans.transform.translation.x
        distance_y = trans.transform.translation.y
        distance_z = trans.transform.translation.z
        
        return distance_x, distance_y, distance_z

    except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
        rospy.logerr("Failed to get transform from 'camera_color_optical_frame' to 'base'")
        return None, None, None

def sphere_callback(data):
    global ball_position
    global params_received
    ball_position.header.stamp = rospy.Time()
    ball_position.header.frame_id = "camera_color_optical_frame"  # Assuming the ball position is in the camera frame
    ball_position.point.x = data.xc
    ball_position.point.y = data.yc
    ball_position.point.z = data.zc
    #rospy.loginfo("Ball position: x=%f, y=%f, z=%f", ball_position.point.x, ball_position.point.y, ball_position.point.z)
    params_received = True

def toolpose_callback(data):
	global tool_twist
	tool_twist = data

def moveCallback(data):
	global can_move
	can_move = data.data


if __name__ == '__main__':
	rospy.init_node('planner_with_distance_and_ball', anonymous=True)
	plan_pub = rospy.Publisher('/plan', Plan, queue_size=10)
	tf_buffer = tf2_ros.Buffer()
	listener = tf2_ros.TransformListener(tf_buffer)
	tf_broadcaster = tf2_ros.TransformBroadcaster()
	sphere_sub = rospy.Subscriber('/sphere_params', SphereParams, sphere_callback)
	toolpose_sub = rospy.Subscriber('/ur5e/toolpose', Twist, toolpose_callback)

	move_sub = rospy.Subscriber('/move_robot', Bool, moveCallback)

	rate = rospy.Rate(10)  # 10 Hz
	plan = Plan()

	while not rospy.is_shutdown():
		distance_x, distance_y, distance_z = calculate_distance()
		#if distance_x is not None and distance_y is not None and distance_z is not None:
			#rospy.loginfo("Distance from camera to base: x=%f, y=%f, z=%f ", distance_x, distance_y, distance_z)

		# Check if ball position is available
		#if 'ball_position' in globals():
		if params_received:
			try:
				# Transform the ball position from camera frame to base frame
				trans = tf_buffer.lookup_transform("base", "camera_color_optical_frame", rospy.Time())
				ball_position_base = tf2_geometry_msgs.do_transform_point(ball_position, trans)
				ball_x_base = ball_position_base.point.x
				ball_y_base = ball_position_base.point.y
				ball_z_base = ball_position_base.point.z

				#rospy.loginfo("Ball position relative to base: x=%f, y=%f, z=%f", ball_x_base, ball_y_base, ball_z_base)

				# Point 1
				plan_point1 = Twist()
				point_mode = UInt8()
				plan_point1.linear.x = tool_twist.linear.x
				plan_point1.linear.y = tool_twist.linear.y
				plan_point1.linear.z = tool_twist.linear.z
				plan_point1.angular.x = tool_twist.angular.x
				plan_point1.angular.y = tool_twist.angular.y
				plan_point1.angular.z = tool_twist.angular.z
				point_mode.data = 0
				plan.points.append(plan_point1)
				plan.modes.append(point_mode)

				# Add the transformed ball position as point 2
				plan_point2 = Twist()
				point_mode = UInt8()
				plan_point2.linear.x = ball_x_base
				plan_point2.linear.y = ball_y_base
				plan_point2.linear.z = tool_twist.linear.z
				plan_point2.angular.x = tool_twist.angular.x
				plan_point2.angular.y = tool_twist.angular.y
				plan_point2.angular.z = tool_twist.angular.z
				point_mode.data = 0
				plan.points.append(plan_point2)
				plan.modes.append(point_mode)

				# Add the transformed ball position as point 3
				plan_point3 = Twist()
				point_mode = UInt8()
				plan_point3.linear.x = ball_x_base
				plan_point3.linear.y = ball_y_base
				plan_point3.linear.z = ball_z_base+0.01
				plan_point3.angular.x = tool_twist.angular.x
				plan_point3.angular.y = tool_twist.angular.y
				plan_point3.angular.z = tool_twist.angular.z
				point_mode.data = 0
				plan.points.append(plan_point3)
				plan.modes.append(point_mode)

				# Add the transformed ball position as point 4
				plan_point4 = Twist()
				point_mode = UInt8()
				plan_point4.linear.x = ball_x_base
				plan_point4.linear.y = ball_y_base
				plan_point4.linear.z = ball_z_base+0.01
				plan_point4.angular.x = tool_twist.angular.x
				plan_point4.angular.y = tool_twist.angular.y
				plan_point4.angular.z = tool_twist.angular.z
				point_mode.data = 2
				plan.points.append(plan_point4)
				plan.modes.append(point_mode)


				# Point 5
				plan_point5 = Twist()
				point_mode = UInt8()
				plan_point5.linear.x = ball_x_base + 0.08
				plan_point5.linear.y = ball_y_base - 0.03
				plan_point5.linear.z = tool_twist.linear.z
				plan_point5.angular.x = tool_twist.angular.x
				plan_point5.angular.y = tool_twist.angular.y
				plan_point5.angular.z = tool_twist.angular.z
				point_mode.data = 0
				plan.points.append(plan_point5)
				plan.modes.append(point_mode)

				# Point 6
				plan_point6 = Twist()
				point_mode = UInt8()
				plan_point6.linear.x = ball_x_base + 0.08
				plan_point6.linear.y = ball_y_base - 0.03
				plan_point6.linear.z = ball_z_base+0.01
				plan_point6.angular.x = tool_twist.angular.x
				plan_point6.angular.y = tool_twist.angular.y
				plan_point6.angular.z = tool_twist.angular.z
				point_mode.data = 0
				plan.points.append(plan_point6)
				plan.modes.append(point_mode)

				#Point 7
				plan_point7 = Twist()
				point_mode = UInt8()
				plan_point7.linear.x = ball_x_base + 0.08
				plan_point7.linear.y = ball_y_base - 0.03
				plan_point7.linear.z = ball_z_base+0.01
				plan_point7.angular.x = tool_twist.angular.x
				plan_point7.angular.y = tool_twist.angular.y
				plan_point7.angular.z = tool_twist.angular.z
				point_mode.data = 1
				plan.points.append(plan_point7)
				plan.modes.append(point_mode)
				

				if can_move:
					# Publish the plan
					plan_pub.publish(plan)
				else:
					if not plan_printed:
						print(plan)
						plan_printed = True

			except tf2_ros.TransformException as e:
				rospy.logerr("Failed to transform ball position to base frame: %s", e)

		rate.sleep()
