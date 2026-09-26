// Trough opto bridge firmware — see plans/read-opto.md and
// design/physical-checklists/trough-opto-bridge.html for the full circuit/context.
//
// Reads the Stern trough opto board (520-7001-00A, or 520-8516-00 via its CN1 "SERIAL IN"
// connector; NXP 74HCT165D shift register) over its VCC/RCK/SCK/MISO/GND connector via hardware
// SPI, and mirrors the 7 opto channels
// (s-trough1..6, s-trough-jam) onto 7 GPIO pins wired into OPP's existing switch wing —
// replacing the fragile hand-soldered per-leg taps that caused the wiring damage logged in
// commit 859a6b9.
//
// Target: bare ATmega328P-PU, internal 8 MHz oscillator (flashed via tools/flash-atmega328p.ps1
// using MiniCore — see that script's header for why fuse values come from MiniCore rather than
// being hand-typed here).

#include <SPI.h>

// ---- Pin map (matches design/physical-checklists/trough-opto-bridge.html, Section 2/3) ----
const uint8_t PIN_RCK = 8;   // PB0 / DIP pin 14 — latch pulse to the 74HC165 (not part of SPI)
// SCK (13/PB5), MISO (12/PB4), MOSI (11/PB3), SS (10/PB2) are driven by the SPI library /
// hardware wiring (SS is also tied high in hardware — see the build sheet).

const uint8_t MIRROR_PINS[7] = {
  3,  // PD3 — bit slot 0 below
  4,  // PD4 — bit slot 1
  5,  // PD5 — bit slot 2
  6,  // PD6 — bit slot 3
  7,  // PD7 — bit slot 4
  A0, // PC0 — bit slot 5
  A1, // PC1 — bit slot 6
};

// ---- Bit-to-channel calibration ----
//
// Bench-verified 2026-09-26 on a 520-8516-00 board by blocking each opto one at a time. Raw byte
// (bit7 first out): bit7 = unused input (always 0), bit6 = jam, bit5..bit0 = trough positions
// 1..6. Every channel reads 1 = clear, 0 = blocked. Array index 0..7 = raw bit7..bit0; values are
// MIRROR_PINS slots (0..5 = trough1..6, 6 = jam).
//
// BIT_INVERT is still unset: the output polarity OPP needs (its switches are `type: NC`, and
// s-trough-jam's active state means a CLEAR path) must be confirmed against MPF's switch states
// on the real cabinet, not assumed here.
const uint8_t UNUSED_SLOT = 0xFF;
uint8_t BIT_CHANNEL[8] = { UNUSED_SLOT, 6, 0, 1, 2, 3, 4, 5 }; // raw bit7..bit0 -> MIRROR_PINS index
bool BIT_INVERT[8]     = { false, false, false, false, false, false, false, false };

// Set to 1 while bench-testing (prints the raw byte + resolved channel states over the bare
// chip's RX/TX pins, e.g. via the USB-serial bridge breakout already in inventory). Leave off
// for final install — it costs nothing functionally to leave on, but there's no need once the
// mapping above is confirmed.
#define DEBUG_SERIAL 1

const unsigned long POLL_INTERVAL_MS = 10;
const uint8_t STABLE_READS_REQUIRED = 3; // simple debounce: require N consecutive matching reads
const unsigned long DEBUG_STREAM_INTERVAL_MS = 200; // unconditional heartbeat, see loop()

uint8_t lastStableByte = 0xFF; // never a real read on a 520-8516-00 (bit7 always 0), so the first stable read applies
uint8_t candidateByte = 0;
uint8_t candidateCount = 0;
unsigned long lastDebugStreamMs = 0;

// RCK is inverted on the board (74HC540 A8 -> Y8 -> 165's SH/LD, confirmed by continuity):
// RCK HIGH = parallel load, RCK LOW = shift. So idle LOW, pulse HIGH to latch.
uint8_t readOptoByte() {
  digitalWrite(PIN_RCK, HIGH);
  delayMicroseconds(5);   // >> 74HC165's minimum load pulse width, negligible at this poll rate
  digitalWrite(PIN_RCK, LOW);
  delayMicroseconds(5);
  return SPI.transfer(0x00); // bit7 = D7 (first channel shifted out) .. bit0 = D0 (last)
}

void applyMirrors(uint8_t raw) {
  for (uint8_t bit = 0; bit < 8; bit++) {
    uint8_t slot = BIT_CHANNEL[bit];
    if (slot == UNUSED_SLOT) continue;
    bool set = (raw >> (7 - bit)) & 0x01;
    if (BIT_INVERT[bit]) set = !set;
    digitalWrite(MIRROR_PINS[slot], set ? HIGH : LOW);
  }
}

void setup() {
  pinMode(PIN_RCK, OUTPUT);
  digitalWrite(PIN_RCK, LOW);

  for (uint8_t i = 0; i < 7; i++) {
    pinMode(MIRROR_PINS[i], OUTPUT);
  }

  SPI.begin();
  // Conservative clock — this only needs to poll a handful of times a second, no reason to push
  // SPI speed on a hand-wired breadboard link.
  SPI.beginTransaction(SPISettings(250000, MSBFIRST, SPI_MODE0));

#if DEBUG_SERIAL
  Serial.begin(9600);
  Serial.println(F("trough-opto-bridge: raw byte is bit7=D7(first)..bit0=D0(last)"));
#endif
}

void loop() {
  uint8_t raw = readOptoByte();

#if DEBUG_SERIAL
  // Unconditional heartbeat, independent of the debounce below — during bench calibration you
  // need to see "nothing has changed" as a continuous stream of identical lines to distinguish
  // it from a dead SPI link (which looks the same as silence otherwise). Rate-limited so it's
  // readable, not gated on any state change.
  unsigned long now = millis();
  if (now - lastDebugStreamMs >= DEBUG_STREAM_INTERVAL_MS) {
    lastDebugStreamMs = now;
    Serial.print(F("raw=0b"));
    for (int8_t b = 7; b >= 0; b--) Serial.print((raw >> b) & 1);
    Serial.println();
  }
#endif

  // Debounce: only commit a reading once it's repeated a few polls in a row, so a single noisy
  // transition (e.g. a ball mid-roll across a sensor edge) doesn't glitch the mirrored switches.
  if (raw == candidateByte) {
    if (candidateCount < 255) candidateCount++;
  } else {
    candidateByte = raw;
    candidateCount = 1;
  }

  if (candidateCount == STABLE_READS_REQUIRED && raw != lastStableByte) {
    lastStableByte = raw;
    applyMirrors(raw);
  }

  delay(POLL_INTERVAL_MS);
}
