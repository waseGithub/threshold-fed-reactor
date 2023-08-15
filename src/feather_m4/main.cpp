#include <SPI.h>
#include <Wire.h>
#include <Adafruit_INA219.h>
#include <Adafruit_MCP4728.h>
#include <Wire.h>

Adafruit_MCP4728 mcp;

Adafruit_INA219 ina219_A(0x40);
Adafruit_INA219 ina219_B(0x41);
Adafruit_INA219 ina219_C(0x44);
Adafruit_INA219 ina219_D(0x45);

const int chipSelect = 10;
int currenthour;
float feed_voltage;
float recirculation_voltage;

void setup(void)
{
  Serial.begin(115200);
  uint32_t currentFrequency;
  if (!mcp.begin(0x60)) {
    Serial.println("Failed to find MCP4728 chip");
    while (1) {
      Serial.println("fuck");
      delay(10);
    }
  }
}

void loop(void)
{

  float shuntvoltage_A = 0;
  float busvoltage_A = 0;
  float current_mA_A = 0;
  float loadvoltage_A = 0;
  float power_mW_A = 0;



  if (!ina219_C.begin())
  {

    Serial.println("Failed to find INA219 A chip");
  }
  else
  {

    shuntvoltage_A = ina219_C.getShuntVoltage_mV();
    busvoltage_A = ina219_C.getBusVoltage_V();
    current_mA_A = ina219_C.getCurrent_mA();
    power_mW_A = ina219_C.getPower_mW();
    loadvoltage_A = busvoltage_A + (shuntvoltage_A / 1000);

    Serial.print("A Bus Voltage:   ");
    Serial.print(busvoltage_A);
    Serial.println(" V");
    Serial.print("A Current:       ");
    Serial.print(current_mA_A);
    Serial.println(" mA");
  }



  if (Serial.available() > 0) {
    String receivedData = Serial.readString();
    // Serial.print("Data in:  ");
    // Serial.println(receivedData);

    // Convert String to char array.
    char inputStr[receivedData.length() + 1];
    receivedData.toCharArray(inputStr, sizeof(inputStr));

    char* token = strtok(inputStr, ":::");
    float num1 = atof(token);

    token = strtok(NULL, ":::");
    float num2 = atof(token);

    // Use num1 and num2 as per your requirement
    // Serial.print("Number 1: ");
    // Serial.println(num1);
    // Serial.print("Number 2: ");
    // Serial.println(num2);

    // If you need to use num1 to set the voltage
    feed_voltage = num1;
    recirculation_voltage = num2;

}
 
  Serial.print("Feed voltage in:  ");
  Serial.println(feed_voltage);

   Serial.print("Recirculation voltage in:  ");
  Serial.println(recirculation_voltage);


  float digital_v_input;
  digital_v_input = (1242.9 * feed_voltage) - 2.796;
  Serial.print("Feed voltage set:  ");
  Serial.println(digital_v_input); 
  Serial.println("");




  mcp.setChannelValue(MCP4728_CHANNEL_D, digital_v_input);
  mcp.saveToEEPROM();
  delay(3000);
}






























// }

// void loop() { delay(1000); }