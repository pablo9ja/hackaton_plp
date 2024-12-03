import streamlit as st
import plotly.express as px
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Healthcare!!!", page_icon=":bar_chart:", layout="wide")

st.title(" :bar_chart: Helpman Healthcare Interactive Dashboard")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

df = pd.read_csv("fake_healthcare_2.csv")
#st.dataframe(df.head())

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

# Sidebar navigation
st.sidebar.header("Navigation")
pages = ["Overview", "Doctors", "Hospital Performance", "Hospital Staff", "Patients", "Quality of Care", "Revenue Streams"]
page = st.sidebar.selectbox("Select a page", pages)

# Page content
if page == "Overview":
    st.header("Overview")
    overview_df = filtered_df.copy()

    # Calculate summary metrics
    metrics = {
        "avg_length_of_stay": overview_df['patient_days'].mean() if 'patient_days' in overview_df.columns else None,
        "total_beds": overview_df['total_beds'].sum() if 'total_beds' in overview_df.columns else None,
        "occupied_beds": overview_df['beds_in_use'].sum() if 'beds_in_use' in overview_df.columns else None,
        "total_admissions": overview_df['daily_admissions'].sum() if 'daily_admissions' in overview_df.columns else None,
        "avg_treatment_cost": overview_df['daily_revenue'].mean() if 'daily_revenue' in overview_df.columns else None,
    }

    available_beds = metrics["total_beds"] - metrics["occupied_beds"] if metrics["total_beds"] and metrics["occupied_beds"] else None
    bed_occupancy_rate = metrics["occupied_beds"] / metrics["total_beds"] * 100 if metrics["total_beds"] and metrics["occupied_beds"] else None

    # Create a single row for the overview charts
    col1, col2, col3, col4, col5 = st.columns(5)

    if metrics["avg_length_of_stay"] is not None:
        col1.metric("Average Length of Stay (days)", f"{metrics['avg_length_of_stay']:.2f}")

    if bed_occupancy_rate is not None:
        col2.metric("Bed Occupancy Rate (%)", f"{bed_occupancy_rate:.2f}")

    if available_beds is not None:
        col3.metric("Available Beds", f"{available_beds:,}")

    if metrics["total_beds"] is not None:
        col4.metric("Total Beds", f"{metrics['total_beds']:,}")

    if metrics["total_admissions"] is not None:
        col5.metric("Total Admissions", f"{metrics['total_admissions']:,}")

    # Additional overview charts
    if 'daily_admissions' in overview_df.columns and 'departments' in overview_df.columns:
        admissions_by_department = overview_df.groupby('departments')['daily_admissions'].sum().reset_index()
        admissions_by_department = admissions_by_department[admissions_by_department['daily_admissions'] > 0]
        if not admissions_by_department.empty:
            st.subheader("Department Distribution of Admitted Patients")
            fig = px.bar(admissions_by_department, x='departments', y='daily_admissions', title='Admissions by Department')
            fig.update_layout(yaxis_tickformat=',')
            st.plotly_chart(fig, use_container_width=True)

    if 'daily_revenue' in overview_df.columns and 'departments' in overview_df.columns:
        revenue_by_department = overview_df.groupby('departments')['daily_revenue'].mean().reset_index()
        revenue_by_department = revenue_by_department[revenue_by_department['daily_revenue'] > 0]
        if not revenue_by_department.empty:
            st.subheader("Average Treatment Costs")
            fig = px.bar(revenue_by_department, x='departments', y='daily_revenue', title='Average Treatment Costs by Department')
            fig.update_layout(yaxis_tickformat=',')
            st.plotly_chart(fig, use_container_width=True)

elif page == "Doctors":
    st.header("Doctors")
    # Add relevant visualizations and metrics for Doctors

elif page == "Hospital Performance":
    st.header("Hospital Performance")
    performance_df = filtered_df.copy()

    metrics = ['patient_days', 'daily_discharge', 'wait_time', 'daily_profit', 'occupancy_rate', 'readmission_rate', 'bed_turnover']
    for metric in metrics:
        if metric in performance_df.columns:
            st.subheader(f"{metric.replace('_', ' ').title()} by Date")
            fig = px.bar(performance_df, x=performance_df.index, y=metric, title=f"{metric.replace('_', ' ').title()} by Date")
            st.plotly_chart(fig, use_container_width=True)
    # Add relevant visualizations and metrics for Hospital Performance

elif page == "Hospital Staff":
    st.header("Hospital Staff")
    staff_df = filtered_df.copy()

    metrics = ['employee_count', 'employee_resign', 'employee_turnover', 'staff_patient_ratio']
    for metric in metrics:
        if metric in staff_df.columns:
            st.subheader(f"{metric.replace('_', ' ').title()} by Date")
            fig = px.bar(staff_df, x=staff_df.index, y=metric, title=f"{metric.replace('_', ' ').title()} by Date")
            st.plotly_chart(fig, use_container_width=True)
    # Add relevant visualizations and metrics for Hospital Staff

