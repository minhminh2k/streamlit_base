import fitz
import yaml
import base64
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
import tempfile
from streamlit_pdf_viewer import pdf_viewer
import streamlit.components.v1 as components


st.set_page_config(
    page_title="AIONA",
    page_icon="📊",
    layout="wide"
)

### Page title
st.sidebar.title('AIONA Front-end')


@st.cache_data
def load_xlsx(file_path):
    return pd.read_excel(file_path)


# Function to create a single-page PDF
def create_single_page_pdf(pdf_path, page_number):
    with fitz.open(pdf_path) as doc:  # Đảm bảo đóng file PDF
        if page_number < doc.page_count:
            # Tạo PDF mới chỉ chứa 1 trang
            new_pdf = fitz.open()
            new_pdf.insert_pdf(doc, from_page=page_number, to_page=page_number)
            
            # Tạo file tạm và lưu PDF
            temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            temp_pdf_path = temp_pdf.name
            temp_pdf.close()  # Đóng file tạm để tránh lỗi
            new_pdf.save(temp_pdf_path)
            new_pdf.close()

            return temp_pdf_path  # Trả về đường dẫn file mới tạo

    return None  # Trả về None nếu trang không hợp lệ

# Load configuration
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Create an authentication object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# Login widget
name, authentication_status, username = authenticator.login('Login', 'main')

# Main app logic based on authentication status
if authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
else:
    authenticator.logout('Logout', 'sidebar')
    # Custom CSS
    st.markdown("""
    <style>
        div[data-testid="stSidebar"] h1 {
            text-align: center !important;
            width: 100% !important;
            font-weight: bold;
        }
                
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        div.stButton > button {
            display: flex;
            align-items: center;
            width: 100%;
            text-align: left;
            padding: 10px;
            background-color: transparent;
            color: #444;
            border: none;
            font-size: 16px;
        }
        div.stButton > button:hover {
            background-color: #f0f0f0;
            color: #0068c9;
        }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'screen' not in st.session_state:
        st.session_state.screen = 'home'

    # Sidebar navigation
    with st.sidebar:        
        if st.button("☀️ AIONA"):
            st.session_state.screen = 'app'
            st.rerun()

        if st.button("📁 Upload File"):
            st.session_state.screen = 'upload'
            st.rerun()
            
        if st.button("📝 Design Documents"):
            st.session_state.screen = 'design'
            st.rerun()
            
        if st.button("🚨 Incident Report"):
            st.session_state.screen = 'incident'
            st.rerun()


    # Main content
    if st.session_state.screen == 'home':
        st.title("Welcome to the App")
        st.write("Select an option from the sidebar to get started.")

    elif st.session_state.screen == 'app':
        st.title('AIONA')
        
    elif st.session_state.screen == 'upload':

        st.title("📁 Upload File")
        uploaded_files = st.file_uploader("Upload a PDF file", type=["pdf"], accept_multiple_files=True)
        if uploaded_files is not None:
            for uploaded_file in uploaded_files:
                st.write("File preview:")
                pdf_data = uploaded_file.read()
                pdf_viewer(pdf_data, width=700, height=1000)
                pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="700" height="500" type="application/pdf"></iframe>'
                # st.markdown(pdf_display, unsafe_allow_html=True)
            
    elif st.session_state.screen == 'design' or st.session_state.screen == 'incident':
        st.title('Search')
        search_term = st.text_input('Search:', '')

        if search_term.strip():
            xlsx_path = 'assets/excel.xlsx'
            data = load_xlsx(xlsx_path)

            # Convert all columns to string type for searching
            data_searchable = data.astype(str)
            mask = data_searchable.apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
            data = data[mask]

            if 'page_size' not in st.session_state:
                st.session_state.page_size = 5
            if 'page' not in st.session_state:
                st.session_state.page = 1

            columns = data.columns.tolist()
            selected_column = st.selectbox("Select a column to filter", columns)

            unique_values = data[selected_column].dropna().unique().tolist()
            
            # Let user select multiple unique values to filter
            selected_values = st.multiselect(f"Filter based on {selected_column}", unique_values, default=[])

            # Apply filter if user selects values
            if selected_values:
                data = data[data[selected_column].isin(selected_values)]

            top_menu = st.columns(3)
            with top_menu[0]:
                sort = st.radio("Sort Data", options=["Yes", "No"], horizontal=1, index=1)
            if sort == "Yes":
                with top_menu[1]:
                    sort_field = st.selectbox("Sort By", options=data.columns)
                with top_menu[2]:
                    sort_direction = st.radio(
                        "Direction", options=["⬆️", "⬇️"], horizontal=True
                    )
                data = data.sort_values(
                    by=sort_field, ascending=sort_direction == "⬆️", ignore_index=True
                )
            bottom_menu = st.columns((4, 1, 1))
            with bottom_menu[2]:
                page_size = st.selectbox("Page Size", options=[5, 10, 25, 50], key="page_size_selectbox")
                st.session_state.page_size = page_size
            with bottom_menu[1]:
                total_pages = max(1, (len(data) + st.session_state.page_size - 1) // st.session_state.page_size, )
                page = st.number_input("Page", min_value=1, max_value=total_pages, step=1, key="page_number_input")
                st.session_state.page = page                
            with bottom_menu[0]:
                st.markdown(f"Page **{st.session_state.page}** of **{total_pages}** ")
            
            if st.session_state.page_size != page_size or st.session_state.page != page:
                st.session_state.page_size = page_size
                st.session_state.page = page
            
            pagination = st.container()

            total_pages = (len(data) + st.session_state.page_size - 1) // st.session_state.page_size

            # Display data by page
            start = (st.session_state.get('page', 1) - 1) * st.session_state.page_size
            end = start + st.session_state.page_size
            display_data = data.iloc[start:end]

            # Header
            header_cols = st.columns([10] + [15] * 3 + [30] * (len(display_data.columns) - 3) + [15])
            with header_cols[0]:
                st.write("**INDEX**")
            for i, column in enumerate(display_data.columns):
                with header_cols[i + 1]:
                    st.write(f"**{column.upper()}**")
            with header_cols[len(display_data.columns) + 1]:
                st.write("**PREVIEW**")
            st.markdown("---")

            # Display table data with preview button
            for idx, row in display_data.iterrows():
                cols = st.columns([10] + [15] * 3 + [30] * (len(row) - 3 ) + [15])
                with cols[0]:
                    st.write(f"{idx + 1}")
                for i, column in enumerate(row.index):
                    with cols[i + 1]:
                        st.write(f"{row[column]}")
                
                with cols[len(row) + 1]:
                    if st.button("Preview PDF", key=f"preview_{idx}"):
                        print(st.session_state.screen)
                        file_path = 'assets/test.pdf'  # Update this with your path
                        if file_path.endswith('.pdf'):
                            page_number = 0  # Change the page number as needed
                            single_page_pdf_path = create_single_page_pdf(file_path, page_number)
                            if single_page_pdf_path:
                                with open(single_page_pdf_path, "rb") as pdf_file:
                                    pdf_data = pdf_file.read()
                                    pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
                                    # pdf_viewer(pdf_data, width=700, height=1000) #, rendering="legacy_iframe")
                                    # components.iframe(f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="700" height="1000" type="application/pdf"></iframe>', height=1000)
                                    st.markdown(f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="700" height="1000" type="application/pdf"></iframe>', unsafe_allow_html=True)
                            else:
                                st.text("Invalid page number.")
                        else:
                            st.text("This file is not a PDF.")
                st.markdown("---")
            
            st.write(f'Found {len(data)} results')
