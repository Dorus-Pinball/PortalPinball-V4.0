// Bench-only diagnostic — NOT the trough-bridge firmware. Slowly toggles the RCK and SCK
// lines (2s per state) so each can be checked by eye with a plain DC-volts multimeter, which
// can't catch the real firmware's microsecond-scale pulses. Probe the Uno's own pin first to
// confirm it's actually toggling, then move the same probe to the Stern board's connector pin
// and confirm it matches — a mismatch there (Uno toggles, board pin doesn't) points at the
// wire/connector; a match on both but the bridge still reads 0x00 points inside the board.
//
// Deliberately bypasses the SPI library for SCK (plain digitalWrite) since SPI only drives SCK
// during an active transfer — no use for a slow multimeter-visible toggle here.
//
// Flash the real atmega328p-trough-bridge.ino back afterward; this sketch does not read MISO.

const uint8_t PIN_RCK = 8;   // same pin as the real firmware
const uint8_t PIN_SCK = 13;  // same pin as the real firmware (normally SPI hardware clock)
const unsigned long HALF_PERIOD_MS = 2000;

void setup() {
  pinMode(PIN_RCK, OUTPUT);
  pinMode(PIN_SCK, OUTPUT);
  Serial.begin(9600);
  Serial.println(F("diag-slow-toggle: RCK (D8) and SCK (D13) toggling every 2s"));
}

void loop() {
  digitalWrite(PIN_RCK, HIGH);
  digitalWrite(PIN_SCK, HIGH);
  Serial.println(F("RCK=HIGH SCK=HIGH"));
  delay(HALF_PERIOD_MS);

  digitalWrite(PIN_RCK, LOW);
  digitalWrite(PIN_SCK, LOW);
  Serial.println(F("RCK=LOW  SCK=LOW"));
  delay(HALF_PERIOD_MS);
}
