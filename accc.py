import time
import numpy as np
from pal.products.qcar import QCar, QCarRealSense

# -------- INIT --------
myCar = QCar(readMode=1, frequency=20)
myCam = QCarRealSense(mode='Depth')

# -------- USER INPUT --------
TARGET_SPEED = float(input("Enter cruise speed (0.1 to 0.5 recommended): "))

# -------- PARAMETERS --------
STOP_DISTANCE = 40
SLOW_DISTANCE = 60

MAX_ACCEL = 0.02
MAX_DECEL = 0.05

FILTER_ALPHA = 0.7

# -------- STATE --------
current_speed = 0.0
filtered_depth = 255.0   # start as FAR (safe)

print("🚗 ADAPTIVE CRUISE CONTROL ACTIVE")
print(f"Target Speed: {TARGET_SPEED}")

try:
    while True:

        steering = 0.0

        # -------- READ DEPTH --------
        myCam.read_depth()
        depth_img = myCam.imageBufferDepthPX

        if len(depth_img.shape) == 3:
            depth_img = depth_img[:, :, 0]

        h, w = depth_img.shape

        center_region = depth_img[h//2-10:h//2+10, w//2-10:w//2+10]

        # -------- FIX DEPTH ISSUE --------
        # Replace invalid 0 values with FAR (255)
        valid_pixels = center_region.copy()
        valid_pixels[valid_pixels == 0] = 255

        raw_depth = float(np.mean(valid_pixels))

        # -------- FILTER --------
        filtered_depth = (FILTER_ALPHA * filtered_depth +
                          (1 - FILTER_ALPHA) * raw_depth)

        # -------- ADAS LOGIC --------
        if filtered_depth <= STOP_DISTANCE:
            desired_speed = 0.0
            status = "🚨 STOP"

        elif filtered_depth <= SLOW_DISTANCE:
            ratio = ((filtered_depth - STOP_DISTANCE) /
                     (SLOW_DISTANCE - STOP_DISTANCE))
            desired_speed = TARGET_SPEED * ratio
            status = "⚠️ SLOW"

        else:
            desired_speed = TARGET_SPEED
            status = "✅ CRUISE"

        # -------- SMOOTH CONTROL --------
        if current_speed < desired_speed:
            current_speed += MAX_ACCEL
            current_speed = min(current_speed, desired_speed)

        elif current_speed > desired_speed:
            current_speed -= MAX_DECEL
            current_speed = max(current_speed, desired_speed)

        # -------- SEND --------
        myCar.write(current_speed, steering)
        myCar.read()

        print(
            f"Raw Depth: {raw_depth:.2f} | "
            f"Filtered: {filtered_depth:.2f} | "
            f"Speed: {current_speed:.2f} | "
            f"{status}"
        )

        time.sleep(0.02)

except KeyboardInterrupt:
    print("🛑 Stopped by user")

finally:
    myCar.write(0, 0)
