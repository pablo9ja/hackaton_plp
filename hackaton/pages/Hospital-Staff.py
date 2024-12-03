import streamlit as st
import plotly.express as px
import pandas as pd

def run():
    pass

st.title(" :bar_chart: Helpman Healthcare Interactive Dashboard For Hospital Staffs")
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
department = st.sidebar.multiselect("Pick your department", df["departments"].unique())
if not department:
    filtered_df = df.copy()
else:
    filtered_df = df[df["departments"].isin(department)]

# Overview Page
#st.header("Overview")
overview_df = filtered_df.copy()


# Calculate summary metrics for employee data
employee_metrics = {
    "total_employee_count": overview_df['employee_count'].sum() if 'employee_count' in overview_df.columns else None,
    "avg_employee_count": overview_df['employee_count'].mean() if 'employee_count' in overview_df.columns else None,
    "total_employee_resign": overview_df['employee_resign'].sum() if 'employee_resign' in overview_df.columns else None,
    "avg_employee_resign": overview_df['employee_resign'].mean() if 'employee_resign' in overview_df.columns else None,
}

# Display the metrics
st.subheader("Employee Summary Metrics")
col1, col2,col3, col4 = st.columns(4)

with col1:
    st.metric("Total Employee Count", f"{employee_metrics['total_employee_count']:.0f}" if employee_metrics['total_employee_count'] is not None else "N/A")
    
with col2:
    st.metric("Average Employee Count", f"{employee_metrics['avg_employee_count']:.2f}" if employee_metrics['avg_employee_count'] is not None else "N/A")

with col3:
    st.metric("Total Employee Resignations", f"{employee_metrics['total_employee_resign']:.0f}" if employee_metrics['total_employee_resign'] is not None else "N/A")
with col4:
    st.metric("Average Employee Resignations", f"{employee_metrics['avg_employee_resign']:.2f}" if employee_metrics['avg_employee_resign'] is not None else "N/A")


# Department-based analysis for employee metrics
department_employee_df = filtered_df.groupby('departments').agg({
    'employee_count': 'sum',
    'employee_resign': 'sum'
}).reset_index()

# Creating columns for metrics visualization
col1, col2 = st.columns(2)

# Bar Chart for Employee Count by Department
with col1:
    st.subheader("Employee Count by Department")
    fig = px.bar(department_employee_df, x='departments', y='employee_count',
                 title='Total Employee Count by Department',
                 labels={'employee_count': 'Employee Count', 'departments': 'Departments'},
                 template="seaborn")
    st.plotly_chart(fig, use_container_width=True)

# Bar Chart for Employee Resignations by Department
with col2:
    st.subheader("Employee Resignations by Department")
    fig = px.bar(department_employee_df, x='departments', y='employee_resign',
                 title='Total Employee Resignations by Department',
                 labels={'employee_resign': 'Employee Resignations', 'departments': 'Departments'},
                 template="seaborn")
    st.plotly_chart(fig, use_container_width=True)

# Time Series for Employee Data
filtered_df["weekly"] = filtered_df.index.to_period("W").start_time
st.subheader('Time Series Analysis of Employee Count')

# Group by weekly and sum the employee_count
linechart = pd.DataFrame(filtered_df.groupby("weekly")["employee_count"].sum()).reset_index()

# Plot the line chart
fig2 = px.line(linechart, x="weekly", y="employee_count", 
               labels={"employee_count": "Employee Count", "weekly": "Week"},
               title='Weekly Employee Count Over Time', 
               height=500, width=1000, template="gridon")

st.plotly_chart(fig2, use_container_width=True)


# Ensure the day_of_week column exists
filtered_df["day_of_week"] = filtered_df.index.day_name()

# Sidebar filter for Day of the Week
st.sidebar.header("Filter by Day of the Week")
day_of_week = st.sidebar.multiselect("Select the Day(s) of the Week", 
                                     filtered_df["day_of_week"].unique())

# Filter by the selected day(s)
if day_of_week:
    filtered_df = filtered_df[filtered_df["day_of_week"].isin(day_of_week)]

# Time Series for Employee Data (Employee Count and Resign)
st.subheader('Time Series Analysis of Employee Count and Employee Resign')

# Group by day of the week and sum the employee_count and employee_resign
employee_data = filtered_df.groupby("day_of_week")[["employee_count", "employee_resign"]].sum().reset_index()

# Sort the days in a week order
days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
employee_data["day_of_week"] = pd.Categorical(employee_data["day_of_week"], categories=days_order, ordered=True)
employee_data = employee_data.sort_values("day_of_week")

# Plot the bar chart for both employee_count and employee_resign
fig = px.bar(employee_data, x="day_of_week", y=["employee_count", "employee_resign"],
             barmode='group', labels={"value": "Count", "day_of_week": "Day of the Week"},
             title="Employee Count and Resignations by Day of the Week", template="plotly_white")

st.plotly_chart(fig, use_container_width=True)

# Group the data by departments and sum employee_count and employee_resign
employee_distribution = filtered_df.groupby('departments')[['employee_count', 'employee_resign']].sum().reset_index()

# Plot the bar chart for employee_count and employee_resign across departments
st.subheader('Employee Count and Resignations by Department')

fig = px.bar(employee_distribution, x='departments', y=['employee_count', 'employee_resign'],
             barmode='group', labels={"value": "Count", "departments": "Departments"},
             title="Employee Count and Resignations Distribution Across Departments",
             template="plotly_white")

st.plotly_chart(fig, use_container_width=True)

