import streamlit as st
from rag_pipeline import answer_query
import os

"""
app.py

Streamlit front-end interface for querying the ISRO RAG assistant.
This UI takes user input, sends it to the RAG pipeline, and displays the results.
"""

# Disable Streamlit's file watcher to prevent unwanted reloads
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"

def main():
    """
    Main function to launch the Streamlit app.
    Sets up page layout, handles user input, calls the RAG pipeline, and displays results.
    """
    st.set_page_config(page_title="🚀 ISRO RAG Assistant", layout="centered")
    st.title("📡 ISRO Annual Report 2025 – RAG Assistant")
    st.markdown("Ask any question based on the ISRO 2025 Annual Report (Text, Table, Images).")

    # User query input
    query = st.text_input("🔍 Enter your query", placeholder="e.g., What are ISRO’s future launch plans?")

    # Button to process query
    if st.button("Get Answer") and query.strip():
        with st.spinner("🤖 Thinking..."):
            try:
                result = answer_query(query)

                # Display results
                st.success("✅ Query processed")
                st.markdown("### 📤 Answer:")
                st.write(result)

            except Exception as e:
                st.error(f"❌ Error occurred while processing: {e}")
    else:
        st.info("💡 Enter a query to begin.")

if __name__ == "__main__":
    main()
