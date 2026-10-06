#include <Arduino.h>
#include <SPI.h>
#include <SD.h>
#include <WiFi.h>
#include <WebServer.h>
#include "esp_timer.h"

// --- Wi-Fi Access Point Configuration ---
#define AP_SSID          "FPV-Audio-Recorder"
#define AP_PASS          ""         // Open network (no password) for 100% phone discovery compatibility
#define AP_CHANNEL       1          // Channel 1 has maximum global compatibility

// --- Onboard LED (ESP32-C3 SuperMini) ---
#define LED_PIN          8          // Built-in Blue LED for status/heartbeat

// --- SD Card Pin Configuration ---
#define SD_CS            7
#define SPI_MOSI         6
#define SPI_MISO         5
#define SPI_SCK          4

// --- Analog Microphone Pin ---
// Connect OUT of MAX4466 OR MAX9814 (with GAIN shorted to VDD)
#define MIC_ADC_PIN      0

// --- Trigger Pin Configuration ---
#define TRIGGER_PIN      10 // Connected to TX pin of Flight Controller

// --- Audio Settings ---
#define SAMPLE_RATE      16000 // 16kHz sampling rate
#define BUFFER_SIZE      512   // Chunk size to write to SD card
#define RING_BUFFER_SIZE 4096  // 4096-sample ring buffer (~256ms buffer)

// --- Real-time DSP Band-Pass Filter ---
class BandPassFilter {
private:
  float alpha_hp;
  float alpha_lp;
  float prev_x = 0;
  float prev_y_hp = 0;
  float prev_y_lp = 0;

public:
  void init(float hp_cutoff, float lp_cutoff, float sample_rate) {
    float dt = 1.0f / sample_rate;
    float RC_hp = 1.0f / (2.0f * PI * hp_cutoff);
    alpha_hp = RC_hp / (RC_hp + dt);

    float RC_lp = 1.0f / (2.0f * PI * lp_cutoff);
    alpha_lp = dt / (RC_lp + dt);
  }

  int16_t process(int16_t sample) {
    float x = (float)sample;
    float y_hp = alpha_hp * (prev_y_hp + x - prev_x);
    prev_x = x;
    prev_y_hp = y_hp;

    float y_lp = prev_y_lp + alpha_lp * (y_hp - prev_y_lp);
    prev_y_lp = y_lp;

    if (y_lp > 32767.0f) return 32767;
    if (y_lp < -32768.0f) return -32768;
    return (int16_t)y_lp;
  }
};

File audioFile;
volatile bool isRecording = false;
bool sdMounted = false;
uint32_t dataSize = 0;
int fileCounter = 1;
BandPassFilter bpFilter;

// Ultra-fast Ring Buffer for background sampling
volatile uint16_t ringBuffer[RING_BUFFER_SIZE];
volatile int ringHead = 0;
volatile int ringTail = 0;

esp_timer_handle_t sampleTimer = NULL;
bool timerRunning = false;
WebServer server(80);

// Hardware Timer Callback (Runs at 16kHz ONLY while recording)
void IRAM_ATTR onSampleTimer(void* arg) {
  if (!isRecording) return;

  uint16_t raw = (uint16_t)analogRead(MIC_ADC_PIN);
  int nextHead = (ringHead + 1) % RING_BUFFER_SIZE;
  if (nextHead != ringTail) {
    ringBuffer[ringHead] = raw;
    ringHead = nextHead;
  }
}

