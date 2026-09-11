// Trough opto bridge firmware — see plans/read-opto.md and
// design/physical-checklists/trough-opto-bridge.html for the full circuit/context.
//
// Reads the Stern trough opto board (520-7001-00A, NXP 74HCT165D shift register) over its
// VCC/RCK/SCK/MISO/GND connector via hardware SPI, and mirrors the 7 opto channels
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

// ---- Bit-to-channel calibration — VERIFY ON THE BENCH, don't trust this as shipped ----
//
// The 74HC165's shift order is fixed (D7 first, D0 last), but WHICH opto channel lands on
// which D-pin is a fact about this specific Stern board that hasn't been traced — the plan
// explicitly flags this as something to confirm empirically (hand-block each opto channel,
// watch which bit changes), not assume from a datasheet. Edit BIT_CHANNEL and BIT_INVERT below
// once you've done that, matching each bit position (0 = D7 .. 7 = D0, i.e. shift-out order) to
// a slot in MIRROR_PINS (or 0xFF if that bit isn't a channel you're using).
//
// Placeholder mapping assumes the natural D7..D1 = trough1..6, D0 = jam order and no inversion —
// almost certainly wrong until you check it, which is exactly why DEBUG_SERIAL exists below.
const uint8_t UNUSED_SLOT = 0xFF;
uint8_t BIT_CHANNEL[8] = { 0, 1, 2, 3, 4, 5, 6, UNUSED_SLOT }; // bit0(D7)..bit7(D0) -> MIRROR_PINS index
bool BIT_INVERT[8]     = { false, false, false, false, false, false, false, false };

// Set to 1 while bench-testing (prints the raw byte + resolved channel states over the bare
// chip's RX/TX pins, e.g. via the USB-serial bridge breakout already in inventory). Leave off
// for final install — it costs nothing functionally to leave on, but there's no need once the
// mapping above is confirmed.
#define DEBUG_SERIAL 1

const unsigned long POLL_INTERVAL_MS = 10;
const uint8_t STABLE_READS_REQUIRED = 3; // simple debounce: require N consecutive matching reads

uint8_t lastStableByte = 0;
uint8_t candidateByte = 0;
uint8_t candidateCount = 0;

uint8_t readOptoByte() {
  digitalWrite(PIN_RCK, LOW);
  delayMicroseconds(5);   // >> 74HC165's minimum load pulse width, negligible at this poll rate
  digitalWrite(PIN_RCK, HIGH);
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
  digitalWrite(PIN_RCK, HIGH);

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
#if DEBUG_SERIAL
    Serial.print(F("raw=0b"));
    for (int8_t b = 7; b >= 0; b--) Serial.print((raw >> b) & 1);
    Serial.println();
#endif
  }

  delay(POLL_INTERVAL_MS);
}