elif page == "Patients":
    st.header("Patients")
    patients_df = filtered_df.copy()

    metrics = ['daily_visits', 'daily_admissions', 'patient_days', 'daily_discharge', 'wait_time', 'staff_patient_ratio']
    for metric in metrics:
        if metric in patients_df.columns:
            st.subheader(f"{metric.replace('_', ' ').title()} by Date")
            fig = px.bar(patients_df, x=patients_df.index, y=metric, title=f"{metric.replace('_', ' ').title()} by Date")
            st.plotly_chart(fig, use_container_width=True)
            # Add relevant visualizations and metrics for Quality of Care

elif page == "Quality of Care":
    st.header("Quality of Care")
    quality_df = filtered_df.copy()

    metrics = ['refer_reason', 'staff_patient_ratio', 'equip_use', 'patient_days']
    for metric in metrics:
        if metric in quality_df.columns:
            st.subheader(f"{metric.replace('_', ' ').title()} by Date")
            fig = px.bar(quality_df, x=quality_df.index, y=metric, title=f"{metric.replace('_', ' ').title()} by Date")
            st.plotly_chart(fig, use_container_width=True)
    # Add relevant visualizations and metrics for Quality of Care

elif page == "Revenue Streams":
    st.header("Revenue Streams")
    revenue_df = filtered_df.copy()

    metrics = ['daily_profit', 'daily_revenue']
    for metric in metrics:
        if metric in revenue_df.columns:
            st.subheader(f"{metric.replace('_', ' ').title()} by Date")
            fig = px.bar(revenue_df, x=revenue_df.index, y=metric, title=f"{metric.replace('_', ' ').title()} by Date")
            st.plotly_chart(fig, use_container_width=True)
            # Add relevant visualizations and metrics for Quality of Care

    # Donut Chart for Revenue Streams
    if 'daily_revenue' in revenue_df.columns:
        st.subheader("Profit Distribution")
        revenue_summary = revenue_df[['daily_revenue']].sum().reset_index()
        revenue_summary.columns = ['Metric', 'Total']
        fig = px.pie(revenue_summary, values='Total', names='Metric', title='profit Distribution', hole=0.5)
        st.plotly_chart(fig, use_container_width=True)
# Detailed Pages
st.header("Detailed Analysis")
department_df = filtered_df.groupby('departments').agg({'beds_in_use': 'sum', 'total_beds': 'first'})
department_df = department_df[department_df['beds_in_use'] > 0]

col1, col2 = st.columns(2)

if not department_df.empty:
    with col1:
        st.subheader("Department Bed In Use")
        fig = px.bar(department_df, x=department_df.index, y='beds_in_use',
                     text=[f'{x:,.2f}' for x in department_df['beds_in_use']],
                     template="seaborn", color='beds_in_use', color_continuous_scale='Viridis')
        fig.update_layout(yaxis_tickformat=',')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Department Available Beds")
        department_df['available_beds'] =  department_df['beds_in_use'] - department_df['total_beds'] 
        
        
        fig = px.bar(department_df, x=department_df.index, y='available_beds',
                     text=[f'{x:,.2f}' for x in department_df['available_beds']],
                     template="seaborn", color='available_beds', color_continuous_scale='Viridis')
        fig.update_layout(yaxis_tickformat=',')
        st.plotly_chart(fig, use_container_width=True)

# Ensure 'patient_days' is included in the aggregation
department_df2 = filtered_df.groupby('departments').agg({
    'daily_visits': 'sum',
    'daily_admissions': 'sum',
    'patient_days': 'sum' if 'patient_days' in filtered_df.columns else None
}).reset_index()

# Remove rows where all values are zero or NaN
department_df2 = department_df2[(department_df2[['daily_visits', 'daily_admissions', 'patient_days']].T != 0).any()]

# Check if 'patient_days' exists in the DataFrame before melting
value_vars = ['daily_visits', 'daily_admissions']
if 'patient_days' in department_df2.columns:
    value_vars.append('patient_days')

department_df_melted = department_df2.melt(id_vars='departments',
                                           value_vars=value_vars,
                                           var_name='Metric', value_name='Count')

# Plotting
with col1:
    st.subheader("Department Daily Visit and Admissions")
    fig = px.bar(department_df_melted, x='departments', y='Count', color='Metric', barmode='group',
                 labels={'Count': 'Count', 'departments': 'Departments'},
                 title='Department Metrics')
    fig.update_layout(yaxis_tickformat=',')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Department Metrics Distribution")
    fig = px.pie(department_df_melted, values='Count', names='Metric',
                 title='Department Metrics Distribution',
                 hole=0.5)
    st.plotly_chart(fig, use_container_width=True)

