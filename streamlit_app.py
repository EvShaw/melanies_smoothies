import streamlit as st
from snowflake.connector import connect
import pandas as pd

# Write directly to the app
st.title("Example Streamlit App :balloon:")
st.write(
    """
    Choose your Fruits!
    """
)

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be: ", name_on_order)

# Retrieve Snowflake connection details from Streamlit secrets
snowflake_secrets = st.secrets["snowflake"]

# Establish a connection to Snowflake
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

# Query data from Snowflake
query = "SELECT FRUIT_NAME FROM smoothies.public.fruit_options"
fruit_options_df = pd.read_sql(query, conn)

# Display the available fruit options
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_options_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)

    # Prepare the SQL insert statement
    insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, name_on_order)
    VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Button to submit the order
    if st.button('Submit Order'):
        conn.cursor().execute(insert_stmt)
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")

# Close the connection
conn.close()