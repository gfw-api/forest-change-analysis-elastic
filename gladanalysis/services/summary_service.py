import pandas as pd
import logging

class SummaryService(object):
    """Class for creating summary stats on glad data
    Takes data from the router and aggregates alerts by user specified intervals
    (day, week, month, year)"""

    @staticmethod
    def create_time_table(dataset, data, agg_type):

        if not data['data']:
            return []

        else:
            df = pd.DataFrame(data['data'])
            df = df.rename(columns={'COUNT(*)': 'count'})

            # standardize the output table to use julian_day
            if dataset == 'terrai':
                df = df.rename(columns={'day': 'julian_day'})

            if agg_type == 'day':
                agg_type = 'julian_day'

            # create datetime column in pandas so we can use its datetime
            # methods to easily summarize our results
            df['alert_date'] = pd.to_datetime(df.year, format='%Y') + pd.to_timedelta(df.julian_day - 1, unit='d')

            # extract month and quarter values from datetime object
            df['month'] = df.alert_date.dt.month
            df['quarter'] = df.alert_date.dt.quarter
            df['week'] = df.alert_date.dt.week

            # start the list of columns to groupby
            groupby_list = ['year']

            # return string formatted day value if day summary requested
            if agg_type == 'julian_day':
                df['alert_date'] = df.alert_date.dt.strftime('%Y-%m-%d')
                groupby_list += ['alert_date']

            if agg_type != 'year':
                groupby_list.append(agg_type)

            grouped = df.groupby(groupby_list).sum()['count'].reset_index()

            return grouped.to_dict(orient='records')
