import streamlit as st
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import PyPDF2
from docx import Document
import base64
from io import BytesIO

# --- Custom CSS for a Professional Look ---
st.markdown(
    """
    <style>
        .css-1d391kg {background-color: #F8F9FA;} /* Light background for a sleek look */
        .css-18e3th9 {padding-top: 0rem;} /* Adjust padding */
        .css-1avcm0n {font-size: 1.5rem; color: #333333;} /* Font customization for title */
        .css-184tjsw {color: #6c757d;} /* Sidebar text color */
        .stButton > button {background-color: #007bff; color: white; border: none; border-radius: 8px;}
        .stButton > button:hover {background-color: #0056b3;}
        .stSelectbox > div > div:first-child {color: #343a40;}
        h1, h2, h3 {color: #007bff;}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Title and Description ---
st.title("✨ Professional Word Cloud Generator")
st.write("Upload a **text file**, **PDF**, or **Word document** to create a visually engaging word cloud. Customize colors, shapes, and more!")

# --- Sidebar for Word Cloud Customization ---
st.sidebar.title("⚙️ Customize Word Cloud")
uploaded_file = st.sidebar.file_uploader("Choose a file", type=["txt", "pdf", "docx"])

# File Reading Functions
def read_txt(file):
    return file.getvalue().decode("utf-8")

def read_docx(file):
    doc = Document(file)
    return " ".join([para.text for para in doc.paragraphs])

def read_pdf(file):
    pdf = PyPDF2.PdfReader(file)
    return " ".join([page.extract_text() for page in pdf.pages])

# Function to filter out stopwords
def filter_stopwords(text, additional_stopwords=[]):
    words = text.split()
    all_stopwords = STOPWORDS.union(set(additional_stopwords))
    filtered_words = [word for word in words if word.lower() not in all_stopwords]
    return " ".join(filtered_words)

# Function to create a download link for the word cloud image
def get_image_download_link(buffered, format_):
    image_base64 = base64.b64encode(buffered.getvalue()).decode()
    return f'<a href="data:image/{format_};base64,{image_base64}" download="wordcloud.{format_}">Download Word Cloud as {format_}</a>'

# Process Uploaded File
if uploaded_file:
    # Read File Content Based on Type
    if uploaded_file.type == "text/plain":
        text = read_txt(uploaded_file)
    elif uploaded_file.type == "application/pdf":
        text = read_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = read_docx(uploaded_file)
    else:
        st.error("Unsupported file type. Please upload a txt, pdf, or docx file.")
        st.stop()

    # Display File Information
    st.write("### File Information")
    st.info(f"**File Name:** {uploaded_file.name}\n\n**File Size:** {uploaded_file.size} bytes")

    # Filter Stopwords
    st.write("### Step 1: Filter Stopwords")
    use_standard_stopwords = st.sidebar.checkbox("Use standard stopwords?", True)
    additional_stopwords = st.sidebar.text_area("Additional stopwords (comma separated)", "")
    additional_stopwords = set(additional_stopwords.split(","))

    if use_standard_stopwords:
        all_stopwords = STOPWORDS.union(additional_stopwords)
    else:
        all_stopwords = additional_stopwords

    text = filter_stopwords(text, all_stopwords)

    # Word Cloud Settings
    st.sidebar.markdown("---")
    st.sidebar.write("**Word Cloud Settings**")
    width = st.sidebar.slider("Width", 400, 2000, 800, 50)
    height = st.sidebar.slider("Height", 200, 2000, 600, 50)
    background_color = st.sidebar.color_picker("Background Color", "#FFFFFF")
    contour_color = st.sidebar.color_picker("Contour Color", "#007bff")
    max_words = st.sidebar.slider("Max Words", 50, 500, 200)

    # Generate Word Cloud
    wordcloud = WordCloud(
        width=width, height=height, background_color=background_color, contour_color=contour_color,
        max_words=max_words, contour_width=1
    ).generate(text)

    # Display Word Cloud
    st.write("### Generated Word Cloud")
    fig, ax = plt.subplots(figsize=(width / 100, height / 100))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

    # Save and Download Word Cloud
    format_ = st.sidebar.selectbox("Download Format", ["png", "jpeg", "svg", "pdf"])
    if st.sidebar.button("Save and Download Word Cloud"):
        buffered = BytesIO()
        plt.savefig(buffered, format=format_)
        st.sidebar.markdown(get_image_download_link(buffered, format_), unsafe_allow_html=True)

    # Display Word Frequency Table
    st.write("### Word Frequency Table")
    words = text.split()
    word_count = pd.DataFrame({"Word": words}).groupby("Word").size().reset_index(name="Count").sort_values("Count", ascending=False)
    st.write(word_count.head(20))  # Show top 20 words

    # Download Word Frequency Table
    csv = word_count.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    st.sidebar.markdown(
        f'<a href="data:file/csv;base64,{b64}" download="word_frequencies.csv">Download Word Frequency Table as CSV</a>',
        unsafe_allow_html=True
    )

# Sidebar Information and Branding
st.sidebar.markdown("---")
st.sidebar.title("💡 About Us")
st.sidebar.write("This app is created by the [Data Science Pro Team](https://github.com/DataSciencePro).")
st.sidebar.write("Get in touch at [Email](mailto:contact@datasciencepro.com)")
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    [![Connect on LinkedIn](https://img.shields.io/badge/Connect%20on-LinkedIn-blue?logo=linkedin)](https://www.linkedin.com/in/furqan-khan-256798268/)
    """
)
st.sidebar.write("Subscribe for more!")
