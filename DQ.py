import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

# Sample Data for Demonstration
df = pd.DataFrame({
    'Category': ['A', 'B', 'C', 'D'],
    'Values': [10, 20, 30, 40]
})

def create_pdf(dataframes, charts):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y_position = height - 40
    
    for i, (title, df) in enumerate(dataframes.items()):
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y_position, title)
        y_position -= 20

        # Draw the dataframe as text
        c.setFont("Helvetica", 10)
        text = df.to_string(index=False)
        for line in text.split('\n'):
            c.drawString(30, y_position, line)
            y_position -= 12

        y_position -= 20  # Space between sections

        if y_position < 100:
            c.showPage()
            y_position = height - 40

    for i, (title, chart) in enumerate(charts.items()):
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y_position, title)
        y_position -= 20

        # Save the chart to a temporary file
        temp_image_path = f"chart_{i}.png"
        chart.savefig(temp_image_path)
        c.drawImage(temp_image_path, 30, y_position - 200, width=500, height=200)
        y_position -= 220

        if y_position < 100:
            c.showPage()
            y_position = height - 40

        # Clean up the temporary file
        os.remove(temp_image_path)

    c.save()
    buffer.seek(0)
    return buffer

st.title("Streamlit Dashboard with Download Option")

tabs = st.tabs(["Tab 1", "Tab 2", "Download"])

dataframes = {}
charts = {}

with tabs[0]:
    st.header("Tab 1: Data and Chart")
    st.write(df)
    dataframes["Tab 1: Data"] = df
    fig1, ax1 = plt.subplots()
    df.plot(kind='bar', x='Category', y='Values', ax=ax1)
    st.pyplot(fig1)
    charts["Tab 1: Chart"] = fig1

with tabs[1]:
    st.header("Tab 2: Another Chart")
    fig2, ax2 = plt.subplots()
    df.plot(kind='line', x='Category', y='Values', ax=ax2)
    st.pyplot(fig2)
    charts["Tab 2: Another Chart"] = fig2

with tabs[2]:
    st.header("Download Dashboard Content")

    if st.button("Download as PDF"):
        pdf_buffer = create_pdf(dataframes, charts)
        st.download_button(label="Download PDF", data=pdf_buffer, file_name="dashboard_content.pdf", mime="application/pdf")
