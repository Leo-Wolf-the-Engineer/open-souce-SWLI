# Arduino Stepper Motor Control Project - Functionality Plan

**Project Goal:** Develop an Arduino sketch for ESP32 that allows controlling a stepper motor (via TMC2209 driver) by receiving position and velocity commands from a desktop computer.  Support for up to 3 motors (X, Y, Z) will be included, starting with the Z motor.

**1. Communication Setup (Serial):**
*   Establish serial communication between the ESP32 and desktop via USB.
*   Baud rate: 115200.

**2. Command Parsing:**
*   Command format: `[MotorName]_[Command],[Value]`
*   Motor Names: `X`, `Y`, `Z` (starting with `Z`)
*   Commands:
    *   `[MotorName]_POS,XX.XXXXXX`: Set target position in millimeters (e.g., `Z_POS,12.345`).
    *   `[MotorName]_VEL,YYYY`: Set velocity in mm/s (e.g., `Z_VEL,5.0`).
    *   `[MotorName]_MOVE`: Move to the set position at the set velocity (e.g., `Z_MOVE`).
    *   `[MotorName]_STOP`: Stop the motor immediately (e.g., `Z_STOP`).
    *   `STOP_ALL`: Stop all motors.
*   ESP32 will parse commands from serial input.
*   Position conversion: mm to steps.
*   Velocity conversion: mm/s to steps/second.

**3. Stepper Motor Control (TMC2209) with UART and AccelStepper Library:**
*   Libraries: AccelStepper for motor control and TMC2209Stepper for driver interface.
*   Motor Constants (to be defined in code):
    *   `STEPS_PER_REVOLUTION = 200;` (1.8-degree motor)
    *   `SCREW_PITCH_MM = 0.5;` (0.5mm pitch screw)
    *   `MICROSTEPPING = 256;` (256x microstepping - set in code for TMC2209 UART)
    *   `CURRENT_AMPS = 0.2;` (Motor current set to 0.2 Amps in code)
*   Steps per mm calculation in code:
    *   `STEPS_PER_MM = (STEPS_PER_REVOLUTION * MICROSTEPPING) / SCREW_PITCH_MM;` (Calculates to 6400 steps/mm)
*   Velocity conversion in code:
    *   `velocity_steps_per_sec = velocity_mm_per_sec * STEPS_PER_MM;`

**4. Basic Feedback:**
*   Optional for the initial stage.

**Next Steps:**
*   Start implementing serial communication and command parsing on ESP32.
*   Integrate AccelStepper library and motor control logic.
*   Test with serial commands from desktop.