import streamlit as st
import pandas as pd
import altair as alt
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Initialize session state
if 'dashboard_generated' not in st.session_state:
    st.session_state.dashboard_generated = False

# Reading CSV files
df = pd.read_csv("percentile_table.csv")
max_df = pd.read_csv("MaximumValueSenseCheck.csv")
missing_df = pd.read_csv("missing_vals_table.csv")
psi_df = pd.read_csv("psi.csv")
indipsi_df = pd.read_csv("indipsi.csv")

# Display Shift Summary
def display_shift_summary():
    shift_columns = ['P10 Shift', 'P25 Shift', 'P50 Shift', 'P75 Shift', 'P90 Shift']
    shift_summary = df[shift_columns].apply(pd.Series.value_counts).fillna(0).astype(int)
    st.write("Shift Summary Count")
    st.dataframe(shift_summary, use_container_width=True)

# Display Shift Values
def display_shift_values(value):
    shift_columns = ['P10 Shift', 'P25 Shift', 'P50 Shift', 'P75 Shift', 'P90 Shift']
    if value in df['Values'].values:
        st.write(f'Shift Values for {value}')
        st.dataframe(df[df['Values'] == value][shift_columns].reset_index(drop=True))

# Display Index Names
def display_index_names(shift_type):
    shift_columns = ['P10 Shift', 'P25 Shift', 'P50 Shift', 'P75 Shift', 'P90 Shift']
    filtered_df = df[(df[shift_columns] == shift_type).any(axis=1)]
    result = {col: filtered_df[filtered_df[col] == shift_type]['Values'].tolist() for col in shift_columns}
    result_df = pd.DataFrame.from_dict(result, orient='index').transpose()
    st.write(f'Shift Values for {shift_type}')
    st.dataframe(result_df, use_container_width=True)

# Display Selected Value
def display_selected_value(value):
    st.write(f'Maximum Value Sense for {value}')
    selected_row = max_df[max_df[max_df.columns[0]] == value]
    st.dataframe(selected_row.reset_index(drop=True))

# Display Grouped Shift
def display_grouped_shift(selected_ranges):
    labels = ["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"]
    bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    max_df['Shift % Range'] = pd.cut(max_df['Shift %'], bins=bins, labels=labels, include_lowest=True)
    grouped = max_df.groupby('Shift % Range')[max_df.columns[0]].apply(list).reset_index()
    filtered_grouped = grouped[grouped['Shift % Range'].isin(selected_ranges)]
    expanded_rows = []
    for _, row in filtered_grouped.iterrows():
        shift_range = row['Shift % Range']
        values = row[max_df.columns[0]]
        for value in values:
            expanded_rows.append({'Shift % Range': shift_range, max_df.columns[0]: value})
    expanded_df = pd.DataFrame(expanded_rows)
    st.write("Values grouped by Shift %")
    st.dataframe(expanded_df)

# Display High Shift
def display_high_shift():
    st.write("Values with Shift % > 50%")
    high_shift = max_df[max_df['Shift %'] > 0.50]
    st.dataframe(high_shift[max_df.columns[0]])

# Display Shift Summary Missing
def display_shift_summary_missing():
    shift_summary = missing_df['Shift'].value_counts().reset_index()
    shift_summary.columns = ['Shift', 'Count']
    st.write("Summary of Missing Values")
    st.dataframe(shift_summary)

# Display Values for Shift
def display_values_for_shift(shift_type):
    filtered_df = missing_df[missing_df['Shift'] == shift_type]
    st.write(f'Shift Type: {shift_type}')
    st.dataframe(filtered_df[filtered_df.columns[0]].reset_index(drop=True))

# Display PSI Overview
def display_psi_overview():
    def color_code_rag(val):
        if val == "No Shift":
            return 'background-color: green'
        elif val == "Moderate Shift":
            return 'background-color: yellow'
        elif val == "Significant Shift":
            return 'background-color: red'
        else:
            return ''
    
    st.write("PSI Values Overview")
    styled_df = psi_df.style.applymap(color_code_rag, subset=['RAG']).hide(axis='index')
    st.dataframe(styled_df,hide_index=True)    
    
# Display Column Details
def display_column_details(selected_attribute):
    st.write(f'PSI for {selected_attribute}')
    psi_value = psi_df[psi_df['Attribute'] == selected_attribute]['PSI'].values[0]
    st.write(f'PSI Value: {psi_value}')
    attribute_data = indipsi_df[indipsi_df['Attribute'] == selected_attribute]
    st.dataframe(attribute_data, use_container_width=True, hide_index=True)
    

    
