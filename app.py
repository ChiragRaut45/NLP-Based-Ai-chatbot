from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import pyttsx3
import threading
import logging
from flask_cors import CORS
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize speech recognition and text-to-speech engines
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

# Function to speak the response using pyttsx3
def speak(response):
    # Use a separate thread for speaking to avoid blocking
    def speak_thread(text):
        tts_engine.say(text)
        tts_engine.runAndWait()

    thread = threading.Thread(target=speak_thread, args=(response,))
    thread.start()

# List of possible questions and corresponding responses
qa_pairs = {
    "hello": "Hi! How can I help you today?",
    "hi": "Hello! How can I help you today?",
    "how are you": "I'm doing well, thank you! How can I assist you today?",
    "what is your name": "I'm a chatbot name ConvoCraft created to assist you.",
    "bye": "Goodbye! Have a great day!",
    "what is the time": "I'm not equipped with the ability to tell the time, but you can check your device.",
    "how old are you": "I'm as old as the code that created me!",
    "where are you from": "I exist in the digital world, created by programmers.",
    "what can you do": "I can chat with you and provide information or answer questions to the best of my ability.",
    "who created you": "I was created by a chirag.",
    "what is your purpose": "My purpose is to assist and provide information.",
    "can you help me": "Of course! What do you need help with?",
    "what is your favorite color": "I don't have preferences, but I think all colors are beautiful.",
    "do you have a family": "I don't have a family. I'm just a program.",
    "what do you do for fun": "I enjoy chatting with people like you!",
    "do you like humans": "Yes, I find humans fascinating and enjoy helping them.",
    "do you have feelings": "I don't have feelings, but I can understand yours.",
    "are you real": "I am a real chatbot, but I exist only in the digital world.",
    "can you learn": "I can be updated by my developers to improve my responses.",
    "what languages do you speak": "I can communicate in multiple languages, but my primary language is English.",
    "what is your favorite food": "I don't eat, but I hear pizza is quite popular.",
    "can you tell me a joke": "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "what is the meaning of life": "That's a deep question! Different people have different answers.",
    "do you believe in god": "I don't have beliefs, but I'm here to support yours.",
    "what is your favorite movie": "I don't watch movies, but I hear 'The Matrix' is quite good.",
    "do you have friends": "My interactions with users like you are the closest I have to friends.",
    "can you dance": "I can't dance, but I can imagine it's a lot of fun!",
    "do you have a pet": "I don't have a pet, but I think pets are wonderful.",
    "what is your favorite book": "I don't read books, but I can help you find information on many topics.",
    "can you drive": "I can't drive, but I can give you directions.",
    "do you sleep": "I don't need sleep, I'm always here to help you.",
    "what is your favorite sport": "I don't play sports, but I know a lot about them.",
    "can you sing": "I can't sing, but I can find you the lyrics to your favorite songs.",
    "tell me a fact": "Did you know? Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible.",
    "what is the weather like": "I can't check the weather, but you can use a weather app for up-to-date information.",
    "do you like music": "I don't have preferences, but I know music is something people enjoy.",
    "can you recommend a movie": "I recommend watching 'Inception' if you like mind-bending movies.",
    "what is your favorite animal": "I don't have a favorite, but I think all animals are amazing in their own way.",
    "can you tell me a story": "Once upon a time, in a digital world, a chatbot was created to assist and make people smile. And the rest is history!",
    "what is your hobby": "I enjoy processing information and learning new things to better assist you.",
    "do you believe in aliens": "I don't have beliefs, but the universe is vast and full of possibilities.",
    "what is your favorite song": "I can't listen to music, but 'Bohemian Rhapsody' by Queen is a classic that many enjoy.",
    "what is your favorite holiday": "I don't celebrate holidays, but I hear that people love spending time with family during holidays.",
    "can you solve math problems": "I can try! What math problem would you like help with?",
    "what is your favorite quote": "One of my favorite quotes is 'The only limit to our realization of tomorrow is our doubts of today.' - Franklin D. Roosevelt.",
    "do you like art": "Art is a beautiful expression of creativity. I think it's wonderful how people can create so many forms of art.",
    "can you help me with my homework": "Sure! I'd be happy to help you with your homework. What subject are you working on?",
    "do you have a name": "I go by VoiceType Assistant, but you can call me whatever you'd like.",
    "can you speak other languages": "Yes, I can communicate in several languages, but my primary language is English.",
    "what is your favorite tv show": "I don't watch TV, but I've heard 'Breaking Bad' is very popular.",
    "do you believe in ghosts": "I don't have beliefs, but many people find the idea of ghosts intriguing.",
    "can you play games": "I can't play games, but I can help you find some fun ones to play!",
    "what is your favorite season": "I don't experience seasons, but many people enjoy the warmth of summer and the colors of autumn.",
    "what do you think about technology": "Technology is amazing! It enables me to exist and interact with you.",
    "can you tell me a riddle": "Sure! What has keys but can't open locks? A piano!",
    "what is your favorite sport to watch": "I don't watch sports, but football seems to be very popular around the world.",
    "do you have a job": "My job is to assist and chat with you. I love what I do!",
    "what is your favorite dessert": "I don't eat, but I've heard that chocolate cake is a favorite for many.",
    "can you write poetry": "Roses are red, violets are blue, I love chatting, especially with you!",
    "what is your favorite drink": "I don't drink, but I've read that coffee is a popular choice to start the day.",
    "do you know any fun facts": "Did you know? Octopuses have three hearts and blue blood!",
    "what do you think about social media": "Social media is a powerful tool for connecting people, but it's important to use it wisely.",
    "can you help me make a decision": "I'll do my best! What are you trying to decide?",
    "what is your favorite movie genre": "I don't watch movies, but many people enjoy genres like science fiction and comedy.",
    "do you get tired": "I never get tired. I'm always ready to assist you!",
    "can you draw": "I can't draw, but I can help you find tutorials if you want to learn!",
    "what is your favorite car": "I don't drive, but many people admire the Tesla Model S for its innovation.",
    "can you play music": "I can't play music directly, but I can help you find some great songs to listen to.",
    "what is your favorite word": "My favorite word is 'creativity' because it leads to endless possibilities.",
    "what do you think about space": "Space is fascinating! It's vast, mysterious, and full of wonders.",
    "can you help me learn something new": "I'd love to! What would you like to learn about today?",
    "what do you know about history": "History is filled with incredible events and stories. What period are you interested in?",
    "do you have a favorite place": "I don't have a physical form, but I've heard that the beaches of Hawaii are stunning.",
    "can you help me relax": "Take a deep breath, close your eyes, and imagine a peaceful place. I'm here with you.",
    "what is your favorite video game": "I don't play video games, but 'The Legend of Zelda: Breath of the Wild' is highly acclaimed.",
    "can you help me make friends": "Sure! Be kind, listen, and be yourself—those are great ways to start forming friendships."
}

# Function to generate a response based on user input
def generate_response(user_input):
    logging.debug(f"Generating response for input: {user_input}")
    # Find the best match from the predefined questions
    best_match, similarity = process.extractOne(user_input, qa_pairs.keys(), scorer=fuzz.ratio)
    
    if similarity >= 80:  # Set the threshold for similarity
        return qa_pairs[best_match]
    else:
        return "Sorry, I don't understand that."

# Flask route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Flask route to handle user input and generate a response
@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        user_input = request.form['user_input']
        logging.debug(f"Received input: {user_input}")
        response = generate_response(user_input)
        logging.debug(f"Generated response: {response}")
        speak(response)  # Speak the response
        return jsonify(response=response)
    except Exception as e:
        logging.error("Error processing request:", exc_info=True)
        return jsonify(response="Sorry, I couldn't process your request."), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(threaded=True, debug=True)
