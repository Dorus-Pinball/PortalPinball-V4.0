// Bench-only diagnostic — NOT the trough-bridge firmware. Confirms RCK/SCK are already proven
// to reach the Stern board (see diag-slow-toggle); this checks whether the board echoes
// anything back at all. Pulses RCK to latch, then never clocks SCK — the 74HC165's QH output
// just holds the first parallel bit (D7) at a steady DC level between latches, instead of
// shifting through all 8 bits in ~32us. Probe the Stern board's own MISO/QH connector pin
// directly (not the Uno) with a DC-volts multimeter: it should sit near 0V or 5V and visibly
// move if you block/unblock whichever physical channel is wired to D7.
//
// Flash the real atmega328p-trough-bridge.ino back afterward; this sketch does not read MISO
// itself (nothing here needs the SPI library — SCK is just held low, not driven).

const uint8_t PIN_RCK = 8;
const uint8_t PIN_SCK = 13;
const unsigned long LATCH_INTERVAL_MS = 3000;

void setup() {
  pinMode(PIN_RCK, OUTPUT);
  pinMode(PIN_SCK, OUTPUT);
  digitalWrite(PIN_RCK, HIGH); // idle
  digitalWrite(PIN_SCK, LOW);  // idle - never clocked in this sketch
  Serial.begin(9600);
  Serial.println(F("diag-hold-latch: pulsing RCK every 3s, SCK held low (no shifting) -"));
  Serial.println(F("probe the board's own MISO/QH pin directly with a multimeter."));
}

void loop() {
  digitalWrite(PIN_RCK, LOW);
  delayMicroseconds(5);
  digitalWrite(PIN_RCK, HIGH);
  Serial.println(F("latched - QH should now hold D7's level until the next pulse"));
  delay(LATCH_INTERVAL_MS);
}
