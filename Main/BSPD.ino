#include "C:\wamp64\bspd_test_module\AD5245\AD5245.cpp"
#include <Wire.h>
#define BAUD_RATE 115200
#define BUFFER_SIZE 24
#define DP_PRECISION 2
#define DEBUG_CH_0 A0
#define DEBUG_CH_1 A1
#define DEBUG_CH_2 A2
#define DEBUG_CH_3 A3
#define DEBUG_CH_4 7  // We can't use A4 and A5 because those are shorted to the I2C bus
#define DEBUG_CH_5 8  // so if you turn on I2C you lose A4 and A5 as ADC pins. Therefore, DEBUG CH 4 and 5 will be digital debug channels

// If you connect anything to A4/A5 during I2C startup, it will hang forever. So don't use A4 and A5 as debug channel inputs. 

TwoWire* i2c_default_twowire = &Wire;
AD5245 ch1(0x2D, i2c_default_twowire);     //  Ch1 has AD0 pulled HIGH, so it has addr 0x2D
AD5245 ch2(0x2C, i2c_default_twowire);     //  Ch2 has AD0 pulled to GND, so it has addr 0x2C
bool i2c_started_successfully = false;

char cmd_buffer[BUFFER_SIZE];
char last_char;
byte cmd_buffer_idx = 0;

char tmp[BUFFER_SIZE];
byte i = 0;
byte tmp_index = 0;

int dpot_pos_1 = 0;
int dpot_pos_2 = 0;

String voltages[8];
String toTransmit;

void setup() {
    // Begin serial and wire
    Serial.begin(BAUD_RATE);
    Serial.println("Serial communication OK.");
    
    Wire.begin();
    Wire.setClock(400000);
    Serial.println("Wire setClock OK.");

    // Set up the analog pins to be inputs
    pinMode(DEBUG_CH_0, INPUT);
    pinMode(DEBUG_CH_1, INPUT);
    pinMode(DEBUG_CH_2, INPUT);
    pinMode(DEBUG_CH_3, INPUT);
    pinMode(DEBUG_CH_4, INPUT);
    pinMode(DEBUG_CH_5, INPUT); 
    Serial.println("Debug signal channels OK.");

    // Start talking with ch1
    i2c_started_successfully = ch1.begin();
    Serial.println(i2c_started_successfully ? "Ch1 D-pot: I2C OK" : "Ch1 D-pot: I2C failed to start");
    Serial.println("Ch1 D-pot: connection status:");
    Serial.println((int)ch1.isConnected());

    // Start talking with ch2
    i2c_started_successfully = ch2.begin();
    Serial.println(i2c_started_successfully ? "Ch2 D-pot: I2C OK" : "Ch2 D-pot: I2C failed to start");
    Serial.println("Ch2 D-pot: connection status:");
    Serial.println((int)ch2.isConnected());
}

