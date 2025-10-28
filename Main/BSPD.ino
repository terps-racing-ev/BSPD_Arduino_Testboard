#include "C:\wamp64\bspd_test_module\AD5245\AD5245.cpp"
#include <Wire.h>
#define BAUD_RATE 115200
#define BUFFER_SIZE 24

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

void setup() {
    // Begin serial and wire
    Serial.begin(BAUD_RATE);
    Serial.println("Serial communication OK.");
    
    Wire.begin();
    Wire.setClock(400000);

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
    
    // [BSPD Faulted?, Voltage on Ch1, Voltage on Ch2]
    
    

}