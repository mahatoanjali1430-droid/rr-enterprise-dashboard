import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="RR Enterprise Analytics", layout="wide")

# Title & Header
st.title("🏭 RR Enterprise — Business Analytics Dashboard")
st.markdown("**Consulting Services:** Client Churn Risk | Visual Revenue Analytics | Inventory ABC Optimization")
st.divider()

# Load Datasets
@st.cache_data
def load_data():
    sales_df = pd.read_csv('rr_enterprise_sales_data.csv')
    sales_df['OrderDate'] = pd.to_datetime(sales_df['OrderDate'])
    risk_df = pd.read_csv('at_risk_clients.csv')
    return sales_df, risk_df

try:
    df_sales, at_risk_clients = load_data()
except Exception as e:
    st.error("Please ensure 'rr_enterprise_sales_data.csv' and 'at_risk_clients.csv' are in the project folder.")
    st.stop()

# Sidebar Filters
st.sidebar.header("Filter Analytics")
selected_category = st.sidebar.multiselect(
    "Select Category", 
    options=df_sales['Category'].unique(), 
    default=df_sales['Category'].unique()
)

filtered_df = df_sales[df_sales['Category'].isin(selected_category)]

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"₹{filtered_df['TotalAmount'].sum():,.2f}")
col2.metric("Total Orders", f"{filtered_df['InvoiceNo'].nunique():,}")
col3.metric("Total Clients", f"{filtered_df['ClientID'].nunique()}")
col4.metric("At-Risk Accounts", f"{len(at_risk_clients)}")

st.divider()

# Tabs for 3 Services
tab1, tab2, tab3 = st.tabs(["📉 Service 1: At-Risk Clients", "📊 Service 2: Revenue Analytics", "📦 Service 3: Inventory ABC Analysis"])

# TAB 1: SERVICE 1
with tab1:
    st.subheader("B2B Client Inactivity & Churn Risk Analysis")
    st.write("Clients flagged with high recency gap and falling order frequency.")
    st.dataframe(at_risk_clients, use_container_width=True)
    
    st.download_button(
        label="📥 Download At-Risk Client List CSV",
        data=at_risk_clients.to_csv(index=False),
        file_name="at_risk_clients_report.csv",
        mime="text/csv"
    )

# TAB 2: SERVICE 2
with tab2:
    st.subheader("Sales & Revenue Dashboard")
    c1, c2 = st.columns(2)
    
    with c1:
        st.write("### Monthly Revenue Trend")
        monthly_rev = filtered_df.resample('ME', on='OrderDate')['TotalAmount'].sum() / 1000
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        ax1.plot(monthly_rev.index.strftime('%b %Y'), monthly_rev.values, marker='o', color='#2b5c8f')
        ax1.set_ylabel("Revenue (₹ Thousands)")
        plt.xticks(rotation=45)
        st.pyplot(fig1)

    with c2:
        st.write("### Category Revenue Contribution")
        cat_rev = filtered_df.groupby('Category')['TotalAmount'].sum().sort_values(ascending=True) / 1000
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.barh(cat_rev.index, cat_rev.values, color='#2b5c8f')
        ax2.set_xlabel("Revenue (₹ Thousands)")
        st.pyplot(fig2)

# TAB 3: SERVICE 3
with tab3:
    st.subheader("Inventory ABC Classification (Dead Stock & Turnover)")
    
    inv = filtered_df.groupby('Category').agg({'TotalAmount': 'sum', 'Quantity': 'sum'}).reset_index()
    inv = inv.sort_values(by='TotalAmount', ascending=False).reset_index(drop=True)
    inv['Cum_Revenue'] = inv['TotalAmount'].cumsum()
    inv['Cum_Perc'] = 100 * inv['Cum_Revenue'] / inv['TotalAmount'].sum()

    def assign_abc(perc):
        if perc <= 70:
            return 'Class A (High Value / Fast Moving)'
        elif perc <= 90:
            return 'Class B (Moderate Value)'
        else:
            return 'Class C (Slow Moving / Dead Stock Risk)'

    inv['ABC_Class'] = inv['Cum_Perc'].apply(assign_abc)
    st.dataframe(inv[['Category', 'Quantity', 'TotalAmount', 'ABC_Class']], use_container_width=True)
