import pandas as pd
import plotly.express as px
import streamlit as st

# 1. Load Data
@st.cache_data
def load_data():
  return pd.read_csv("amazon-python.csv")  # Use your exact CSV file name

df = load_data()
# 2. Add spaces around the ampersand in the Category column
df['Category'] = df['Category'].str.replace("&"," & ",regex=False)

# 3. Filter out the junk brand before generating the dashboard
df = df[df["Brand"]!="Unlisted/Junk"]

# 4. Page Config
st.set_page_config(page_title="Amazon Analytics Dashboard", layout="wide")





# 5. Sidebar Filters
st.sidebar.header("Filter Options")
# Category Filter
selected_categories = st.sidebar.multiselect(
"Select Category:",
options=df["Category"].dropna().unique(),
default=df["Category"].dropna().unique()[:3]
)
# Rating Filter Slider
min_rating = st.sidebar.slider(
"Minimum Rating:",min_value=0.0,max_value=5.0,value=0.0,step=0.5
)
# Apply both filters together
df_filtered = df[
(df["Category"].isin(selected_categories))&(df["Rating"] >= min_rating)
]
# 6. Header & Top Metric Cards
st.title("📦 Amazon Product & Pricing Intelligence")

col1, col2, col3, col4 = st.columns(4)

with col1:
  st.metric("Total Products", f"{len(df_filtered):,}")

with col2:
  st.metric(
      "Avg Discounted Price", f"₹{df_filtered['Discounted Price'].mean():,.2f}"
  )

with col3:
  st.metric("Avg Rating", f"{df_filtered['Rating'].mean():.2f} ⭐")

with col4:
  # Handles percentage correctly whether raw value is 0.51 or 51.9
  avg_discount = df_filtered["Discount Percentage"].mean()
  if avg_discount < 1:
    avg_discount_str = f"{avg_discount * 100:.1f}%"
  else:
    avg_discount_str = f"{avg_discount:.1f}%"
  st.metric("Avg Discount", avg_discount_str)

st.divider()

# 7. Visualizations
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
  st.subheader("Price vs. Rating Correlation")
  fig_scatter = px.scatter(
      df_filtered,
      x="Discounted Price",
      y="Rating",
      color="Category",
      size="Rating Count",
      hover_data=["Product Name"],
      trendline="ols",
  )
  st.plotly_chart(fig_scatter, use_container_width=True)

with chart_col2:
  st.subheader("Top 10 Brands by Product Count")
  top_brands = df_filtered["Brand"].value_counts().head(10).reset_index()
  top_brands.columns = ["Brand", "Count"]
  fig_bar = px.bar(
      top_brands,
      x="Count",
      y="Brand",
      orientation="h",
      color="Count",
      color_continuous_scale="Viridis",
  )
  fig_bar.update_layout(yaxis={"categoryorder": "total ascending"})
  st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# 8. Data Preview at the Bottom
st.subheader("Filtered Data Preview")
st.dataframe(df_filtered.head(10))

# Convert filtered dataframe to CSV

csv_data = df_filtered.to_csv(index=False).encode("utf-8")

st.download_button(
label="📥 Download Filtered Data (CSV)",
data = csv_data,
file_name = "filtered_amazon_products.csv",
mime = "text/csv"
)