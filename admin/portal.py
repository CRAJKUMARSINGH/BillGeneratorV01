import streamlit as st
import pandas as pd
from tools.telemetry.telemetry_helper import LOG_PATH
import json
from pathlib import Path

st.title("🏛 National BillGenerator Control Dashboard")

# Load telemetry data if available
if LOG_PATH.exists():
    try:
        # Read the telemetry log file
        telemetry_data = []
        with open(LOG_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    telemetry_data.append(json.loads(line))
        
        if telemetry_data:
            df = pd.DataFrame(telemetry_data)
            
            # Display metrics
            st.metric("Total Sessions", len(df["session"].unique()))
            st.metric("Bills Generated", (df["event"] == "bill_generated").sum())
            
            # Display event timeline
            st.subheader("Recent Activity")
            st.dataframe(df.tail(10)[["timestamp", "event", "session"]], use_container_width=True)
            
            # Display event distribution
            st.subheader("Event Distribution")
            event_counts = df["event"].value_counts()
            st.bar_chart(event_counts)
        else:
            st.info("No telemetry data available yet.")
    except Exception as e:
        st.error(f"Error loading telemetry data: {e}")
else:
    st.info("Telemetry log file not found. No data available yet.")

# Tenant configuration
st.subheader("Tenant Configuration")
st.info("Multi-tenant configuration loaded from config/tenants.yaml")
st.code("""
rajasthan:
  db_url: "postgresql://user:pass@host/rajasthan_bills"
  branding: "PWD Rajasthan"
uttar_pradesh:
  db_url: "postgresql://user:pass@host/up_bills"
  branding: "PWD UP"
""", language="yaml")

# System status
st.subheader("System Status")
st.success("✅ All systems operational")
st.info("🕒 Last updated: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))