# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import math
from datetime import datetime, time
import numpy as np

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

MAX_TIME_INDEX = 72
pred_idx = []

def time_to_index(date_time):
    return date_time.hour * 3 + int(math.floor(date_time.minute / 20))

def time_to_date_index(date_time):
    dtime = date_time.date - date(date_time.year, 1, 1)
    return dtime.days

def index_to_time(index):
    if index > 72:
        return None
    hour = index / 3
    minute = (index % 3) * 20
    return datetime(year=2017, month=10, day=1, hour=hour, minute=minute)

def my_att_interpolation(route_day_att):
    '''
    replace missing value (denoted by 0) with prev and next value average
    '''
    assert len(route_day_att) == MAX_TIME_INDEX
    y = np.zeros(MAX_TIME_INDEX)
    prev_att = 0.0
    for i in range(MAX_TIME_INDEX):
        if route_day_att[i] < 1e-3:
            # find later att
            ii = i + 1
            next_att = 0.0
            while ii < MAX_TIME_INDEX and route_day_att[ii] < 1e-3:
                ii += 1
            if ii < MAX_TIME_INDEX:
                next_att = route_day_att[ii]
                k = ii - i + 1
                # 1st of k divide point
                route_day_att[i] = ((k - 1)*prev_att + next_att) / k
            else:
                route_day_att[i] = prev_att
        prev_att = y[i] = route_day_att[i]
    return y


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

pred_start_idx = time_to_index(time(hour=8,minute=0))
pred_end_idx = time_to_index(time(hour=10, minute=0))
pred_idx.extend(range(pred_start_idx, pred_end_idx))

pred_start_idx = time_to_index(time(hour=17, minute=0))
pred_end_idx = time_to_index(time(hour=19, minute=0))
pred_idx.extend(range(pred_start_idx, pred_end_idx))
