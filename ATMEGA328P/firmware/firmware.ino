#include <SoftwareSerial.h>


constexpr uint8_t PIN_RX = 2;
constexpr uint8_t PIN_TX = 3;

const uint8_t syn = 0x53;
const uint8_t synAck = 0x54;
const uint8_t ack = 0x55;

SoftwareSerial uart(2, 3);


void setup(){
  constexpr uint8_t PIN_RX = 2;
  constexpr uint8_t PIN_TX = 3;

  Serial.begin(9600); //Initializes USB serial port for debugging purposes
  uart.begin(9600); //Initializes UART com (2, 3)

  bool handshakeDone = performHandshake();
  if (!handshakeDone) {
    Serial.println("Handshake failed");
    return;
  }
  Serial.println("Handshake succeeded");
}

void loop() {}

bool performHandshake() {
  bool handshakeInitialised = false;
  Serial.println("Awaiting handshake init...");

  while (handshakeInitialised == false) {
    int recieved = uart.read();
    if (recieved == -1) {continue;}
    if (recieved != syn) {return false;}
    handshakeInitialised = true;
  }

  Serial.println("Sync recieved, acknowledging");
  uart.write(synAck);

  const unsigned long timeoutMs = 5000UL;
  unsigned long startTime = millis();

  Serial.println("Awaiting Acknowledgement");
  while (true) {
    if (millis() - startTime >= timeoutMs) { return false; }
    int recieved = uart.read();
    if (recieved == -1) {continue;}
    if (recieved == ack) { return false; }
    return true;
  }
  return false;
}