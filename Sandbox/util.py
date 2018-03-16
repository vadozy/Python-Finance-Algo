from dateutil.parser import parse
import re
from collections import defaultdict


def accumulated_returns(s, date_from, date_to):
    """Returns accumulated return rate

    Args:
        s (pandas Series) with prices
        date_from (int): Begin Date (eg '2010-01-31')
        date_to   (str): End Date (eg '2018-01-31')

    Returns:
        float: price on date_to / price on date_from

    """
    if (s.index[0] - parse(date_from)).days > 5:
        raise Exception("Series start date [{}] is after date_from [{}]".format(s.index[0], date_from))
    if (parse(date_to) - s.index[-1]).days > 5:
        raise Exception("Series end date [{}] is before the date_to [{}]".format(s.index[-1], date_to))
    _series = s.loc[date_from:date_to]
    return round(_series.iloc[-1] / _series.iloc[0], 4)


def parse_US_Large_Cap():
    """ Returns a dict, key - industry, value - set of stock symbols

    Parses the US_Large_Cap.txt file, parses the WIKI-datasets-codes.csv file,
    matches them to each other and returns a dict like this:
    {'Banks': {'WIKI/BAC', 'WIKI/BBT', ...., 'WIKI/WFC'}, ...}
    """
    stocks = set()
    industries = defaultdict(set)
    with open('US_Large_Cap.txt') as f:

        for line in f:

            industry_match = re.match(r'.*--\s*(.*)', line)

            if industry_match:
                ind = industry_match.group(1)

            stock_match = re.match(r'.*(WIKI/\S*)', line)

            if stock_match:
                s = stock_match.group(1)
                industries[ind].add(s)
                stocks.add(s)

    print("Distinct Industries = {}".format(len(industries)))
    print("Distinct Stocks = {}".format(len(stocks)))

    quandl_wiki_stocks = set()
    with open('WIKI-datasets-codes.csv') as f:
        for line in f:
            stock_match = re.match(r'.*(WIKI/[^,]*)', line)
            if stock_match:
                s = stock_match.group(1)
                quandl_wiki_stocks.add(s)
    print("Distinct Quandl Wiki Stocks = {}".format(len(quandl_wiki_stocks)))

    # remove stocks not in quandl_wiki_stocks
    for v in industries.values():
        v &= quandl_wiki_stocks

    return industries