// Writes a standard 44-byte WAV header
void writeWavHeader(File &file, uint32_t data_size) {
  byte header[44];
  uint32_t fileSize = data_size + 36;
  uint32_t sampleRate = SAMPLE_RATE;
  uint32_t byteRate = SAMPLE_RATE * 2; // 16-bit Mono

  // RIFF header
  header[0] = 'R'; header[1] = 'I'; header[2] = 'F'; header[3] = 'F';
  header[4] = (byte)(fileSize & 0xFF);
  header[5] = (byte)((fileSize >> 8) & 0xFF);
  header[6] = (byte)((fileSize >> 16) & 0xFF);
  header[7] = (byte)((fileSize >> 24) & 0xFF);
  header[8] = 'W'; header[9] = 'A'; header[10] = 'V'; header[11] = 'E';

  // "fmt " sub-chunk
  header[12] = 'f'; header[13] = 'm'; header[14] = 't'; header[15] = ' ';
  header[16] = 16; header[17] = 0; header[18] = 0; header[19] = 0; // PCM
  header[20] = 1; header[21] = 0; // AudioFormat
  header[22] = 1; header[23] = 0; // Mono (1 channel)
  header[24] = (byte)(sampleRate & 0xFF);
  header[25] = (byte)((sampleRate >> 8) & 0xFF);
  header[26] = (byte)((sampleRate >> 16) & 0xFF);
  header[27] = (byte)((sampleRate >> 24) & 0xFF);
  header[28] = (byte)(byteRate & 0xFF);
  header[29] = (byte)((byteRate >> 8) & 0xFF);
  header[30] = (byte)((byteRate >> 16) & 0xFF);
  header[31] = (byte)((byteRate >> 24) & 0xFF);
  header[32] = 2; header[33] = 0; // BlockAlign
  header[34] = 16; header[35] = 0; // 16 bits per sample

  // "data" sub-chunk
  header[36] = 'd'; header[37] = 'a'; header[38] = 't'; header[39] = 'a';
  header[40] = (byte)(data_size & 0xFF);
  header[41] = (byte)((data_size >> 8) & 0xFF);
  header[42] = (byte)((data_size >> 16) & 0xFF);
  header[43] = (byte)((data_size >> 24) & 0xFF);

  file.seek(0);
  file.write(header, 44);
}

int getNextFileCounter() {
  if (!sdMounted) return 1;
  int counter = 1;
  while (true) {
    String filename = "/rec_" + String(counter) + ".wav";
    if (!SD.exists(filename)) {
      break;
    }
    counter++;
  }
  return counter;
}

// Start Wi-Fi Access Point on Channel 1 with Safe 8.5dBm TX Power
void startWiFiAP() {
  Serial.println("Configuring Wi-Fi AP...");

  WiFi.persistent(false);
  WiFi.disconnect(true);
  delay(100);
  WiFi.mode(WIFI_AP);

  // Lower TX power prevents RF reflection and brownouts on ESP32-C3 SuperMini
  WiFi.setTxPower(WIFI_POWER_8_5dBm);

  IPAddress local_IP(192, 168, 4, 1);
  IPAddress gateway(192, 168, 4, 1);
  IPAddress subnet(255, 255, 255, 0);
  WiFi.softAPConfig(local_IP, gateway, subnet);

  // Open network (no password) on Channel 1 for 100% phone discovery compatibility
  bool apStarted = WiFi.softAP(AP_SSID, NULL, 1);

  if (apStarted) {
    Serial.println("SUCCESS: Wi-Fi AP is Broadcasting!");
    Serial.print("SSID: ");
    Serial.println(AP_SSID);
    Serial.print("AP MAC Address: ");
    Serial.println(WiFi.softAPmacAddress());
    Serial.print("Connect to: http://");
    Serial.println(WiFi.softAPIP());
  } else {
    Serial.println("ERROR: Failed to start Wi-Fi SoftAP!");
  }

  server.begin();
}

