#include <Arduino_MKRIoTCarrier.h>
MKRIoTCarrier carrier;

float acc_x, acc_y, acc_z;
float gy_x, gy_y, gy_z;



void setup() {
  carrier.noCase();
  carrier.begin();


  Serial.begin(9600);


}

void loop() {
  float temperature = carrier.Env.readTemperature();
  float humidity = carrier.Env.readHumidity();
  float pressure = carrier.Pressure.readPressure();


  acceleration();
  gyro();
}


void acceleration() {
  if (carrier.IMUmodule.accelerationAvailable())
    {
      carrier.IMUmodule.readAcceleration(acc_x, acc_y, acc_z);
      Serial.print("acceleration: ");
      Serial.println(acc_x);
    }
}

void gyro() {
  if (carrier.IMUmodule.gyroscopeAvailable())
    {
      carrier.IMUmodule.readGyroscope(gy_x, gy_y, gy_z);
      Serial.print("gyroscope: ");
      Serial.println(gy_x);
    }
}
