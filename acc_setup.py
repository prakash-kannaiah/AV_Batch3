import os
import time
import sys
import math

from qvl.qcar2 import QLabsQCar2
from qvl.system import QLabsSystem
from qvl.real_time import QLabsRealTime
#from qvl.person import QLabsPerson
from qvl.basic_shape import QLabsBasicShape
from qvl.qlabs import QuanserInteractiveLabs
from qvl.free_camera import QLabsFreeCamera

#from pal.resources import rtmodels

# environment objects
#import pal.resources.rtmodels as rtmodels

#endregion  

def setup(
        dist=5,
        initialPosition=[3.370, 0, 0],
        initialOrientation=[0, 0, math.pi],
        # s1_location = [-12.5, 0, 0.5],#block position
        s1_rotation = [0,0,0],
        s1_scale = [2,10,10],#size of block
        cam_location = [-5.266, 12.454, 7.928],
        cam_rotation = [0, 0.473, -1.562]        
    ):
    s1_location = [-dist-1, 0, 0.5]

    # Try to connect to Qlabs
    os.system('clear')
    qlabs = QuanserInteractiveLabs()
    # Ensure that QLabs is running on your local machine
    print("Connecting to QLabs...")
    if (not qlabs.open("localhost")):
        print("Unable to connect to QLabs")
        sys.exit()
        return
    print("Connected to QLabs")

    # Delete any previous QCar instances and stop any running spawn models
    qlabs.destroy_all_spawned_actors()
    QLabsRealTime().terminate_all_real_time_models()
    time.sleep(0.5)
    # region: QCar spawn description


    # Spawn a QCar at the given initial pose
    hqcar = QLabsQCar2(qlabs)
    hqcar.spawn_id(
        actorNumber=0,
        location=[x for x in initialPosition],
        rotation=initialOrientation,
        waitForConfirmation=True
    )
    
    # Create a new camera view and attach it to the QCar
    hcamera = QLabsFreeCamera(qlabs)
    hcamera.spawn(cam_location, cam_rotation)
    hcamera.possess()
    #hqcar.possess()
    # endregion

    
    # creates an instance of the person
    shape1 = QLabsBasicShape(qlabs)
    shape1.spawn_id(actorNumber=0, location=s1_location, rotation=s1_rotation, scale=s1_scale, configuration=0, waitForConfirmation=True)
    shape1.set_material_properties(color=[252/255,144/255,3/255], roughness=0.0, metallic=False, waitForConfirmation=True)
    
    
    # Start spawn model
    rtModel = os.path.normpath(os.path.join(os.environ['RTMODELS_DIR'], 'QCar2/QCar2_Workspace_studio'))
    QLabsRealTime().start_real_time_model(rtModel)

    return hqcar

if __name__ == '__main__':
    # XXX Add processing of command line arguments
    d = int(input("Enter distance of block from car (default 5): ") or "5")
    setup(dist=d)