// HTML Web Interface
void handleRoot() {
  String html = "<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>";
  html += "<title>FPV Audio Recorder</title><style>";
  html += "body{font-family:system-ui,-apple-system,sans-serif;background:#121212;color:#e0e0e0;padding:15px;margin:0;}";
  html += ".card{background:#1e1e1e;border-radius:12px;padding:16px;margin-bottom:16px;box-shadow:0 4px 12px rgba(0,0,0,0.5);}";
  html += "h1{font-size:22px;margin:0 0 10px;color:#4caf50;display:flex;align-items:center;gap:8px;}";
  html += ".status{font-size:14px;color:#aaa;margin-bottom:15px;line-height:1.6;}";
  html += ".badge{display:inline-block;padding:4px 8px;border-radius:4px;font-weight:bold;font-size:12px;}";
  html += ".badge-rec{background:#f44336;color:#fff;}";
  html += ".badge-idle{background:#4caf50;color:#fff;}";
  html += ".file-item{display:flex;flex-direction:column;gap:8px;padding:12px;background:#2a2a2a;border-radius:8px;margin-bottom:10px;}";
  html += ".file-info{display:flex;justify-content:space-between;font-weight:600;font-size:16px;color:#fff;}";
  html += ".file-meta{font-size:13px;color:#888;}";
  html += "audio{width:100%;height:36px;margin-top:4px;}";
  html += ".actions{display:flex;gap:10px;margin-top:6px;}";
  html += "a.btn{flex:1;text-align:center;padding:10px;border-radius:6px;text-decoration:none;font-weight:600;font-size:14px;}";
  html += ".btn-download{background:#007bff;color:#fff;}";
  html += ".btn-delete{background:#dc3545;color:#fff;max-width:80px;}";
  html += ".refresh{display:block;text-align:center;padding:12px;background:#4caf50;color:#fff;border-radius:8px;text-decoration:none;font-weight:bold;margin-top:15px;}";
  html += "</style></head><body>";

  html += "<div class='card'>";
  html += "<h1>🎙️ FPV Audio Recorder</h1>";
  html += "<div class='status'>";
  html += "Status: " + String(isRecording ? "<span class='badge badge-rec'>● RECORDING ACTIVE</span>" : "<span class='badge badge-idle'>● STANDBY</span>") + "<br>";
  html += "Storage: " + String(sdMounted ? "<span style='color:#4caf50;'>MicroSD Ready</span>" : "<span style='color:#f44336;'>MicroSD Mount Failed</span>");
  html += "</div></div>";

  html += "<div class='card'>";
  html += "<h2>📁 Recorded Audio Files</h2>";

  int count = 0;
  if (sdMounted) {
    File root = SD.open("/");
    if (root) {
      File file = root.openNextFile();
      while (file) {
        String name = String(file.name());
        if (!file.isDirectory() && name.endsWith(".wav")) {
          count++;
          size_t sizeBytes = file.size();
          float sizeMB = sizeBytes / (1024.0 * 1024.0);
          int durationSec = sizeBytes / (SAMPLE_RATE * 2);
          int mins = durationSec / 60;
          int secs = durationSec % 60;

          html += "<div class='file-item'>";
          html += "<div class='file-info'><span>" + name + "</span><span>" + String(sizeMB, 2) + " MB</span></div>";
          html += "<div class='file-meta'>Duration: ~" + String(mins) + "m " + (secs < 10 ? "0" : "") + String(secs) + "s</div>";
          html += "<audio controls preload='none' src='/stream?file=" + name + "'></audio>";
          html += "<div class='actions'>";
          html += "<a class='btn btn-download' href='/download?file=" + name + "'>📥 Download</a>";
          html += "<a class='btn btn-delete' href='/delete?file=" + name + "' onclick=\"return confirm('Delete " + name + "?')\">🗑️ Delete</a>";
          html += "</div>";
          html += "</div>";
        }
        file = root.openNextFile();
      }
      root.close();
    }
  }

  if (count == 0) {
    html += "<p style='color:#777;text-align:center;'>No recordings found on SD card.</p>";
  }

  html += "<a class='refresh' href='/'>🔄 Refresh List</a>";
  html += "</div>";
  html += "</body></html>";

  server.send(200, "text/html", html);
}

