#include <SoftwareSerial.h>

SoftwareSerial piSerial(2, 3); // RX = 2, TX = 3

String incomingMessage = "";

int rightPin1 = 12;
int rightPin2 = 13;
int leftPin1 = 10;
int leftPin2 = 11;


bool validHandshake = false;

void setup() {
  pinMode(rightPin1, OUTPUT); 
  pinMode(rightPin2, OUTPUT);
  pinMode(leftPin1, OUTPUT); 
  pinMode(leftPin2, OUTPUT);  

  piSerial.begin(9600);
  Serial.begin(9600);


  
}

void loop() {
  if (validHandshake) {
    while (piSerial.available() > 0){
      char c = piSerial.read();
      
      Serial.print("Received: ");
      Serial.println(c);

      if (c == 'D') {
        forward();
      }
      else if (c == 'R') {
        right();
      }
      else if (c == 'L') {
        left();
      }
      else if (c == 'B') {
        backward();
      }
      else {
        stop();
      }
    }
  } else {
      validHandshake = handShake();
      stop();
  }
}

void forward() {
  digitalWrite(rightPin1, HIGH); 
  digitalWrite(rightPin2, LOW); 
  digitalWrite(leftPin1, HIGH); 
  digitalWrite(leftPin2, LOW);
}

void backward() {
  digitalWrite(rightPin1, LOW); 
  digitalWrite(rightPin2, HIGH); 
  digitalWrite(leftPin1, LOW); 
  digitalWrite(leftPin2, HIGH);
}

void left(){
  digitalWrite(rightPin1, HIGH); 
  digitalWrite(rightPin2, LOW); 
  digitalWrite(leftPin1, LOW); 
  digitalWrite(leftPin2, HIGH);
}

void right() {
  digitalWrite(rightPin1, LOW); 
  digitalWrite(rightPin2, HIGH);
  digitalWrite(leftPin1, HIGH); 
  digitalWrite(leftPin2, LOW);
}

void stop() {
  digitalWrite(rightPin1, LOW); 
  digitalWrite(rightPin2, LOW); 
  digitalWrite(leftPin1, LOW); 
  digitalWrite(leftPin2, LOW);
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
