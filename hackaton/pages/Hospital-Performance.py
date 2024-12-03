import streamlit as st
import plotly.express as px
import pandas as pd

def run():
    pass

st.title(" :bar_chart: Helpman Healthcare Hospital Performance Interactive Dashboard")

st.write("Information about the app.")

st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

df = pd.read_csv("fake_healthcare_2.csv")

# Ensure the date column is datetime and set as index
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

# Getting the min and max date
startDate = df.index.min()
endDate = df.index.max()

st.sidebar.header("Filter by Date")
date1 = st.sidebar.date_input("Start Date", startDate)
date2 = st.sidebar.date_input("End Date", endDate)

# Ensure the input dates are within the data range
date1 = pd.to_datetime(date1)
date2 = pd.to_datetime(date2)

# Filter the DataFrame based on selected dates
df = df[(df.index >= date1) & (df.index <= date2)].copy()

st.sidebar.header("Choose your filter: ")

# Create filter for Department
wait = st.sidebar.multiselect("Hospital wait time", df["wait_time"].unique())
if not wait:
    df2 = df.copy()
else:
    df2 = df[df["wait_time"].isin(wait)]

# Create filter for Refer Reason
refer = st.sidebar.multiselect("Pick the refer reason", df2["refer_reason"].unique())
if not refer:
    df3 = df2.copy()
else:
    df3 = df2[df2["refer_reason"].isin(refer)]

# Create filter for Staff to Patient Ratio
staff_patient = st.sidebar.multiselect("Pick the Staff to Patient Ratio", df3["staff_patient_ratio"].unique())
if not staff_patient:
    filtered_df = df3.copy()
else:
    filtered_df = df3[df3["staff_patient_ratio"].isin(staff_patient)]

# Overview Page
st.header("Overview")

# Calculate summary metrics for patient data
patient_metrics = {
    "total_patient_days": df['patient_days'].sum() if 'patient_days' in df.columns else None,
    "total_daily_discharge": df['daily_discharge'].sum() if 'daily_discharge' in df.columns else None,
    "avg_wait_time": df['wait_time'].mean() if 'wait_time' in df.columns else None,
    "total_daily_readmission": df['daily_readmission'].sum() if 'daily_readmission' in df.columns else None,
}

# Display the metrics
st.subheader("Patient Summary Metrics")
col1, col2,col3, col4 = st.columns(4)

with col1:
    st.metric("Total Patient Days", f"{patient_metrics['total_patient_days']:.0f}" if patient_metrics['total_patient_days'] is not None else "N/A")
with col2:
    st.metric("Total Daily Discharges", f"{patient_metrics['total_daily_discharge']:.0f}" if patient_metrics['total_daily_discharge'] is not None else "N/A")

with col3:
    st.metric("Average Wait Time (minutes)", f"{patient_metrics['avg_wait_time']:.2f}" if patient_metrics['avg_wait_time'] is not None else "N/A")
with col4:
    st.metric("Total Daily Readmissions", f"{patient_metrics['total_daily_readmission']:.0f}" if patient_metrics['total_daily_readmission'] is not None else "N/A")



# Filter the dataset for admission_rate vs readmission_rate
filtered_admission_df = filtered_df[['wait_time', 'admission_rate', 'daily_discharge']]

# Visualizing admission_rate vs readmission_rate filtered by wait_time
st.header("Admission Rate vs daily_discharge Rate by Wait Time")

# Plotting the scatter plot
fig = px.scatter(filtered_admission_df,
                 x='admission_rate',
                 y='daily_discharge',
                 color='wait_time',
                 labels={'admission_rate': 'Admission Rate', 'readmission_rate': 'Readmission Rate'},
                 title='Admission Rate vs daily_discharge Rate (colored by Wait Time)',
                 template='plotly_dark',
                 hover_data=['wait_time'])

# Add trendline if desired
fig.update_traces(marker=dict(size=10, opacity=0.7))

st.plotly_chart(fig, use_container_width=True)


# Filter the dataset for equip_count and equip_use
filtered_equip_df = filtered_df[['wait_time', 'equip_count', 'equip_use']]

# Sum the values for equip_count and equip_use within the filtered dataset
aggregated_data = filtered_equip_df[['equip_count', 'equip_use']].sum()

# Create a doughnut chart
st.header("Equipment Usage")

# Preparing data for the doughnut chart
doughnut_data = pd.DataFrame({
    'Metric': ['Equipment Dormant', 'Equipment In-use'],
    'Value': [aggregated_data['equip_count'], aggregated_data['equip_use']]
})

# Plot the doughnut chart (pie chart with hole)
fig = px.pie(doughnut_data, values='Value', names='Metric', title='Equipment Use Distribution',
             hole=0.4, labels={'Value': 'Total Value', 'Metric': 'Metrics'}, 
             template="plotly_dark", color_discrete_sequence=px.colors.sequential.RdBu)

# Display the doughnut chart in Streamlit
st.plotly_chart(fig, use_container_width=True)


# Time Series Analysis
st.subheader('Time Series Analysis')
filtered_df["weekly"] = filtered_df.index.to_period("W")
linechart = pd.DataFrame(filtered_df.groupby(filtered_df["weekly"].dt.strftime("%b : %d"))["daily_visits"].sum()).reset_index()
fig2 = px.line(linechart, x="weekly", y="daily_visits", labels={"Patient": "count"}, height=500, width=1000, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

# Analysis of least wait time by department
st.subheader("Department with Least Wait Time")

# Group by departments to find the one with the least average wait time
wait_time_by_department = filtered_df.groupby('departments')['wait_time'].mean().reset_index()

# Find department with the least wait time
min_wait_time_department = wait_time_by_department.loc[wait_time_by_department['wait_time'].idxmin()]

st.write(f"Department with the least average wait time: **{min_wait_time_department['departments']}**")
st.write(f"Average wait time: **{min_wait_time_department['wait_time']:.2f} minutes**")

# Plotting wait times for all departments
fig3 = px.bar(wait_time_by_department, x='departments', y='wait_time', title="Wait Time by Department",
              labels={'wait_time': 'Average Wait Time (Minutes)', 'departments': 'Departments'},
              color='wait_time', color_continuous_scale='Blues')

st.plotly_chart(fig3, use_container_width=True)
