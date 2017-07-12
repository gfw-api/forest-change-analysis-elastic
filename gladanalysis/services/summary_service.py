import collections
import datetime
import calendar
import logging

class SummaryService(object):
    """Class for creating summary stats on glad data"""

    @staticmethod
    def julian_day_to_date(year, jd):
        month = 1
        day = 0
        while jd - calendar.monthrange(year,month)[1] > 0 and month < 12:
            jd = jd - calendar.monthrange(year,month)[1]
            month = month + 1
        return year, month, jd

    @staticmethod
    def aggregate_glad_values_day(data, from_year, from_date, to_year, to_date):

        values = []
        values_from_year = []
        values_to_year = []
        values_mid_year = []
        agg_values = {}

        from_year = (int(from_year))
        from_date = (int(from_date))
        to_year = (int(to_year))
        to_date = (int(to_date))

        if from_year == to_year:

            for y in data['data']:
                if y['julian_day'] in range(from_date, to_date):
                    values.append(y['julian_day'])

            count = collections.Counter(values)
            agg_values[from_year] = count

            return agg_values

        elif (from_year + 1) == to_year:

            for y in data['data']:
                if y['year'] == from_year:
                    if y['julian_day'] in range(from_date, 365):
                        values_from_year.append(y['julian_day'])
                elif y['year'] == to_year:
                    if y['julian_day'] in range(1, to_date):
                        values_to_year.append(y['julian_day'])

            count_from_year = collections.Counter(values_from_year)
            count_to_year = collections.Counter(values_to_year)

            agg_values[from_year] = count_from_year
            agg_values[to_year] = count_to_year

            return agg_values

        else:
            for y in data['data']:
                if y['year'] == from_year:
                    if y['julian_day'] in range(from_date, 365):
                        values_from_year.append(y['julian_day'])
                elif y['year'] == to_year:
                    if y['julian_day'] in range(1, to_date):
                        values_to_year.append(y['julian_day'])
                elif y['year'] == (from_year + 1):
                    values_mid_year.append(y['julian_day'])

            count_from_year = collections.Counter(values_from_year)
            count_mid_year = collections.Counter(values_mid_year)
            count_to_year = collections.Counter(values_to_year)

            agg_values[from_year] = count_from_year
            agg_values[(from_year + 1)] = count_mid_year
            agg_values[to_year] = count_to_year

            agg_data = dict((k, dict(v)) for k, v in agg_values.iteritems())

            return agg_data

    @staticmethod
    def aggregate_glad_values_year(data, from_year, to_year):

        from_year = (int(from_year))
        to_year = (int(to_year))

        agg_values = {}
        values_2015 = []
        values_2016 = []
        values_2017 = []

        for y in data['data']:
            if y['year'] == 2015:
                values_2015.append(y['julian_day'])
            elif y['year'] == 2016:
                values_2016.append(['julian_day'])
            elif y['year'] == 2017:
                values_2017.append(['julian_day'])

        agg_values[2015] = len(values_2015)
        agg_values[2016] = len(values_2016)
        agg_values[2017] = len(values_2017)

        return agg_values

    @staticmethod
    def agg_by_week_month(values, from_year):

        date_values = []
        wk_values = []
        m_values = []

        agg_values = {}

        for value in values:
            year, month, day = SummaryService.julian_day_to_date(from_year, value)
            date_values.append([year, month, day])
            m_values.append(month)

        for time in date_values:
            wk = datetime.date(time[0],time[1],time[2]).isocalendar()[1]
            wk_values.append(wk)

        wk_count = collections.Counter(wk_values)
        m_count = collections.Counter(m_values)

        return wk_count, m_count

    @staticmethod
    def format_agg_data_week_month(values_from_year, from_year, to_year=None, values_mid_year=None, values_to_year=None):

        agg_values_week = {}
        agg_values_month = {}

        wk_count_from_year = SummaryService.agg_by_week_month(values_from_year, from_year)[0]
        m_count_from_year = SummaryService.agg_by_week_month(values_from_year, from_year)[1]
        if values_mid_year:
            wk_count_mid_year = SummaryService.agg_by_week_month(values_mid_year, from_year)[0]
            m_count_mid_year = SummaryService.agg_by_week_month(values_mid_year, from_year)[1]
        if values_to_year:
            wk_count_to_year = SummaryService.agg_by_week_month(values_to_year, from_year)[0]
            m_count_to_year = SummaryService.agg_by_week_month(values_to_year, from_year)[1]

        agg_values_week[from_year] = wk_count_from_year
        agg_values_month[from_year] = m_count_from_year
        if values_mid_year:
            agg_values_week[(from_year + 1)] = wk_count_mid_year
            agg_values_month[(from_year + 1)] = m_count_mid_year
        if values_to_year:
            agg_values_week[to_year] = wk_count_to_year
            agg_values_month[to_year] = m_count_to_year

        agg_data_week = dict((k, dict(v)) for k, v in agg_values_week.iteritems())
        agg_data_month = dict((k, dict(v)) for k, v in agg_values_month.iteritems())

        return agg_data_week, agg_data_month

    @staticmethod
    def aggregate_glad_values_week_month(data, from_year, from_date, to_year, to_date):

        from_year = (int(from_year))
        from_date = (int(from_date))
        to_year = (int(to_year))
        to_date = (int(to_date))

        values = []
        values_from_year = []
        values_mid_year = []
        values_to_year = []

        if from_year == to_year:

            for y in data['data']:
                if y['julian_day'] in range(from_date, to_date):
                    values.append(y['julian_day'])

            agg_data_week = SummaryService.format_agg_data_week_month(values, from_year)[0]
            agg_data_month = SummaryService.format_agg_data_week_month(values, from_year)[1]

            return agg_data_week, agg_data_month

        elif (from_year + 1) == to_year:

            for y in data['data']:
                if y['year'] == from_year:
                    if y['julian_day'] in range(from_date, 365):
                        values_from_year.append(y['julian_day'])
                elif y['year'] == to_year:
                    if y['julian_day'] in range(1, to_date):
                        values_to_year.append(y['julian_day'])

            agg_data_week = SummaryService.format_agg_data_week_month(values_from_year, from_year, to_year=to_year, values_to_year=values_to_year)[0]
            agg_data_month = SummaryService.format_agg_data_week_month(values_from_year, from_year, to_year=to_year, values_to_year=values_to_year)[1]

            return agg_data_week, agg_data_month

        else:

            for y in data['data']:
                if y['year'] == from_year:
                    if y['julian_day'] in range(from_date, 365):
                        values_from_year.append(y['julian_day'])
                elif y['year'] == to_year:
                    if y['julian_day'] in range(1, to_date):
                        values_to_year.append(y['julian_day'])
                elif y['year'] == (from_year + 1):
                    values_mid_year.append(y['julian_day'])

            agg_data_week = SummaryService.format_agg_data_week_month(values_from_year, from_year, to_year=to_year, values_mid_year=values_mid_year, values_to_year=values_to_year)[0]
            agg_data_month = SummaryService.format_agg_data_week_month(values_from_year, from_year, to_year=to_year, values_mid_year=values_mid_year, values_to_year=values_to_year)[1]

            return agg_data_week, agg_data_month
