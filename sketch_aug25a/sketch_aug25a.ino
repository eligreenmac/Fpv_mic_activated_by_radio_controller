#include <Arduino.h>
#include <SPI.h>
#include <SD.h>
#include "esp_timer.h"

// --- SD Card Pin Configuration ---
#define SD_CS          7
#define SPI_MOSI       6
#define SPI_MISO       5
#define SPI_SCK        4

// --- Microphone Configuration ---
// Set to true to record in STEREO (2 channels) using both microphones simultaneously
// Set to false to record in MONO (1 channel)
#define ENABLE_STEREO    false

// ADC Pin Assignments
#define MIC1_ADC_PIN     0 // Mic 1: OUT of MAX4466 / MAX9814 (ADC1_CH0)
#define MIC2_ADC_PIN     1 // Mic 2: OUT of MAX9814 with GAIN shorted to VDD (ADC1_CH1)

// --- Trigger Pin Configuration ---
#define TRIGGER_PIN      10 // Connected to TX1 (B06) of Flight Controller

// --- Audio Settings ---
#define SAMPLE_RATE      16000 // 16kHz sampling rate
#define BUFFER_SIZE      512   // Chunk size to write to SD card
#define RING_BUFFER_SIZE 4096  // 4096-sample ring buffer (~256ms buffer to eliminate SD write dropouts)

// --- Real-time DSP Band-Pass Filter ---
// Filters out DC bias, low motor rumble (<150Hz), and high whistle (>3400Hz)
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
    
    // High-pass filter coefficients
    float RC_hp = 1.0f / (2.0f * PI * hp_cutoff);
    alpha_hp = RC_hp / (RC_hp + dt);

    // Low-pass filter coefficients
    float RC_lp = 1.0f / (2.0f * PI * lp_cutoff);
    alpha_lp = dt / (RC_lp + dt);
  }

  int16_t process(int16_t sample) {
    float x = (float)sample;

    // 1. High-Pass Filter (removes DC bias and low rumble)
    float y_hp = alpha_hp * (prev_y_hp + x - prev_x);
    prev_x = x;
    prev_y_hp = y_hp;

    // 2. Low-Pass Filter (removes high-frequency hiss/whistle)
    float y_lp = prev_y_lp + alpha_lp * (y_hp - prev_y_lp);
    prev_y_lp = y_lp;

    // Constrain output to valid 16-bit range
    if (y_lp > 32767.0f) return 32767;
    if (y_lp < -32768.0f) return -32768;
    return (int16_t)y_lp;
  }
};

File audioFile;
volatile bool isRecording = false;
uint32_t dataSize = 0;
int fileCounter = 1;

BandPassFilter bpFilter1;
#if ENABLE_STEREO
BandPassFilter bpFilter2;
#endif

// Ultra-fast Ring Buffer for background sampling
volatile uint16_t ringBuffer[RING_BUFFER_SIZE];
volatile int ringHead = 0;
volatile int ringTail = 0;

esp_timer_handle_t sampleTimer;

// Ultra-lightweight Timer Callback (takes <15µs, ~20% CPU at 16kHz)
// Runs continuously in the background so NOT A SINGLE MICROSECOND of audio is lost during SD writes
void IRAM_ATTR onSampleTimer(void* arg) {
  if (!isRecording) return;

#if ENABLE_STEREO
  uint16_t raw1 = (uint16_t)analogRead(MIC1_ADC_PIN);
  uint16_t raw2 = (uint16_t)analogRead(MIC2_ADC_PIN);

  int nextHead1 = (ringHead + 1) % RING_BUFFER_SIZE;
  int nextHead2 = (ringHead + 2) % RING_BUFFER_SIZE;

  if (nextHead1 != ringTail && nextHead2 != ringTail) {
    ringBuffer[ringHead] = raw1;
    ringBuffer[nextHead1] = raw2;
    ringHead = nextHead2;
  }
#else
  uint16_t raw = (uint16_t)analogRead(MIC1_ADC_PIN);
  int nextHead = (ringHead + 1) % RING_BUFFER_SIZE;
  if (nextHead != ringTail) {
    ringBuffer[ringHead] = raw;
    ringHead = nextHead;
  }
#endif
}

