import collections
import datetime
import calendar
import pandas as pd
import logging

class SummaryService(object):
    """Class for creating summary stats on glad data
    Takes data from the router and aggregates alerts by user specified intervals (day, week, month, year)"""

    @staticmethod
    def create_time_table(dataset, data, agg_type):

        if not data['data']:
            data_format = None

            return data_format

        else:
            df = pd.DataFrame(data['data'])
            df = df.rename(columns={'COUNT(*)': 'count'})

            # create datetime column in pandas so we can pull
            if dataset == 'glad':
                df['alert_date'] = pd.to_datetime(df.year, format='%Y') + pd.to_timedelta(df.julian_day - 1, unit='d')
            elif dataset == 'terrai':
                df['alert_date'] = pd.to_datetime(df.year, format='%Y') + pd.to_timedelta(df.day - 1, unit='d')

            # extract month and quarter values from datetime object
            df['month'] = df.alert_date.dt.month
            df['quarter'] = df.alert_date.dt.quarter
            df['week'] = df.alert_date.dt.week

            index_list = ['year']

            if agg_type != 'year':
                index_list.append(agg_type)

            grouped = df.groupby(index_list).sum()['count'].reset_index()

            # format as a dict so we can iterate over it
            output = grouped.set_index(index_list).to_dict(orient='index')

            data_format = {}

            if agg_type == 'year':
                for year_val, count_dict in output.iteritems():
                    data_format[year_val] = count_dict['count']

            else:
                for (year_val, index_val), count_dict in output.iteritems():
                    try:
                        data_format[year_val][index_val] = count_dict['count']

                    except KeyError:
                        data_format[year_val] = {}
                        data_format[year_val][index_val] = count_dict['count']

            return data_format
