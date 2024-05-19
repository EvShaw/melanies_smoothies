import streamlit as st
from snowflake.connector import connect
import pandas as pd
import requests
import json

st.title("Example Streamlit App :balloon:")
st.write(
    """
    Choose your Fruits!
    """
)

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be: ", name_on_order)

snowflake_secrets = st.secrets["snowflake"]

conn = connect(
    user=snowflake_secrets["user"],
    password=snowflake_secrets["password"],
    account=snowflake_secrets["account"],
    role=snowflake_secrets["role"],
    warehouse=snowflake_secrets["warehouse"],
    database=snowflake_secrets["database"],
    schema=snowflake_secrets["schema"],
    client_session_keep_alive=snowflake_secrets["client_session_keep_alive"]
)

query = "SELECT FRUIT_NAME FROM smoothies.public.fruit_options"
fruit_options_df = pd.read_sql(query, conn)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_options_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    # ingredients_string = ''
    ingredients_string = ', '.join(ingredients_list)

    insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, name_on_order)
    VALUES ('{ingredients_string}', '{name_on_order}')
    """

    for fruit_chosen in ingredients_list:
        ingredients_string = fruit_chosen + ' '
        st.subheader(fruit_chosen + ' Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + {fruit_chosen})

        if fruityvice_response.status_code == 200:
            response_json = fruityvice_response.json()
            
            # Normalize the JSON data (flattening nested structures if necessary)
            fv_df = pd.json_normalize(response_json)
            
            # Display the DataFrame using Streamlit
            st.dataframe(fv_df, use_container_width=True)
            
        else:
            st.error(f"Error fetching data: {fruityvice_response.status_code}")
        
    
    if st.button('Submit Order'):
        conn.cursor().execute(insert_stmt)
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")


conn.close()


