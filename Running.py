import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from streamlit_option_menu import option_menu
from pathlib import Path


# Display Title and Description
st.title("🏃‍♂️Running and Cycling Report🚴‍♂️")
# st.markdown("Enter the details of the new record below.")

selected = option_menu(
        menu_title    = None,
        options       = ["Running and Cycling Data Entry", "Running and Cycling Reports", "Dashboard"],
        icons         = ["diagram-3-fill", "bar-chart-fill"],
        menu_icon     = "cast",
        default_index = 0,
        orientation   = "horizontal"
)
conn = st.connection("gsheets", type=GSheetsConnection)
existing_data = conn.read(wordsheet="Running", usecols=list(range(6)), ttl=5)
existing_data = existing_data.dropna(how="all")

if selected == "Running and Cycling Data Entry":
        st.subheader(f"{selected}")
        
        # Establishing a Google Sheets connection
        conn = st.connection("gsheets", type=GSheetsConnection)

        # Fetch existing running data
        existing_data = conn.read(wordsheet="Running", usecols=list(range(6)), ttl=5)
        existing_data = existing_data.dropna(how="all")

        # List of Activities
        Activity = [
            "Running",
            "Cycling"
        ]


        # Onboarding New Running form
        with st.form(key="Running_form"):
            Date = st.date_input(label='Choose the date*')
            Activity = st.selectbox("Activity*", options=Activity, index=None)
            Distance = st.text_input("Distance KM")
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
                                "Date": Date.strftime("%d-%m-%Y"),
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
    
if selected == "Running and Cycling Reports":
        st.subheader(f"{selected}")
        
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Fetch existing running data
        existing_data = conn.read(worksheet="Running", usecols=list(range(6)), ttl=5)
        existing_data = existing_data.dropna(how="all")
        
        st.dataframe(existing_data)    

if selected == "Dashboard":
        st.subheader(f"{selected}")
        
        with open('style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        
        Left_column, Right_column = st.columns(2)
            
        with Left_column:
            Total_distance = int(existing_data["Distance KM"].sum())
            st.metric(label="Total Distance", value=(f"{Total_distance} KM"))       
        with Right_column:    
            Total_calories = int(existing_data["Calories"].sum())
            d = st.metric(label="Total Calories", value=(f"{Total_calories}"))
        
    
        
