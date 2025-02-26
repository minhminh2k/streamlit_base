import streamlit as st

# Retrieve the selected ID from session state
selected_id = st.session_state.get('selected_id', 1)

# Display details for the selected item
st.write(f"## Detail Page for Item {selected_id}")
st.write(f"**ID:** {selected_id}")
st.write(f"**Description:** This is the description for Item {selected_id}.")

# Add a button to go back to the main page
if st.button("Back to Main Page"):
    st.switch_page("test.py")