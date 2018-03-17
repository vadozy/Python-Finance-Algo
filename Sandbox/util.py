import datetime
import calendar
from dateutil.parser import parse
import re
from collections import defaultdict


def valid_dates(s, date_from, date_to, leniency=4):
    """Validates that pandas Series s index is within date_from:date_to

    Parameters
    ----------
    s : pandas Series
       pandas Series with DateTime monotonic index
    date_from : datetime.datetime or datetime.date or str 'YYYY-mm-dd'
       The date that shoud be within Series index (up to leniency)
    date_to : datetime.datetime or datetime.date or str 'YYYY-mm-dd'
       The date that shoud be within Series index (up to leniency)
    leniency     : int
        Number of days that Series index is allowed to spill out from date_from:date_to

    Returns
    -------
    valid : `bool`
       True if valid, False otherwise
    """
    if not s.index.is_monotonic:
        raise Exception("Series index is not monotonic (not sorted")

    date_from = _convert_date(date_from)
    date_to   = _convert_date(date_to)

    if (s.index[0].date() - date_from).days > 5:
        print("Series start date [{}] is after date_from [{}]".format(s.index[0], date_from))
        return False
    if (date_to - s.index[-1].date()).days > 5:
        print("Series end date [{}] is before the date_to [{}]".format(s.index[-1], date_to))
        return False

    return True


def accumulated_returns(s, date_from, date_to):
    """Returns accumulated return rate

    Args:
    s (pandas Series) with prices
        datetime.datetime or datetime.date or str 'YYYY-mm-dd'
    date_from (datetime.datetime or datetime.date or str 'YYYY-mm-dd')
        Begin Date (eg '2010-01-31')
    date_to   (datetime.datetime or datetime.date or str 'YYYY-mm-dd')
        End Date (eg '2018-01-31')

    Returns:
        float: price on date_to / price on date_from

    """
    if not valid_dates(s, date_from, date_to):
        raise Exception("Series index [ {} : {} ] is not within [ {} : {} ]".format(s.index[0], s.index[-1], date_from, date_to))

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


def add_months(sourcedate, months):
    """Adds months to the sourcedate (adjusting the day if necessary)

    Parameters
    ----------
    sourcedate : datetime.datetime or datetime.date
       The date to which months will be added
    months     : int
        Nimber of months to add to sourcedate

    Returns
    -------
    newdate : `datetime.date`
       sourcedate plus months
    """
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])

    return datetime.date(year, month, day)


def generate_periods(start_date, end_date, months):
    """Retunrs list of tuples of 2 dates, with months difference in each tuple

    For example calling generate_periods('2010-01-25', '2010-08-25', 3) retunrs:
        [(datetime.date(2010, 1, 25), datetime.date(2010, 4, 25)),
         (datetime.date(2010, 4, 25), datetime.date(2010, 7, 25))]

    Parameters
    ----------
    start_date : datetime.datetime or datetime.date or str 'YYYY-mm-dd'
       The date from which the list is generated
    end_date : datetime.datetime or datetime.date or str 'YYYY-mm-dd'
       The date up till which the list is generated
    months     : int
        Nimber of months between dates in each tuple

    Returns
    -------
    list of periods : `list of tuples - (datetime.date, datetime.date)`
       list of generated periods
    """
    start_date = _convert_date(start_date)
    end_date   = _convert_date(end_date)

    ret = []
    d1 = start_date
    d2 = add_months(d1, months)
    while d2 <= end_date:
        ret.append((d1, d2))
        d1, d2 = d2, add_months(d2, months)

    if len(ret) == 0:
        raise Exception("Could not generate {} months periods between {} and {}".format(months, start_date, end_date))
    return ret


def _convert_date(date):
    """Retunrs datetime.date type

    Parameters
    ----------
    date : datetime.datetime or datetime.date or str 'YYYY-mm-dd'
       The date to be converted to datetime.date

    Returns
    -------
    date : datetime.datetime
        converted date
    """
    if isinstance(date, str):
        date = parse(date).date()
    elif isinstance(date, datetime.datetime):
        date = date.date()
    elif isinstance(date, datetime.date):
        date = date
    else:
        raise Exception("Unexpected Date Type")

    return date
