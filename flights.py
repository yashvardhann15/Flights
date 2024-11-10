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
    rvalue_index = (day_of_month - 1) * 24 + hour + 10  # 0-based index
    return rvalue_index

# Function to check flight conditions with detailed analysis
def check_flight_conditions(month, date, time, user_inputs, required_attributes):
    rvalue_index = calculate_rvalue_index(date, time)
    analysis_results = []
    overall_status = True

    for parameter, user_value in user_inputs.items():
        if user_value is not None:  # Only analyze parameters with input values
            data = load_data(month, parameter)
            
            # Locate the row that matches all required attributes
            matched_row = data[
                (data["Airports"] == required_attributes["Airports"])
            ]

            if matched_row.empty:
                st.error(f"Data not found for {parameter}")
                continue

            # Get threshold value for the specific time
            threshold = matched_row.iloc[0, rvalue_index]
            
            # Determine if condition is met
            is_satisfied = user_value > threshold
            
            analysis_results.append({
                'Parameter': parameter,
                'User Value': user_value,
                'Threshold': threshold,
                'Status': 1 if is_satisfied else 0
            })
            
            if not is_satisfied:
                overall_status = False

    return analysis_results, 1 if overall_status else 0

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

# Check flight conditions and display results
if st.button("Check Takeoff Status"):
    analysis_results, final_status = check_flight_conditions(
        month, 
        date.strftime("%Y-%m-%d"), 
        time.strftime("%H:%M"), 
        user_inputs, 
        required_attributes
    )
    
    # Create a styled dataframe
    if analysis_results:
        df = pd.DataFrame(analysis_results)
        
        # Function to style the Status column
        def color_status(val):
            color = 'background-color: #90EE90' if val == 1 else 'background-color: #FFB6C1'
            return color

        # Apply styling to the dataframe
        styled_df = df.style.applymap(color_status, subset=['Status'])
        
        # Display the styled table
        st.write("Detailed Analysis:")
        st.dataframe(styled_df)
        
        # Display final status with color
        status_color = "#90EE90" if final_status == 1 else "#FFB6C1"
        st.markdown(
            f"""
            <div style="padding: 10px; background-color: {status_color}; border-radius: 5px; margin: 10px 0;">
                <h3 style="margin: 0;">Final Status: {final_status}</h3>
                <p style="margin: 5px 0;">{"The flight will take off." if final_status == 1 else "The flight will not take off."}</p>
            </div>
            """,
            unsafe_allow_html=True
        )