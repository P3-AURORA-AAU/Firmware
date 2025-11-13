#include "Arduino.h"
#include <Arduino_MKRIoTCarrier.h>

const int UART_MAX_LENTH = 12;

MKRIoTCarrier carrier;

float acc_x, acc_y, acc_z;
float gy_x, gy_y, gy_z;

constexpr uint8_t PIN_RX = 1;
constexpr uint8_t PIN_TX = 2;

const uint8_t syn = 0x53;
const uint8_t synAck = 0x54;
const uint8_t ack = 0x55;


Uart uart(&sercom2, PIN_RX, PIN_TX, SERCOM_RX_PAD_3, UART_TX_PAD_2);

byte cmd[UART_MAX_LENTH];




// external Relays right
const int RELAY1 = 3;
const int RELAY2 = 15;

// external Relays left
const int RELAY3 = 16;
const int RELAY4 = 17;

//mkr iot carrier relays 
const int DPDT_RIGTH = 18;
const int DPDT_LEFT = 19; 


struct Speed {
  int Left;
  int Right;
};

const Speed SLOW   = {100, 50};
const Speed MEDIUM = {100, 0};
const Speed FAST   = {100, -50};
const Speed SUPER  = {100, -100};


enum StanderdSpeed {
  FullSpeed = 100,
  HalfSpeed = 50,
  NoMovment = 0,
};

Speed MotorSpeed = {0,0};

void setup(){
  carrier.noCase();
  carrier.begin();

  pinMode(RELAY1, OUTPUT);
  pinMode(RELAY2, OUTPUT);
  pinMode(RELAY3, OUTPUT);
  pinMode(RELAY4, OUTPUT);
  pinMode(DPDT_LEFT, OUTPUT);
  pinMode(DPDT_RIGTH, OUTPUT);
  
  carrier.Relay1.open();
  carrier.Relay2.open();

  Serial.begin(9600); //Initializes USB serial port for debugging purposes
  uart.begin(9600); //Initializes UART com (1, 2)

  bool handshakeDone = performHandshake();
  if (!handshakeDone) {
    Serial.println("Handshake failed");
    return;
  }
  Serial.println("Handshake succeeded");
}

void loop() {
  int count = readUart(cmd, UART_MAX_LENTH);
  Serial.print("cmd byte lenth: ");
  Serial.println(count);
  switch (cmd[0]) {
    case 0x61:
      setSpeed(cmd);
      break;
    case 0x62:
      setDir(cmd);
      break;
    case 0x63:
      sensorRequset(cmd);
    break;
  }
  ParseMotor();
}

void turn(Speed speed, bool inverse = false) {
  if (!inverse) {
    MotorSpeed.Left = speed.Left;
    MotorSpeed.Right = speed.Right;
  } else {
    MotorSpeed.Right = speed.Left;
    MotorSpeed.Left = speed.Right;
  }
}

void setDir(byte* cmd) {
  int angle = cmd[1];
  switch (angle) {
    case 0: // sebastians problem
      ;
      break;
    case 360:// sebastians problem
    ;
      break;

    default:
      break;

  }

  if (angle > 130) { turn(SUPER); }
  else if (angle > 50 && angle  < 130) { turn(FAST); }
  else if (MotorSpeed.Left == 0) { turn(MEDIUM); }
  else { turn(SLOW); }
}

void sensorRequset(byte* cmd){
switch (cmd[1]) {
    case 0x01:
      accData();
      break;
    case 0x02:
      gyroData();
      break;
    case 0x03:
      MoistMeterData();
      break;
    case 0x04:
      tempData();
      break;
    case 0x06:
      pressureData();
      break;
    
    default:
      break;

  }
}


void setSpeed (byte* cmd) {
  switch (cmd[1]) {
    case 0x01:
      MotorSpeed.Left = 0;
      MotorSpeed.Right = 0;
      break;
    case 0x02:
      MotorSpeed.Left = 50;
      MotorSpeed.Right = 50;
      break;
    case 0x03:
      MotorSpeed.Left = 100;
      MotorSpeed.Right = 100;
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

int readUart(byte* buffer, int maxLen) {
    int count = 0;
    while (uart.available() && count < maxLen) {
        int b = uart.read();
        if (b != -1) buffer[count++] = (byte)b;
    }
    return count; // number of bytes read
}
 

void ParseMotor() {
  int left = MotorSpeed.Left
  int right = MotorSpeed.Right

  switch ( left ) {
    case 100:
      digitalWrite(DPDT_LEFT, HIGH);
      digitalWrite(RELAY3, HIGH);
      digitalWrite(RELAY4, LOW);
      break;
    case 50:
      digitalWrite(DPDT_LEFT, LOW);
      digitalWrite(RELAY3, HIGH);
      digitalWrite(RELAY4, LOW);
      break;
    case -100:
      digitalWrite(DPDT_LEFT, HIGH);
      digitalWrite(RELAY3, LOW);
      digitalWrite(RELAY4, HIGH);
      break;
    case -50:
      digitalWrite(DPDT_LEFT, LOW);
      digitalWrite(RELAY3, LOW);
      digitalWrite(RELAY4, HIGH);
      break;
    default:
      digitalWrite(RELAY3, LOW);
      digitalWrite(RELAY4, LOW);
      break;
  }
  switch ( right ) {
    case 100:
      digitalWrite(DPDT_RIGHT, HIGH);
      digitalWrite(RELAY1, HIGH);
      digitalWrite(RELAY2, LOW);
      break;
    case 50:
    digitalWrite(DPDT_RIGTH, LOW);
    digitalWrite(RELAY1, HIGH);
    digitalWrite(RELAY2, LOW);
      break;
    case -100:
      digitalWrite(DPDT_RIGHT, HIGH);
      digitalWrite(RELAY1, LOW);
      digitalWrite(RELAY2, HIGH);
      break;
    case -50:
      digitalWrite(DPDT_RIGHT, LOW);
      digitalWrite(RELAY1, LOW);
      digitalWrite(RELAY2, HIGH);
      break;
    default:
      digitalWrite(RELAY1, LOW);
      digitalWrite(RELAY2, LOW);
      break;
  }
}
