# -*- coding: utf-8 -*-
#!/usr/bin/env python

import math
from datetime import datetime

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

def time_to_index(date_time):
    return date_time.hour * 3 + int(math.floor(date_time.minute / 20))

def index_to_time(index):
    if index > 72:
        return None
    hour = index / 3
    minute = (index % 3) * 20
    return datetime(year=2017, month=10, day=1, hour=hour, minute=minute)


def att_mape(d_rt, p_rt, routes, time_windows):
    '''
    Mean Absolute Percentage Error
    '''
    num_r = len(routes)
    num_t = len(time_windows)
    
    mape = 0.0
    for r in routes:
        sum_t = 0.0
        for t in time_windows:
            if d_rt[r][t] < 1e-3:
                d_rt[r][t] = p_rt[r][t]
            sum_t += math.fabs(d_rt[r][t] - p_rt[r][t]) / d_rt[r][t]
        sum_t /= num_t
        mape += sum_t
    mape = mape / num_r
    return mape


def vol_mape(f_rt, p_rt, toll_dirs, time_windows):
    '''
    Mean Absolute Percentage Error
    '''
    num_c = len(toll_dirs)
    num_t = len(time_windows)

    mape = 0.0
    for c in toll_dirs:
        sum_t = 0.0
        for t in time_windows:
            sum_t += math.fabs(f_rt[c][t] - p_rt[c][t]) / p_rt[c][t]
        sum_t /= num_t
        mape += sum_t
    mape = mape / num_c
    return mape
