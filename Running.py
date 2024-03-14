import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Display Title and Description
st.title("Running and Cycling Report")
st.markdown("Enter the details of the new record below.")

# Establishing a Google Sheets connection
conn = st.experimental_connection("gsheets", type=GSheetsConnection)

# Fetch existing running data
existing_data = conn.read(wordsheet="Running", usecols=list(range(6)), ttl=5)
existing_data = existing_data.dropna(how="all")

# List of Activities
Activity = [
    "Running",
    "Cycling"
]
Distance = [
    "5 KM",
    "6 KM",
    "7 KM",
    "8 KM",
    "9 KM",
    "10 KM",
    "12 Km",
    "15 KM",
    "21 KM"
]

# Onboarding New Running form
with st.form(key="Running_form"):
    Date = st.date_input(label='Choose the date*')
    Activity = st.selectbox("Activity*", options=Activity, index=None)
    Distance = st.selectbox("Distance KM", options=Distance, index=None)
    Duration = st.text_input("Duration")
    Calories = st.number_input("Calories")
    Target_Distance = st.text_input("Target Distance")
    
    # Mark Mandatory fields
    st.markdown("**required*")
    
    submit_button = st.form_submit_button("Submit the records")
    
    # If the submit button is pressed
    if submit_button:
        # Check if all mandatory fields are filled
        if not Activity:
            st.warning("Ensure all mandatory fields are filled.")
            st.stop()
        else:
            # Create a new row of running data
            running_data = pd.DataFrame(
                [
                    {
                        "Date": Date.strftime("%Y-%m-%d"),
                        "Activity": Activity,
                        "Distance KM": Distance,
                        "Duration": Duration,
                        "Calories": Calories,
                        "Target Distance": Target_Distance,
                        
                        
                    }
                ]
            ) 
            
            # Add the new running data to the existing data
            updated_df = pd.concat([existing_data, running_data], ignore_index=True)
            
            # Update Google Sheets with the new running data
            conn.update(worksheet="Running", data=updated_df)
            
            st.success("Running details successfully submitted!") 