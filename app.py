import streamlit as st
import google.generativeai as genai
from PIL import Image

# Streamlit page config
st.set_page_config(page_title="Gemini Vehicle Buyer Bot", page_icon="🚘")
st.title("🚘 Gemini Vehicle Buyer Assistant with Chatbot")

st.sidebar.header("💬 Chat with Vehicle Advisor")
st.sidebar.markdown("Ask follow-up questions after analysis!")

# API Key Input (from user)
api_key = st.text_input("🔑 Enter your Google API Key:", type="password")

# Prompt for Gemini Vision analysis
VEHICLE_ANALYSIS_PROMPT = """
You're a smart vehicle buyer and automotive analyst.

Given the image of a vehicle (car, bike, etc.), provide a buyer-style report. Structure your response with:

1. **Vehicle Type**: Car / Bike / SUV / etc.
2. **Brand & Model**
3. **Estimated Year of Manufacture**
4. **Condition**: New / Good / Average / Poor
5. **Color & Appearance**
6. **Visible Features**: Accessories, modifications
7. **Estimated Market Price in INR**
8. **Is it worth buying?**
9. **Confidence Level (0-100%)**
10. **Buyer Notes**: Observations like number plate region, environment, damage, dealership/private sale, etc.

Be analytical but easy to understand. Use bullet points or tables if needed.
"""

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# File uploader
uploaded_image = st.file_uploader("📤 Upload a car or bike image", type=["jpg", "jpeg", "png"])

# Proceed only if API key is provided
if api_key:
    try:
        genai.configure(api_key=api_key)

        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image, caption="📷 Uploaded Vehicle", use_column_width=True)

            if st.button("🔍 Analyze Vehicle"):
                st.write("Analyzing with Gemini Vision... Please wait.")
                model = genai.GenerativeModel("gemini-pro-vision")
                response = model.generate_content(
                    [VEHICLE_ANALYSIS_PROMPT, image],
                    stream=False
                )
                report = response.text
                st.markdown("### ✅ Vehicle Buyer Report")
                st.markdown(report)

                st.session_state.vehicle_report = report
                st.session_state.chat_history.append({"role": "assistant", "text": report})

        # Chatbot section
        if "vehicle_report" in st.session_state:
            user_input = st.sidebar.text_input("💬 Your question to the buyer bot:")

            if user_input:
                chat_model = genai.GenerativeModel("gemini-pro")
                chat = chat_model.start_chat(history=[
                    {"role": "user", "parts": st.session_state.vehicle_report}
                ])
                reply = chat.send_message(user_input)
                answer = reply.text

                st.sidebar.markdown("**🤖 Bot says:**")
                st.sidebar.markdown(answer)

                st.session_state.chat_history.append({"role": "user", "text": user_input})
                st.session_state.chat_history.append({"role": "assistant", "text": answer})

            st.sidebar.markdown("---")
            for msg in st.session_state.chat_history[::-1]:
                role = "🧍‍♂️ You" if msg["role"] == "user" else "🤖 Bot"
                st.sidebar.markdown(f"**{role}:** {msg['text']}")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
else:
    st.warning("⚠️ Please enter your Google API key to start analysis.")
