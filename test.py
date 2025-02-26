import streamlit as st
import pandas as pd

# Sample data
data = pd.DataFrame({
    'ID': [1, 2, 3],
    'Name': ['Item 1', 'Item 2', 'Item 3'],
    'Description': ['Description 1', 'Description 2', 'Description 3']
})

# Initialize session state to track the active tab
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 'Main'

# Function to render the main page
def render_main_page():
    st.write("## Main Page")
    
    # Display the table with buttons
    for _, row in data.iterrows():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**{row['Name']}** - {row['Description']}")
        with col2:
            if st.button(f"View {row['ID']}", key=f"btn_{row['ID']}"):
                # Set the active tab to the corresponding detail tab
                st.session_state.active_tab = f"Detail {row['ID']}"
                st.rerun()  # Force a rerun to update the UI

# Function to render a detail page
def render_detail_page(item_id):
    item = data[data['ID'] == item_id].iloc[0]
    st.write(f"## Detail Page for {item['Name']}")
    st.write(f"**ID:** {item['ID']}")
    st.write(f"**Description:** {item['Description']}")
    
    if st.button("Back to Main Page"):
        # Set the active tab back to the main page
        st.session_state.active_tab = 'Main'
        st.rerun()  # Force a rerun to update the UI

# Render content based on the active tab
if st.session_state.active_tab == 'Main':
    render_main_page()
else:
    # Extract the item ID from the active tab name
    item_id = int(st.session_state.active_tab.split()[-1])
    render_detail_page(item_id)
    
