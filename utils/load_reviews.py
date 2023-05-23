import pandas as pd


def _rename_columns(df):
    return df.rename(columns={'title': 'Title',
                              'review': 'Review',
                              'stars': 'Rating',
                              'iso': 'Country',
                              'date': 'Date',
                              'store': 'OS',
                              'id': 'ID'})


def _subset(df):
    return df[['Title', 'Review', 'Rating', 'Country', 'Date', 'OS', 'ID']]


def _clean(df):
    return df.dropna(subset=['Rating', 'Country', 'Date', 'OS', 'ID'])


def _map_os(df):
    df.loc[:, 'OS'] = df.OS.map({'apple': 'iOS', 'google_play': 'Android'})
    return df


def read_reviews(path):
    df = pd.read_json(path)
    df = _rename_columns(df)
    df = _subset(df)
    df = _clean(df)
    df = _map_os(df)
    return df
