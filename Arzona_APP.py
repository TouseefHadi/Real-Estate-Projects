import pandas as pd
import streamlit as st
import plotly.graph_objs as go
import gdown
import os

# Google Drive file ID and URL
file_id = '1L69uaQbqFQuAYGcZAkBMsvUQ-jdycY0FMfvjZ9WZ7HI'
url = f'https://drive.google.com/uc?id={file_id}'
file_path = 'Zillow_Data_Complete.xlsx'

# Download the file from Google Drive
if not os.path.exists(file_path):
    gdown.download(url, file_path, quiet=False)

# Load the Excel file and list the available sheets
xls = pd.ExcelFile(file_path)
sheet_names = xls.sheet_names

# Function to load a specific sheet
def load_sheet(sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df = df.dropna(axis=1, how='all')
    return df

# Function to convert all Date columns to datetime format
def convert_dates(df):
    for col in df.columns:
        if 'Date' in col:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

# Function to prepare data for plotting
def prepare_plot_data(df, address):
    df = df[df['Address'] == address]
    
    if df.empty:
        return [], [], None, None, None, None, None, None, None, None
    
    dates, prices = [], []
    phone, listed_by, zillow_link = None, None, None
    bedrooms, bathrooms, area_sqft, days_on_zillow, built_in = None, None, None, None, None
    
    if 'Phone' in df.columns:
        phone = df['Phone'].dropna().unique()
        phone = phone[0] if len(phone) > 0 else None

    if 'Listed By' in df.columns:
        listed_by = df['Listed By'].dropna().unique()
        listed_by = listed_by[0] if len(listed_by) > 0 else None

    if 'Zillow Links' in df.columns:
        zillow_link = df['Zillow Links'].dropna().unique()
        zillow_link = zillow_link[0] if len(zillow_link) > 0 else None

    if 'Bedrooms' in df.columns:
        bedrooms = df['Bedrooms'].dropna().unique()
        bedrooms = bedrooms[0] if len(bedrooms) > 0 else None

    if 'Bathrooms' in df.columns:
        bathrooms = df['Bathrooms'].dropna().unique()
        bathrooms = bathrooms[0] if len(bathrooms) > 0 else None

    if 'Area (sqft)' in df.columns:
        area_sqft = df['Area (sqft)'].dropna().unique()
        area_sqft = area_sqft[0] if len(area_sqft) > 0 else None

    if 'Days on Zillow' in df.columns:
        days_on_zillow = df['Days on Zillow'].dropna().unique()
        days_on_zillow = days_on_zillow[0] if len(days_on_zillow) > 0 else None

    if 'Built in' in df.columns:
        built_in = df['Built in'].dropna().unique()
        built_in = built_in[0] if len(built_in) > 0 else None

    for i in range(1, 11):
        date_col = f'Date{i}'
        price_col = f'Price{i}'
        if date_col in df.columns and price_col in df.columns:
            date_values = df[date_col].dropna()
            price_values = df[price_col].dropna()
            
            if not date_values.empty and not price_values.empty:
                dates.extend(date_values)
                prices.extend(price_values)

    return dates, prices, phone, listed_by, zillow_link, bedrooms, bathrooms, area_sqft, days_on_zillow, built_in

# Streamlit app setup
st.title("Arizona Properties Dashboard")
st.sidebar.header("Settings")

# Select sheet from sidebar
sheet_name = st.sidebar.selectbox("Select Sheet", sheet_names)
df = load_sheet(sheet_name)
df = convert_dates(df)

# Select address
addresses = df['Address'].dropna().unique()
selected_address = st.sidebar.selectbox("Select Address", addresses)

# Prepare data for plotting
dates, prices, phone, listed_by, zillow_link, bedrooms, bathrooms, area_sqft, days_on_zillow, built_in = prepare_plot_data(df, selected_address)

# Plot the data
if dates:
    formatted_dates = [date.strftime('%m/%d/%Y') for date in dates]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(range(len(dates))),  # Use integer indices for x-axis
        y=prices,
        marker_color='royalblue',
        name='Prices'
    ))
    fig.add_trace(go.Scatter(
        x=list(range(len(dates))),  # Use integer indices for x-axis
        y=prices,
        mode='lines+markers',
        marker=dict(color='red'),
        line=dict(color='red', width=2),
        name='Price Trend'
    ))
    
    fig.update_layout(
        title=f'Price Changes for Address: {selected_address}',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_tickmode='array',
        xaxis_tickvals=list(range(len(dates))),
        xaxis_ticktext=formatted_dates,
        xaxis_tickangle=-45,
        template='plotly_dark'
    )
    
    st.plotly_chart(fig)

# Display address information
if phone or listed_by or zillow_link or bedrooms or bathrooms or area_sqft or days_on_zillow or built_in:
    st.sidebar.subheader("Address Information")
    if phone:
        st.sidebar.write(f"**Phone:** {phone}")
    if listed_by:
        st.sidebar.write(f"**Listed By:** {listed_by}")
    if zillow_link:
        st.sidebar.write(f"**Zillow Link:** [View on Zillow]({zillow_link})")
    if bedrooms:
        st.sidebar.write(f"**Bedrooms:** {bedrooms}")
    if bathrooms:
        st.sidebar.write(f"**Bathrooms:** {bathrooms}")
    if area_sqft:
        st.sidebar.write(f"**Area (sqft):** {area_sqft}")
    if days_on_zillow:
        st.sidebar.write(f"**Days on Zillow:** {days_on_zillow}")
    if built_in:
        st.sidebar.write(f"**Built in:** {built_in}")

st.sidebar.info("Select a sheet and address to view the price trend.")
