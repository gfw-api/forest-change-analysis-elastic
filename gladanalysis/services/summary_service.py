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
    def aggregate_glad_values_week(data, from_year, from_date, to_year, to_date):

        from_year = (int(from_year))
        from_date = (int(from_date))
        to_year = (int(to_year))
        to_date = (int(to_date))

        values = []
        values_from_year = []
        values_mid_year = []
        values_to_year = []

        date_values_from_year = []
        date_values_mid_year = []
        date_values_to_year = []
        wk_values_from_year = []
        wk_values_mid_year = []
        wk_values_to_year = []

        agg_values = {}

        if from_year == to_year:

            for y in data['data']:
                if y['julian_day'] in range(from_date, to_date):
                    values.append(y['julian_day'])

            for value in values:
                year, month, day = SummaryService.julian_day_to_date(from_year, value)
                date_values_from_year.append([year, month, day])

            for time in date_values_from_year:
                wk = datetime.date(time[0],time[1],time[2]).isocalendar()[1]
                wk_values_from_year.append(wk)

            wk_count = collections.Counter(wk_values_from_year)
            agg_values[from_year] = wk_count
            agg_data = dict((k, dict(v)) for k, v in agg_values.iteritems())

            return agg_data

        elif (from_year + 1) == to_year:

            for y in data['data']:
                if y['year'] == from_year:
                    if y['julian_day'] in range(from_date, 365):
                        values_from_year.append(y['julian_day'])
                elif y['year'] == to_year:
                    if y['julian_day'] in range(1, to_date):
                        values_to_year.append(y['julian_day'])

            for value in values_from_year:
                year, month, day = SummaryService.julian_day_to_date(from_year, value)
                date_values_from_year.append([year, month, day])

            for time in date_values_from_year:
                wk = datetime.date(time[0],time[1],time[2]).isocalendar()[1]
                wk_values_from_year.append(wk)

            for value in values_to_year:
                year, month, day = SummaryService.julian_day_to_date(from_year, value)
                date_values_to_year.append([year, month, day])

            for time in date_values_to_year:
                wk = datetime.date(time[0],time[1],time[2]).isocalendar()[1]
                wk_values_to_year.append(wk)

            wk_count_from_year = collections.Counter(wk_values_from_year)
            wk_count_to_year = collections.Counter(wk_values_to_year)
            agg_values[from_year] = wk_count_from_year
            agg_values[to_year] = wk_count_to_year
            agg_data = dict((k, dict(v)) for k, v in agg_values.iteritems())

            return agg_data

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

            for value in values_from_year:
                year, month, day = SummaryService.julian_day_to_date(from_year, value)
                date_values_from_year.append([year, month, day])

            for time in date_values_from_year:
                wk = datetime.date(time[0],time[1],time[2]).isocalendar[1]
                wk_values_from_year.append(wk)

            for value in values_to_year:
                year, month, day = SummaryService.julian_day_to_date(from_year, value)
                date_values_to_year.append([year, month, day])

            for time in date_values_to_year:
                wk = datetime.date(time[0],time[1],time[2]).isocalendar()[1]
                wk_values_to_year.append(wk)

            for value in values_mid_year:
                year, month, day = SummaryService.julian_day_to_date(from_year, value)
                date_values_mid_year.append([year, month, day])

            for time in date_values_mid_year:
                wk = datetime.date(time[0],time[1],time[2]).isocalendar()[1]
                wk_values_mid_year.append(wk)

            count_from_year = collections.Counter(wk_values_from_year)
            count_mid_year = collections.Counter(wk_values_mid_year)
            count_to_year = collections.Counter(wk_values_to_year)

            agg_values[from_year] = count_from_year
            agg_values[(from_year + 1)] = count_mid_year
            agg_values[to_year] = count_to_year

            agg_data = dict((k, dict(v)) for k, v in agg_values.iteritems())

            return agg_data
