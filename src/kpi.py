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
    wanted_data['profit_musd'] = wanted_data['revenue_musd_num'] - wanted_data['budget_musd_num']
    return wanted_data


def highest_profit(wanted_data):
    idx = wanted_data['profit_musd'].idxmax()
    return wanted_data.loc[idx][['title', 'profit_musd']]


def lowest_profit(wanted_data):
    idx = wanted_data['profit_musd'].idxmin()
    return wanted_data.loc[idx][['title', 'profit_musd']]


def highest_roi(wanted_data):
    wanted_data['roi'] = wanted_data['revenue_musd_num'] / wanted_data['budget_musd_num']
    filtered = wanted_data[wanted_data['budget_musd_num'] >= 10]
    idx = filtered['roi'].idxmax()
    return wanted_data.loc[idx][['title', 'roi']]


def lowest_roi(wanted_data):
    wanted_data['roi'] = wanted_data['revenue_musd_num'] / wanted_data['budget_musd_num']
    filtered = wanted_data[wanted_data['budget_musd_num'] >= 10]
    idx = filtered['roi'].idxmin()
    return wanted_data.loc[idx][['title', 'roi']]


def most_voted(wanted_data):
    idx = wanted_data['vote_count'].idxmax()
    return wanted_data.loc[idx][['title', 'vote_count']]


def highest_rated(wanted_data):
    filtered = wanted_data[wanted_data['vote_count'] >= 10]
    idx = filtered['vote_average'].idxmax()
    return wanted_data.loc[idx][['title', 'vote_average']]


def lowest_rated(wanted_data):
    filtered = wanted_data[wanted_data['vote_count'] >= 10]
    idx = filtered['vote_average'].idxmin()
    return wanted_data.loc[idx][['title', 'vote_average']]


def most_popular(wanted_data):
    idx = wanted_data['popularity'].idxmax()
    return wanted_data.loc[idx][['title', 'popularity']]
