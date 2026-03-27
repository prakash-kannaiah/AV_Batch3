import keyboard
import time
import numpy as np
from pal.products.qcar import QCar, QCarRealSense

# -------- INIT --------
myCar = QCar(readMode=1, frequency=20)
myCam = QCarRealSense(mode='Depth')

BASE_SPEED = 0.35

STOP_DISTANCE = 25
SAFE_DISTANCE = 40

avoid_mode = None
avoid_timer = 0

print("SMART AVOIDANCE + MANUAL CONTROL 🚗")
print("Arrow Keys → Drive | CTRL+C → Quit")

try:
    while True:

        throttle = 0.0
        steering = 0.0

        # -------- DEPTH --------
        myCam.read_depth()
        depth_img = myCam.imageBufferDepthPX

        if len(depth_img.shape) == 3:
            depth_img = depth_img[:, :, 0]

        h, w = depth_img.shape

        left_region   = depth_img[h//2-20:h//2+20, w//4-20:w//4+20]
        center_region = depth_img[h//2-20:h//2+20, w//2-20:w//2+20]
        right_region  = depth_img[h//2-20:h//2+20, 3*w//4-20:3*w//4+20]

        left_depth   = float(np.mean(left_region))
        center_depth = float(np.mean(center_region))
        right_depth  = float(np.mean(right_region))

        # -------- MANUAL INPUT --------
        if keyboard.is_pressed('up'):
            throttle = BASE_SPEED

        if keyboard.is_pressed('down'):
            throttle = -BASE_SPEED

        # Manual steering (only if NOT auto avoiding)
        manual_steering = 0.0
        if keyboard.is_pressed('left'):
            manual_steering = 0.4

        if keyboard.is_pressed('right'):
            manual_steering = -0.4

        # -------- AUTO AVOIDANCE --------
        if throttle > 0:  # only when moving forward

            if avoid_mode == "left":
                steering = 0.6
                throttle = BASE_SPEED * 0.6
                avoid_timer += 1

                if center_depth > SAFE_DISTANCE and left_depth > SAFE_DISTANCE:
                    avoid_mode = "straight"
                    avoid_timer = 0

            elif avoid_mode == "right":
                steering = -0.6
                throttle = BASE_SPEED * 0.6
                avoid_timer += 1

                if center_depth > SAFE_DISTANCE and right_depth > SAFE_DISTANCE:
                    avoid_mode = "straight"
                    avoid_timer = 0

            elif avoid_mode == "straight":
                steering = 0.0
                throttle = BASE_SPEED * 0.6
                avoid_timer += 1

                if avoid_timer > 10:
                    avoid_mode = None
                    avoid_timer = 0

            else:
                # NORMAL MODE
                if center_depth <= STOP_DISTANCE:

                    if left_depth > right_depth:
                        avoid_mode = "left"
                        print("↖️ AUTO LEFT")

                    else:
                        avoid_mode = "right"
                        print("↗️ AUTO RIGHT")

                elif center_depth <= SAFE_DISTANCE:
                    throttle = BASE_SPEED * 0.5
                    steering = manual_steering  # allow manual steering
                    print("⚠️ SLOW")

                else:
                    steering = manual_steering  # normal driving

        else:
            # If not moving forward → manual control only
            steering = manual_steering
            avoid_mode = None
            avoid_timer = 0

        # -------- SEND --------
        myCar.write(throttle, steering)
        myCar.read()

        print(
            f"L:{left_depth:.1f} C:{center_depth:.1f} R:{right_depth:.1f} | "
            f"Mode:{avoid_mode} | T:{throttle:.2f} S:{steering:.2f}"
        )

        time.sleep(0.02)

except KeyboardInterrupt:
    print("Stopped")

finally:
    myCar.write(0, 0)
