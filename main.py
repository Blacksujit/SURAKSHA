import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from wordcloud import WordCloud
from utils.db import setup_db, get_search_trends, get_common_terms, save_document, get_document_types, save_query, get_user_history, get_document_count, get_most_searched_queries, save_search
from utils.document_parser import parse_document
import sqlite3

# Initialize the database
setup_db()

def main():
    st.title("🔏Suraksha🔏-- 🛅Secure Document Query Application🛅")
    st.sidebar.title("Options")

    # Sidebar navigation
    sidebar_option = st.sidebar.radio("Select Page", ["Upload Document", "Search", "Dashboard"])

    user_id = st.sidebar.text_input("Enter your user ID:", value="default_user")

    if sidebar_option == "Upload Document":
        upload_document(user_id)
    elif sidebar_option == "Search":
        perform_search_query(user_id)
    elif sidebar_option == "Dashboard":
        if user_id:
            display_dashboard(user_id)
        else:
            st.warning("Please enter your user ID to access the dashboard.")

def upload_document(user_id):
    uploaded_file = st.sidebar.file_uploader("Upload Document", type=["pdf", "docx", "txt"])

    if uploaded_file:
        doc_text = parse_document(uploaded_file)
        save_document(user_id, uploaded_file.name, doc_text)  # Save as plain text
        st.success("Document uploaded and saved securely.")

def perform_search_query(user_id):
    uploaded_file = st.sidebar.file_uploader("Upload Document", type=["pdf", "docx", "txt"], key='search')
    user_query = st.text_input("Enter your query:")

    if st.button("Search"):
        if uploaded_file:
            doc_text = parse_document(uploaded_file)
            results = perform_search(user_query, doc_text)
            st.write(results)
            save_query(user_id, user_query, results)  # Save query and result
            save_search(user_id, user_query)  # Save search for trends
        else:
            st.warning("Please upload a document before performing a search.")

    if st.sidebar.button("Download Chat History"):
        history = get_user_history(user_id)
        if history:
            st.sidebar.download_button("Download", data=history, file_name="chat_history.txt")
        else:
            st.sidebar.warning("No chat history found for the user.")

def display_dashboard(user_id):
    st.header("Dashboard")

    show_doc_count = st.sidebar.checkbox("Show Document Count", value=True)
    show_queries = st.sidebar.checkbox("Show Most Searched Queries", value=True)
    show_doc_types = st.sidebar.checkbox("Show Document Type Distribution", value=True)
    show_search_trends = st.sidebar.checkbox("Show Search Trends", value=True)
    show_wordcloud = st.sidebar.checkbox("Show Word Cloud", value=True)

    if show_doc_count:
        doc_count = get_user_document_count(user_id)
        st.subheader("Number of Documents Uploaded")
        st.write(doc_count)

    if show_queries:
        st.subheader("Most Searched Queries")
        queries = get_user_most_searched_queries(user_id)
        if queries:
            query_text = [f"{query[0]}: {query[1]}" for query in queries]
            query_counts = [query[1] for query in queries]

            fig, ax = plt.subplots()
            ax.bar(query_text, query_counts, color='skyblue')
            ax.set_xlabel("Queries")
            ax.set_ylabel("Count")
            ax.set_title("Most Searched Queries")
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig)
        else:
            st.write("No search queries found for this user.")

    if show_doc_types:
        st.subheader("Document Type Distribution")
        doc_types = get_document_types(user_id)
        if doc_types:
            types, counts = zip(*doc_types)
            fig, ax = plt.subplots()
            ax.pie(counts, labels=types, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"))
            ax.set_title("Document Types")
            st.pyplot(fig)
        else:
            st.write("No document type data available.")

    if show_search_trends:
        st.subheader("Search Trends Over Time")
        search_trends = get_search_trends(user_id)
        if search_trends:
            dates, counts = zip(*search_trends)
            df = pd.DataFrame({"Date": dates, "Search Count": counts})
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            df_resampled = df.resample('M').sum()
            fig, ax = plt.subplots()
            ax.plot(df_resampled.index, df_resampled['Search Count'], marker='o', linestyle='-', color='b')
            ax.set_xlabel("Date")
            ax.set_ylabel("Search Count")
            ax.set_title("Search Trends Over Time")
            st.pyplot(fig)
        else:
            st.write("No search trends data available.")

    if show_wordcloud:
        st.subheader("Word Cloud of Common Terms")
        common_terms = get_common_terms(user_id)
        if common_terms:
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(common_terms))
            fig, ax = plt.subplots()
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.write("No common terms data available.")

def perform_search(query, doc_text):
    """Simple keyword-based search. Can be replaced with more advanced methods."""
    if query.lower() in doc_text.lower():
        return f"Found: {query}"
    else:
        return "No results found"

def get_user_document_count(user_id):
    """Returns the number of documents uploaded by the user."""
    conn = sqlite3.connect('secure_db.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM documents WHERE user_id = ?', (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_user_most_searched_queries(user_id):
    """Returns the most searched queries for the user."""
    conn = sqlite3.connect('secure_db.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT query, COUNT(*) as count FROM queries WHERE user_id = ? GROUP BY query ORDER BY count DESC', (user_id,))
    queries = cursor.fetchall()
    conn.close()
    return queries

if __name__ == "__main__":
    main()