// Download WAV file
void handleDownload() {
  if (!sdMounted || !server.hasArg("file")) {
    server.send(400, "text/plain", "Missing file parameter or SD unmounted");
    return;
  }
  String filename = server.arg("file");
  if (!filename.startsWith("/")) filename = "/" + filename;

  if (!SD.exists(filename)) {
    server.send(404, "text/plain", "File not found");
    return;
  }
  File downloadFile = SD.open(filename, FILE_READ);
  if (!downloadFile) {
    server.send(500, "text/plain", "Failed to open file");
    return;
  }
  server.sendHeader("Content-Disposition", "attachment; filename=\"" + filename.substring(1) + "\"");
  server.streamFile(downloadFile, "audio/wav");
  downloadFile.close();
}

// Stream audio for in-browser playback
void handleStream() {
  if (!sdMounted || !server.hasArg("file")) {
    server.send(400, "text/plain", "Missing file parameter or SD unmounted");
    return;
  }
  String filename = server.arg("file");
  if (!filename.startsWith("/")) filename = "/" + filename;

  if (!SD.exists(filename)) {
    server.send(404, "text/plain", "File not found");
    return;
  }
  File streamFile = SD.open(filename, FILE_READ);
  if (!streamFile) {
    server.send(500, "text/plain", "Failed to open file");
    return;
  }
  server.streamFile(streamFile, "audio/wav");
  streamFile.close();
}

// Delete file from SD card
void handleDelete() {
  if (sdMounted && server.hasArg("file")) {
    String filename = server.arg("file");
    if (!filename.startsWith("/")) filename = "/" + filename;
    if (SD.exists(filename)) {
      SD.remove(filename);
      Serial.println("Deleted: " + filename);
    }
  }
  server.sendHeader("Location", "/");
  server.send(303);
}

void startRecording() {
  if (isRecording) return;

  if (!sdMounted) {
    Serial.println("Cannot record: MicroSD card is not mounted!");
    return;
  }

  ringHead = 0;
  ringTail = 0;

  String filename = "/rec_" + String(fileCounter++) + ".wav";
  audioFile = SD.open(filename, FILE_WRITE);
  if (!audioFile) {
    Serial.println("Error: Failed to open file: " + filename);
    return;
  }
  dataSize = 0;
  writeWavHeader(audioFile, dataSize);
  isRecording = true;

  // Start 16kHz hardware sampling timer ONLY when recording starts
  if (sampleTimer && !timerRunning) {
    esp_timer_start_periodic(sampleTimer, 1000000 / SAMPLE_RATE);
    timerRunning = true;
  }

  Serial.println("Started recording to: " + filename);
}

void stopRecording() {
  if (!isRecording) return;
  isRecording = false;

  // Stop sampling timer immediately to free CPU
  if (sampleTimer && timerRunning) {
    esp_timer_stop(sampleTimer);
    timerRunning = false;
  }

  // Flush remaining ring buffer samples
  int available = (ringHead - ringTail + RING_BUFFER_SIZE) % RING_BUFFER_SIZE;
  if (available > 0 && audioFile) {
    int16_t writeBuffer[available];
    for (int i = 0; i < available; i++) {
      uint16_t raw = ringBuffer[ringTail];
      ringTail = (ringTail + 1) % RING_BUFFER_SIZE;
      int16_t sample = (int16_t)((((int)raw) - 2048) << 4);
      writeBuffer[i] = bpFilter.process(sample);
    }
    audioFile.write((const uint8_t*)writeBuffer, available * sizeof(int16_t));
    dataSize += available * sizeof(int16_t);
  }

  if (audioFile) {
    writeWavHeader(audioFile, dataSize);
    audioFile.close();
    Serial.print("Stopped recording. File saved. Total size: ");
    Serial.print(dataSize);
    Serial.println(" bytes.");
  }
}

