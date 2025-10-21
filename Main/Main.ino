void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ;
  }
}

void loop() {
  if (Serial.available()) {
    String receivedData = Serial.readStringUntil('\n');
    Serial.print("Python sent: ");
    Serial.println(receivedData);
  }
}