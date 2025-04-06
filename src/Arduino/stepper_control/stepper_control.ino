#define ARDUINO 100
//#include "C:\\\\Users\\\\Leo\\\\Documents\\\\Arduino\\\\libraries\\\\AccelStepper\\src\\AccelStepper.h"
#include <AccelStepper.h>
#include <string.h> // Required for strtok

// --- Motor Configuration ---
#define MOTOR_STEP_PIN 2  // Define your step pin
#define MOTOR_DIR_PIN 0   // Define your direction pin
#define MOTOR_ENABLE_PIN 4 // Define your enable pin (optional)

#define STEPS_PER_REVOLUTION 200.0
#define SCREW_PITCH_MM 0.5
#define MICROSTEPPING 16.0
#define STEPS_PER_MM (STEPS_PER_REVOLUTION * MICROSTEPPING) / SCREW_PITCH_MM

// --- Motor Instance ---
AccelStepper stepper_z(AccelStepper::DRIVER, MOTOR_STEP_PIN, MOTOR_DIR_PIN);

// --- Global Variables ---
float targetPositionMM_Z = 0.0;
float velocityMM_per_sec_Z = 0.0;

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB
  }
  Serial.println("Stepper Control Sketch Started");

    // --- TMC2209 Setup ---
    // 1. Include TMC2209Stepper library (Ensure library is installed via Library Manager: Sketch -> Include Library -> Manage Libraries...)
    //    You can search for "TMC2209Stepper by Teemu Mäntynen" in the Library Manager
    //#include <TMCStepper.h>
  
    // 2. Define TMC2209 pins - Software Serial Example (adjust pins and Serial port as needed for your wiring)
    //#define TMC_SERIAL_RX_PIN 5  // Arduino RX pin connected to TMC2209 TX pin
    //#define TMC_SERIAL_TX_PIN 17  // Arduino TX pin connected to TMC2209 RX pin
    //#define SERIAL_PORT Serial1 // Choose your Serial port: Serial1, Serial2 or Serial3 for HardwareSerial, or Serial for SoftwareSerial
  
    //    For SoftwareSerial, uncomment and adjust pins:
    // #include <SoftwareSerial.h>
    // SoftwareSerial tmcSerial(TMC_SERIAL_RX_PIN, TMC_SERIAL_TX_PIN);
  
    // 3. Create TMC2209Stepper instance using either SoftwareSerial or HardwareSerial
    //    Ensure R_SENSE is correctly defined for your sense resistors
    //TMCStepper driver(&SERIAL_PORT, 0.11f); // Hardware Serial - R_SENSE is the sense resistor value (e.g., 0.11 Ohm)
    // TMC2209Stepper driver(&tmcSerial, R_SENSE);   // Software Serial - R_SENSE is the sense resistor value (e.g., 0.11f for 0.11 Ohm)
  
    // IMPORTANT: R_SENSE value depends on your hardware. It's the resistance of the sense resistor connected to the TMC2209.
    // Common values are 0.11f for 0.11 Ohm resistors or 0.33f for 0.33 Ohm resistors.
    // Incorrect R_SENSE value can lead to incorrect current readings and driver malfunction.
    // #define R_SENSE 0.11f // Example for 0.11 Ohm sense resistor -  verify your board's resistor value!
  
    // 4. Initialize serial communication for TMC2209
    //SERIAL_PORT.begin(115200); // Match baud rate in your TMC2209 datasheet and configuration (usually 115200)
    //driver.begin();         // Initialize driver communication and verify connection
    //driver.setMicrosteps(MICROSTEPPING);
    //driver.setCurrent(0.2f); // Set current to 0.2 amps
    // driver.setPowerDownMode(TMC2209_POWERDOWN_MODE_0); // Optional: Set power down mode if needed (TMC2209_POWERDOWN_MODE_0 is default)
  
    // --- Motor setup (AccelStepper) ---
    stepper_z.setMaxSpeed(100.0); // Set max speed in steps/second - adjust as needed
    stepper_z.setAcceleration(10.0); // Set acceleration in steps/second/second - adjust as needed
    if (MOTOR_ENABLE_PIN != -1) { // Enable pin is optional, set to -1 if not used
      pinMode(MOTOR_ENABLE_PIN, OUTPUT);
      digitalWrite(MOTOR_ENABLE_PIN, LOW); // Enable motor driver (adjust polarity if needed)
    }
  }

void loop() {
  if (Serial.available() > 0) {
    String commandString = Serial.readStringUntil('\n');
    commandString.trim(); // Remove leading/trailing whitespace

    parseCommand(commandString);
  }
  stepper_z.run(); // Keep running the motor if it's moving
}

void parseCommand(String command) {
  char commandCharArray[command.length() + 1]; // Convert String to char array
  strcpy(commandCharArray, command.c_str());

  char *commandToken = strtok(commandCharArray, "_"); // Tokenize by underscore

  if (commandToken != NULL) {
    String motorName = String(commandToken);

    if (motorName == "Z") {
      char *actionToken = strtok(NULL, ","); // Tokenize by comma
      char *valueToken = strtok(NULL, ",");

      if (actionToken != NULL) {
        String action = String(actionToken);

        if (action == "POS" && valueToken != NULL) {
          targetPositionMM_Z = atof(valueToken);
          Serial.print("Z Target Position (mm): ");
          Serial.println(targetPositionMM_Z);
        } else if (action == "VEL" && valueToken != NULL) {
          velocityMM_per_sec_Z = atof(valueToken);
          stepper_z.setMaxSpeed(velocityMM_per_sec_Z * STEPS_PER_MM); // Set max speed in steps/second
          Serial.print("Z Velocity (mm/s): ");
          Serial.println(velocityMM_per_sec_Z);
        } else if (action == "MOVE") {
          long targetPositionSteps = targetPositionMM_Z * STEPS_PER_MM;
          stepper_z.moveTo(targetPositionSteps);
          Serial.print("Z Moving to position (mm): ");
          Serial.println(targetPositionMM_Z);
        } else if (action == "STOP") {
          stepper_z.stop();
          Serial.println("Z Motor Stopped");
        } else {
          Serial.println("Unknown Z command");
        }
      }
    } else if (motorName == "STOP") { //STOP_ALL command
        if(String(strtok(NULL, ",")) == "ALL"){
            stepper_z.stop(); // Stop Z motor for now, add others later
            Serial.println("All Motors Stopped");
        }
    }
     else {
      Serial.println("Unknown Motor Command");
    }
  }
}
