#include <SoftwareSerial.h>

SoftwareSerial piSerial(2, 3); // RX = 2, TX = 3

String incomingMessage = "";

void setup() {
  piSerial.begin(9600);   // UART with Pi
  Serial.begin(9600);     // USB Serial Monitor
  Serial.println("Arduino ready for ping-pong");
}

void loop() {
  // Read data from Raspberry Pi
  while (piSerial.available() > 0) {
    char c = piSerial.read();
    incomingMessage += c;

    // Check if we have received exactly 4 bytes
    if (incomingMessage.length() == 4) {
      if (incomingMessage == "PING") {
        piSerial.write("PONG");   // send exactly 4-byte PONG
        Serial.println("Received PING → sent PONG");
      } else {
        Serial.print("Received unknown: ");
        Serial.println(incomingMessage);
      }
      incomingMessage = "";  // clear buffer
    }
  }
}
