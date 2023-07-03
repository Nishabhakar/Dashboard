import base64
import pandas as pd
import streamlit as st
import io

st.set_page_config(page_title="Data", page_icon=":bar_chart:", layout="wide")

def process_uploaded_file(uploaded_file):
    if uploaded_file.type == 'text/csv':
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        df = pd.read_excel(uploaded_file, engine='openpyxl')
    else:
        return None
    
    return df

# Upload CSV and Excel sheets to the app and create the tables
def upload_data():
    uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True)

    if uploaded_files:
        merged_df = pd.DataFrame()  # Initialize an empty DataFrame for merging
        
        for uploaded_file in uploaded_files:
            df = process_uploaded_file(uploaded_file)
            
            if df is not None:
                merged_df = pd.concat([merged_df, df], ignore_index=True)
        
        if not merged_df.empty:
            # Remove duplicates from the merged DataFrame
            merged_df.drop_duplicates(inplace=True)
            
            # Apply filtering
            st.sidebar.header("Please filter here:")
            country = st.sidebar.multiselect("Select the country:", options=merged_df["Country"].unique(), default=[], key="country_dropdown")
            network = st.sidebar.multiselect("Select the network:", options=merged_df["Network"].unique(), default=merged_df["Network"].unique())
            
            # Filter the data
            filtered_df = merged_df[(merged_df["Country"].isin(country)) & (merged_df["Network"].isin(network))]
            
            # Remove duplicate rows from the filtered data
            filtered_df.drop_duplicates(inplace=True)

            if not filtered_df.empty:
                # Calculate minimum price in USD from merged data
                min_price = filtered_df['Price in USD'].min()
                
                # Display minimum price
                st.write("Minimum Price (USD):", min_price)

                # Display the minimum price row with specified column styles
                min_row = filtered_df.loc[filtered_df['Price in USD'] == min_price, ["Country", "Network", "Price in USD", "Service Provider"]]
                min_row = min_row.drop_duplicates()  # Remove duplicate rows
                min_row_styled = min_row.style.apply(lambda x: ['background-color: black; color: white'] * len(x), axis=0)
                st.header("Minimum price in USD")
                st.dataframe(min_row_styled)
                
                # Display the filtered data table
                st.write('<style> th {background-color: black; color: white;} </style>', unsafe_allow_html=True)
                st.dataframe(filtered_df)
            
                # Download filtered data as Excel
                output_file = io.BytesIO()
                filtered_df.to_excel(output_file, index=False, header=True)
                output_file.seek(0)
                b64 = base64.b64encode(output_file.read()).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="filtered_data.xlsx">Download Filtered Data</a>'
                st.markdown(href, unsafe_allow_html=True)
                
                st.success("Filtered data is ready for download.")
            else:
                st.warning("No data found after filtering.")

# Run the application
if __name__ == '__main__':
    st.title("Dashboard of Multiple Excel Sheets")
    upload_data()