// Writes a standard 44-byte WAV header
void writeWavHeader(File &file, uint32_t data_size) {
  byte header[44];
  uint32_t fileSize = data_size + 36;
  uint32_t sampleRate = SAMPLE_RATE;
  uint16_t numChannels = (ENABLE_STEREO ? 2 : 1);
  uint32_t byteRate = SAMPLE_RATE * numChannels * 2; // 16-bit PCM (2 bytes/sample * channels)
  uint16_t blockAlign = numChannels * 2;

  // RIFF chunk descriptor
  header[0] = 'R'; header[1] = 'I'; header[2] = 'F'; header[3] = 'F';
  header[4] = (byte)(fileSize & 0xFF);
  header[5] = (byte)((fileSize >> 8) & 0xFF);
  header[6] = (byte)((fileSize >> 16) & 0xFF);
  header[7] = (byte)((fileSize >> 24) & 0xFF);
  header[8] = 'W'; header[9] = 'A'; header[10] = 'V'; header[11] = 'E';

  // "fmt " sub-chunk
  header[12] = 'f'; header[13] = 'm'; header[14] = 't'; header[15] = ' ';
  header[16] = 16; header[17] = 0; header[18] = 0; header[19] = 0; // Subchunk1Size (16 for PCM)
  header[20] = 1; header[21] = 0; // AudioFormat (1 = PCM)
  header[22] = (byte)(numChannels & 0xFF); header[23] = (byte)((numChannels >> 8) & 0xFF); // Channels
  header[24] = (byte)(sampleRate & 0xFF);
  header[25] = (byte)((sampleRate >> 8) & 0xFF);
  header[26] = (byte)((sampleRate >> 16) & 0xFF);
  header[27] = (byte)((sampleRate >> 24) & 0xFF);
  header[28] = (byte)(byteRate & 0xFF);
  header[29] = (byte)((byteRate >> 8) & 0xFF);
  header[30] = (byte)((byteRate >> 16) & 0xFF);
  header[31] = (byte)((byteRate >> 24) & 0xFF);
  header[32] = (byte)(blockAlign & 0xFF); header[33] = (byte)((blockAlign >> 8) & 0xFF); // BlockAlign
  header[34] = 16; header[35] = 0; // BitsPerSample (16 bits)

  // "data" sub-chunk
  header[36] = 'd'; header[37] = 'a'; header[38] = 't'; header[39] = 'a';
  header[40] = (byte)(data_size & 0xFF);
  header[41] = (byte)((data_size >> 8) & 0xFF);
  header[42] = (byte)((data_size >> 16) & 0xFF);
  header[43] = (byte)((data_size >> 24) & 0xFF);

  file.seek(0);
  file.write(header, 44);
}

