import pandas as pd
from dateutil.parser import parse


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
