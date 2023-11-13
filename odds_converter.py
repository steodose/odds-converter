#### Odds Converter Streamlit App

import streamlit as st
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fractions import Fraction
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.badges import badge
#from st_aggrid import JsCode, AgGrid, GridOptionsBuilder



# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Odds Converter", page_icon=":game_die:")


# ---- MAINPAGE ----
st.title(":game_die: Odds Converter Tool")
st.markdown(""" 
This app allows you to quickly reference sports betting odds and their implied probabilities using various international systems. A **Between The Pipes** app by [Stephan Teodosescu](https://stephanteodosescu.com/).
""")


"---"

# App logo (not working)
# def btp_logo():
#         add_logo("/Users/Stephan/Desktop/R Projects/personal-website/BTP (3).png", height=300)

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

# ---- Odds table ----

tab1, tab2 = st.tabs(["📈 Odds", "🗃 About"])

@st.cache_data #used to be st.cache I believe
def load_data():
    df = pd.read_csv('https://raw.githubusercontent.com/steodose/odds-converter/main/odds.csv')
    return df

df = load_data()
df = df[['american_moneyline', 'fraction', 'decimal', 'implied_probability']] # switch column ordering
#rename columns
df = df.rename(columns={"american_moneyline": "American Moneyline", "fraction": "Fraction", "decimal": "Decimal", 
                  "implied_probability": "Implied Probability"})


# Odds lookup table and bar chart
tab1.subheader("Conversion Lookup")
tab1.text('Investigate different odds systems and their implied probability conversions')

# Set colormap equal to seaborn color palette
cm = sns.color_palette("coolwarm", as_cmap=True)

def color_negative_red(value):
  """
  Colors elements in a dateframe
  green if positive and red if
  negative. Does not color NaN
  values.
  """

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


# gd = GridOptionsBuilder.from_dataframe(df)
# gd.configure_selection(selection_mode='', use_checkbox= "TRUE")

# gridoptions = gd.build()
# AgGrid(df, height=400, gridOptions=gridoptions,
#        allow_unsafe_jscode="TRUE"

# About page
tab2.subheader("About")
st.markdown("""
        Betting odds are the foundation of sports betting. They’re set by bookmakers, 
        and they tell you the implied probability for a given bet to win. The odds tell 
        you how much you’ll win on any wager. The odds are the first thing to look at 
        when talking about a sports bet, and they lay the table for all the steps that come 
        next. They tell you what the expected outcome is for both teams, and can be listed
        in American odds, fractional odds and decimal odds. All three express the same thing.
        For more info, see [this explainer here](https://www.mlive.com/betting/guides/odds/#:~:text=For%20an%20underdog%2C%20the%20equation,denominator%20%2B%20numerator). 

        """)


example_twitter()
example_github()