void loop() {
    // Read instruction from computer
    if (Serial.available() > 0) {
      last_char = (char)Serial.read();
      Serial.println(last_char);

      // Case "[": move buffer index to the front of the buffer
      // and clear buffer
      // (this is what allows the Arduino to ignore any random 
      // characters coming in over serial that aren't part of anything)
      if (last_char == '[') {
        cmd_buffer_idx = 0;
        memset(cmd_buffer, 0, sizeof(cmd_buffer));
      }

      // Case "]": read what's on the buffer and act on the 
      // instructions within
      else if (last_char == ']') {
        /*
        * Read channel 1 value
        */
        Serial.println("Reading ch1...");

        // Clear temporary character array and prepare to 
        // copy a subset of cmd_buffer to tmp
        memset(tmp, 0, sizeof(tmp));
        tmp_index = 0;

        // Ch1 value: keep copying characters
        // into the tmp char array until we hit a comma
        // or the end of the char buffer
        i = 0;
        while (i < cmd_buffer_idx && cmd_buffer[i] != ',') {
          tmp[tmp_index] = cmd_buffer[i];
          i++;
          tmp_index++;
        }

        // Convert whatever chars are in tmp
        // into an int
        dpot_pos_1 = atoi(tmp);
        Serial.println("dpot_pos_1:");
        Serial.println(dpot_pos_1);

        /*
        * Read channel 2 value
        */
        Serial.println("Reading ch2...");

        // Clear temporary character array and prepare to 
        // copy a subset of cmd_buffer to tmp again
        memset(tmp, 0, sizeof(tmp));
        tmp_index = 0;

        // Ch2 value: keep copying characters
        // into the tmp char array until we hit a comma
        // or the end of the char buffer
        // (i is still on the position with the comma, so
        // we need to advance it one more before we get to 
        // the actual ch2 value)
        i++;
        while (i < cmd_buffer_idx && cmd_buffer[i] != ',') {
          tmp[tmp_index] = cmd_buffer[i];
          i++;
          tmp_index++;
        }

        // Convert whatever chars are in tmp
        // into an int and set dpot_pos_2 to that
        dpot_pos_2 = atoi(tmp);
        Serial.println("dpot_pos_2:");
        Serial.println(dpot_pos_2);

        /*
        * Validate dpot_pos_1 and dpot_pos_2 values
        * and send them to the ICs over I2C
        * (0 is not valid since 0 is an error code atoi
        * uses to say that it couldn't turn a char array into an int)
        */
        if (dpot_pos_1 < 1 || dpot_pos_1 > 256) {
          Serial.println("Ch1 invalid setting for d-pot!");
        } else {
          // TODO: make it actually talk with the chip
        }
        if (dpot_pos_2 < 1 || dpot_pos_2 > 256) {
          Serial.println("Ch2 invalid setting for d-pot!");
        } else {
          // TODO: make it actually talk with the chip
        }
      }

      // Other cases: add the character to the buffer
      else {
        if (cmd_buffer_idx < BUFFER_SIZE) {
          cmd_buffer[cmd_buffer_idx] = last_char;
          cmd_buffer_idx++;
        }
      }
    }

    // Even if there are no commands to be read from the laptop,
    // still carry out background tasks such as sending updates
    // to the laptop
    
    /*
    * Signals we have to read:
    * Ch1 Real Voltage (ANALOG)
    * Ch2 Real Voltage (ANALOG)
    * Accelerator Reference (ANALOG)
    * Brake Reference (ANALOG)
    * BSPD Fault/OK Signal (DIGITAL)
    * Acc and Brake (Debug Signal) (DIGITAL)
    *
    * This code doesn't care what's connected to what pins,
    * it just reads voltages off 4 analog channels/2 digital channels and reports
    * them back to the computer. 
    */
    voltages[0] = String( analogRead(DEBUG_CH_0) * (5.0 / 1023.0), DP_PRECISION );
    delayMicroseconds(150);
    voltages[1] = String( analogRead(DEBUG_CH_1) * (5.0 / 1023.0), DP_PRECISION );
    delayMicroseconds(150);
    voltages[2] = String( analogRead(DEBUG_CH_2) * (5.0 / 1023.0), DP_PRECISION );
    delayMicroseconds(150);
    voltages[3] = String( analogRead(DEBUG_CH_3) * (5.0 / 1023.0), DP_PRECISION );
    delayMicroseconds(150);
    voltages[4] = (digitalRead(DEBUG_CH_4) == HIGH ? "HI" : "LO");
    delayMicroseconds(150);
    voltages[5] = (digitalRead(DEBUG_CH_5) == HIGH ? "HI" : "LO");
    delayMicroseconds(150);

    toTransmit = "[";
    for (i = 0; i < 6; i += 1) {
      toTransmit += voltages[i];
      toTransmit += ",";
    }
    toTransmit += String( dpot_pos_1 );
    toTransmit += ",";
    toTransmit += String( dpot_pos_2 );
    toTransmit += "]";
    Serial.println(toTransmit);
}