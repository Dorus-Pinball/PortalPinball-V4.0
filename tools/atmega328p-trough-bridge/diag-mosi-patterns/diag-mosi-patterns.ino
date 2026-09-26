// Bench-only diagnostic — NOT the trough-bridge firmware. Tests whether this board's shift
// register needs something other than a dummy 0x00 on MOSI to produce live data — e.g. an
// address/command/select byte, the way a real Stern SPIKE CPU might talk to a "node" board,
// as opposed to a bare standalone 74HC165 (which shouldn't care what's on MOSI for the first
// 8 bits shifted out, but this board has proven itself correct in a real machine while reading
// as a constant, unresponsive byte here — see plans/read-opto.md's "Bench findings" for context).
//
// Cycles through a handful of MOSI test bytes. For each, pulses RCK to latch, then clocks out
// THREE consecutive bytes (24 clocks total, not just 8) in case the real data only shows up
// after a longer clock train, or a preceding status/ID byte. Prints what was sent and all three
// bytes received, continuously, so you can watch for ANY change while blocking sensors.
//
// Flash the real atmega328p-trough-bridge.ino back afterward.

#include <SPI.h>

const uint8_t PIN_RCK = 8;

// Full 0-255 sweep instead of a handful of hand-picked bytes — uint8_t wraps naturally.
uint8_t patternIndex = 0;

const unsigned long CYCLE_DELAY_MS = 50; // ~12.8s per full 256-value sweep

void printBinary(uint8_t b) {
  for (int8_t i = 7; i >= 0; i--) Serial.print((b >> i) & 1);
}

void setup() {
  pinMode(PIN_RCK, OUTPUT);
  digitalWrite(PIN_RCK, HIGH);

  SPI.begin();
  SPI.beginTransaction(SPISettings(250000, MSBFIRST, SPI_MODE0));

  Serial.begin(9600);
  Serial.println(F("diag-mosi-patterns: latch, then 3 bytes clocked with a rotating MOSI test pattern"));
  Serial.println(F("format: sent=0bXXXXXXXX  recv1=0bXXXXXXXX recv2=0bXXXXXXXX recv3=0bXXXXXXXX"));
}

void loop() {
  uint8_t testByte = patternIndex;
  patternIndex++; // wraps 255 -> 0

  digitalWrite(PIN_RCK, LOW);
  delayMicroseconds(5);
  digitalWrite(PIN_RCK, HIGH);
  delayMicroseconds(5);

  uint8_t r1 = SPI.transfer(testByte);
  uint8_t r2 = SPI.transfer(testByte);
  uint8_t r3 = SPI.transfer(testByte);

  Serial.print(F("sent=0b")); printBinary(testByte);
  Serial.print(F("  recv1=0b")); printBinary(r1);
  Serial.print(F(" recv2=0b")); printBinary(r2);
  Serial.print(F(" recv3=0b")); printBinary(r3);
  Serial.println();

  delay(CYCLE_DELAY_MS);
}
