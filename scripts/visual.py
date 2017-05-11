# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import math
from datetime import datetime, date, time, timedelta
import numpy as np
from scipy import interpolate
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
from aggregate_travel_time import avgTravelTime
from aggregate_volume import avgVolume
from utils import DATETIME_FORMAT, time_to_index

dataDir = 'dataSets'
MAX_TIME_SIZE = 72

start_year  = 2016
start_month = 7
start_day   = 19
end_year    = 2016
end_month   = 10
end_day     = 1
start_date  = date(year = start_year, month = start_month, day = start_day)
end_date    = date(year = end_year,   month = end_month,   day = end_day)

class viewer(object):
    def __init__(self, in_file, contextDir='training_local', file_suffix='.csv'):
        self.in_file = in_file
        self.contextDir = contextDir
        self.file_suffix = file_suffix
        self.start_date = start_date
        self.end_date = end_date

    def load_training_file(self, in_file):
        pass

    def view_data_of_date(self, day):
        pass

    def view_data_of_dates(self, dates):
        pass

    def view_time_window_in_days(self, time_index, days):
        pass


class att_viewer(viewer):
    def __init__(self, in_file, contextDir='training_local', file_suffix='.csv'):
        super(att_viewer, self).__init__(in_file, contextDir, file_suffix)
        self.hist_att = {}
        self.routes = []

    def load_training_file(self):
        hist_att_file = avgTravelTime('/'.join([dataDir, self.contextDir, self.in_file]))
        
        fr = open(hist_att_file, 'r')
        fr.readline()
        lines = fr.readlines()
        for i in xrange(len(lines)):
            line = lines[i].replace('"', '').split(',')
            intersection_id = line[0]
            tollgate_id = line[1]
            route_id = intersection_id + '-' + tollgate_id
            if route_id not in self.hist_att:
                self.hist_att[route_id] = {}
            
            trace_start_time = line[2]
            trace_start_time = datetime.strptime(trace_start_time, DATETIME_FORMAT)
            start_date = trace_start_time.date()
            if start_date not in self.hist_att[route_id]:
                self.hist_att[route_id][start_date] = np.zeros(MAX_TIME_SIZE)

            if start_date < self.start_date:
                self.start_date = start_date
            elif start_date > self.end_date:
                self.end_date = start_date

            att = float(line[-1])
            time_window_index = time_to_index(trace_start_time)
            self.hist_att[route_id][start_date][time_window_index] = att

        self.routes = sorted(self.hist_att.keys())


    def view_data_of_date(self, day):
        if day < self.start_date or day > self.end_date:
            print 'Day', day, 'out of range.'
            return
        num_route = len(self.routes)
        x = np.array(range(MAX_TIME_SIZE))
        lines = [] # np.array((num_route, MAX_TIME_SIZE))
        fig, ax = plt.subplots()
        for i in range(num_route):
            route_id = self.routes[i]
            if day not in self.hist_att[route_id]:
                lines.append(ax.plot(x, np.zeros(MAX_TIME_SIZE), '-', label=route_id))
            else:
                lines.append(ax.plot(x, np.array(self.hist_att[route_id][day]), '-', label=route_id))
        ax.legend(loc='upper right')
        plt.show()

    
    def view_data_of_dates(self, day, day_num):
        num_route = len(self.routes)
        x = np.array(range(MAX_TIME_SIZE * day_num))
        lines = []
        fig, ax = plt.subplots()
        for i in range(num_route):
            route_id = self.routes[i]
            y = []
            for d in range(day_num):
                cur_day = day + timedelta(days=d)
                if cur_day not in self.hist_att[route_id]:
                    y.extend(np.zeros(MAX_TIME_SIZE))
                else:
                    y.extend(self.hist_att[route_id][cur_day])
            lines.append(ax.plot(x, np.array(y), '-', label=route_id))
        ax.legend(loc='upper right')
        plt.show()


    def view_route_data_of_date(self, route_id, day, smooth=False, origin=False):
        if route_id not in self.hist_att:
            print 'Route', route_id, 'not in data.'
            return
        if day not in self.hist_att[route_id]:
            print 'Data of day', day, 'not in data.'
            return
        fig, ax = plt.subplots()
        x = np.array(range(MAX_TIME_SIZE))
        y = []
        y.extend(self.hist_att[route_id][day])
        if smooth:
            print 'Data smoothing...'
            if origin:
                line_tmp = ax.plot(x, np.array(y), '-', label=route_id+'_origin')
            # tck = interpolate.splrep(x, y, k=3, s=2000)
            # y = interpolate.splev(x, tck, der=0)
            # cutoff = 500
            # fs = 5000
            # y = butter_lowpass_filtfilt(y, cutoff, fs)
            y = my_att_interpolation(self.hist_att[route_id][day])
        label=route_id
        if origin:
            label = label + '_smooth'
        line = ax.plot(x, np.array(y), '-', label=label)
        ax.legend(loc='upper right')
        plt.show()


    def view_route_data_of_dates(self, route_id, day, num_day, smooth=False, origin=False):
        if route_id not in self.hist_att:
            print 'Route', route_id, 'not in data.'
            return
        if day not in self.hist_att[route_id]:
            print 'Data of day', day, 'not in data.'
            return
        fig, ax = plt.subplots()
        x = np.array(range(MAX_TIME_SIZE * num_day))
        y = []
        y_ori = []
        for d in range(num_day):
            cur_day = day + timedelta(days=d)
            if cur_day not in self.hist_att[route_id]:
                print 'Day', cur_day, 'out of range. Ignoring...'
                y.extend(np.zeros(MAX_TIME_SIZE))
                y_ori.extend(np.zeros(MAX_TIME_SIZE))
                continue
            else:
                if smooth:
                    if origin:
                        y_ori.extend(self.hist_att[route_id][cur_day])
                    tmp = my_att_interpolation(self.hist_att[route_id][cur_day])
                    y.extend(tmp)
                else:
                    y.extend(self.hist_att[route_id][cur_day])
        
        line = ax.plot(x, np.array(y), '-', label=route_id)
        if origin:
            line_ori = ax.plot(x, np.array(y_ori), ':', label=route_id+'_ori')
        ax.legend(loc='upper right')
        plt.show()


