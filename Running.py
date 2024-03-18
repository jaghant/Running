import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from streamlit_option_menu import option_menu
import numpy as np



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
df = existing_data
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
        st.subheader("Running & Cycling Data Analysis")
        st.write("----")
        
        # KPI Cards
        col = st.columns(4)
            
        with col[0]:
            Total_distance = int(existing_data["Distance KM"].sum())
            st.metric(label="Total Distance", value=(f"{Total_distance} KM"))       
        with col[1]:    
            Total_calories = int(existing_data["Calories"].sum())
            st.metric(label="Total Calories", value=(f"{Total_calories}"))
        with col[2]:
            group_running = df[df["Activity"]=="Running"]
            total_running_distance = int(group_running["Distance KM"].sum())
            st.metric(label="Running Distance", value=(f"{total_running_distance} KM"))
        with col[3]:
            group_cycling = df[df["Activity"]=="Cycling"]
            total_cycling_distance = int(group_cycling["Distance KM"].sum())
            st.metric(label="Cycling Distance", value=(f"{total_cycling_distance} KM"))
        st.write("---")
        
