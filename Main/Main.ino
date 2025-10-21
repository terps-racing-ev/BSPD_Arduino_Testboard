void setup() {
  Serial.begin(115200);
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