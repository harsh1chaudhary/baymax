from flask import Flask, request, jsonify, render_template, send_from_directory
import google.generativeai as genai

# Create Flask app with static folder configuration
app = Flask(__name__, static_folder='public')

# Configure Google Generative AI API
genai.configure(api_key="AIzaSyDJNleTEiqY2tJRddmskckRm6XG3YuACBk")

# Set generation configuration for the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    
)

# Start the chat session
chat_session = model.start_chat(history=[])

@app.route('/')
def home():
    # Serve index.html from the public folder
    return send_from_directory('public', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Send the user message to the chat session and get a response
    response = chat_session.send_message(user_message)
    
    return jsonify({'response': response.text})

if __name__ == '__main__':
    app.run(debug=True)
