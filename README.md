# FPV Microphone Activated by Radio Controller 🎙️🚁

An autonomous, ultra-low-latency voice/audio recording system for FPV drones. Powered by an **ESP32-C3 Super Mini** and analog **MAX4466 / MAX9814** microphone(s), recording directly to a MicroSD card in standard 16-bit PCM WAV format.

Recording is triggered seamlessly from a radio controller switch (AUX channel) via Betaflight `PINIO` resource remapping on a Flight Controller UART TX pin.

---

## Features
- **Remote Control Trigger**: Start and stop recording on-the-fly using an AUX switch on your RC transmitter (e.g. EdgeTX/OpenTX/TBS/ELRS).
- **100% Video/Audio Sync**: Continuous background hardware-timer ADC sampling with ring-buffering guarantees zero dropped samples during SD card sector writes, keeping audio perfectly synchronized with 60fps/120fps action camera video.
- **Dual Microphone & Stereo Support**:
  - **Single Mic (Mono)**: MAX4466 (trimpot gain) or MAX9814 (AGC).
  - **Dual Mic (Stereo)**: Record 2 channels simultaneously (e.g. Front/Pilot Voice + Rear/Motor Ambience).
- **Anti-Saturation AGC (MAX9814)**: Connect `GAIN` to `VDD` to lock the MAX9814 at its minimum **40dB gain**, allowing the built-in Automatic Gain Control (AGC) to suppress loud motor blasts while keeping voices clear.
- **Adjustable Trimmer (MAX4466)**: Built-in potentiometer to physically dial down gain to 25x.
- **Real-time DSP Band-Pass Filter**: Dual digital filters eliminate sub-audible frame vibrations (<150Hz) and high-frequency propeller whistle (>3400Hz) directly on the ESP32-C3 FPU.
- **Crash & Power-Loss Protection**: Periodically flushes and syncs data to the SD card so recordings remain intact even if the LiPo battery ejects during a crash.
- **Automatic File Indexing**: Automatically scans the SD card on boot to find the next available `/rec_N.wav` index, preventing accidental overwrites.

---

## Hardware Wiring

### ESP32-C3 Super Mini Pinout

| Component | Component Pin | ESP32-C3 Pin | Notes |
| :--- | :--- | :--- | :--- |
| **Mic 1: MAX4466 / MAX9814** | `VCC / VDD` | `3.3` | Regulated 3.3V |
| | `GND` | `G` (GND) | Shared Ground |
| | `OUT` | `0` (GPIO 0) | ADC1_CH0 Analog Input (Left / Mono) |
| **Mic 2: MAX9814 (Optional)** | `VDD` | `3.3` | 3.3V Power |
| | `GND` | `G` | Ground |
| | `OUT` | `1` (GPIO 1) | ADC1_CH1 Analog Input (Right Channel) |
| | `GAIN` | `VDD` *(Short)* | **Locks gain to 40dB (Minimum)** for high noise |
| **MicroSD SPI Module** | `VCC / 3v3` | `3.3` | 3.3V Power |
| | `GND` | `G` | Ground |
| | `MISO` | `5` | SPI MISO |
| | `MOSI` | `6` | SPI MOSI |
| | `SCK / CLK` | `4` | SPI SCK |
| | `CS` | `7` | SPI Chip Select |
| **Flight Controller** | `4.5V / 5V` | `5V` | Powered from FC (USB or LiPo) |
| | `GND` | `G` | Shared Ground |
| | `TX1 (e.g. B06)` | `10` (GPIO 10) | 3.3V Logic Trigger Input |

---

## Microphone Gain Configuration

### 1. MAX9814 (Automatic Gain Control - AGC)
- **40dB Gain (Recommended for FPV)**: Connect/solder a bridge wire between the **`GAIN`** pin and the **`VDD`** pin. This locks the amplifier to 40dB and lets the AGC compress loud propeller/motor noise automatically.
- **50dB Gain**: Connect `GAIN` to `GND`.
- **60dB Gain**: Leave `GAIN` disconnected (floating).

### 2. MAX4466 (Manual Potentiometer)
- Turn the brass screw on the back **counter-clockwise (left)** almost all the way to dial the gain down to 25x.

---

## Mono vs. Stereo Mode
In the Arduino sketch (`sketch_aug25a.ino`), configure:
```cpp
#define ENABLE_STEREO true  // Set to 'true' for 2-channel Stereo, or 'false' for 1-channel Mono
```

---

## Betaflight Setup (PINIO Trigger)

To control the recording trigger from your radio transmitter using a spare TX pad (e.g. `TX1`):

1. Connect your flight controller to **Betaflight Configurator**.
2. Go to the **CLI** tab and find your TX1 pin name by typing:
   ```text
   resource
   ```
   *(Look for `resource SERIAL_TX 1 <PIN>`, e.g. `B06`).*

3. Remap the pin to `PINIO 1` by executing:
   ```text
   resource SERIAL_TX 1 NONE
   resource PINIO 1 B06
   set pinio_config = 1,129,129,129
   set pinio_box = 40,255,255,255
   save
   ```

4. Go to the **Modes** tab in Betaflight Configurator:
   - Find the **USER1** mode.
   - Click **Add Range** and assign it to your desired **AUX** switch.
   - Set the active range so that flipping the switch activates `USER1` (outputs 3.3V on TX1) to start recording, and deactivates it (0V on TX1) to stop and save the WAV file.

---

## Arduino IDE Settings
- **Board**: `ESP32C3 Dev Module`
- **USB CDC On Boot**: `Enabled` *(Essential for Serial Monitor output)*
- **Upload Speed**: `921600` or `115200`
- **Flash Frequency**: `80MHz`
- **MicroSD Format**: `FAT32`
