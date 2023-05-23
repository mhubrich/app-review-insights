################################################################################
# Setup
################################################################################
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px

from config import style
from config import config
from utils.word_tokenizer import WordTokenizer
from utils.load_reviews import read_reviews
from utils.word_rating_counter import WordRatingCounter


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
df = read_reviews('./example/data/app_reviews.json')
wt = WordTokenizer(config.LANGUAGE, config.BLACKLIST)
df.loc[:, 'tokens'] = df.Review.apply(lambda x: wt.tokenize(x.lower(), config.NGRAMS)).astype(object)


def filter_data(dff,
                word=None,
                rating_range=None,
                countries=None,
                channels=None,
                start_date=None,
                end_date=None):
    if channels:
        dff = dff[dff.OS.isin(channels)]
    if countries:
        dff = dff[dff.Country.isin(countries)]
    if rating_range:
        dff = dff[(dff.Rating >= rating_range[0]) & (dff.Rating <= rating_range[1])]
    if start_date:
        dff = dff[dff.Date >= start_date]
    if end_date:
        dff = dff[dff.Date <= end_date]
    if word:
        dff = dff[dff.Review.str.lower().str.contains(word.strip().lower())]
    return dff


################################################################################
# Components
################################################################################

input_word = dbc.Input(
    id='input-word',
    type='search',
    placeholder='Search for word',
    debounce=True
)

slider_ratings = dcc.RangeSlider(
    id='slider-ratings',
    min=1,
    max=5,
    step=1,
    marks={
        1: '1☆',
        2: '2☆',
        3: '3☆',
        4: '4☆',
        5: '5☆'
    },
    value=[1, 5],
    allowCross=False
)

dropdown_country = dcc.Dropdown(
    id='dropdown-country',
    options=[{'label': x, 'value': x} for x in sorted(df.Country.unique())],
    placeholder='Select countries',
    multi=True,
    style=style.DROPDOWN
)

dropdown_channel = dcc.Dropdown(
    id='dropdown-channel',
    options=[{'label': x, 'value': x} for x in sorted(df.OS.unique())],
    placeholder='Select channels',
    multi=True,
    style=style.DROPDOWN
)

range_date = dcc.DatePickerRange(
    id='range-date',
    min_date_allowed=df.Date.min(),
    max_date_allowed=df.Date.max(),
    start_date=df.Date.min(),
    end_date=df.Date.max(),
    display_format='MMM D, YYYY'
)

button_pos_words = dbc.Button('MORE',
    id='button-pos-words',
    n_clicks=0,
    class_name='ml-1',
    style={'font-size': '.4em'}
)

button_neg_words = dbc.Button('MORE',
    id='button-neg-words',
    n_clicks=0,
    class_name='ml-1',
    style={'font-size': '.4em'}
)

card_pos_words = dbc.Card([
        dbc.CardHeader('Best Ratings'),
        dbc.CardBody(html.H5(button_pos_words, id='card-pos-words')),
    ],
    color='primary',
    outline=True
)

card_neg_words = dbc.Card([
        dbc.CardHeader('Worst Ratings'),
        dbc.CardBody(html.H5(button_neg_words, id='card-neg-words')),
    ],
    color='primary',
    outline=True
)

card_num_reviews = dbc.Card([
        dbc.CardHeader('Number of Reviews'),
        dbc.CardBody(html.H4(id='card-num-reviews')),
    ],
    color='primary',
    outline=True
)

card_avg_rating = dbc.Card([
        dbc.CardHeader('Average Rating'),
        dbc.CardBody(html.H4(id='card-avg-rating')),
    ],
    color='primary',
    outline=True
)

graph_scatter = dcc.Graph(
    id='graph-scatter'
)

################################################################################
# Callbacks
################################################################################
def update_card_pos_words(dff, words):
    return [dbc.Badge(x, class_name='ml-1', style=style.BADGE) for x in words] + \
           [button_pos_words]


def update_card_neg_words(dff, words):
    return [dbc.Badge(x, class_name='ml-1', style=style.BADGE) for x in words] + \
           [button_neg_words]


def update_card_num_reviews(dff):
    return len(dff)


def update_card_avg_rating(dff):
    return str(round(dff.Rating.mean(), 1)) + '☆'


def update_graph(dff):
    fig = px.scatter(dff, x='Date', y='Rating', range_y=[0.75, 5.25])
    fig.update_traces(marker=dict(size=20))
    return fig


@app.callback(
    [Output('card-pos-words', 'children'),
     Output('card-neg-words', 'children'),
     Output('card-num-reviews', 'children'),
     Output('card-avg-rating', 'children'),
     Output('graph-scatter', 'figure'),
     Output('memory', 'data')],
    [Input('input-word', 'value'),
     Input('slider-ratings', 'value'),
     Input('dropdown-country', 'value'),
     Input('dropdown-channel', 'value'),
     Input('range-date', 'start_date'),
     Input('range-date', 'end_date'),
     Input('button-pos-words', 'n_clicks'),
     Input('button-neg-words', 'n_clicks')],
     [State('memory', 'data')])
def update_UI(word, rating_range, countries, channels, start_date,
              end_date, n_clicks_pos, n_clicks_neg, data):
    # First, filter dataframe based on paramters
    dff = filter_data(df,
                      rating_range=rating_range,
                      countries=countries,
                      channels=channels,
                      start_date=start_date,
                      end_date=end_date)
    dff_word = filter_data(dff, word=word)

    # Next, determine word-button frequency
    data = data or {'clicks_pos': 1, 'clicks_neg': 1}
    changed_id = dash.callback_context.triggered[0]['prop_id']
    if 'button-pos-words' in changed_id:
        data['clicks_pos'] = data['clicks_pos'] + 1
    elif 'button-neg-words' in changed_id:
        data['clicks_neg'] = data['clicks_neg'] + 1
    else:
        data['clicks_pos'] = 1
        data['clicks_neg'] = 1
    counter = WordRatingCounter(dff)
    return update_card_pos_words(dff, counter.ratings_pos(data['clicks_pos'] * config.NUM_BUTTON_WORDS)), \
           update_card_neg_words(dff, counter.ratings_neg(data['clicks_neg'] * config.NUM_BUTTON_WORDS)), \
           update_card_num_reviews(dff_word), \
           update_card_avg_rating(dff_word),  \
           update_graph(dff_word), \
           data

################################################################################
# Content
################################################################################

sidebar = html.Div(
    [
        html.P(html.H3('Filter')),
        html.Hr(),
        html.P([html.H6('Word'), input_word]),
        html.P([html.H6('Rating'), slider_ratings]),
        html.P([html.H6('Country'), dropdown_country]),
        html.P([html.H6('Channel'), dropdown_channel]),
        html.P([html.H6('Date'), range_date])
    ],
    style=style.SIDEBAR
)

content = html.Div(
    [
        dbc.Row([dbc.Col(card_pos_words), dbc.Col(card_neg_words)]),
        dbc.Row([dbc.Col(card_num_reviews), dbc.Col(card_avg_rating)]),
        graph_scatter
    ],
    style=style.CONTENT
)

app.layout = html.Div([dcc.Store(id='memory'),
                       sidebar,
                       content])

################################################################################
# Run
################################################################################
if __name__ == '__main__':
    app.run_server(debug=True)
