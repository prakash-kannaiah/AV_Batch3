import os
import time
import sys
import math
import keyboard

from qvl.qcar2 import QLabsQCar2
from qvl.system import QLabsSystem
from qvl.real_time import QLabsRealTime
from qvl.basic_shape import QLabsBasicShape
from qvl.qlabs import QuanserInteractiveLabs
from qvl.free_camera import QLabsFreeCamera

def setup(
        initialPosition=[1, 2, 0],      
        initialOrientation=[0, 0, 0],   
        s1_location = [12.7, 2, 1.5],   
        s1_rotation = [0,0,0],
        s1_scale = [3,3,3],             
        cam_location = [-5.266, 12.454, 7.928],
        cam_rotation = [0, 0.473, -1.562]        
    ):

    os.system('clear' if os.name == 'posix' else 'cls')
    qlabs = QuanserInteractiveLabs()
    
    print("Connecting to QLabs...")
    if (not qlabs.open("localhost")):
        print("Unable to connect to QLabs")
        sys.exit()
    print("Connected to QLabs")

    qlabs.destroy_all_spawned_actors()
    QLabsRealTime().terminate_all_real_time_models()
    time.sleep(0.5)

    hqcar = QLabsQCar2(qlabs)
    hqcar.spawn_id(
        actorNumber=0,
        location=initialPosition,
        rotation=initialOrientation,
        waitForConfirmation=True
    )
    
    hcamera = QLabsFreeCamera(qlabs)
    hcamera.spawn(cam_location, cam_rotation)
    hcamera.possess()

    shape1 = QLabsBasicShape(qlabs)
    shape1.spawn_id(actorNumber=0, location=s1_location, rotation=s1_rotation, scale=s1_scale, configuration=0, waitForConfirmation=True)
    shape1.set_material_properties(color=[255/255,0/255,0/255], roughness=0.0, metallic=True, waitForConfirmation=True)
    
    return hqcar

def manual_control(hqcar):
    print("Control active. Use Arrow Keys to drive. Press 'ESC' to terminate.")
    
    speed = 2.0 
    turn_angle = math.pi / 6 
    
    while True:
        forward_cmd = 0.0
        turn_cmd = 0.0

        if keyboard.is_pressed('up'):
            forward_cmd = speed
        elif keyboard.is_pressed('down'):
            forward_cmd = -speed

        if keyboard.is_pressed('right'):
            turn_cmd = turn_angle
        elif keyboard.is_pressed('left'):
            turn_cmd = -turn_angle

        if keyboard.is_pressed('esc'):
            hqcar.set_velocity_and_request_state(0, 0, False, False, False, False, False)
            break

        hqcar.set_velocity_and_request_state(
            forward=forward_cmd, 
            turn=turn_cmd, 
            headlights=False, 
            leftTurnSignal=False, 
            rightTurnSignal=False, 
            brakeSignal=False, 
            reverseSignal=False
        )
        
        time.sleep(0.05) 

if __name__ == '__main__':
    car = setup()
    manual_control(car)
