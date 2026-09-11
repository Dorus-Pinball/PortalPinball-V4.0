// Bench-only diagnostic — NOT the trough-bridge firmware. Poor-man's logic analyzer: streams up
// to 4 spare Uno digital pins continuously so multiple U1 (74HC165) pins can be watched live
// while physically moving the trough board over its emitters, without needing dedicated logic
// analyzer hardware. Wire spare Uno pins A2/A3/A4/A5 directly to whichever U1 legs you want to
// watch (which physical U1 pin goes to which channel is tracked in conversation, not code).
//
// Flash the real atmega328p-trough-bridge.ino back afterward.

const uint8_t CHANNEL_PINS[4] = { A2, A3, A4, A5 };
const unsigned long STREAM_INTERVAL_MS = 150;

void setup() {
  for (uint8_t i = 0; i < 4; i++) {
    pinMode(CHANNEL_PINS[i], INPUT);
  }
  Serial.begin(9600);
  Serial.println(F("diag-multichannel-read: A2 A3 A4 A5"));
}

void loop() {
  Serial.print(digitalRead(CHANNEL_PINS[0]));
  Serial.print(' ');
  Serial.print(digitalRead(CHANNEL_PINS[1]));
  Serial.print(' ');
  Serial.print(digitalRead(CHANNEL_PINS[2]));
  Serial.print(' ');
  Serial.println(digitalRead(CHANNEL_PINS[3]));
  delay(STREAM_INTERVAL_MS);
}
