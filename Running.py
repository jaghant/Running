import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from streamlit_option_menu import option_menu
import numpy as np
import plotly.express as px
import altair as alt
from datetime import datetime, timedelta
import calendar



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

if selected == "Running and Cycling Data Entry":
        st.subheader(f"{selected}")
        
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
        st.subheader(f"{selected}")
        
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Fetch existing running data
        existing_data = conn.read(worksheet="Running", usecols=list(range(8)), ttl=5)
        existing_data = existing_data.dropna(how="all")
        
        st.dataframe(existing_data)    

if selected == "Dashboard":
        st.subheader("Running & Cycling Data Analysis")
        st.write("----")
        
        conn = st.connection("gsheets", type=GSheetsConnection)
        existing_data = conn.read(wordsheet="Running", usecols=list(range(8)), ttl=5)
        existing_data = existing_data.dropna(how="all")
        df = existing_data

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
            total_running_distance = (group_running["Distance KM"].sum())
            st.metric(label="Running Distance", value=(f"{total_running_distance} KM"))
        with col[3]:
            group_cycling = df[df["Activity"]=="Cycling"]
            total_cycling_distance = (group_cycling["Distance KM"].sum())
            st.metric(label="Cycling Distance", value=(f"{total_cycling_distance} KM"))
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
        st.write("Year Wise Distance KM")
        st.altair_chart(year_chart, use_container_width=True)
        
    #----------------------Last 12 Months data------------------------
        
        # Filter data for last 12 months
        # last_12_months = select_activity[select_activity['Date'] >= datetime.today() - timedelta(days=365)]
        # st.write(last_12_months)
        monthly_groupby = select_activity.groupby('Month')['Distance KM'].sum().reset_index()
        # st.write(monthly_groupby)
        
        fig_month = px.line(
            monthly_groupby,
            x = "Month",
            y = "Distance KM",
            orientation = "v",
            title = "<b>Month Wise Running Distance</b>",
            color_discrete_sequence = ["#12A999"] * len(monthly_groupby),
            text="Distance KM",
            template = "plotly_white",
            markers="**",
        )
        fig_month.update_traces(texttemplate='%{text:.2s}', textposition='top center')
        fig_month.update_layout(
                    plot_bgcolor = "rgba(0,0,0,0)",
                    xaxis        = (dict(showgrid=False)),
                    yaxis        = (dict(showgrid=False))
                )
        st.write(fig_month)
