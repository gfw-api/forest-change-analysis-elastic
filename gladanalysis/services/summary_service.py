import collections
import datetime
import calendar
import pandas as pd

class SummaryService(object):
    """Class for creating summary stats on glad data"""

    @staticmethod
    def create_time_table(dataset, data, agg_type):

        df = pd.DataFrame(data['data'])

        # create datetime column in pandas so we can pull
        if dataset == 'glad':
            df['alert_date'] = pd.to_datetime(df.year, format='%Y') + pd.to_timedelta(df.julian_day - 1, unit='d')
        elif dataset == 'terrai':
            df['alert_date'] = pd.to_datetime(df.year, format='%Y') + pd.to_timedelta(df.day - 1, unit='d')

        # extract month and quarter values from datetime object
        df['month'] = df.alert_date.dt.month
        df['quarter'] = df.alert_date.dt.quarter

        # pandas week calculations are different; need to use this instead
        df['week'] = df.alert_date.apply(lambda x: x.isocalendar()[1])

        print df

        if agg_type == 'year':
            grouped = df.groupby(['year']).size().reset_index()
        else:
            grouped = df.groupby(['year', agg_type]).size().reset_index()
        grouped = grouped.rename(columns={0: 'count'})

        # no idea how this works, but it does
        # https://stackoverflow.com/questions/41998624/
        output = grouped.groupby('year')[[agg_type, 'count']].apply(
                         lambda x: x.set_index(agg_type).to_dict(orient='index')).to_dict()

        data_format = {}
        if agg_type == 'year':
            for year in output.keys():
                data_format[year] = output[year][year]['count']
        else:
            for year in output.keys():
                data_format[year] = {}
                for agg in output[year]:
                    data_format[year][agg] = output[year][agg]['count']

        return data_format