def display_column_graph(selected_attribute):
    df = indipsi_df

    # Convert percentage strings to float
    df['Benchmark %Acc'] = df['Benchmark %Acc'].str.rstrip('%').astype(float)
    df['Validation %Acc'] = df['Validation %Acc'].str.rstrip('%').astype(float)

    # Filter dataframe based on the selected attribute
    filtered_df = df[df['Attribute'] == selected_attribute]

    # Plotting with Plotly
    fig = go.Figure()

    # Bar chart for Validation %Acc
    fig.add_trace(go.Bar(
        x=filtered_df['Nodes'],
        y=filtered_df['Validation %Acc'],
        name='Validation %Acc',
        marker_color='blue'
    ))

    # Line chart for Benchmark %Acc
    fig.add_trace(go.Scatter(
        x=filtered_df['Nodes'],
        y=filtered_df['Benchmark %Acc'],
        name='Benchmark %Acc',
        mode='lines+markers',
        marker_color='red'
    ))

    # Adding labels and title
    fig.update_layout(
        title=f'Validation %Acc and Benchmark %Acc for {selected_attribute}',
        xaxis_title='Nodes',
        yaxis_title='Percentage Accuracy',
        legend=dict(x=0.01, y=0.99)
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig)

# Sidebar Configuration
st.sidebar.header("Data Configuration")
total_months = st.sidebar.number_input("Total Months", value=12)
benchmark_months = st.sidebar.number_input("Benchmark Months", value=6)
nodes_considered = st.sidebar.number_input("Nodes Considered", value=10)
generate_button = st.sidebar.button("Generate Dashboard")

if generate_button or st.session_state.dashboard_generated:
    st.session_state.dashboard_generated = True
    st.title('Data Quality Checks Dashboard')
    st.sidebar.write("Current Month = Dec 2023")
    st.sidebar.write("RAG Status for PSI:")
    st.sidebar.image("PSI.png", caption="RAG Status for PSI", width=300)
    st.sidebar.write("RAG Status for Percentile Variation:")
    st.sidebar.image("Percentile.png", caption="RAG Status for Percentile Variation", width=300)
    st.sidebar.write("RAG Status for Missing Value Checks:")
    st.sidebar.image("Missing.png", caption="RAG Status for Missing Value Checks", width=300)

    tabs = st.tabs(["Population Stability Index", "Percentile Variation", "Maximum Value Sense Checks", "Missing Value Checks", "Columnar View"])

    with tabs[0]:
        st.header("Population Stability Index")
        st.write("The Population Stability Index (PSI) measures the stability of a population's distribution.")
        st.write("It helps to monitor changes in the distribution of a variable over time.")
        with st.expander("1. PSI Values Overview"):
            display_psi_overview()
        with st.expander("2. Select Column"):
            unique_columns = psi_df["Attribute"].unique()
            selected_column = st.selectbox("Select Column", unique_columns)
            display_column_details(selected_column)
        with st.expander("Graphical Representation"):
            display_column_graph(selected_column)

    with tabs[1]:
        st.header("Percentile Variation")
        st.write("Percentile Variation shows the shift in percentiles of a distribution over time.")
        st.write("It helps to understand how different segments of the population are shifting.")
        with st.expander("1. Shift Summary Table"):
            display_shift_summary()
        with st.expander("2. Shift Values for Selected Column"):
            value = st.selectbox("Select Column", df['Values'].unique())
            display_shift_values(value)
        with st.expander("3. Shift Type View"):
            shift_types = ["No Shift", "Moderate Shift", "Significant Shift", "Blanks"]
            shift_type = st.selectbox("Select Shift Type", shift_types)
            display_index_names(shift_type)

    with tabs[2]:
        st.header("Max Value Sense Check")
        st.write("Maximum Value Sense Checks validate the reasonableness of the maximum values in the dataset.")
        st.write("It ensures that the highest values conform to expected ranges and business rules.")        
        with st.expander("1. Select Value"):
            selected_value = st.selectbox("Select Value", max_df[max_df.columns[0]].unique())
            display_selected_value(selected_value)
        with st.expander("2. Values with Shift > 50%"):
            display_high_shift()
        with st.expander("3. Shift Grouping"):
            range_labels = ["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"]
            selected_ranges = st.multiselect("Select Ranges", range_labels, default=range_labels)
            display_grouped_shift(selected_ranges)

    with tabs[3]:
        st.header("Missing Value Checks")
        st.write("Missing Value Checks analyze the presence and patterns of missing values in the dataset.")
        st.write("It helps to understand the extent and impact of missing data on analysis.")
        with st.expander("1. Data Preview"):
            st.dataframe(missing_df, use_container_width=True)
        with st.expander("2. Summary of Shift Column"):
            display_shift_summary_missing()
        with st.expander("3. Values for Selected Shift Type"):
            shift_types_missing = missing_df["Shift"].unique()
            selected_shift_type = st.selectbox("Select Shift Type", shift_types_missing)
            display_values_for_shift(selected_shift_type)

    with tabs[4]:
        st.header("Columnar View")
        st.write("The Columnar View provides detailed insights into individual columns of the dataset.")
        st.write("It allows for a focused examination of specific attributes and their statistics.")
        st.write("Content for Population")
