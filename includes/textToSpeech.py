import pyttsx3

def textToSpeech(text):
    # Initialize engine
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    # Initialize engine
    engine.setProperty('rate', 150)   # Set speech speed to 150 words per minute
    engine.setProperty('voice', voices[0].id)   # Use female voice for English language
    # Convert text to speech
    engine.say(text)
    # Play the speech
    engine.runAndWait()
