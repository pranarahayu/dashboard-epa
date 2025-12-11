import streamlit as st
import pandas as pd
from datetime import date, timedelta

def run():
    st.set_page_config(
        page_title="Home Page",
    )

    st.write("# Selamat datang di Dashboard Internal TSG!")

    st.markdown(
        """
        Placeholder.
    """
    )

if __name__ == "__main__":
    run()

from menu import menu
menu()
