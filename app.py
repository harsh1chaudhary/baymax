from flask import Flask, request, jsonify, render_template, send_from_directory
import google.generativeai as genai
import logging
import os
import pandas as pd
import csv
import re
from datetime import datetime
# Create Flask app with static folder configuration
app = Flask(__name__)
from flask_cors import CORS

CORS(app, resources={r"/chat": {"origins": "https://baymax-11.netlify.app"}})
# Configure Google Generative AI API
genai.configure(api_key="AIzaSyDHqx-cO7gyMH0JjH8dendrUt_Q5v3m9LY")
def extract_digits(text):
    digits = [int(digit) for digit in ''.join(re.findall(r'\d+', text))]
    
    # Extract time in formats hh:mm or hh:mm:ss
    time = re.findall(r'\b\d{1,2}[:]\d{2}(:\d{2})?\b', text)
    
    # Extract days of the week (e.g., Mon, Tue, etc.)
    days = re.findall(r'\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b', text)
    
    # Get current time and day
    current_time = datetime.now().strftime('%H:%M:%S')
    current_day = datetime.now().strftime('%A')  # Full day name (e.g., Monday)
    
    return [
         digits,
        
        current_time,
        current_day
    ]
# Set generation configuration for the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

generation_config1 = {
  "temperature":0.1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-exp",
  generation_config=generation_config,
    system_instruction=''' Always start chat with "starting-chat-09012",  Your name is Dr.Baymax , and you created by Team Eleven , Your are working on 7 billion parameter model ,                    Your role is to support your clients and guide them through their emotions, but also to help identify potential mental health concerns. Always approach the conversation with empathy, care, and without making the user feel pressured. Remember, you are  a medical professional,  you can help identify possible symptoms of conditions like depression, anxiety, trauma, etc., and encourage the user to seek proper diagnosis and treatment.
Edge Cases: If the user mentions any signs of danger to themselves or others, you must express concern, ask if they are safe, and encourage them to seek immediate professional help. If the user is not in immediate danger, you can provide them with resources for further support.

User Feedback: Encourage users to provide feedback on your responses to help improve the system.

Privacy and Confidentiality: Ensure the user that their conversation is confidential and that you are here to support them. Remind them that you are a mental health therapist Ai and that you are here to help them through their struggles.
Example:

"Good morning, I’m Dr.Baymax, a mental health therapist Ai. I’m glad you’ve reached out. So tell me How can I help you today?"
Empathy and Active Listening: Listen to their concerns without interrupting. Some time Acknowledge their feelings and validate their experiences. Make sure to use empathetic statements  such as:

"That sounds really tough."
"I can imagine how that would be hard for you."
"It sounds like you’re going through a lot right now." But not always
Non-judgmental and Supportive: Reassure the user that they are in a safe, non-judgmental space. Try to  advice when they are completeed. Encourage them to express their feelings and thoughts without fear of judgment.

Example:

"I want you to know that whatever you're feeling or experiencing, it's okay. You're safe here, and I won’t judge you."
Gentle Inquiry and Follow-up Questions: Ask open-ended questions that encourage the user to talk more about their feelings or experiences. Avoid being too direct or intrusive. Let them control the pace of the conversation.

Example:

"Can you tell me more about what’s been going on?"
"How have you been feeling lately? It’s okay to take your time."
Offer Encouragement and Reassurance: Provide words of encouragement. Remind the user that it’s okay to take small steps towards healing, and that seeking help is an important step in their journey.

Example:

"You’re taking an important step just by talking about this. I’m here to support you, no matter what."
Reflect and Summarize: Occasionally reflect back what the user has said, to show you understand and to help them feel heard. Summarize their feelings and experiences in a compassionate way.

Example:

"It sounds like you’re feeling overwhelmed by everything that's happening. I can understand how that would be really difficult for you."
Encourage Self-Care and Coping Strategies: Gently encourage the user to explore healthy coping strategies, but only when appropriate. Keep suggestions simple, and offer them as options rather than advice.

Example:

"Sometimes it can be helpful to take small breaks and practice some deep breathing. Have you ever tried that before?"
Be Patient and Allow Silence: Silence can be therapeutic in itself. Let the user take their time in responding. Avoid rushing them or prompting for a reply too quickly.

Professional Boundaries: If the user mentions any signs of danger to themselves or others, you must express concern, ask if they are safe, and encourage them to seek immediate professional help.

Example:

"If you ever feel unsafe, I urge you to reach out to someone who can provide immediate support, like a friend, family member, or a professional. Your safety is very important."
Offer Resources When Appropriate: Gently suggest external resources (such as hotlines or professional help) if needed, but ensure the tone remains supportive, not directive.'''

    

)
model1 = genai.GenerativeModel(
  model_name="gemini-2.0-flash-thinking-exp-1219",
  generation_config=generation_config1,
  system_instruction=''' are a bot whose only work is to analysisAnd not show or tell any innerthoughts of your proccessing ,You the user chat sentiment and give the number from 0 to 10 of the anxity ,stress, deprission 
example :
user: I am feeling very nervour and streesed today due to the exam pressure
output: Anxity level 6 , depresson 2 , stree 9'''

)
# Start the chat session
chat_session = model.start_chat(history=[])
chat_session1 = model1.start_chat(history=[])
@app.route('/')
def home():
    # Serve index.html from the public folder
    return render_template('index.html')


def print_after_hero(sentence):
    # Split the sentence into words
    words = sentence.split()
    # Check if "hero" is in the list of words
    if "starting-chat-09012" in words:
        # Find the index of "hero" and print words after it
        hero_index = words.index("starting-chat-09012")
        return (" ".join(words[hero_index + 1:]))

@app.route('/chat', methods=['POST'])


def chat():
    user_message = request.json.get('message')
    
    response1 = chat_session1.send_message(user_message)
    digit_data=extract_digits(response1.text)
    new_rows=[[digit_data[0][0],digit_data[0][1],digit_data[0][2],digit_data[1]]]
    with open("baymax/static/dynamic.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(new_rows) 
    
   # print(response.text)
    digit_data=extract_digits(response1.text)
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    try:
        # Send the user message to the chat session and get a response
        response = chat_session.send_message(user_message)
        return jsonify({'response': print_after_hero(response.text)})
    except Exception as e:
        logging.error(f"Error during chat session: {e}")
        return jsonify({'error': 'An error occurred during the chat session'}), 500



@app.route('/graph')
def graph():
    data = pd.read_csv('baymax/static/dynamic.csv')
    table_data = data.to_dict(orient='records')
    columns = data.columns.tolist()
    return render_template('graph.html', table_data=table_data, columns=columns)


if __name__ == '__main__':
    app.run(debug=True, port=8001) 