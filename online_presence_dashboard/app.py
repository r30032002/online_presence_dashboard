import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# --------------------------
# Load and prepare traffic data
# --------------------------
df = pd.read_csv("data/processed/traffic.csv")

# Convert 'Date' column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Remove commas and convert company columns to numeric safely
for col in df.columns[1:]:
    df[col] = df[col].astype(str).str.replace(',', '').replace('nan', '0')
    df[col] = pd.to_numeric(df[col], errors='coerce')

df.fillna(0, inplace=True)
df = df.sort_values("Date")
companies = df.columns[1:]

# --------------------------
# Streamlit App Config
# --------------------------
st.set_page_config(page_title="Online Presence Tracker", layout="wide")
st.title("📊 Online Presence Dashboard – Assistive Tech Companies")
st.subheader("Source Data from SemRush Analytics")

# --------------------------
# Tabs for navigation
# --------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Overview",
    "📈 Company Detail",
    "🔀 Compare Companies",
    "🏆 Most Visited Companies",
    "🗺️ Map of Retail Stores",
])

# --------------------------
# Tab 1 – Overview
# --------------------------
with tab1:
    st.header("Monthly Traffic (All Companies)")

    melted_df = df.melt(id_vars='Date', var_name='Company', value_name='Visits')
    fig = px.line(melted_df, x="Date", y="Visits", color="Company", markers=True)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📄 Raw Traffic Data")
    st.dataframe(df, use_container_width=True)

# --------------------------
# Tab 2 – Company Detail
# --------------------------
with tab2:
    st.header("Company Level Insights")
    selected_company = st.selectbox("Select a company", companies)

    company_data = df[["Date", selected_company]].copy()
    company_data['Previous'] = company_data[selected_company].shift(1)
    company_data['Change'] = company_data[selected_company] - company_data['Previous']
    company_data['% Change'] = (company_data['Change'] / company_data['Previous']) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Latest Visits", int(company_data[selected_company].iloc[-1]))
    col2.metric("Monthly Change", f"{int(company_data['Change'].iloc[-1]):+}")
    col3.metric("% Change", f"{company_data['% Change'].iloc[-1]:+.1f}%")

    fig = px.line(company_data, x="Date", y=selected_company,
                  title=f"Monthly Visits for {selected_company}", markers=True,
                  labels={selected_company: "Visits"})
    st.plotly_chart(fig, use_container_width=True)

# --------------------------
# Tab 3 – Compare Companies
# --------------------------
with tab3:
    st.header("Compare Companies")
    selected = st.multiselect("Select companies to compare", companies, default=list(companies[:3]))

    if selected:
        df_comp = df[["Date"] + selected].copy()
        melted = df_comp.melt(id_vars="Date", var_name="Company", value_name="Visits")
        fig = px.line(melted, x="Date", y="Visits", color="Company",
                      title="Monthly Visits Comparison", markers=True)
        st.plotly_chart(fig, use_container_width=True)

# --------------------------
# Tab 4 – Leaderboard
# --------------------------
with tab4:
    st.header("Traffic Leaderboard (Latest Month)")

    latest_row = df.iloc[-1]
    prev_row = df.iloc[-2]

    leaderboard = pd.DataFrame({
        "Company": companies,
        "Latest Visits": latest_row[1:].values,
        "Previous Visits": prev_row[1:].values
    })

    leaderboard["Change"] = leaderboard["Latest Visits"] - leaderboard["Previous Visits"]
    leaderboard["% Change"] = (leaderboard["Change"] / leaderboard["Previous Visits"]) * 100
    leaderboard = leaderboard.sort_values("Latest Visits", ascending=False)

    st.dataframe(leaderboard.style.format({
        "Latest Visits": "{:,.0f}",
        "Previous Visits": "{:,.0f}",
        "Change": "{:+,.0f}",
        "% Change": "{:+.1f}%"
    }))

# --------------------------
# Tab 5 – Map of Retail Stores
# --------------------------
with tab5:
    st.header("🗺️ Map of Retail Stores")

    # Load store locations CSV
    stores_df = pd.read_csv("data/processed/joint_ils_aid_geocoded.csv")

    # Create base map centered on Australia
    m = folium.Map(location=[-25.0, 133.0], zoom_start=4)

    # Color palette for store types
    type_colors = {
        'ILS': 'blue',
        "Aidacare": "green",
    }

    # Add markers for each store
    for _, row in stores_df.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"<b>{row['Store']}</b><br>{row['Address']}<br>{row['Phone Number']}",
            icon=folium.Icon(color=type_colors.get(row['Type'], 'red'), icon='info-sign')
        ).add_to(m)

    # --------------------------
    # Add Legend
    # --------------------------
    legend_html = """
     <div style="
     position: fixed; 
     bottom: 50px; left: 50px; width: 150px; height: 90px; 
     background-color: white; 
     border:2px solid grey; 
     z-index:9999; 
     font-size:14px;
     padding: 10px;
     ">
     <b>Store Type Legend</b><br>
     &nbsp;<i class="fa fa-map-marker fa-2x" style="color:lightblue"></i>&nbsp; ILS<br>
     &nbsp;<i class="fa fa-map-marker fa-2x" style="color:green"></i>&nbsp; Aidacare<br>
     </div>
     """
    m.get_root().html.add_child(folium.Element(legend_html))

    # Display map in Streamlit
    st_folium(m, width=1000, height=600)
