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
            country_options = ['Select All'] + merged_df["Country"].unique().tolist()
            country = st.sidebar.multiselect("Select the country:", options=country_options, default=[], key="country_dropdown")
            if "Select All" in country:
                country = merged_df["Country"].unique().tolist()  # Select all countries
            
            network_options = ['Select All'] + merged_df["Network"].unique().tolist()
            network = st.sidebar.multiselect("Select the network:", options=network_options, default=[], key="network_dropdown")
            if "Select All" in network:
                network = merged_df["Network"].unique().tolist()  # Select all networks
            # st.sidebar.header("Please filter here:")
            # country = st.sidebar.multiselect("Select the country:", options=merged_df["Country"].unique(), default=[], key="country_dropdown")
            # #country = st.sidebar.multiselect("Select the country:", options=merged_df["Country"].unique(), default=merged_df["Country"].unique())
            # network = st.sidebar.multiselect("Select the network:", options=merged_df["Network"].unique(), default=merged_df["Network"].unique())

            # Filter the data
            filtered_df = merged_df[(merged_df["Country"].isin(country)) & (merged_df["Network"].isin(network))]
            filtered_df = filtered_df.sort_values(by='Price in USD')

            # Remove duplicate rows from the filtered data
            filtered_df.drop_duplicates(inplace=True)

            if not filtered_df.empty:
                # Calculate minimum price in USD from merged data
                min_price = filtered_df['Price in USD'].min()
                
                # Display minimum price
                st.write("Minimum Price (USD):", min_price)


                # Display the minimum price rows with specified column styles
                min_row = filtered_df.loc[filtered_df['Price in USD'] == min_price, ["Country", "Network", "Price in USD", "Service Provider"]]
                min_rows_styled = min_row.style.apply(lambda x: ['background-color: black; color: white'] * len(x), axis=0)
                st.header("Minimum price in USD by Country amoung filtered data")
                st.dataframe(min_rows_styled)

                max_row = filtered_df.loc[filtered_df['Price in USD'] == min_price, ["Country", "Network", "Price in USD", "Service Provider"]]
                max_rows_styled = max_row.style.apply(lambda x: ['background-color: black; color: white'] * len(x), axis=0)
                st.header("Maximum price in USD by Country amoung filtered data")
                st.dataframe(max_rows_styled)
            
                
            # Get the rows with the minimum price for each country
            min_default = merged_df.loc[merged_df.groupby('Country')['Price in USD'].idxmin()]
            min_default = min_default.sort_values(by='Price in USD')

            min_default_styled = min_default.style.apply(lambda x: ['background-color: black; color: white'] * len(x), axis=0)
            st.header("Minimum price in USD in all Countries")
            st.dataframe(min_default_styled)

            max_default = merged_df.loc[merged_df.groupby('Country')['Price in USD'].idxmax()]
            max_default = max_default.sort_values(by='Price in USD')

            max_default_styled = min_default.style.apply(lambda x: ['background-color: black; color: white'] * len(x), axis=0)
            st.header("Maximum price in USD in all Countries")
            st.dataframe(max_default_styled)

            # Download filtered data as Excel
            output_file = io.BytesIO()
            min_default.to_excel(output_file, index=False, header=True)
            output_file.seek(0)
            b64 = base64.b64encode(output_file.read()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="min_data.xlsx">Download min_Data</a>'
            st.markdown(href, unsafe_allow_html=True)

            st.success("Data is ready for download.")

            # Display the filtered data table
            st.header("Filtered Data")
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

