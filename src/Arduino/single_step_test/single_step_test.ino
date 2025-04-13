// Define stepper motor control pins
#define STEP_PIN 2
#define DIR_PIN 3

// Define measurement parameters
#define NUM_STEPS 10 // Number of measurement points in each direction
#define STEP_DELAY_MS 300 // Delay at each measurement point

void setup() {
  Serial.begin(115200);
  // Initialize stepper motor pins
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  digitalWrite(DIR_PIN, HIGH); // Set initial direction (negative)
}

void loop() {
  Serial.println("starting...");
  // Move in negative direction and measure single steps
  digitalWrite(DIR_PIN, HIGH); // Negative direction
  for (int i = 0; i < NUM_STEPS; i++) {
    stepOnce();
    delay(STEP_DELAY_MS);
  }

  // Move back to 0 and measure single steps
  digitalWrite(DIR_PIN, LOW); // Positive direction (back to 0)
  for (int i = 0; i < NUM_STEPS; i++) {
    stepOnce();
    delay(STEP_DELAY_MS);
  }
  
  Serial.println("Program done");

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
