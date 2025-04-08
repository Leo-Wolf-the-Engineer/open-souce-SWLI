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
#define CURRENT 150
#define MICROSTEPPING 64
#define STEPS_PER_MM (STEPS_PER_REVOLUTION * MICROSTEPPING) / SCREW_PITCH_MM

// --- Motor Instance ---
AccelStepper stepper_z(AccelStepper::DRIVER, MOTOR_STEP_PIN, MOTOR_DIR_PIN);

// --- Global Variables ---
float targetPositionMM_Z = 0.0;
float velocityMM_per_sec_Z = 0.0;

// --- TMC2209 Setup ---
// Include TMC2209Stepper library
#include <TMCStepper.h>
  
// Define TMC2209 pins - Software Serial Example
#define SERIAL_PORT Serial2 // Choose your Serial port: Serial1, Serial2 or Serial3
  
// Create TMC2209Stepper instance using either SoftwareSerial or HardwareSerial
#define R_SENSE 0.11f // Sense resistor value on your TMC2209 module (check the markings)
#define DRIVER_ADDRESS 0b00 // Default UART address if MS1 and MS2 are low

// Create a TMC2209Stepper object for UART communication
TMC2209Stepper driver(&SERIAL_PORT, R_SENSE, DRIVER_ADDRESS);

void setup() {
  Serial.begin(115200);
  while (!Serial);
  Serial.println("Initializing TMC2209 via UART...");
  driver.begin();
  driver.microsteps(MICROSTEPPING);
  Serial.print("Microsteps set to: ");
  Serial.println(driver.microsteps());
  driver.rms_current(CURRENT);
  Serial.print("Run current set to: ");
  Serial.println(driver.rms_current());
  Serial.println("TMC2209 configuration complete.");
  stepper_z.setMaxSpeed(51200.0); // Set max speed in steps/second (raw microsteps)
  stepper_z.setAcceleration(1000.0); // Set acceleration in steps/second/second (raw microst
  Serial.print("Steps per MM (effective): ");
  Serial.println(STEPS_PER_MM);

  if (MOTOR_ENABLE_PIN != -1) {
    pinMode(MOTOR_ENABLE_PIN, OUTPUT);
    digitalWrite(MOTOR_ENABLE_PIN, LOW);
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
