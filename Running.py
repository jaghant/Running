import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from streamlit_option_menu import option_menu
import numpy as np
import plotly.express as px
import altair as alt
from datetime import datetime, timedelta
import calendar
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw



# Display Title and Description
st.title("🏃‍♂️Running and Cycling Report🚴‍♂️")
# st.markdown("Enter the details of the new record below.")

selected = option_menu(
        menu_title    = None,
        options       = ["Running and Cycling Data Entry", "Running and Cycling Reports", "Dashboard"],
        icons         = ["clipboard2-data-fill", "table", "bar-chart-fill"],
        menu_icon     = "cast",
        default_index = 0,
        orientation   = "horizontal"
)

if selected == "Running and Cycling Data Entry":
        col = st.columns(3)
        with col[1]:
            st.write(f"{selected}")
        
        # Establishing a Google Sheets connection
        conn = st.connection("gsheets", type=GSheetsConnection)

        # Fetch existing running data
        existing_data = conn.read(wordsheet="Running", usecols=list(range(8)), ttl=6)
        existing_data = existing_data.dropna(how="all")

        # List of Activities
        Activity = [
            "Running",
            "Cycling"
        ]

        # --- DROP DOWN VALUES FOR SELECTING THE PERIOD ---
        years = [datetime.today().year, datetime.today().year + 1]
        months = list(calendar.month_name[1:])
        # Onboarding New Running form
        with st.form(key="Running_form"):
            Date = st.date_input(label='Choose the date*')
            Month = st.selectbox("Select Month:", months, key="month")
            Year = st.selectbox("Select Year:", years, key="year")
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
                                "Month": Month,
                                "Year": Year
                                
                            }
                        ]
                    ) 
                    
                    # Add the new running data to the existing data
                    updated_df = pd.concat([existing_data, running_data], ignore_index=True)
                    
                    # Update Google Sheets with the new running data
                    conn.update(worksheet="Running", data=updated_df)
                    
                    st.success("Running details successfully submitted!") 

if selected == "Running and Cycling Reports":
        col = st.columns(3)
        with col[1]:
            st.write(f"{selected}")
        
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Fetch existing running data
        
        existing_data = conn.read(worksheet="Running", usecols=list(range(8)), ttl=5)
        existing_data = existing_data.dropna(how="all")
        
        st.dataframe(existing_data)    

