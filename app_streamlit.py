import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
import time # For the loading spinner

# --- Page Configuration and Styling ---
st.set_page_config(page_title="Student Finance App", layout="wide")
st.title("🎓 Student Finance Navigator")
st.markdown("Your personal guide to managing money on campus and beyond.")

# Use st.session_state to persist data across reruns
if 'goals' not in st.session_state:
    st.session_state.goals = {}
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'challenge' not in st.session_state:
    st.session_state.challenge = None
if 'weekly_spending' not in st.session_state:
    st.session_state.weekly_spending = {}

# Base URL for your Flask API
FLASK_API_URL = "https://student-finance-app.onrender.com"

# --- Main Sections ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Dashboard", 
    "Spending Analysis", 
    "Goals & Budgeting", 
    "Campus Chatbot",
    "Challenges"
])

# --- Tab 1: Dashboard (Prediction) ---
with tab1:
    st.header("Financial Insight Generator ✨")
    st.write("Enter a transaction to get a quick prediction of whether it's a major expense.")
    
    # User input for the prediction model
    transaction_amount = st.number_input("Transaction Amount:", min_value=0.0, format="%.2f")

    # Use st.spinner for a visual loading state
    if st.button("Get Prediction 🔮"):
        if transaction_amount > 0:
            with st.spinner('Thinking...'):
                time.sleep(1) # Simulate a delay for the model
                try:
                    # Send the raw data to the Flask API
                    response = requests.post(f"{FLASK_API_URL}/predict", json={'amount': transaction_amount})
                    if response.status_code == 200:
                        prediction_result = response.json()
                        prediction = prediction_result.get('prediction')
                        
                        if prediction == 1:
                            st.success("🎉 The model predicts this is a significant expense! Maybe for tuition or a big textbook purchase.")
                        else:
                            st.info("✅ The model predicts this is a regular expense like daily campus coffee.")
                    else:
                        st.error("❌ Error from the backend API. Please check your Flask server.")
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the Flask API. Please ensure your server is running.")
        else:
            st.warning("Please enter a valid amount.")

