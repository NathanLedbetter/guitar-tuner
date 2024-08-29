import time
import librosa
import numpy
import pyaudio
import wave

CHUNK = 1024
RATE = 22050
FORMAT = pyaudio.paInt16
CHANNELS = 1

print("CTRL + C to exit")
start = time.perf_counter()

try:
    while True:

        #Taking snippets of live audio input then saving to a wav file
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        frames = []
        seconds = 2
        for i in range (0, int(RATE / CHUNK * seconds)):
            data = stream.read(CHUNK)
            frames.append(data)
        start = time.perf_counter()
        stream.stop_stream()
        stream.close()
        p.terminate()

        #TODO get rid of unnecessary file I/O here
        wf = wave.open("output.wav", 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        #Reading in and trimming the file contents
        #trim returns an array of two items, the first item is the trimmed array
        audio_array, sample_rate = librosa.load("output.wav")
        audio_array = librosa.effects.trim(audio_array)[0]

        #Fast Fourier transform
        sp = numpy.fft.fft(audio_array)
        freqs = numpy.fft.fftfreq(len(audio_array))
        #get the 32 loudest frequencies, this allows us to sort the root note from the harmonics, which may be louder than the root in the recording
        #print("FFT Time: %.2f" % (time.perf_counter() - start), "seconds")
        indices = sp.argsort()[-32:]
        #get the index of the lowest frequency (root note) from these
        lowest = min(indices)

        #calculate the frequency in hertz
        freq = freqs[lowest]
        freq_in_hertz = freq * sample_rate
        print("Frequency: %.2f" % freq_in_hertz, "Hz")
        #Determine which note to tune towards - there's gotta be a better way to do this
        match freq_in_hertz:
            case hz if 40 <= hz < 80:
                print(">>E")
            case hz if 80 <= hz < 84:
                print(">E<")
            case hz if 84 <= hz < 95:
                print("E<<")
            case hz if 95 <= hz < 108:
                print(">>A")
            case hz if 108 <= hz < 112:
                print(">A<")
            case hz if 112 <= hz < 128:
                print("A<<")
            case hz if 128 <= hz < 145:
                print(">>D")
            case hz if 145 <= hz < 149:
                print(">D<")
            case hz if 149 <= hz < 175:
                print("D<<")
            case hz if 175 <= hz < 194:
                print(">>G")
            case hz if 194 <= hz < 198:
                print(">G<")
            case hz if 240 <= hz < 254:
                print(">B<")
            case hz if 326 <= hz < 334:
                print(">e<")
            case hz if 334 <= hz:
                print("e<")
            
#1 (E)	329.63 Hz	E4
#2 (B)	246.94 Hz	B3
#3 (G)	196.00 Hz	G3
#4 (D)	146.83 Hz	D3
#5 (A)	110.00 Hz	A2
#6 (E)	82.41 Hz	E2

#TODO
#fine-tune notes ranges
#visual display
#create dictionary of value ranges
#get it working correctly on a server
         
except KeyboardInterrupt:
    pass

end = time.perf_counter()
print("Runtime: %.2f" % (time.perf_counter() - start), "seconds")