class vol_viewer(viewer):
    def __init__(self, in_file, contextDir='training_local', file_suffix='.csv'):
        super(vol_viewer, self).__init__(in_file, contextDir, file_suffix)
        self.hist_vol = {}
        self.toll_dirs = []

    def load_training_file(self):
        hist_vol_file = avgVolume('/'.join([dataDir, self.contextDir, self.in_file]))

        fr = open(hist_vol_file, 'r')
        fr.readline()

        lines = fr.readlines()
        for i in xrange(len(lines)):
            line = lines[i].replace('"', '').split(',')
            tollgate_id = line[0]
            direction = line[3]
            tolldir = tollgate_id + '-' + direction
            if tolldir not in self.hist_vol:
                self.hist_vol[tolldir] = {}
            
            start_time = datetime.strptime(line[1][1:], DATETIME_FORMAT)
            start_date = start_time.date()
            if start_date not in self.hist_vol[tolldir]:
                self.hist_vol[tolldir][start_date] = np.zeros(MAX_TIME_SIZE)
            
            if start_date < self.start_date:
                self.start_date = start_date
            elif start_date > self.end_date:
                self.end_date = start_date
            
            vol = float(line[-1])
            time_window_index = time_to_index(start_time)
            self.hist_vol[tolldir][start_date][time_window_index] = vol
        
        self.toll_dirs = sorted(self.hist_vol.keys())

    def view_data_of_date(self, day):
        if day < self.start_date or day > self.end_date:
            print 'Day', day, 'out of range.'
            return
        num_toll = len(self.toll_dirs)
        x = np.array(range(MAX_TIME_SIZE))
        lines = []
        fig, ax = plt.subplots()
        for i in range(num_toll):
            toll_dir = self.toll_dirs[i]
            if day not in self.hist_vol[toll_dir]:
                lines.append(ax.plot(x, np.zeros(MAX_TIME_SIZE), '-', label=toll_dir))
            else:
                lines.append(ax.plot(x, np.array(self.hist_vol[toll_dir][day]), '-', label=toll_dir))
        ax.legend(loc='upper right')
        plt.show()
        

    def view_data_of_dates(self, day, day_num):
        if day < self.start_date or day > self.end_date:
            print 'Warning! Date out of range', day
            return
        num_toll = len(self.toll_dirs)
        x = np.array(range(MAX_TIME_SIZE * day_num))
        lines = []
        fig, ax = plt.subplots()
        for i in range(num_toll):
            toll_dir = self.toll_dirs[i]
            y = []
            for d in range(day_num):
                cur_day = day + timedelta(days=d)
                if cur_day not in self.hist_vol[toll_dir]:
                    y.extend(np.zeros(MAX_TIME_SIZE))
                else:
                    y.extend(self.hist_vol[toll_dir][cur_day])
            # end for loop
            lines.append(ax.plot(x, np.array(y), '-', label=toll_dir))
        ax.legend(loc='upper right')
        plt.show()


    def view_tolldir_data_of_date(self, tolldir, day, smooth=False, origin=False):
        if tolldir not in self.hist_vol:
            print 'Tollgate-direction', tolldir, 'not in history data.'
            return
        if day < self.start_date or day > self.end_date:
            print 'Day out of range.', day
            return
        fig, ax = plt.subplots()
        x = np.array(range(MAX_TIME_SIZE))
        y = []
        y.extend(self.hist_vol[tolldir][day])
        if smooth:
            print 'Data smoothing...'
            if origin:
                line_ori = ax.plot(x, np.array(y), ':', label=tolldir+'_ori')
            y = my_vol_smoothing(self.hist_vol[tolldir][day])
        label=tolldir
        if origin:
            label += '_smo'
        line = ax.plot(x, np.array(y), '-', label=label)
        ax.legend(loc='upper right')
        plt.show()

    
    def view_tolldir_data_of_dates(self, tolldir, day, day_num, smooth=False, origin=False):
        if tolldir not in self.hist_vol:
            print 'Warning! Tollgate direction', tolldir, 'not in history data.'
            return
        if day < self.start_date or day > self.end_date:
            print 'Day', day, 'out of range.'
            return
        fig, ax = plt.subplots()
        x = np.array(range(MAX_TIME_SIZE * day_num))
        y = []
        y_ori = []
        for d in range(day_num):
            cur_day = day + timedelta(days=d)
            if cur_day not in self.hist_vol[tolldir]:
                print 'Day', cur_day, 'out of range. Ignoring...'
                y.extend(np.zeros(MAX_TIME_SIZE))
                continue
            else:
                if smooth:
                    if origin:
                        y_ori.extend(self.hist_vol[tolldir][cur_day])
                    tmp = my_vol_smoothing(self.hist_vol[tolldir][cur_day])
                    y.extend(tmp)
                else:
                    y.extend(self.hist_vol[cur_day])
        # end loop
        line = ax.plot(x, np.array(y), '-', label=tolldir)
        if origin:
            line_ori = ax.plot(x, np.array(y_ori), ':', label=tolldir+'_ori')
        ax.legend(loc='upper right')
        plt.show()


