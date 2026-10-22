from robotclient import RobotClient

robot = RobotClient()
robot.connect("192.168.0.84")
robot.enable(wait=True)
robot.home(wait=True)
robot.enter_exec_mode(wait=True)
robot.move_joints(0, -60, 60, 0, 0, 0, speed=0.2)
robot.wait_motion_complete()
