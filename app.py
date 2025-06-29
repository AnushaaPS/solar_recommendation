import streamlit as st
import google.generativeai as genai
import base64
import json
import os
import io
from PIL import Image


# Configure Gemini API
genai.configure(api_key="AIzaSyBtjKMFrjLt-rJdFGmDLv7zdILwQDAD8Vs")
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

st.set_page_config(page_title="Solar Rooftop Analyzer", layout="wide")
st.title("🌞 AI-Powered Rooftop Solar Analyzer")

st.sidebar.header("Upload Satellite Image")
uploaded_file = st.sidebar.file_uploader("Choose a rooftop satellite image", type=["jpg", "jpeg", "png"])

# Analyze using Gemini
@st.cache_data(show_spinner=False)
def analyze_image_with_gemini(image_bytes):
    try:
        # Convert image bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))


        prompt = (
            "Analyze this rooftop image and provide a JSON object with: "
            "usable_rooftop_area_sqm, roof_type, estimated_energy_output_per_year_kWh, "
            "panel_recommendation, estimated_cost, savings_per_year"
        )

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([prompt, image], stream=False)


        raw_output = response.text
        start = raw_output.find("{")
        end = raw_output.rfind("}") + 1
        json_data = json.loads(raw_output[start:end])
        return json_data

    except Exception as e:
        st.error("❌ Failed to parse AI response.")
        st.write("Error:", e)
        return None

# ROI Calculator
@st.cache_data(show_spinner=False)
def calculate_roi(cost, savings_per_year):
    try:
        roi_years = round(cost / savings_per_year, 2)
        return roi_years
    except:
        return "N/A"

if uploaded_file:
    image_bytes = uploaded_file.read()
    with st.spinner("Analyzing rooftop..."):
        ai_data = analyze_image_with_gemini(image_bytes)

    if ai_data:
        st.subheader("📈 Solar Potential Summary")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Usable Rooftop Area (sqm)", ai_data.get("usable_rooftop_area_sqm", "N/A"))
            st.metric("Roof Type", ai_data.get("roof_type", "N/A"))
            st.metric("Panel Recommendation", ai_data.get("panel_recommendation", "N/A"))

        with col2:
            energy = ai_data.get("estimated_energy_output_per_year_kWh", "N/A")
            st.metric("Estimated Energy Output (kWh/year)", energy)
            estimated_cost = float(ai_data.get("estimated_cost", 10000))
            savings = float(ai_data.get("savings_per_year", 1200))
            roi = calculate_roi(estimated_cost, savings)
            st.metric("ROI Estimate (Years)", roi)

        st.subheader(":bar_chart: ROI Details")
        st.write(f"**Estimated Cost**: ${estimated_cost}")
        st.write(f"**Estimated Annual Savings**: ${savings}")

        st.subheader(":gear: Full JSON Output")
        st.json(ai_data)
else:
    st.info("Please upload a satellite image of your rooftop to begin analysis.")