void recordAudioStep() {
  if (!isRecording) return;

  int available = (ringHead - ringTail + RING_BUFFER_SIZE) % RING_BUFFER_SIZE;

  if (available >= BUFFER_SIZE) {
    int16_t writeBuffer[BUFFER_SIZE];
    for (int i = 0; i < BUFFER_SIZE; i++) {
      uint16_t raw = ringBuffer[ringTail];
      ringTail = (ringTail + 1) % RING_BUFFER_SIZE;
      int16_t sample = (int16_t)((((int)raw) - 2048) << 4);
      writeBuffer[i] = bpFilter.process(sample);
    }

    size_t bytesToWrite = BUFFER_SIZE * sizeof(int16_t);
    audioFile.write((const uint8_t*)writeBuffer, bytesToWrite);
    dataSize += bytesToWrite;

    static uint32_t lastFlushTime = 0;
    uint32_t now = millis();
    if (now - lastFlushTime > 4000) {
      lastFlushTime = now;
      audioFile.flush();
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(1500);

  Serial.println("\n==========================================");
  Serial.println("   FPV Voice Recorder + Wi-Fi Server      ");
  Serial.println("==========================================");

  // 1. Setup Web Server routes
  server.on("/", handleRoot);
  server.on("/download", handleDownload);
  server.on("/stream", handleStream);
  server.on("/delete", handleDelete);

  // 2. Start Wi-Fi Access Point immediately on boot
  startWiFiAP();

  // 3. Setup Status LED & ADC resolution (12-bit)
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  analogReadResolution(12);
  pinMode(MIC_ADC_PIN, INPUT);

  // 4. Initialize DSP Filter
  bpFilter.init(150.0f, 3400.0f, (float)SAMPLE_RATE);

  // 5. Setup trigger pin with pull-down
  pinMode(TRIGGER_PIN, INPUT_PULLDOWN);

  // 6. Initialize SD Card
  SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI, SD_CS);
  for (int retry = 0; retry < 3; retry++) {
    if (SD.begin(SD_CS, SPI, 40000000) || SD.begin(SD_CS)) {
      sdMounted = true;
      break;
    }
    delay(150);
  }

  if (sdMounted) {
    Serial.println("MicroSD Card: MOUNTED OK");
    fileCounter = getNextFileCounter();
  } else {
    Serial.println("MicroSD Card: NOT DETECTED (Check insertion)");
  }

  // 7. Create hardware sampling timer (only start during recording)
  const esp_timer_create_args_t timerArgs = {
    .callback = &onSampleTimer,
    .arg = NULL,
    .dispatch_method = ESP_TIMER_TASK,
    .name = "mic_sampler",
    .skip_unhandled_events = true
  };
  esp_timer_create(&timerArgs, &sampleTimer);

  Serial.println("------------------------------------------");
  Serial.print("Next Recording File: /rec_");
  Serial.print(fileCounter);
  Serial.println(".wav");
  Serial.print("Wi-Fi Network Name: ");
  Serial.println(AP_SSID);
  Serial.println("Wi-Fi Security:     OPEN (No Password)");
  Serial.println("Web Address:        http://192.168.4.1");
  Serial.println("==========================================\n");
}

void loop() {
  // Visual heartbeat LED (Blinks slow when idle, fast when recording)
  static uint32_t lastBlinkTime = 0;
  static bool ledState = false;
  uint32_t blinkInterval = isRecording ? 100 : 600; // 100ms on REC, 600ms on STANDBY
  if (millis() - lastBlinkTime >= blinkInterval) {
    lastBlinkTime = millis();
    ledState = !ledState;
    digitalWrite(LED_PIN, ledState ? HIGH : LOW);
  }

  // Allow 3 seconds boot stabilization before listening to trigger
  if (millis() > 3000) {
    bool triggerState = (digitalRead(TRIGGER_PIN) == HIGH);

    // Start Recording
    if (triggerState && !isRecording) {
      delay(50);
      if (digitalRead(TRIGGER_PIN) == HIGH) {
        startRecording();
      }
    }
    // Stop Recording
    else if (!triggerState && isRecording) {
      delay(50);
      if (digitalRead(TRIGGER_PIN) == LOW) {
        stopRecording();
      }
    }
  }

  // Stream audio while recording
  if (isRecording) {
    recordAudioStep();
  }

  // Handle web server clients
  server.handleClient();
  delay(2);
}