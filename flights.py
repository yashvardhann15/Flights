import pandas as pd
from datetime import datetime
import streamlit as st

# Function to load data based on month and parameter
def load_data(month, parameter):
    file_path = f"{month}/{parameter}.csv"
    return pd.read_csv(file_path)

# Function to calculate the rvalue index
def calculate_rvalue_index(date, time):
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    hour = int(time.split(":")[0])
    day_of_month = date_obj.day
    rvalue_index = (day_of_month - 1) * 24 + hour + 10 # 0-based index
    return rvalue_index

# Function to check flight conditions
def check_flight_conditions(month, date, time, user_inputs, required_attributes):
    rvalue_index = calculate_rvalue_index(date, time)
    failed_conditions = []

    for parameter, user_value in user_inputs.items():
        data = load_data(month, parameter)
        
        # Locate the row that matches all required attributes
        matched_row = data[
            (data["Airports"] == required_attributes["Airports"])
        ]

        if matched_row.empty:
            failed_conditions.append(parameter)
            return f"Data not found for the given attributes: {', '.join(failed_conditions)}"

        # Get threshold value for the specific time
        threshold = matched_row.iloc[0, rvalue_index]  
        
        # Skip check if user_value is None
        if user_value is not None and user_value <= threshold:
            failed_conditions.append(parameter)

    # Return result
    if failed_conditions:
        return f"It will not fly due to these attributes: {', '.join(failed_conditions)}"
    return "The flight will take off."

# Streamlit UI
st.title("Flight Takeoff Predictor")

# Collect required attribute inputs as strings
required_attributes = {
    "Airports": st.text_input("Airport"),
}

# Select month, date, and time
month = st.selectbox("Select Month", ["june", "july", "aug"])
date = st.date_input("Select Date")
year = st.selectbox("Select Year", list(range(2006, 2025)))
time = st.time_input("Select Time")

# Parameter inputs
parameters = ["temperature", "vgrd", "vlc", "ugrd", "vis", "pressure", "ppt", "hc", "lc", "mc", "gust"]
user_inputs = {}

st.write("Enter values for specific parameters if known; others will be considered True by default.")
for param in parameters:
    user_inputs[param] = st.number_input(f"{param}", value=None)

# Check flight conditions
if st.button("Check Takeoff Status"):
    result = check_flight_conditions(
        month, 
        date.strftime("%Y-%m-%d"), 
        time.strftime("%H:%M"), 
        user_inputs, 
        required_attributes
    )
    st.write(result)