def get_file_name(rela_path, in_file, contextDir, file_suffix='csv'):
    file_path = '/'.join([rela_path, contextDir, in_file+file_suffix])
    assert os.path.exists(file_path)
    return file_path


def butter_lowpass(cutoff, fs, order=5):
    '''
    used in butter_lowpass_filtfilt
    '''
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def butter_lowpass_filtfilt(data, cutoff, fs, order=5):
    '''
    used to do data smoothing, but not suitable for att and vol smoothing
    '''
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y


def my_att_interpolation(route_day_att):
    '''
    replace missing value (denoted by 0) with prev and next value average
    '''
    assert len(route_day_att) == MAX_TIME_SIZE
    y = np.zeros(MAX_TIME_SIZE)
    prev_att = 0.0
    for i in range(MAX_TIME_SIZE):
        if route_day_att[i] < 1e-3:
            # find later att
            ii = i + 1
            next_att = 0.0
            while ii < MAX_TIME_SIZE and route_day_att[ii] < 1e-3:
                ii += 1
            if ii < MAX_TIME_SIZE:
                next_att = route_day_att[ii]
                k = ii - i + 1
                # 1st of k divide point
                route_day_att[i] = ((k - 1)*prev_att + next_att) / k
            else:
                route_day_att[i] = prev_att
        prev_att = y[i] = route_day_att[i]
    return y


def my_vol_smoothing(tolldir_day_vol):
    return tolldir_day_vol


def main():
    day = date(year=2016, month=10, day=1)
    
    viewer_a = att_viewer('trajectories(table 5)_local', contextDir='training_local')
    viewer_a.load_training_file()
    viewer_a.view_data_of_date(day)
    viewer_a.view_data_of_dates(day, 3)
    viewer_a.view_route_data_of_date('C-3', day, smooth=True, origin=True)
    viewer_a.view_route_data_of_dates('C-3', day, 3, smooth=True, origin=True)

    viewer_b = vol_viewer('volume(table 6)_local', contextDir='training_local')
    viewer_b.load_training_file()
    viewer_b.view_data_of_date(day)
    viewer_b.view_data_of_dates(day, 3)
    viewer_b.view_tolldir_data_of_date('1-1', day, smooth=True, origin=True)
    viewer_b.view_tolldir_data_of_dates('1-1', day, 3, smooth=True, origin=True)


if __name__ == '__main__':
    main()
