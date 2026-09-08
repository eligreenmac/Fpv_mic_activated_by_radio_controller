# FPV Microphone Activated by Radio Controller 🎙️🚁

An autonomous, ultra-low-latency voice/audio recording system for FPV drones. Powered by an **ESP32-C3 Super Mini** and an analog **MAX4466** or **MAX9814** microphone, recording directly to a MicroSD card in standard 16-bit PCM WAV format.

Recording is triggered seamlessly from a radio controller switch (AUX channel) via Betaflight `PINIO` resource remapping on a Flight Controller UART TX pin.

---

## Supported Microphones (Drop-in Replacements)

You can choose either of the following two microphones (both connect to **GPIO 0** without any code changes):

### Option 1: MAX4466 (Adjustable Potentiometer)
- **Wiring**: `OUT` ➔ `GPIO 0`, `VCC` ➔ `3.3`, `GND` ➔ `G`.
- **Tuning**: Turn the small trimmer potentiometer on the back **counter-clockwise (left)** almost all the way down to dial the gain down to 25x (minimum) to prevent motor sound saturation.

### Option 2: MAX9814 (Automatic Gain Control - AGC)
- **Wiring**: `OUT` ➔ `GPIO 0`, `VDD` ➔ `3.3`, `GND` ➔ `G`.
- **Gain Setting**: Solder/bridge a short wire between the **`GAIN`** pin and the **`VDD`** pin. This locks the gain to **40dB (Minimum)**, enabling the hardware AGC to automatically compress loud motor noise while capturing clear audio without clipping.

---

## Hardware Wiring Table

| Component | Component Pin | ESP32-C3 Pin | Notes |
| :--- | :--- | :--- | :--- |
| **Microphone (MAX4466 or MAX9814)** | `VCC / VDD` | `3.3` | Regulated 3.3V Power |
| | `GND` | `G` (GND) | Shared Ground |
| | `OUT` | `0` (GPIO 0) | ADC1_CH0 Analog Input |
| | *`GAIN` (MAX9814 only)* | *`VDD` (Short)* | *Locks gain to 40dB (Minimum)* |
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

## Features
- **Remote Control Trigger**: Start and stop recording on-the-fly using an AUX switch on your RC transmitter (e.g. EdgeTX/OpenTX/TBS/ELRS).
- **100% Video/Audio Sync**: Continuous background hardware-timer ADC sampling with ring-buffering guarantees zero dropped samples during SD card sector writes, keeping audio perfectly synchronized with 60fps/120fps action camera video.
- **Real-time DSP Band-Pass Filter**: Filters out sub-audible frame vibrations (<150Hz) and high-frequency propeller whistle (>3400Hz) directly on the ESP32-C3 FPU.
- **Crash & Power-Loss Protection**: Periodically flushes data to the SD card so recordings remain intact even if the LiPo battery ejects during a crash.
- **Automatic File Indexing**: Automatically scans the SD card on boot to find the next available `/rec_N.wav` index, preventing accidental overwrites.

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
