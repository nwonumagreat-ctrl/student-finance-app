from flask import Flask, request, jsonify

app = Flask(__name__)

# Mock prediction logic (replace with your actual model)
def predict_expense(amount):
    """
    Mocks a machine learning model to predict if an expense is significant.
    For this example, any amount over ₦20,000 is considered "significant".
    """
    # Use a more realistic value for Naira
    if amount >= 20000:
        return 1 # Significant
    else:
        return 0 # Regular

# Mock chatbot logic (a simple rule-based system)
def get_chatbot_response(user_message):
    """
    Provides canned responses to common student finance questions.
    """
    user_message = user_message.lower()

    if "budget" in user_message or "how much" in user_message:
        return "You can check your budget goals in the 'Goals & Budgeting' tab. Remember to set a budget for your most common expenses!"
    elif "save money" in user_message or "saving tips" in user_message:
        return "Try setting a weekly spending challenge in the 'Challenges' tab. A little bit of savings each week adds up!"
    elif "significant expense" in user_message:
        return "A significant expense is an unusual or high-value transaction that might be a one-time cost, like a laptop or a textbook. The model flags these to help you notice them."
    elif "hello" in user_message or "hi" in user_message or "hey" in user_message:
        return "Hi there! I'm your financial assistant. How can I help you manage your student finances today?"
    elif "thank you" in user_message or "thanks" in user_message:
        return "You're welcome! Happy to help you on your financial journey."
    elif "who are you" in user_message:
        return "I'm the AI-powered financial assistant for your Student Finance Navigator app. My goal is to help you make smarter money decisions!"
    else:
        return "I'm sorry, I didn't understand that. You can ask me about saving money, your budget, or what a significant expense is."

# --- API Endpoints ---
@app.route("/predict", methods=['POST'])
def predict():
    data = request.json
    amount = data.get('amount')
    prediction = predict_expense(amount)
    return jsonify({'prediction': prediction})

@app.route("/chatbot", methods=['POST'])
def chatbot():
    data = request.json
    user_message = data.get('message')
    response = get_chatbot_response(user_message)
    return jsonify({'response': response})

if __name__ == "__main__":
    app.run(port=5000, debug=True)


