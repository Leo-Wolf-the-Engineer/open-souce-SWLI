// Define stepper motor control pins
#define STEP_PIN 2
#define DIR_PIN 0
#define EN_PIN 4

// Define measurement parameters
#define RANGE_MM 0.45
#define NUM_STEPS 40 // Number of measurement points in each direction
#define STEPS_PER_MM 25600
#define NUM_STEPS_PER_MEASUREMENT (0.45 * STEPS_PER_MM / NUM_STEPS) // Steps to move for each measurement
//2*2*2*2*2*2*2*2*3*3*5
#define STEP_DELAY_MS 300 // Delay at each measurement point

void setup() {
  Serial.begin(115200);
  // Initialize stepper motor pins
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  pinMode(EN_PIN, OUTPUT);
  digitalWrite(EN_PIN, LOW); // Turn on TMC
}

void loop() {
  delay(500);
  // Move in negative direction and measure
  digitalWrite(DIR_PIN, LOW); // Negative direction
  for (int i = 0; i < NUM_STEPS; i++) {
    for(int j = 0; j < NUM_STEPS_PER_MEASUREMENT; j++){
      stepOnce();
    }
    delay(STEP_DELAY_MS);
  }

  // Move back to 0 and measure
  digitalWrite(DIR_PIN, HIGH); // Positive direction (back to 0)
  for (int i = 0; i < NUM_STEPS; i++) {
    for(int j = 0; j < NUM_STEPS_PER_MEASUREMENT; j++){
      stepOnce();
    }
    delay(STEP_DELAY_MS);
  }

  delay(1000);
  digitalWrite(EN_PIN, HIGH); // Turn off TMC

  // Stop after one cycle
  while (true) {
    delay(1000); // Wait forever
  }
}

void stepOnce() {
  digitalWrite(STEP_PIN, HIGH);
  delayMicroseconds(100); // Adjust pulse width as needed
  digitalWrite(STEP_PIN, LOW);
  delayMicroseconds(100); // Adjust pulse width as needed
}
