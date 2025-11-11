#include <SoftwareSerial.h>
#include <Arduino_MKRIoTCarrier.h>


MKRIoTCarrier carrier;

float acc_x, acc_y, acc_z;
float gy_x, gy_y, gy_z;

constexpr uint8_t PIN_RX = 2;
constexpr uint8_t PIN_TX = 3;

const uint8_t syn = 0x53;
const uint8_t synAck = 0x54;
const uint8_t ack = 0x55;


SoftwareSerial uart(2, 3);

int speed = 0;


void setup(){
  carrier.noCase();
  carrier.begin();
  
  carrier.Relay1.open();
  carrier.Relay2.open();

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

void loop() {
  [byte] cmd = uart.read();
  switch (cmd[0]) {
    case 0x61:
      setSpeed(cmd);
      break;
    case 0x62:
      break;
    case 0x63:
      sensorRequset(cmd);
    break;
  }
}

void sensorRequset([byte] cmd){
switch (cmd[1]) {
    case 0x01:
      accData();
      break;
    case: 0x02:
      gyroData();
      break;
    case 0x03:
      MoistMeterData();
      break;
    case: 0x04:
      tempData();
      break;
    case 0x03:
      pressureData();
      break;
    
    default:
      break;

  }
}


void setSpeed ([byte] cmd) {
  switch (cmd[1]) {
    case 0x01:
      speed = 0;
      break;
    case: 0x02:
      speed = 50;
      break;
    case 0x03:
      speed = 100;
      break;
    default:
      break;

  }
}

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
    Serial.println(recieved);
    if (recieved != ack) { return false; }
    return true;
  }
  return false;
}


void MoistMeterData() {uart.write(carrier.Env.readHumidity());}
void tempData() {uart.write(carrier.Env.readTemperature());}
void pressureData() {uart.write(carrier.Pressure.readPressure());}
void accData() {
  if (carrier.IMUmodule.accelerationAvailable())
    {
      carrier.IMUmodule.readAcceleration(acc_x, acc_y, acc_z);
      uart.write(acc_x);
    }
}

void gyroData() {
  if (carrier.IMUmodule.gyroscopeAvailable())
    {
      carrier.IMUmodule.readGyroscope(gy_x, gy_y, gy_z);
      uart.write(gy_x);
    }
}

