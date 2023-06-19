import pyaudio
import wave
from scipy.io import wavfile
import noisereduce as nr

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 512
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "temp.wav"
device_index = 2

audio = pyaudio.PyAudio()
index = 6


def audio_init():
    global index

    print("----------------------record device list---------------------")
    info = audio.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))

    print("-------------------------------------------------------------")

    index = int(input())
    print("recording via index (selected device) " + str(index))


def record(noise_reduction=False):
    global index, audio, FORMAT, CHANNELS, RATE, CHUNK, RECORD_SECONDS, WAVE_OUTPUT_FILENAME
    stop = False

    while not stop:
        print("Press 's' to start recording and 'q' to stop recording [don't forget to press 'Enter']")
        if 's' in input():
            stream = audio.open(format=FORMAT, channels=CHANNELS,
                                rate=RATE, input=True, input_device_index=index,
                                frames_per_buffer=CHUNK)
            print("Recording started")
            Recordframes = []

            while True:
                for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                    data = stream.read(CHUNK)
                    Recordframes.append(data)
                if stop:
                    break

                if 'q' in input():
                    print("Recording stopped")
                    stop = True

            stream.stop_stream()
            stream.close()
            audio.terminate()

            # save audio file
            waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')

            waveFile.setnchannels(CHANNELS)
            waveFile.setsampwidth(audio.get_sample_size(FORMAT))
            waveFile.setframerate(RATE)
            waveFile.writeframes(b''.join(Recordframes))
            waveFile.close()

    if noise_reduction:
        # load data
        rate, data = wavfile.read(WAVE_OUTPUT_FILENAME)

        # perform noise reduction
        reduced_noise = nr.reduce_noise(y=data, sr=rate, n_jobs=3)

        # write audio to file
        wavfile.write("temp.wav", rate, reduced_noise)