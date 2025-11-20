import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

# Page config
st.set_page_config(
    page_title="Gym Workout Logger",
    page_icon="🏋️‍♂️",
    layout="wide"
)

# File to store data
DATA_FILE = "workout_data.json"

# Initialize or load data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            return pd.DataFrame(data)
    return pd.DataFrame(columns=['Date', 'Exercise', 'Sets', 'Reps', 'Weight'])

def save_data(df):
    with open(DATA_FILE, 'w') as f:
        json.dump(df.to_dict('records'), f)

# Load data
if 'df' not in st.session_state:
    st.session_state.df = load_data()

# Title and header
st.title("🏋️‍♂️ Gym Workout Logger")
st.markdown("---")

# Sidebar for navigation
menu = st.sidebar.radio(
    "Navigation",
    ["➕ Log Workout", "📊 View Data", "📈 Analytics"]
)

# ==================== LOG WORKOUT ====================
if menu == "➕ Log Workout":
    st.header("Log Your Workout")
    
    col1, col2 = st.columns(2)
    
    with col1:
        workout_date = st.date_input(
            "Date",
            datetime.now(),
            help="Select workout date"
        )
        
        exercise = st.selectbox(
            "Exercise",
            [
                "Bench Press",
                "Squat",
                "Deadlift",
                "Shoulder Press",
                "Pull-ups",
                "Barbell Row",
                "Leg Press",
                "Bicep Curl",
                "Tricep Extension",
                "Lat Pulldown",
                "Other"
            ]
        )
        
        if exercise == "Other":
            exercise = st.text_input("Enter Exercise Name")
    
    with col2:
        sets = st.number_input("Sets", min_value=1, max_value=10, value=3)
        reps = st.number_input("Reps", min_value=1, max_value=50, value=10)
        weight = st.number_input("Weight (kg)", min_value=0.0, step=2.5, value=20.0)
    
    st.markdown("---")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    
    with col_btn1:
        if st.button("✅ Add Workout", type="primary", use_container_width=True):
            if exercise:
                new_entry = pd.DataFrame({
                    'Date': [workout_date.strftime('%Y-%m-%d')],
                    'Exercise': [exercise],
                    'Sets': [sets],
                    'Reps': [reps],
                    'Weight': [weight]
                })
                
                st.session_state.df = pd.concat([st.session_state.df, new_entry], ignore_index=True)
                save_data(st.session_state.df)
                st.success("✅ Workout logged successfully!")
                st.balloons()
            else:
                st.error("Please enter an exercise name!")
    
    with col_btn2:
        if st.button("🗑️ Clear All Data", use_container_width=True):
            st.session_state.df = pd.DataFrame(columns=['Date', 'Exercise', 'Sets', 'Reps', 'Weight'])
            save_data(st.session_state.df)
            st.success("All data cleared!")

# ==================== VIEW DATA ====================
elif menu == "📊 View Data":
    st.header("Workout History")
    
    if st.session_state.df.empty:
        st.info("📝 No workout data yet. Start logging your workouts!")
    else:
        # Date filter
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Convert Date column to datetime for filtering
            st.session_state.df['Date'] = pd.to_datetime(st.session_state.df['Date'])
            min_date = st.session_state.df['Date'].min().date()
            max_date = st.session_state.df['Date'].max().date()
            
            start_date = st.date_input(
                "From Date",
                min_date,
                min_value=min_date,
                max_value=max_date
            )
        
        with col2:
            end_date = st.date_input(
                "To Date",
                max_date,
                min_value=min_date,
                max_value=max_date
            )
        
        with col3:
            exercise_filter = st.multiselect(
                "Filter by Exercise",
                options=st.session_state.df['Exercise'].unique(),
                default=st.session_state.df['Exercise'].unique()
            )
        
        # Filter data
        mask = (
            (st.session_state.df['Date'] >= pd.to_datetime(start_date)) &
            (st.session_state.df['Date'] <= pd.to_datetime(end_date)) &
            (st.session_state.df['Exercise'].isin(exercise_filter))
        )
        filtered_df = st.session_state.df[mask].copy()
        
        # Format date for display
        filtered_df['Date'] = filtered_df['Date'].dt.strftime('%Y-%m-%d')
        
        if filtered_df.empty:
            st.warning("No data found for the selected filters.")
        else:
            # Display statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Workouts", len(filtered_df))
            
            with col2:
                total_volume = (filtered_df['Sets'] * filtered_df['Reps'] * filtered_df['Weight']).sum()
                st.metric("Total Volume (kg)", f"{total_volume:,.0f}")
            
            with col3:
                st.metric("Exercises", filtered_df['Exercise'].nunique())
            
            with col4:
                st.metric("Max Weight", f"{filtered_df['Weight'].max():.1f} kg")
            
            st.markdown("---")
            
            # Display table with delete option
            st.subheader("Workout Log")
            
            # Add index column
            display_df = filtered_df.reset_index(drop=True)
            display_df.index = display_df.index + 1
            
            st.dataframe(
                display_df,
                use_container_width=True,
                height=400
            )
            
            # Export options
            col1, col2 = st.columns(2)
            
            with col1:
                csv = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"workout_log_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                if st.button("🗑️ Delete Selected Records", use_container_width=True):
                    st.warning("This feature requires row selection. Use the CSV download for now.")

