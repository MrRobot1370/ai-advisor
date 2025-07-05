import speech_recognition as sr

def speechToText():
    # obtain audio from the microphone
    r = sr.Recognizer()
    r.pause_threshold = 1  # seconds of silence needed to consider the user has finished speaking
    r.dynamic_energy_threshold = True  # automatically adjust the energy threshold based on ambient noise
    r.dynamic_energy_adjustment_damping = 0.15  # how quickly to adjust the threshold, higher means faster
    r.dynamic_energy_ratio = 1.5  # how much louder than the ambient noise the audio needs to be before it is considered speech

    with sr.Microphone() as source:
        print("Speak something...")
        audio = r.listen(source, phrase_time_limit=15)  # listen for up to 15 seconds

    try:
        # recognize speech using Google Speech Recognition
        text = r.recognize_google(audio)
        return("You said: " + text)
    except sr.UnknownValueError:
        return("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        return("Could not request results from Google Speech Recognition service; {0}".format(e))