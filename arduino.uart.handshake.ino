#include <SoftwareSerial.h>

SoftwareSerial piSerial(2, 3); // RX = 2, TX = 3

String incomingMessage = "";
bool validHandshake = false;

void setup() {
  piSerial.begin(9600);
  Serial.begin(9600);
  Serial.println("Arduino ready for ping-pong");

  
  Serial.println(piSerial.available());

  validHandshake = handShake();
  Serial.print("Handshake status: ");
  Serial.println(validHandshake ? "OK" : "FAILED");
  
  Serial.print("serial status: ");
  Serial.println(piSerial.available() ? "OK" : "FAILED");
  
}

void loop() {
  if (piSerial.available()) {
    validHandshake = handShake();
    Serial.print("Handshake status: ");
    Serial.println(validHandshake ? "OK" : "FAILED");
  }
}

bool handShake() {
  while (piSerial.available() > 0) {
    char c = piSerial.read();
    incomingMessage += c;
    Serial.print("Received: ");
    Serial.println(incomingMessage);

    if (c == 'A') {
      piSerial.write("B");  // Reply to 'A'
      Serial.println("Sent: B");
      incomingMessage = "";
      return false;
    } 
    else if (c == 'C') {
      Serial.println("Handshake complete!");
      incomingMessage = "";
      return true;
    } 
    else {
      Serial.print("Unexpected: ");
      Serial.println(c);
      incomingMessage = "";
      return false;
    }
  }
  return validHandshake; // Keep last state if no new data
}