if selected == "Dashboard":
        col = st.columns(3)
        with col[1]:
            st.subheader("Dashboard")
        
        selected = option_menu(
        menu_title    = None,
        options       = ["Yearly Report", "Daily Report"],
        icons         = ["diagram-3-fill", "bar-chart-fill"],
        menu_icon     = "cast",
        default_index = 0,
        orientation   = "horizontal"
        )
        if selected == "Yearly Report":
            
            st.subheader("-------------🏃‍♂️-------------Yearly Report-------------🚴‍♂️-------------")
            st.write("----")
            conn = st.connection("gsheets", type=GSheetsConnection)
            existing_data = conn.read(wordsheet="Running", usecols=list(range(8)), ttl=5)
            existing_data = existing_data.dropna(how="all")
            df = existing_data

            # KPI Cards
            col1 = st.columns(5)
            with col1[0]:
                st.write("Total Distance")
            with col1[1]:
                st.write("Duration")
            with col1[2]:
                st.write("Calories")
            with col1[3]:
                st.write("Running Distance")
            with col1[4]:
                st.write("Cycling Distance")                
    
                
            col2 = st.columns(5)
            
            with col2[0]:
                Total_distance = (existing_data["Distance KM"].sum())
                st.subheader((f"{Total_distance:.1f} KM"))
            with col2[1]:
                existing_data["Duration"] =  pd.to_timedelta(existing_data["Duration"])
                timing_data = existing_data["Duration"].sum()
                st.subheader(timing_data)
            with col2[2]:    
                Total_calories = int(existing_data["Calories"].sum())
                st.subheader((f"{Total_calories}"))
            with col2[3]:
                group_running = df[df["Activity"]=="Running"]
                total_running_distance = (group_running["Distance KM"].sum())
                st.subheader((f"{total_running_distance:.1f} KM"))
            with col2[4]:
                group_cycling = df[df["Activity"]=="Cycling"]
                total_cycling_distance = (group_cycling["Distance KM"].sum())
                st.subheader((f"{total_cycling_distance:.1f} KM"))
            st.write("---")
    #---------------------- Data Charts-----------------------
            
            # Add new column of month
            # df['Date'] = pd.to_datetime(df.Date)
            # df['Month']=df['Date'].map(lambda x:x.month)
            
            # Add new column of year
            # df['Year']=df['Date'].map(lambda x:x.year)
        
            activity = st.multiselect(
                "Select the activity:",
                options=df["Activity"].unique(),
                default=df["Activity"].unique()
            )
            select_activity = df.query("Activity ==@activity")
            # st.write(select_activity)
            yearly_groupby = select_activity.groupby('Year')['Distance KM'].sum().reset_index()
            # Create bar chart in year wise data
            year_bars = alt.Chart(yearly_groupby).mark_bar().encode(
                x = 'Year:Q',
                y = 'Distance KM:Q'
            )
            
            year_text = year_bars.mark_text(
                align = 'center',
                baseline = 'bottom',
                size = 20,
                dx=0,
            ).encode(
                text = 'Distance KM:Q'
            )
            
            year_chart = (year_bars + year_text).properties(
                width = 200,
                height= 400
            )
            st.subheader("------------🏃‍♂️--------Year Wise Distance KM----------🚴‍♂️----------")
            st.altair_chart(year_chart, use_container_width=True)
        
            
        if selected == "Daily Report":
                st.subheader("Daily Report")
                st.write("----")
                
                
                conn = st.connection("gsheets", type=GSheetsConnection)
                existing_data = conn.read(wordsheet="Running", usecols=list(range(8)), ttl=5)
                existing_data = existing_data.dropna(how="all")
                df = existing_data
                
                # Define the correct order of months
                month_order = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
                ]
                
                # Convert 'Month' column to categorical with the specified order
                df['Month'] = pd.Categorical(df['Month'], categories=month_order, ordered=True)
                sort_month=df.sort_values("Month")
                
                # Sort month value
                months=sort_month["Month"].unique()
            
                current_month = datetime.now().month
                current_month_name = months[current_month - 1] 
                         
                month = st.sidebar.multiselect(
                "Select The Month:",
                months,
                default=[current_month_name]
                )
                year = st.sidebar.multiselect(
                "Select The Year:",
                options=df["Year"].unique(),
                default=df["Year"].unique()
                )
                activity = st.sidebar.multiselect(
                    "Select The Activity:",
                    options=df["Activity"].unique(),
                    default=df["Activity"].unique()
                )
                
                daily_report = df.query("Month ==@month & Year ==@year & Activity==@activity")     
                
                # KPI Cards
                col1 = st.columns(5)
                with col1[0]:
                    st.write("Total Distance")
                with col1[1]:
                    st.write("Duration")
                with col1[2]:
                    st.write("Calories")
                with col1[3]:
                    st.write("Running Distance")
                with col1[4]:
                    st.write("Cycling Distance")                
                col2 = st.columns(5)
                    
                with col2[0]:
                    Total_distance = (daily_report["Distance KM"].sum())
                    st.subheader((f"{Total_distance:.1f} KM"))       
                with col2[1]:      
                    daily_report["Duration"] =  pd.to_timedelta(daily_report["Duration"])
                    timing_data = daily_report["Duration"].sum()
                    st.subheader((f"{timing_data}"))  
                with col2[2]:
                    Total_calories = int(daily_report["Calories"].sum())
                    st.subheader((f"{Total_calories}"))
                with col2[3]:
                    group_running = daily_report[daily_report["Activity"]=="Running"]
                    total_running_distance = (group_running["Distance KM"].sum())
                    st.subheader((f"{total_running_distance:.1f} KM"))
                with col2[4]:
                    group_cycling = daily_report[daily_report["Activity"]=="Cycling"]
                    total_cycling_distance = (group_cycling["Distance KM"].sum())
                    st.subheader((f"{total_cycling_distance:.1f} KM"))
                st.write("---")
                
                # st.line_chart(
                #     daily_report,
                #     x="Date",
                #     y="Distance KM",
                # )
                
                fig = px.line(daily_report, x="Date", y="Distance KM", text="Distance KM", markers=True)
                st.plotly_chart(fig)
