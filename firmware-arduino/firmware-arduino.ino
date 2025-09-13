#include <SPI.h>
#include <Adafruit_NeoPixel.h>

#define LED_PIN    6
#define US_PER_LED 3
#define MAX_SERIAL_READ 502
#define SPI_READY_PIN 3

#define CMD_ID_INIT   0x10
#define CMD_ID_CLEAR  0x20
#define CMD_ID_SHOW   0x21
#define CMD_ID_SINGLE 0x30
#define CMD_ID_STRING 0x31

//#define DEBUG 1

typedef uint8_t CmdType;
typedef uint16_t StringLen;

typedef struct {
  uint16_t id;
  uint8_t r;
  uint8_t g;
  uint8_t b;
} LEDState;



LEDState *led;
CmdType *cmd_type;
StringLen *num_leds_to_set;
StringLen led_string_length;

// vars to be modified by the SPI ISR
volatile uint16_t spi_bytes_in_buf;
volatile uint16_t bytes_pending;
volatile uint8_t buf[MAX_SERIAL_READ];

// we just assume that we'll never let this buffer overflow.
// its a christmas tree after all.
ISR (SPI_STC_vect) {
  buf[spi_bytes_in_buf++] = SPDR;
  // tail-drop
  //if(spi_bytes_in_buf >= bytes_pending) {
  //   PORTD |= 0b00000100;
  //}
  
}

// wait for the buffer to fill up more, return the current global cursor
// location as the start of the available bytes, and advance it by the
// number of bytes received.
// Not checking if the amount of bytes to be received exceeds the
// remaining buffer size.  Whoops.
void waitForSPIBytes(uint16_t num_bytes) {
  bytes_pending = num_bytes;
  //digitalWrite(SPI_READY_PIN, LOW);
  delay(1);
  while(spi_bytes_in_buf < num_bytes) { }
#ifdef DEBUG
  Serial.print("Got ");
  Serial.print(spi_bytes_in_buf, DEC);
  Serial.print("/");
  Serial.print(num_bytes,DEC);
  Serial.print(" bytes: ");
  for(int i=0;i<30;i++) { Serial.print(buf[i],DEC); Serial.print(","); } 
  Serial.print("\n");
#endif
}

void setup() {
  // zeroes
  led_string_length = 0;

  // MISO pin
  pinMode(MISO,OUTPUT);

  // SPI READY pin
  //pinMode(SPI_READY_PIN,OUTPUT);

  // Set slave mode and attach ISR for SPI comms  
#ifdef DEBUG  
  // 115200 is the fastest known to work before i tried the crazy 500,000 speeds etc.
  Serial.begin(115200);
  Serial.flush();
  Serial.print("XMasduino started.\n");
  Serial.println(sizeof(LEDState));
#endif
  SPCR |= _BV(SPE);
  SPI.attachInterrupt();

  // block SPI to start
  //digitalWrite(SPI_READY_PIN, HIGH);
}

void loop() {
  uint8_t *bufcur = buf;
  spi_bytes_in_buf = 0;

  // wait for there to be enough bytes in the buf to determine the next move
  waitForSPIBytes(sizeof(CmdType));
  cmd_type = (CmdType *)bufcur;
  bufcur++;
  switch(*cmd_type) {
    case CMD_ID_SINGLE:
      waitForSPIBytes(sizeof(LEDState));
      led = (LEDState *)bufcur;
      strip.setPixelColor(led->id, strip.Color(led->g, led->r, led->b));
      strip.show();
      break;
    case CMD_ID_STRING:
      // set the string flag, get the amount of LEDs we've been fed, and wait for the rest of the data
      waitForSPIBytes(sizeof(StringLen));
      num_leds_to_set = (StringLen *)bufcur;
      bufcur += sizeof(StringLen);
      waitForSPIBytes(*stringlen * sizeof(LEDState));
      led = (LEDState *)bufcur;
      
      // set stringlen leds to the values in the buf
      for(int i=0;i<*stringlen;i++) {
        strip.setPixelColor(led->id, strip.Color(led->g, led->r, led->b));
#ifdef DEBUG
        Serial.print("\tSet LED: ");
        Serial.println(led->id,DEC);
#endif
        led++;
      }
      break;
    case CMD_ID_INIT:
      waitForSPIBytes(sizeof(StringLen));
      led_string_length = (StringLength *)bufcur;
      
      Adafruit_NeoPixel strip(led_string_length, LED_PIN, NEO_GRB + NEO_KHZ800);
      strip.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
      strip.show();            // Turn OFF all pixels ASAP
      strip.setBrightness(255); // Set BRIGHTNESS to about 1/5 (max = 255)
    case CMD_ID_SHOW:
      strip.show();
      break;
    case CMD_ID_CLEAR:
      strip.clear();
      strip.show();
      break;
  }
}
