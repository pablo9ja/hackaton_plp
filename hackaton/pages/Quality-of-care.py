
import streamlit as st
import plotly.express as px
import pandas as pd

def run():
    pass
st.title(" :bar_chart: Helpman Healthcare Quality of care Interactive Dashboard")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

st.write("Quality of care")


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
    df2 = df.copy()
else:
    df2 = df[df["departments"].isin(department)]

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
overview_df = filtered_df.copy()

# Calculate summary metrics
avg_length_of_stay = overview_df['patient_days'].mean()
total_beds = overview_df['total_beds'].sum()
occupied_beds = overview_df['beds_in_use'].sum()
bed_occupancy_rate = occupied_beds / total_beds * 100
total_admissions = overview_df['daily_admissions'].sum()
avg_treatment_cost = overview_df['daily_revenue'].mean()

# Create a single row for the overview charts
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Average Length of Stay (days)", f"{avg_length_of_stay:.2f}")

with col2:
    st.metric("Bed Occupancy Rate (%)", f"{bed_occupancy_rate:.2f}")

with col3:
    st.metric("Occupied Beds", occupied_beds)

with col4:
    st.metric("Total Beds", total_beds)

with col5:
    st.metric("Total Admissions", total_admissions)

# Additional overview charts
st.subheader("Department Distribution of Admitted Patients")
admissions_by_department = overview_df.groupby('departments')['daily_admissions'].sum().reset_index()
fig = px.bar(admissions_by_department, x='departments', y='daily_admissions', title='Admissions by Department')
st.plotly_chart(fig, use_container_width=True)

st.subheader("Average Treatment Costs")
fig = px.bar(overview_df, x='departments', y='daily_revenue', title='Average Treatment Costs by Department')
st.plotly_chart(fig, use_container_width=True)

# Detailed Pages
st.header("Detailed Analysis")
department_df = filtered_df.groupby('departments').agg({'beds_in_use': 'sum', 'total_beds': 'first'})

col1, col2 = st.columns(2)

with col1:
    st.subheader("Department Bed In Use")
    fig = px.bar(department_df, x=department_df.index, y='beds_in_use',
                 text=[f'{x:,.2f}' for x in department_df['beds_in_use']],
                 template="seaborn", color='beds_in_use', color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Department Bed In Use")
    fig = px.bar(department_df, x=department_df.index, y='beds_in_use',
                 text=[f'{x:,.2f}' for x in department_df['beds_in_use']],
                 template="seaborn", color='beds_in_use', color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)

department_df2 = filtered_df.groupby('departments').agg({
    'daily_visits': 'sum',
    'daily_admissions': 'sum',
    'patient_days': 'sum'
}).reset_index()
department_df_melted = department_df2.melt(id_vars='departments',
                                           value_vars=['daily_visits', 'daily_admissions', 'patient_days'],
                                           var_name='Metric', value_name='Count')

with col1:
    st.subheader("Department Daily Visit and Admissions")
    fig = px.bar(department_df_melted, x='departments', y='Count', color='Metric', barmode='group',
                 labels={'Count': 'Count', 'departments': 'Departments'},
                 title='Department Metrics')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Department Metrics Distribution")
    fig = px.pie(department_df_melted, values='Count', names='Metric',
                 title='Department Metrics Distribution',
                 hole=0.5)
    st.plotly_chart(fig, use_container_width=True)

filtered_df["weekly"] = filtered_df.index.to_period("W")
st.subheader('Time Series Analysis')
linechart = pd.DataFrame(filtered_df.groupby(filtered_df["weekly"].dt.strftime("%b : %d"))["daily_visits"].sum()).reset_index()
fig2 = px.line(linechart, x="weekly", y="daily_visits", labels={"Patient": "count"}, height=500, width=1000, template="gridon")
st.plotly_chart(fig2, use_container_width=True)
