
int rightPin1 = 12;
int rightPin2 = 13;
int leftPin1 = 10;
int leftPin2 = 11;


bool drive = true;

void setup() {
  pinMode(rightPin1, OUTPUT); 
  pinMode(rightPin2, OUTPUT);
  pinMode(leftPin1, OUTPUT); 
  pinMode(leftPin2, OUTPUT);  


  Serial.begin(9600);


  right();
}

void loop() {
  
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