# --- Tab 2: Spending Analysis (Data Visualization) ---
with tab2:
    st.header("Your Spending Breakdown 📊")
    st.write("Add your transactions to see a visual summary of where your money is going.")
    
    col1, col2 = st.columns(2)
    with col1:
        # Student-specific categories
        category = st.selectbox("Category", ['Tuition/Fees', 'Textbooks', 'Campus Food', 'Social Life', 'Groceries', 'Dorm/Rent', 'Transportation', 'Other'])
    with col2:
        amount = st.number_input("Amount", min_value=0.0, format="%.2f", key="viz_amount")
    
    if st.button("Add Transaction ➕"):
        if amount > 0:
            st.session_state.transactions.append({'Category': category, 'Amount': amount})
            # Also update weekly spending for the challenges
            st.session_state.weekly_spending[category] = st.session_state.weekly_spending.get(category, 0) + amount
            st.success("Transaction added!")
        else:
            st.warning("Please enter a valid amount.")
    
    # Create the DataFrame and chart
    if st.session_state.transactions:
        df_transactions = pd.DataFrame(st.session_state.transactions)
        df_summary = df_transactions.groupby('Category')['Amount'].sum().reset_index()
        
        st.subheader("Spending Chart")
        fig = px.pie(
            df_summary, 
            values='Amount', 
            names='Category', 
            title='Spending by Category',
            color_discrete_sequence=px.colors.sequential.Sunset # Adds a nice color theme
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Recent Transactions")
        st.dataframe(df_transactions)
    else:
        st.info("No transactions added yet. Add some to see the charts!")

# --- Tab 3: Goals & Budgeting ---
with tab3:
    st.header("Set Your Financial Goals 🎯")
    st.write("Set a budget for a category and get a notification if you're close to exceeding it.")

    goal_category = st.selectbox("Select Category for Goal", ['Tuition/Fees', 'Textbooks', 'Campus Food', 'Social Life', 'Groceries', 'Dorm/Rent', 'Transportation', 'Other'], key="goal_category")
    goal_amount = st.number_input("Target Amount (₦)", min_value=0.0, format="%.2f", key="goal_amount")

    if st.button("Set Budget ✨"):
        st.session_state.goals[goal_category] = goal_amount
        st.success(f"Budget set: ₦{goal_amount} for {goal_category}.")

    if st.session_state.transactions and st.session_state.goals:
        st.subheader("Budget Progress")
        df_transactions = pd.DataFrame(st.session_state.transactions)
        
        for category, target in st.session_state.goals.items():
            if not df_transactions.empty:
                current_spending = df_transactions[df_transactions['Category'] == category]['Amount'].sum()
                
                # Check for notifications
                if current_spending >= target:
                    st.error(f"⚠️ **Warning!** You have reached your ₦{target} budget for **{category}**.")
                elif current_spending / target >= 0.8:
                    st.warning(f"🔔 **Heads up!** You're at {current_spending/target:.0%} of your ₦{target} budget for **{category}**.")

                # Display progress using st.metric for better visuals
                remaining = target - current_spending
                st.metric(
                    label=f"Progress for {category} Budget", 
                    value=f"₦{current_spending:.2f}",
                    delta=f"₦{remaining:.2f} remaining" if remaining > 0 else "Budget Reached!"
                )
                st.progress(min(1.0, current_spending / target))
    else:
        st.info("Set a budget and add some transactions to see your progress.")

# --- Tab 4: AI-Powered Chatbot ---
with tab4:
    st.header("Chat with Your Financial Assistant 🤖")
    st.write("Ask questions about student finance, budgeting, and more!")

    # Display chat messages from history on app rerun
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is your question?"):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Get response from the backend
        try:
            with st.spinner("Assistant is typing..."):
                response = requests.post(f"{FLASK_API_URL}/chatbot", json={'message': prompt})
                if response.status_code == 200:
                    bot_response = response.json().get('response', "Sorry, I couldn't get a response.")
                    # Display assistant response in chat message container
                    with st.chat_message("assistant"):
                        st.write(bot_response)
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
                else:
                    st.error("Error from chatbot API.")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the Flask API. Please ensure your server is running.")

# --- Tab 5: Challenges (Gamification) ---
with tab5:
    st.header("Weekly Financial Challenges 🏆")
    st.write("Complete challenges to master your money management skills!")

    if not st.session_state.challenge:
        st.subheader("Start a New Challenge")
        challenge_category = st.selectbox("Select Challenge Category", ['Campus Food', 'Social Life', 'Groceries', 'Transportation'], key="challenge_category")
        challenge_limit = st.number_input("Set your weekly spending limit (₦):", min_value=0.0, format="%.2f", key="challenge_limit")
        if st.button("Accept Challenge"):
            st.session_state.challenge = {
                'category': challenge_category,
                'limit': challenge_limit,
                'is_completed': False
            }
            st.success(f"Challenge accepted! Try to spend less than ₦{challenge_limit} on {challenge_category} this week.")
    else:
        st.subheader("Your Current Challenge")
        challenge = st.session_state.challenge
        
        current_spending = st.session_state.weekly_spending.get(challenge['category'], 0)
        progress = min(current_spending / challenge['limit'], 1.0) if challenge['limit'] > 0 else 0
        
        st.markdown(f"**Challenge:** Spend less than **₦{challenge['limit']}** on **{challenge['category']}** this week.")
        st.progress(progress, text=f"Progress: ₦{current_spending:.2f} / ₦{challenge['limit']:.2f}")

        if progress < 1.0:
            st.info(f"You're on track! Keep going to beat the challenge.")
        else:
            st.error("You've exceeded your challenge limit! Better luck next week.")

        if st.button("Complete Week & Check Progress"):
            if current_spending <= challenge['limit']:
                st.session_state.challenge['is_completed'] = True
                st.success("🎉 Challenge Completed! Congratulations on managing your spending! 🎉")
                st.balloons()
            else:
                st.error("Challenge failed. You went over your limit.")
            
            # Reset weekly spending for a new week/challenge
            st.session_state.weekly_spending = {}
            st.session_state.challenge = None
            st.session_state.transactions = []

        if st.button("Abandon Challenge"):
            st.session_state.challenge = None
            st.session_state.weekly_spending = {}
            st.info("Challenge abandoned. You can start a new one anytime.")




