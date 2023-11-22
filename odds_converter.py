#### Odds Converter Streamlit App

import streamlit as st
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fractions import Fraction
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.badges import badge
import altair as alt
#from st_aggrid import JsCode, AgGrid, GridOptionsBuilder



# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Odds Converter", page_icon=":game_die:")

# Display BTP logo image
logo_path_or_url = '/Users/Stephan/Desktop/R Projects/personal-website/BTP (3).png'
#st.image(logo_path_or_url, width=100)  # Adjust width as needed

# Create a two-column layout
col1, col2 = st.columns([1, 5])

# Display the logo in the first column
col1.image(logo_path_or_url, width=100)  # Adjust the width to fit your logo

# Set the title in the second column
col2.title(":game_die: Odds Converter Tool")


# ---- MAINPAGE ----
#st.title(":game_die: Odds Converter Tool")
st.markdown(""" 
This app allows you to quickly reference sports betting odds and their implied probabilities using various international systems. A **Between The Pipes** app by [Stephan Teodosescu](https://stephanteodosescu.com/).
""")

"---"

# GitHub badge
def example_github():
    badge(type="github", name="steodose/odds-converter")

# twitter badge
def example_twitter():
    badge(type="twitter", name="steodosescu")

# define functions for odds calcs
def moneyline_to_implied_probability(moneyline):
    """
    Convert American moneyline odds to implied probability.
    """
    if moneyline > 0:
        probability = 100 / (moneyline + 100)
    else:
        probability = -moneyline / (-moneyline + 100)
    return round(probability * 100, 1)  # Returns percentage to one decimal place

def moneyline_to_decimal_odds(moneyline):
    """
    Convert American moneyline odds to decimal odds.
    """
    if moneyline > 0:
        decimal_odds = moneyline / 100 + 1
    else:
        decimal_odds = 100 / -moneyline + 1
    return round(decimal_odds, 2)

def moneyline_to_fractional_odds(moneyline):
    """
    Convert American moneyline odds to simplified fractional odds.
    """
    if moneyline > 0:
        fraction = Fraction(moneyline, 100).limit_denominator()
    else:
        fraction = Fraction(100, -moneyline).limit_denominator()
    return f"{fraction.numerator}/{fraction.denominator}"



# ---- Sidebar ----

# Moneyline odds selection
st.sidebar.header('Selector')
moneyline = st.sidebar.number_input('Enter American Moneyline Odds', value=-110)

st.sidebar.write("""
                 Based on your selection you can see the chances of a team winning the game expressed in
                 fractional odds, decimal odds, and the implied probability on the right. 
                 """)

implied_probability = moneyline_to_implied_probability(moneyline)
fractional_odds = moneyline_to_fractional_odds(moneyline)
decimal_odds = moneyline_to_decimal_odds(moneyline)


# ---- KPIs Section ----

col1, col2, col3 = st.columns(3)
col1.metric(label="Implied Probability", value=f"{implied_probability}%")
col2.metric(label="Fractional Odds", value=fractional_odds)
col3.metric(label="Decimal Odds", value=decimal_odds)

style_metric_cards(border_color = '#CCC',
                   border_left_color = '#FF4B4B')

"---"

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📈 Lookup Table", "📊 Probability Chart", "🗃 About"])


# ---- Lookup table ----

with tab1:
    tab1.subheader("Conversion Lookup")
    tab1.text('Investigate different odds systems and their implied probability conversions')

    @st.cache_data #used to be st.cache I believe
    def load_data():
        df = pd.read_csv('https://raw.githubusercontent.com/steodose/odds-converter/main/odds.csv')
        return df

    df = load_data()
    df = df[['american_moneyline', 'fraction', 'decimal', 'implied_probability']] # switch column ordering

    #rename columns
    df = df.rename(columns={"american_moneyline": "American Moneyline", "fraction": "Fraction", "decimal": "Decimal", 
                    "implied_probability": "Implied Probability"})

    # Set colormap equal to seaborn color palette
    cm = sns.color_palette("vlag_r", as_cmap=True) #_r reverses color palette

    def color_negative_red(value):
    #Colors elements in a dateframe, green if positive and red if, negative. Does not color NaN values.
        if value < 0:
            color = 'green'
        elif value > 0:
            color = 'red'
        else:
            color = 'black'

        return 'color: %s' % color

    st.dataframe(df.style
                .background_gradient(cmap=cm, subset=['Implied Probability'])
                .applymap(color_negative_red, subset=['American Moneyline'])
                .format({'American Moneyline': "{:.0f}",
                        'Decimal': "{:.2f}",
                        'Implied Probability': "{:.1%}"}),
                hide_index=True    
                )


# ---- Probability Chart Tab ----
with tab2:
    tab2.subheader("Probability Chart")
    tab2.text('Win-Loss chances')
    # Calculate probabilities
    implied_probability_win = moneyline_to_implied_probability(moneyline)
    implied_probability_loss = 100 - implied_probability_win

    # Data for bar chart
    prob_data = pd.DataFrame({
            'Outcome': ['Win', 'Loss'],
            'Probability': [implied_probability_win, implied_probability_loss],
            'Color': ['#4E79A7', '#F28E2B']  # Specify colors for each bar
        })

    # Altair bar chart
    # chart = alt.Chart(prob_data).mark_bar(cornerRadiusTopLeft=10,
    #     cornerRadiusTopRight=10
    #     ).encode(
    #         x=alt.X('Outcome', sort='descending', title=None),  # Remove 'Outcome' label and reverse order
    #         y=alt.Y('Probability', scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(format='%')),  # Set y-axis range and format
    #         color=alt.Color('Color', scale=None)  # Use the specified hex colors
    #     )

    # Altair bar chart
    bars = alt.Chart(prob_data).mark_bar(cornerRadiusTopLeft=10,
        cornerRadiusTopRight=10
        ).encode(
            x=alt.X('Outcome', sort='descending', title=None),  # Remove 'Outcome' label and reverse order
            y=alt.Y('Probability:Q', scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(format='%')),  # Adjusted scale
            color=alt.Color('Color', scale=None)  # Use the specified hex colors
        )

        # Text layer for displaying percentages on bars
    text = bars.mark_text(
            align='center',
            baseline='middle',
            dy=-10  # Adjust the vertical position of the text
        ).encode(
            text=alt.Text('Probability:Q', format='.1f')  # Format the text with one decimal
        )

        # Combine the bar and text layers
    chart = alt.layer(bars, text)
        
    # Display Altair chart in Streamlit
    st.altair_chart(chart, use_container_width=True)


# ---- About Tab ----
with tab3:
    tab3.subheader("About")
    # Place the content for the About section here
    tab3.markdown("""
         Betting odds are the foundation of sports betting. They’re set by bookmakers, 
        and they tell you the implied probability for a given bet to win. The odds tell 
        you how much you’ll win on any wager. They tell you what the expected outcome is for both teams, and can be listed
        in American odds, fractional odds and decimal odds. All three express the same thing.
        For more info, see [this explainer here](https://www.mlive.com/betting/guides/odds/#:~:text=For%20an%20underdog%2C%20the%20equation,denominator%20%2B%20numerator). 
        """)


example_twitter()
example_github()

