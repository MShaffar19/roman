import sys
import numpy as np
import math 
import time
import random
import os
rootdir = os.path.dirname(os.path.dirname(__file__))
os.sys.path.insert(0, rootdir)
from roman.ur import *
from roman.ur.scripts.interface import *

#############################################################
# State and Command unit tests 
#############################################################
def vec_test():
    print(f"Running {__file__}::{vec_test.__name__}()")
    p = Vec(10)
    assert len(p) == 10
    p = Joints(1,2,3,4,5,6)
    assert np.all(p.array == [1,2,3,4,5,6])
    p = Tool(0,1,2,3,4,5)
    assert np.all(p.array == [0, 1,2,3,4,5])
    x = np.zeros(6)
    x[:] = p
    assert np.all(x == p.array)
    p[:] = [1,1,1,2,2,2]
    assert np.all(p.array == [1,1,1,2,2,2])
    p = Joints.fromarray(x, clone=False)
    x[0]=100
    assert np.all(x == p.array)
    p = Tool.fromarray(x, clone=True)
    x[0]=0
    assert x[0] != p[0]
    print("Passed.")

def state_test():
    print(f"Running {__file__}::{state_test.__name__}()")
    s = State()
    assert s.time() == 0
    assert s.cmd_id() == 0
    assert not s.is_contact()
    assert not s.is_moving()
    assert not s.is_goal_reached()
    assert type(s.joint_positions()) is Joints
    assert type(s.joint_speeds()) is Joints
    assert type(s.tool_pose()) is Tool
    assert type(s.tool_speed()) is Tool
    assert type(s.target_joint_positions()) is Joints
    assert type(s.target_joint_speeds()) is Joints
    assert type(s.target_tool_pose()) is Tool
    assert type(s.target_tool_speed()) is Tool
    assert type(s.tool_force()) is Tool
    assert type(s.joint_torques()) is Joints
    assert type(s.tool_acceleration()) is np.ndarray
    assert type(s.sensor_force()) is Tool

    s = State.fromarray(np.arange(UR_STATE_ENTRIES_COUNT))
    assert s.time() == UR_STATE_TIME
    assert s.cmd_id() == UR_STATE_CMD_ID
    assert s.is_contact() #UR_STATE_STATUS
    assert not s.is_moving()
    assert not s.is_goal_reached()
    assert np.all(s.joint_positions().array == np.arange(*UR_STATE_JOINT_POSITIONS))
    assert np.all(s.joint_speeds().array == np.arange(*UR_STATE_JOINT_SPEEDS))
    assert np.all(s.tool_pose().array == np.arange(*UR_STATE_TOOL_POSE))
    assert np.all(s.tool_speed().array == np.arange(*UR_STATE_TOOL_SPEED))
    assert np.all(s.target_joint_positions().array == np.arange(*UR_STATE_TARGET_JOINT_POSITIONS))
    assert np.all(s.target_joint_speeds().array == np.arange(*UR_STATE_TARGET_JOINT_SPEEDS))
    assert np.all(s.target_tool_pose().array == np.arange(*UR_STATE_TARGET_TOOL_POSE))
    assert np.all(s.target_tool_speed().array == np.arange(*UR_STATE_TARGET_TOOL_SPEED))
    assert np.all(s.tool_force().array == np.arange(*UR_STATE_TOOL_FORCE))
    assert np.all(s.joint_torques().array == np.arange(*UR_STATE_JOINT_TORQUES))
    assert np.all(s.tool_acceleration() == np.arange(*UR_STATE_TOOL_ACCELERATION))
    assert np.all(s.sensor_force().array == np.arange(*UR_STATE_SENSOR_FORCE))

    print("Passed.")

def command_test():
    print(f"Running {__file__}::{command_test.__name__}()")
    c = Command()
    assert c.id() == 0
    assert c.kind() == UR_CMD_KIND_MOVE_JOINTS_SPEED
    assert type(c.target_speed()) is Joints
    assert c.max_acceleration() == UR_DEFAULT_ACCELERATION
    assert type(c.force_low_bound()) is Tool
    assert type(c.force_high_bound()) is Tool
    assert c.contact_handling() == 0
    assert type(c.target_position()) is Joints
    assert c.max_speed() == UR_DEFAULT_MAX_SPEED
    assert c.controller() == 0

    c = Command.fromarray(np.arange(UR_CMD_ENTRIES_COUNT))
    assert c.id() == UR_CMD_ID
    assert c.kind() == UR_CMD_KIND
    assert np.all(c.target_speed().array == np.arange(*UR_CMD_MOVE_TARGET_SPEED))
    assert c.max_acceleration() == UR_CMD_MOVE_MAX_ACCELERATION
    assert np.all(c.force_low_bound().array == np.arange(*UR_CMD_MOVE_FORCE_LOW_BOUND))
    assert np.all(c.force_high_bound().array == np.arange(*UR_CMD_MOVE_FORCE_HIGH_BOUND))
    assert c.contact_handling() == UR_CMD_MOVE_CONTACT_HANDLING
    assert np.all(c.target_position().array == np.arange(*UR_CMD_MOVE_TARGET_POSITION))
    assert c.max_speed() == UR_CMD_MOVE_MAX_SPEED
    assert c.controller() == UR_CMD_MOVE_CONTROLLER
    print("Passed.")

