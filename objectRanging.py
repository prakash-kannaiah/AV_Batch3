
import cv2
import numpy as np
import time
from pal.products.qcar import QCarRealSense, QCar


#------------- functions -------------
def acquire_images(myCam):
    myCam.read_RGB()
    rgb = myCam.imageBufferRGB
    myCam.read_depth()
    depth = myCam.imageBufferDepthPX
    return rgb, depth

def ranging(depth):
    if depth is None:
        return None, None
    d = np.squeeze(depth)
    h, w = d.shape
    #uy, ly = h // 3, (2 * h) // 3
    uy, ly = 261, 262
    lx, rx = w // 3, (2 * w) // 3
    crop = d[uy:ly, lx:rx]
    obj_dis = np.min(crop)
    return crop, obj_dis

#------------- main -------------
myCam = QCarRealSense(mode='RGB, Depth')
myCar = QCar(readMode=1, frequency=10)

try:
    while True:
        rgb, depth = acquire_images(myCam)
        roi, obj_dis = ranging(depth)

        print("distane:", obj_dis)
        time.sleep(0.1)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


except KeyboardInterrupt:
    print("\nProgram stopped by user (CTRL+C).")

cv2.destroyAllWindows()
