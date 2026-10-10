import pandas as pd
import streamlit as st
import plotly.express as px

# set page title
st.set_page_config(page_title='Sales_dashboard', page_icon='📊', layout='wide')
# load data with optimization 
@ st.cache_data
def load_data():
    #load the data
    df = pd.read_excel("powerquery_sales_data.xlsx", sheet_name="clean with powerquery")
    return df
df = load_data()
# sidebar columns with filters
st.sidebar.header("Columns")
filters = {}
# Loop through every column in your dataset and stack them in the sidebar
for col_names in df.columns:
    # get unique values, set all to reset the filter
    unique_values = ["All"] + list(df[col_names].dropna().unique())
    col_type = df[col_names].dtype
    with st.sidebar.expander(f"📌 {col_names} `{col_type}`"):
        #st.caption(f"Data Type: `{col_type}`")
        selected_val = st.multiselect(f"filter {col_names}", options=unique_values, default=unique_values, key=f"v_filter_{col_names}")
        filters[col_names] = selected_val

# apply filters to data frame
filtered_df = df.copy()
for col_names, selected_values in filters.items():
        # If the user selected items, filter the dataframe using .isin()
        if selected_values:
             filtered_df = filtered_df[filtered_df[col_names].isin(selected_values)]

# main dashboard
col1, col2 = st.columns([4.5,2.5])
with col1:
    st.markdown("# **Sales Dashboard**")
    st.markdown("#### A comprehensive overview of orders, revenue performance & customer metrics")
    st.markdown("----")
    # top KPI's to present on screen
    total_revenue = filtered_df["Net Amount"].sum()
    total_item_sold = filtered_df['Quantity'].sum()
    total_orders = filtered_df['Order ID'].nunique()
    st.markdown("### Top KPI's Summary Cards")
    with st.container(border=True):
        colmd1, colmd2, colmd3 = st.columns([2, 1, 1])
    with colmd1:
        st.metric("Revenue", f"Rs {total_revenue:,.2f}")
    with colmd2:
        st.metric("Item Sold", f"{total_item_sold}")
    with colmd3:
        st.metric("Total Orders", total_orders)

with col2:
    st.subheader("Data Quality")
    with st.container(border=True):
         col1, col2 = st.columns([2, 1])
         with col1:
            st.markdown(f"**Null values:** {df.isnull().sum().sum()}")
            st.markdown(f"**Duplicate rows:** {df.duplicated().sum()}")
         with col2:
            total_outliers = {}
            for cl in df[['Quantity', 'Unit Price', 'Net Amount']]:
                q1 = df[cl].quantile(0.25)
                q3 = df[cl].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 *iqr
                upper_bound = q3 + 1.5 * iqr
                outliers = df[(df[cl] < lower_bound) | (df[cl] > upper_bound)]
                total_outliers[cl] = len(outliers)
            st.markdown("Outliers")
            for col_name, count in total_outliers.items():
                st.markdown(f"{col_name}: {count}")
    with st.container(border=True):
        st.caption(" **Note:** Outlier represent legitimate bulk or premium orders. No need to be removed.")        
st.markdown("----")
# trend line
filtered_df["clean_date"] = pd.to_datetime(filtered_df["Order Date"]).dt.strftime('%b %d, %Y')
trend_df =filtered_df.groupby("clean_date")['Net Amount'].sum().reset_index()
# line plot
trend_fig = px.line(trend_df, x='clean_date', y='Net Amount', title = "<b>Revenue Trend Over Time</b>", markers=True, line_shape="spline")
trend_fig.update_layout(
plot_bgcolor = "rgba(0,0,0,0)",
paper_bgcolor = "rgba(0,0,0,0)",
font = dict(color = "rgba(0,0,0,0.8)"),
xaxis = dict(title="", showgrid = True, gridcolor = "rgba(128,128,128,0.2)", tickformat="%b %d, %Y"),
yaxis = dict(title="", showgrid =True, gridcolor ="rgba(128,128,128,0.2)"),
margin=dict(l=0, r=0, t=40, b=0),
)
st.plotly_chart(trend_fig, use_container_width=True)
st.markdown("----")
# further analysis and KPI's, visualization  
top_cat = filtered_df.groupby('Category')['Net Amount'].sum().reset_index()
top_cat = top_cat.sort_values(by='Net Amount', ascending=False)
top_cat_5 = top_cat.head(10)
st.markdown("### Top Categories by Revenue ")
col_a, col_b = st.columns([2,4])
with col_a:
    st.dataframe(top_cat_5, use_container_width=True, hide_index=True)
with col_b:
    # creat the plotly horizontal bar chart
    fig = px.bar(top_cat, x= 'Net Amount', y='Category', orientation='h', title="<b>Revenue Distribution by Category</b>", text_auto=".2s", color='Net Amount', color_continuous_scale="teal")
    # customize layout to adap dynamically
    fig.update_layout(
        plot_bgcolor = "rgba(0,0,0,0)",
        paper_bgcolor = "rgba(0,0,0,0)",
        font = dict(color = "rgba(0,0,0,0.8)"),
        xaxis = dict(title = "Net Revenue (Rs)", showgrid = True, gridcolor = "rgba(128,128,128,0.2)"),
        yaxis = dict(title = "", showgrid = False),
        margin = dict(l=0, r=0, t=40, b=0),
        coloraxis_showscale = False
        )
    st.plotly_chart(fig, use_container_width=True)
st.markdown("----")

# top cities by revenue
top_city = filtered_df.groupby('City')['Net Amount'].sum().reset_index()
top_city = top_city.sort_values(by='Net Amount', ascending=False)
top_city_5 = top_city.head(4)
st.markdown("### Top Cities by Revenue ")
col_a1, col_b1 = st.columns([2,4])
with col_a1:
    st.dataframe(top_city_5, use_container_width=True, hide_index=True)
with col_b1:
    fig_pi = px.pie(top_city_5, names='City', values='Net Amount', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_pi, use_container_width=True)
st.markdown("----")
with st.expander("Summary Report"):
    st.markdown(
    """
#### **Category performance and Demand Drivers:**
Core Revenue Anchors: Grocery (leading at ~17k Rs) and Personal Care (~14k Rs) are the primary revenue engines, capturing the highest consumer spend.
Mid-Tier Demand: Categories like Snacks (~10k Rs), Beverages (~8.8k Rs), and Household (~7.9k Rs) maintain steady, consistent transaction volumes.
Underperforming Segments: Bakery, Sweets, and Health Drinks (~1.9k Rs) show minimal revenue contribution, indicating low baseline demand or constrained product visibility in these categories.

#### **Geographic Distribution & Market Share:**
Primary Hub: Lahore anchors the platform's regional performance, commanding the largest share at 33.9%.
Balanced Secondary Markets: Gujranwala (23.2%), Narowal (22.5%), and Ghaziabad (20.4%) form a remarkably well-balanced secondary footprint, each contributing roughly one-fifth of overall revenue.
#### **Recommendation:**
- Prioritize stock availability and supply chain reliability for Grocery and Personal Care to prevent stockouts during peak ordering hours.
- Leverage the high traffic of Grocery and Snacks by introducing bundle deals or checkout recommendations for lagging segments like Bakery and Health Drinks to lift average order value (AOV).
- While Lahore leads, secondary markets like Gujranwala and Narowal hold substantial combined weight (~45.7%). Implement targeted local promotions and localized delivery speed incentives in these high-potential cities to challenge Lahore's dominance.
"""
)
st.markdown("----")