#############################################################
# Controller unit tests. 
# These don't actually interact with the arm (sim or real)
#############################################################
class Connection(object):
    """Mock connection"""
    def connect(self):
        pass
    def disconnect(self):
        pass
    def send(self, cmd, state):
        pass

def chain_test():
    """Verify that nothing complains when chaining arm controllers"""
    print(f"Running {__file__}::{chain_test.__name__}()")
    con = Connection()
    arm_ctrl = ArmController(con)
    force_calib_ctrl = EMAForceCalibrator(arm_ctrl)
    touch_ctrl = TouchController(force_calib_ctrl)

    cmd = Command(target_position=Tool(0.1,0.1,0.1,0,0,0), force_low_bound=Tool(-1,-1,-1,-1,-1,-1), force_high_bound=Tool(1,1,1,1,1,1))
    state = State()
    state[:] = touch_ctrl(cmd)
    print("Passed.")

def arm_controller_test():
    """Verifies the lowest level arm controller, without sim or the real arm"""
    print(f"Running {__file__}::{arm_controller_test.__name__}()")
    arm_ctrl = ArmController(Connection())
    cmd = Command(target_position=Tool(1,1,1,0,0,0))
    state = arm_ctrl(cmd)
    assert not state.is_goal_reached()
    cmd = Command(target_position=Tool(0,0,0,0,0,0))
    state = arm_ctrl(cmd)
    assert state.is_goal_reached()

    cmd = Command(target_position=Joints(1,1,1,0,0,0))
    state = arm_ctrl(cmd)
    assert not state.is_goal_reached()
    cmd = Command(target_position=Joints(0,0,0,0,0,0))
    state = arm_ctrl(cmd)
    assert state.is_goal_reached()

    cmd = Command(target_speed=Joints(1,1,1,0,0,0))
    state = arm_ctrl(cmd)
    assert not state.is_goal_reached()
    cmd = Command(target_speed=Joints(0,0,0,0,0,0))
    state = arm_ctrl(cmd)
    assert state.is_goal_reached()
    
    print("Passed.")

def force_calibration_controller_test():
    """Verifies the contact detection controller, without sim or the real arm"""
    print(f"Running {__file__}::{force_calibration_controller_test.__name__}()")
    arm_state = State()
    alpha=0.2
    ctrl = EMAForceCalibrator(lambda cmd: (arm_state), alpha=alpha)
    cmd = Command()
    state = ctrl(cmd)
    assert np.all(ctrl.force_average.array == 0)
    
    arm_state.sensor_force()[:] = [2,2,2,2,2,2]
    cmd = Command()
    state = ctrl(cmd)
    assert np.all(ctrl.force_average.array != 0)
    assert state.sensor_force().allclose(np.array([2,2,2,2,2,2])*(1-alpha), 0.001)

    for i in range(100):
        state = ctrl(cmd)
    assert ctrl.force_average.allclose([2,2,2,2,2,2], 0.001)
    assert state.sensor_force().allclose([0,0,0,0,0,0], 0.001)

    arm_state.sensor_force()[:] = [0,0,0,0,0,0]
    state = ctrl(cmd)
    assert state.sensor_force().allclose(np.array([-2,-2,-2,-2,-2,-2])*(1-alpha), 0.001)

    for i in range(100):
        state = ctrl(cmd)
    assert ctrl.force_average.allclose([0,0,0,0,0,0], 0.001)
    assert state.sensor_force().allclose([0,0,0,0,0,0], 0.001)
   
    print("Passed.")

def touch_controller_test():
    """Verifies the intentional touch controller, without sim or the real arm"""
    print(f"Running {__file__}::{touch_controller_test.__name__}()")
    arm_state = State()
    arm_state[State._STATUS] = State._STATUS_FLAG_GOAL_REACHED
    cmd = Command(target_position=Joints(0,0,0,0,0,0))
    ctrl = TouchController(lambda cmd: (arm_state), validation_count=3)
    state = ctrl(cmd)
    assert not state.is_goal_reached()
    assert state.is_done()

    arm_state[State._STATUS] = State._STATUS_FLAG_CONTACT
    cmd = Command(target_position=Joints(1,1,1,1,1,1))
    state = ctrl(cmd)
    assert not state.is_goal_reached()
    assert not state.is_done()
    state = ctrl(cmd)
    state = ctrl(cmd)
    state = ctrl(cmd)
    assert state.is_goal_reached()
    assert state.is_done()

    print("Passed.")

#############################################################
# Runner
#############################################################
def run():
    vec_test()
    state_test()
    command_test()

    chain_test()
    arm_controller_test()
    force_calibration_controller_test()
    touch_controller_test()
   
if __name__ == '__main__':
    run()
