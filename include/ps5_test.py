import serial
import time
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

PORT = 'COM5'
BAUD_RATE = 115200

# Ignore tiny analog movements near center
DEADZONE = 0.12

def apply_deadzone(value, deadzone):
    """Filters out stick drift and re-scales input from 0.0 to 1.0."""
    if abs(value) < deadzone:
        return 0.0
    
    # Preserve sign while scaling the remaining range smoothly
    sign = 1.0 if value > 0 else -1.0
    return sign * ((abs(value) - deadzone) / (1.0 - deadzone))

def main():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("Error: No controller detected!")
        return

    controller = pygame.joystick.Joystick(0)
    controller.init()
    print(f"Connected Controller: {controller.get_name()}")

    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        print(f"Serial stream open on {PORT}.")
        print("Move Left Analog Stick to adjust pan/tilt speed. Press PS/Options to exit.")

        running = True
        last_sent_p = 0.0
        last_sent_t = 0.0

        while running:
            pygame.event.pump()

            # Exit check
            for i in range(controller.get_numbuttons()):
                if controller.get_button(i) and i in [9, 10, 12, 15]:
                    running = False

            # Read raw analog values (-1.0 to +1.0)
            raw_x = controller.get_axis(0) if controller.get_numaxes() > 0 else 0.0
            raw_y = controller.get_axis(1) if controller.get_numaxes() > 1 else 0.0

            # Filter deadzone (Note: Analog Stick UP is naturally -1.0, so invert Y)
            pan_val = apply_deadzone(raw_x, DEADZONE)
            tilt_val = apply_deadzone(-raw_y, DEADZONE)

            # Stream vector update if joystick position changed significantly
            if abs(pan_val - last_sent_p) > 0.02 or abs(tilt_val - last_sent_t) > 0.02:
                packet = f"V,{pan_val:.2f},{tilt_val:.2f}\n"
                ser.write(packet.encode())
                last_sent_p = pan_val
                last_sent_t = tilt_val

            time.sleep(0.01)  # 100Hz polling rate

        # Send stop command before exiting
        ser.write(b"V,0.00,0.00\n")
        ser.close()

    except serial.SerialException as e:
        print(f"Serial Error: {e}")

if __name__ == '__main__':
    main()