# Time Series Analysis
filtered_df["weekly"] = filtered_df.index.to_period("W")
if 'daily_visits' in filtered_df.columns:
    st.subheader('Time Series Analysis')
    linechart = pd.DataFrame(filtered_df.groupby(filtered_df["weekly"].dt.strftime("%b : %d"))["daily_visits"].sum()).reset_index()
    fig2 = px.line(linechart, x="weekly", y="daily_visits", labels={"Patient": "count"}, height=500, width=1000, template="gridon")
    fig2.update_layout(yaxis_tickformat=',')
    st.plotly_chart(fig2, use_container_width=True)

# Department Metrics Filter
st.sidebar.header("Choose Department Metrics")
metrics = ['daily_visits', 'daily_admissions', 'wait_time', 'daily_revenue', 'daily_profit', 'ctf_daily']
selected_metrics = st.sidebar.multiselect("Select metrics to display", metrics)

# Filter and display department metrics if selected
if selected_metrics:
    filtered_metrics_df = df.groupby('departments')[selected_metrics].sum().reset_index()
    
    # Remove departments with NaN or zero values for selected metrics
    for metric in selected_metrics:
        if metric in filtered_metrics_df.columns:
            filtered_metrics_df = filtered_metrics_df[filtered_metrics_df[metric].notna() & (filtered_metrics_df[metric] > 0)]
    
    # Check if there are any departments left after filtering
    if filtered_metrics_df.empty:
        st.write("No data available for the selected metrics.")
    else:
        st.subheader("Department Metrics")
        for metric in selected_metrics:
            if metric in filtered_metrics_df.columns:
                fig = px.bar(filtered_metrics_df, x='departments', y=metric,
                             title=f"{metric.replace('_', ' ').title()} by Department")
                st.plotly_chart(fig, use_container_width=True)
        
        # Profit Level Analysis
        if 'daily_profit' in filtered_metrics_df.columns:
            st.subheader("Profit Level by Department")
            fig = px.bar(filtered_metrics_df, x='departments', y='daily_profit',
                         title='Daily Profit by Department')
            st.plotly_chart(fig, use_container_width=True)
        
        # Cost Analysis: Calculate cost from revenue and profit
        if 'daily_revenue' in filtered_metrics_df.columns and 'daily_profit' in filtered_metrics_df.columns:
            filtered_metrics_df['daily_cost'] = filtered_metrics_df['daily_revenue'] - filtered_metrics_df['daily_profit']
            st.subheader("Cost Analysis")
            fig = px.bar(filtered_metrics_df, x='departments', y='daily_cost',
                         title='Daily Cost by Department')
            st.plotly_chart(fig, use_container_width=True)
        
        # Insights
        st.subheader("Metric Summary")
        metrics_summary = {}
        for metric in selected_metrics:
            if metric in filtered_metrics_df.columns:
                mean_value = filtered_metrics_df[metric].mean()
                max_value = filtered_metrics_df[metric].max()
                min_value = filtered_metrics_df[metric].min()
                metrics_summary[metric] = {
                    'Mean': mean_value,
                    'Max': max_value,
                    'Min': min_value
                }
        
        if metrics_summary:
            metrics_df = pd.DataFrame(metrics_summary).T
            st.write("**Metrics Summary:**")
            st.dataframe(metrics_df)
            
        if 'daily_cost' in filtered_metrics_df.columns:
            avg_cost = filtered_metrics_df['daily_cost'].mean()
            st.write(f"**Average Cost**: {avg_cost:.2f}")

else:
    st.write("No metrics selected.")

# Day of the Week Filter
st.sidebar.header("Filter by Day of the Week")
days_of_week = df['day_of_week'].unique()
selected_days = st.sidebar.multiselect("Select days of the week", days_of_week)

# Filter and display data based on selected days
if selected_days:
    filtered_days_df = df[df['day_of_week'].isin(selected_days)]
    
    # Check if there is data after filtering
    if filtered_days_df.empty:
        st.write("No data available for the selected days of the week.")
    else:
        st.subheader("Day of the Week Analysis")
        
        # Bar Plot for Metrics by Day of the Week
        if 'daily_visits' in filtered_days_df.columns:
            day_of_week_visits = filtered_days_df.groupby('day_of_week')['daily_visits'].sum().reset_index()
            fig = px.bar(day_of_week_visits, x='day_of_week', y='daily_visits',
                         title='Total Daily Visits by Day of the Week')
            st.plotly_chart(fig, use_container_width=True)
        
        # Pie Chart for Metrics Distribution by Day of the Week
        if 'daily_revenue' in filtered_days_df.columns:
            day_of_week_revenue = filtered_days_df.groupby('day_of_week')['daily_revenue'].sum().reset_index()
            fig = px.pie(day_of_week_revenue, values='daily_revenue', names='day_of_week',
                         title='Profit Distribution by Day of the Week', hole=0.5)
            st.plotly_chart(fig, use_container_width=True)
else:
    st.write("No days of the week selected.")