# ==================== ANALYTICS ====================
elif menu == "📈 Analytics":
    st.header("Workout Analytics")
    
    if st.session_state.df.empty:
        st.info("📝 No workout data yet. Start logging your workouts!")
    else:
        # Prepare data
        df = st.session_state.df.copy()
        df['Date'] = pd.to_datetime(df['Date'])
        df['Total_Volume'] = df['Sets'] * df['Reps'] * df['Weight']
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            days_back = st.selectbox(
                "Time Period",
                [7, 14, 30, 60, 90, 180, 365],
                format_func=lambda x: f"Last {x} days"
            )
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        df_filtered = df[df['Date'] >= cutoff_date]
        
        if df_filtered.empty:
            st.warning(f"No data available for the last {days_back} days.")
        else:
            # ========== WEEKLY PROGRESS GRAPH ==========
            st.subheader("📈 Weekly Progress")
            
            # Group by week and exercise
            df_filtered['Week'] = df_filtered['Date'].dt.to_period('W').dt.to_timestamp()
            weekly_data = df_filtered.groupby(['Week', 'Exercise'])['Total_Volume'].sum().reset_index()
            
            fig_weekly = px.line(
                weekly_data,
                x='Week',
                y='Total_Volume',
                color='Exercise',
                title='Weekly Training Volume by Exercise',
                labels={'Total_Volume': 'Volume (kg)', 'Week': 'Week'},
                markers=True
            )
            fig_weekly.update_layout(height=400)
            st.plotly_chart(fig_weekly, use_container_width=True)
            
            st.markdown("---")
            
            # ========== PIE CHART - EXERCISE DISTRIBUTION ==========
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🥧 Exercise Distribution")
                
                exercise_volume = df_filtered.groupby('Exercise')['Total_Volume'].sum().reset_index()
                
                fig_pie = px.pie(
                    exercise_volume,
                    values='Total_Volume',
                    names='Exercise',
                    title='Total Volume by Exercise',
                    hole=0.4
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # ========== BAR CHART - DATE WISE ==========
            with col2:
                st.subheader("📊 Daily Workout Volume")
                
                daily_volume = df_filtered.groupby('Date')['Total_Volume'].sum().reset_index()
                
                fig_bar = px.bar(
                    daily_volume,
                    x='Date',
                    y='Total_Volume',
                    title='Daily Training Volume',
                    labels={'Total_Volume': 'Volume (kg)', 'Date': 'Date'},
                    color='Total_Volume',
                    color_continuous_scale='Blues'
                )
                fig_bar.update_layout(height=400)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            st.markdown("---")
            
            # ========== EXERCISE-WISE PROGRESS ==========
            st.subheader("💪 Exercise-Wise Progress")
            
            selected_exercise = st.selectbox(
                "Select Exercise",
                df_filtered['Exercise'].unique()
            )
            
            exercise_df = df_filtered[df_filtered['Exercise'] == selected_exercise]
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Weight progression
                fig_weight = px.line(
                    exercise_df,
                    x='Date',
                    y='Weight',
                    title=f'{selected_exercise} - Weight Progress',
                    markers=True
                )
                fig_weight.update_layout(height=300)
                st.plotly_chart(fig_weight, use_container_width=True)
            
            with col2:
                # Volume progression
                fig_volume = px.line(
                    exercise_df,
                    x='Date',
                    y='Total_Volume',
                    title=f'{selected_exercise} - Volume Progress',
                    markers=True,
                    color_discrete_sequence=['green']
                )
                fig_volume.update_layout(height=300)
                st.plotly_chart(fig_volume, use_container_width=True)
            
            # ========== SUMMARY STATISTICS ==========
            st.markdown("---")
            st.subheader("📊 Summary Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Workouts",
                    len(df_filtered),
                    f"+{len(df_filtered) - len(df[df['Date'] < cutoff_date])}"
                )
            
            with col2:
                total_vol = df_filtered['Total_Volume'].sum()
                st.metric(
                    "Total Volume",
                    f"{total_vol:,.0f} kg"
                )
            
            with col3:
                avg_vol = df_filtered.groupby('Date')['Total_Volume'].sum().mean()
                st.metric(
                    "Avg Daily Volume",
                    f"{avg_vol:,.0f} kg"
                )
            
            with col4:
                most_trained = df_filtered['Exercise'].value_counts().index[0]
                st.metric(
                    "Most Trained",
                    most_trained
                )

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Gym Workout Logger** 🏋️‍♂️
    
    Track your workouts and monitor your progress!
    
    Features:
    - Log exercises, sets, reps, weight
    - View workout history
    - Analyze progress with charts
    - Export data to CSV
    """
)

st.sidebar.markdown("---")
st.sidebar.caption("Made with ❤️ using Streamlit")