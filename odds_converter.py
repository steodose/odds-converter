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


# ---- Function definitions ------ #

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

# Define additional conversion function for decimal odds
def decimal_to_implied_probability(decimal_odds):
    probability = 1 / decimal_odds
    return round(probability * 100, 1)  # Convert to percentage

# Define Decimal to Fractional Odds conversion function
def decimal_to_fractional_odds(decimal_odds):
    # Convert decimal odds to a Fraction and reduce it
    fractional_odds = Fraction(decimal_odds - 1).limit_denominator()
    return f"{fractional_odds.numerator}/{fractional_odds.denominator}"

# Define Decinal to American odds conversion function
def decimal_to_american_odds(decimal_odds):
    if decimal_odds >= 2.0:
        # For favorites
        american_odds = (decimal_odds - 1) * 100
    else:
        # For underdogs
        american_odds = -100 / (decimal_odds - 1)
    return round(american_odds)


# Define $ Total Winnings function 
def to_win(bet_amount, moneyline):
    """
    Convert American moneyline odds to total winings.
    """
    if moneyline > 0:
        winnings = bet_amount * moneyline/100
    else:
        winnings = bet_amount * 100 / abs(moneyline)
    return bet_amount + winnings 




# ---- MAINPAGE UI ----

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Odds Converter", page_icon=":game_die:")

# Display BTP logo image
logo_path_or_url = 'https://raw.githubusercontent.com/steodose/odds-converter/master/BTP.png'

#st.image(logo_path_or_url, width=100)  # Adjust width as needed

# Create a two-column layout for the rest of the content
col1, col2 = st.columns([1, 5])

# Display the logo in the first column
col1.image(logo_path_or_url, width=100)  # Adjust the width to fit your logo

# Set the title in the second column
col2.title(":game_die: Odds Converter Tool")

st.markdown(""" 
This app allows you to quickly reference sports betting odds and their implied probabilities using various international systems. A **Between The Pipes** app by [Stephan Teodosescu](https://stephanteodosescu.com/).
""")

"---"

# ---- Sidebar ----

# Sidebar for odds type selection and moneyline + bet amount inputs

st.sidebar.header('Selector')

odds_type = st.sidebar.radio("Select Odds Type", ["American", "Decimal"],
                            captions = ["Common in the U.S.", "Common in Europe, Australia and Canada."])

if odds_type == "American":
    odds = st.sidebar.number_input('Enter American Moneyline Odds', value=-110)
    implied_probability = moneyline_to_implied_probability(odds)
    fractional_odds = moneyline_to_fractional_odds(odds)
    decimal_odds = moneyline_to_decimal_odds(odds)
else:
    odds = st.sidebar.number_input('Enter Decimal Odds', value=1.91)
    implied_probability = decimal_to_implied_probability(odds)
    fractional_odds = decimal_to_fractional_odds(odds)
    american_odds = decimal_to_american_odds(odds)

bet_amount = st.sidebar.number_input('Enter Bet Amount ($)', value=100, min_value=0)

# Calculate the total payout
total_payout = to_win(bet_amount, odds if odds_type == "American" else american_odds)
profit = total_payout - bet_amount
expected_value = (profit * (implied_probability/100)) - (1-(implied_probability/100) * bet_amount)


# ---- KPIs Section ----

col1, col2, col3 = st.columns(3)

col1.metric(label="Implied Probability", value=f"{implied_probability}%")
if odds_type == "American":
    col2.metric(label="Fractional Odds", value=fractional_odds)
    col3.metric(label="Decimal Odds", value=decimal_odds)
else:
    col2.metric(label="Fractional Odds", value=fractional_odds)
    col3.metric(label="American Odds", value=american_odds)


# Bet payouts and expected value KPIs
col1, col2, col3 = st.columns(3)
#col1.metric("To Win", value = "$100")
col1.metric(label="Total Payout", value=f"${total_payout:.2f}")
col2.metric("Profit (Earnings)", value=f"${profit:.2f}")
col3.metric("Expected Value", value=f"${expected_value:.2f}")

style_metric_cards(border_color = '#CCC',
                   border_left_color = '#AA0000')

