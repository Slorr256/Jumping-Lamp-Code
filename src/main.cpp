#include <Arduino.h>
#include <ESP32Servo.h>

#define PAN_PIN  26
#define TILT_PIN 27

#define MIN_ANGLE 0.0f
#define MAX_ANGLE 180.0f

// Maximum degrees moved per loop iteration at full stick tilt
#define MAX_SPEED_STEP 8.0f  

Servo panServo;
Servo tiltServo;

float targetPan = 90.0f;
float targetTilt = 90.0f;

// Normalized speed vectors (-1.0 to 1.0) received from Python
float panSpeed = 0.0f;
float tiltSpeed = 0.0f;

void setup() {
  Serial.begin(115200);

  panServo.setPeriodHertz(50);
  tiltServo.setPeriodHertz(50);

  panServo.attach(PAN_PIN, 500, 2400);
  tiltServo.attach(TILT_PIN, 500, 2400);

  panServo.write((int)targetPan);
  tiltServo.write((int)targetTilt);
}

void loop() {
  // Read velocity packets: "V,<panSpeed>,<tiltSpeed>\n"
  if (Serial.available() > 0) {
    String line = Serial.readStringUntil('\n');
    if (line.startsWith("V,")) {
      int firstComma = line.indexOf(',');
      int secondComma = line.indexOf(',', firstComma + 1);
      
      if (firstComma != -1 && secondComma != -1) {
        String pStr = line.substring(firstComma + 1, secondComma);
        String tStr = line.substring(secondComma + 1);
        
        panSpeed = pStr.toFloat();   // Range: -1.0 to 1.0
        tiltSpeed = tStr.toFloat();  // Range: -1.0 to 1.0
      }
    }
  }

  // Scale step size by joystick deflection factor
  targetPan += panSpeed * MAX_SPEED_STEP;
  targetTilt += tiltSpeed * MAX_SPEED_STEP;

  // Constrain within physical servo limits (0 to 180 degrees)
  targetPan = constrain(targetPan, MIN_ANGLE, MAX_ANGLE);
  targetTilt = constrain(targetTilt, MIN_ANGLE, MAX_ANGLE);

  panServo.write((int)targetPan);
  tiltServo.write((int)targetTilt);

  // ~100Hz refresh rate for fluid analog responsiveness
  delay(10);
}