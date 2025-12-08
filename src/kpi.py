# 
import pandas as pd

def clean_budget_revenue(wanted_data):
    cols = ['budget_musd', 'revenue_musd']
    for column in cols:
        wanted_data[column + '_num'] = (
            wanted_data[column]
            .str.replace('$', '', regex=False)
            .str.replace('M', '', regex=False)
            .astype(float)
        )
    return wanted_data


def highest_revenue(wanted_data):
    idx = wanted_data['revenue_musd_num'].idxmax()
    return wanted_data.loc[idx][['title', 'revenue_musd_num']]


def highest_budget(wanted_data):
    idx = wanted_data['budget_musd_num'].idxmax()
    return wanted_data.loc[idx][['title', 'budget_musd_num']]


def compute_profit(wanted_data):
    wanted_data['profit_musd'] = df['revenue_musd_num'] - df['budget_musd_num']
    return df


def highest_profit(df):
    idx = df['profit_musd'].idxmax()
    return df.loc[idx][['title', 'profit_musd']]


def lowest_profit(df):
    idx = df['profit_musd'].idxmin()
    return df.loc[idx][['title', 'profit_musd']]


def highest_roi(df):
    df['roi'] = df['revenue_musd_num'] / df['budget_musd_num']
    filtered = df[df['budget_musd_num'] >= 10]
    idx = filtered['roi'].idxmax()
    return df.loc[idx][['title', 'roi']]


def lowest_roi(df):
    df['roi'] = df['revenue_musd_num'] / df['budget_musd_num']
    filtered = df[df['budget_musd_num'] >= 10]
    idx = filtered['roi'].idxmin()
    return df.loc[idx][['title', 'roi']]


def most_voted(df):
    idx = df['vote_count'].idxmax()
    return df.loc[idx][['title', 'vote_count']]


def highest_rated(df):
    filtered = df[df['vote_count'] >= 10]
    idx = filtered['vote_average'].idxmax()
    return df.loc[idx][['title', 'vote_average']]


def lowest_rated(df):
    filtered = df[df['vote_count'] >= 10]
    idx = filtered['vote_average'].idxmin()
    return df.loc[idx][['title', 'vote_average']]


def most_popular(df):
    idx = df['popularity'].idxmax()
    return df.loc[idx][['title', 'popularity']]