"---"

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["📈 Lookup Table", "📊 Probability Chart", "📰 Glossary", "🗃 About"])


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

    # Depending on the odds type, calculate win and loss probabilities
    if odds_type == "American":
        implied_probability_win = moneyline_to_implied_probability(odds)
    else:  # For Decimal odds
        implied_probability_win = decimal_to_implied_probability(odds)

    implied_probability_loss = 100 - implied_probability_win

    # Data for bar chart
    prob_data = pd.DataFrame({
            'Outcome': ['Win', 'Loss'],
            'Probability': [implied_probability_win/100, implied_probability_loss/100],
            'Color': ['#4E79A7', '#F28E2B']  # Specify colors for each bar
        })


    # Altair bar chart
    bars = alt.Chart(prob_data).mark_bar(cornerRadiusTopLeft=10,
        cornerRadiusTopRight=10
        ).encode(
            x=alt.X('Outcome', sort='descending', 
                    axis=alt.Axis(labelAngle=0, title='Bet Outcome', titleFontWeight='bold')),  # Reverse order
            y=alt.Y('Probability:Q', scale=alt.Scale(domain=[0, 1]), 
                    axis=alt.Axis(labels=False, title='Probability', titleFontWeight='bold')),  # Adjusted scale
            color=alt.Color('Color', scale=None)  # Use the specified hex colors
        )

        # Text layer for displaying percentages on bars
    text = bars.mark_text(
            align='center',
            baseline='middle',
            dy=-10  # Adjust the vertical position of the text
        ).encode(
            text=alt.Text('Probability:Q', format='.1%')  # Format the text with one decimal
        )

        # Combine the bar and text layers
    chart = alt.layer(bars, text)
        
    # Display Altair chart in Streamlit
    st.altair_chart(chart, use_container_width=True)


# ---- Glossary ----
with tab3:
    tab3.subheader("Glossary")
    tab3.markdown("""
         - **American odds**: Odds expression indicating return relative to 100 unit base figure. Whenever there is a minus (-) you lay that amount
        to win `$100`, where there is a plus (+) you win that amount for every `$100` you bet.
        
        - **Decimal odds**: Odds expression (sometimes referred to as European odds) where the odds are shown in decimal format.
                  The format is a simple numerical representation of the potential return of a bet, which includes the stake amount.

        - **Expected value**: The amount a player can expect to win or lose if they were to place a bet on the same odds many times over, 
                  calculated through a simple equation multiplying your probability of winning with the amount you could win per bet (profit), 
                  and subtracting the probability of losing multiplied by the amount lost per bet. For example, if your calculated EV is `-$2.00`
                for a `$10` bet, this suggests you will lose an average of `$2` for every `$10` staked.

        - **Fractional odds**: Odds expression (most commonly used in the UK) which presents odds in a fractional format.

        - **Laying the Points**: Backing the favorite on the Points Spread and therefore accepting the points Handicap.
                  
        - **Moneyline**: A bet on the outcome of a match/game. One of three basic bet types.
                  
        - **Odds**: A representation of the perceived frequency of an event derived from the underlying probability which enables betting.
                  
        - **Over/Under**: Bet on whether the total of any given variable (like a point total) will be over or under the mark set by a bookmaker.
                  
        - **Spread**: Also known as points spread, it's the measure of perceived difference in the abilities of participants in a given event 
                  as illustrated in the Handicap/Spread market. The favorite is always indicated by a minus sign (e.g. -6.5pts) and the underdog
                   by a plus sign (e.g.+6.5pts).
        
        - **Vigorish**: Also know as Vig, Juice, Margin, or Commission. North American term for the implied charge that a bookmaker 
                  adds for taking bets on any given market, traditionally 10 percent for Money Line, Points Spread and Totals. 
                  It representes the implied cost of placing a bet set by the bookmaker. Bookmakers inflate the perceived 
                  likelihood of an event, as represented in their odds, suggesting it is more likely than underlying probability.
        """)
    

# ---- About Tab ----
with tab4:
    tab4.subheader("About")
    # Place the content for the About section here
    tab4.markdown("""
         Betting odds are the foundation of sports betting. They’re set by bookmakers, 
        and they tell you the implied probability for a given bet to win. The odds tell 
        you how much you’ll win on any wager. They tell you what the expected outcome is for both teams, and can be listed
        in American odds, fractional odds and decimal odds. All three express the same thing.
        For more info, see [this explainer here](https://www.mlive.com/betting/guides/odds/#:~:text=For%20an%20underdog%2C%20the%20equation,denominator%20%2B%20numerator). 
        """)


example_twitter()
example_github()

