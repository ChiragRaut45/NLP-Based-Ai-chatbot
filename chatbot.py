import speech_recognition as sr
import pyttsx3
import openai  # Optional for advanced responses

# Initialize speech recognition and text-to-speech engines
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

# Set OpenAI API key if using GPT model (optional)
# openai.api_key = 'your-api-key-here'

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            user_input = recognizer.recognize_google(audio)
            print(f"You said: {user_input}")
            return user_input
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            print("Sorry, my speech service is down.")
            return None

def speak(response):
    tts_engine.say(response)
    tts_engine.runAndWait()

def generate_response(user_input):
    # Example: Rule-based response
    if "hello" in user_input.lower():
        return "Hello! How can I help you today?"
    elif "how are you" in user_input.lower():
        return "I'm a bot, so I don't have feelings, but thanks for asking!"
    elif "bye" in user_input.lower():
        return "Goodbye! Have a great day!"
    else:
        # Optional: Use OpenAI GPT model for response
        # response = openai.Completion.create(
        #     engine="text-davinci-003",
        #     prompt=user_input,
        #     max_tokens=50
        # )
        # return response.choices[0].text.strip()
        return "Sorry, I don't understand that."

def get_input():
    choice = input("Would you like to speak (s) or type (t) your message? ").strip().lower()
    if choice == 's':
        return listen()
    elif choice == 't':
        return input("Please type your message: ").strip()
    else:
        print("Invalid choice, please try again.")
        return get_input()

# Main loop to keep the chatbot running
while True:
    user_input = get_input()
    if user_input:
        response = generate_response(user_input)
        print(f"Bot: {response}")
        speak(response)
        if "bye" in user_input.lower():
            break