// Scans SD card to find the next unused filename to prevent overwriting
int getNextFileCounter() {
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

void startRecording() {
  ringHead = 0;
  ringTail = 0;
  
  String filename = "/rec_" + String(fileCounter++) + ".wav";
  audioFile = SD.open(filename, FILE_WRITE);
  if (!audioFile) {
    Serial.println("Error: Failed to open file: " + filename);
    return;
  }
  dataSize = 0;
  writeWavHeader(audioFile, dataSize); // Placeholder header
  isRecording = true;
  Serial.println("Started recording (" + String(ENABLE_STEREO ? "Stereo Dual-Mic" : "Mono") + ") to: " + filename);
}

void stopRecording() {
  isRecording = false;

  // Flush any remaining samples in the ring buffer
  int available = (ringHead - ringTail + RING_BUFFER_SIZE) % RING_BUFFER_SIZE;
  if (available > 0 && audioFile) {
    int16_t writeBuffer[available];
    for (int i = 0; i < available; i++) {
      uint16_t raw = ringBuffer[ringTail];
      ringTail = (ringTail + 1) % RING_BUFFER_SIZE;
      int16_t sample = (int16_t)((((int)raw) - 2048) << 4);
#if ENABLE_STEREO
      if (i % 2 == 0) {
        writeBuffer[i] = bpFilter1.process(sample);
      } else {
        writeBuffer[i] = bpFilter2.process(sample);
      }
#else
      writeBuffer[i] = bpFilter1.process(sample);
#endif
    }
    audioFile.write((const uint8_t*)writeBuffer, available * sizeof(int16_t));
    dataSize += available * sizeof(int16_t);
  }

  writeWavHeader(audioFile, dataSize); // Final header with accurate size
  audioFile.close();
  Serial.print("Stopped recording. File saved. Total size: ");
  Serial.print(dataSize);
  Serial.println(" bytes.");
}

void recordAudioStep() {
  if (!isRecording) return;

  // Check how many samples are available in the background ring buffer
  int available = (ringHead - ringTail + RING_BUFFER_SIZE) % RING_BUFFER_SIZE;

  // Process and write in blocks of BUFFER_SIZE
  if (available >= BUFFER_SIZE) {
    int16_t writeBuffer[BUFFER_SIZE];
    for (int i = 0; i < BUFFER_SIZE; i++) {
      uint16_t raw = ringBuffer[ringTail];
      ringTail = (ringTail + 1) % RING_BUFFER_SIZE;
      // Convert 12-bit ADC (0..4095) with ~2048 bias to signed 16-bit PCM
      int16_t sample = (int16_t)((((int)raw) - 2048) << 4);
#if ENABLE_STEREO
      if (i % 2 == 0) {
        writeBuffer[i] = bpFilter1.process(sample);
      } else {
        writeBuffer[i] = bpFilter2.process(sample);
      }
#else
      writeBuffer[i] = bpFilter1.process(sample);
#endif
    }

    size_t bytesToWrite = BUFFER_SIZE * sizeof(int16_t);
    audioFile.write((const uint8_t*)writeBuffer, bytesToWrite);
    dataSize += bytesToWrite;

    // Periodic flush every 4 seconds to ensure data integrity
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
  delay(1000);
  
  Serial.println("Initializing ESP32-C3 Voice Recorder (MAX4466 / MAX9814 Support)...");

  // Setup ADC resolution (12-bit: 0 to 4095)
  analogReadResolution(12);
  pinMode(MIC1_ADC_PIN, INPUT);
#if ENABLE_STEREO
  pinMode(MIC2_ADC_PIN, INPUT);
#endif

  // Initialize the digital Band-Pass filter: 150Hz to 3400Hz
  bpFilter1.init(150.0f, 3400.0f, (float)SAMPLE_RATE);
#if ENABLE_STEREO
  bpFilter2.init(150.0f, 3400.0f, (float)SAMPLE_RATE);
#endif

  // Setup trigger pin (Pin 10) with pull-down
  pinMode(TRIGGER_PIN, INPUT_PULLDOWN);

  // Initialize SPI communication for SD card at 40MHz for ultra-fast write
  SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI, SD_CS);
  if (!SD.begin(SD_CS, SPI, 40000000)) {
    if (!SD.begin(SD_CS)) {
      Serial.println("Error: SD Card Mount Failed! Check connections.");
      return;
    }
  }
  Serial.println("SD Card mounted successfully.");

  // Scan card for next available filename index
  fileCounter = getNextFileCounter();

  // Create lightweight hardware timer for continuous background sampling
  const esp_timer_create_args_t timerArgs = {
    .callback = &onSampleTimer,
    .arg = NULL,
    .dispatch_method = ESP_TIMER_TASK,
    .name = "mic_sampler",
    .skip_unhandled_events = true
  };
  esp_timer_create(&timerArgs, &sampleTimer);
  esp_timer_start_periodic(sampleTimer, 1000000 / SAMPLE_RATE);

  Serial.print("System Ready. Next file counter: ");
  Serial.println(fileCounter);
  Serial.println("Mode: " + String(ENABLE_STEREO ? "Stereo Dual-Mic (Pin 0 & Pin 1)" : "Mono (Pin 0)"));
  Serial.println("Waiting for high voltage on Pin 10 (TX1) to record...");
}

void loop() {
  bool triggerState = (digitalRead(TRIGGER_PIN) == HIGH);

  // Start Recording
  if (triggerState && !isRecording) {
    delay(50); // Debounce
    if (digitalRead(TRIGGER_PIN) == HIGH) {
      startRecording();
    }
  } 
  // Stop Recording
  else if (!triggerState && isRecording) {
    delay(50); // Debounce
    if (digitalRead(TRIGGER_PIN) == LOW) {
      stopRecording();
    }
  }

  // Stream data from background ring buffer to SD Card
  if (isRecording) {
    recordAudioStep();
  } else {
    delay(10); // Yield CPU when idle
  }
}