# -*- coding: utf-8 -*-
#!/usr/bin/env python

'''
avg travel time predictor
'''

import os
from datetime import datetime, date, time, timedelta
import numpy as np
from aggregate_travel_time import avgTravelTime
from visual import my_att_interpolation
from utils import index_to_time, time_to_index, pred_idx, MAX_TIME_INDEX, DATETIME_FORMAT

file_suffix = '.csv'

class att_predictor(object):
    def __init__(self, data_dir, context_dir, raw_file, result_dir):
        self.data_dir = data_dir
        self.context_dir = context_dir
        self.raw_file = raw_file
        self.result_dir = result_dir
        self.hist_att = dict() # hist avg travel time of every route, date and time window
        self.hist_avg = dict() # hist avg travel time of every route, time window
        self.test_days = dict()
        self.test_att = dict()
    
    def process_raw_file(self):
        '''
        preprocess raw data file
        '''
        print 'preprocess raw data file'
        raw_file_path = '/'.join([self.data_dir, self.context_dir, self.raw_file])
        hist_att_f = avgTravelTime(raw_file_path)
        return hist_att_f
    
    def process_hist_file(self, hist_att_f):
        '''
        save data according to route, date and time
        '''
        print 'save data according to route, date and time...'
        with open(hist_att_f, 'r') as fr:
            fr.readline()
            for _line in fr:
                line = _line.replace('"', '').split(',')
                intersection_id = line[0]
                tollgate_id = line[1]

                route_id = intersection_id + '-' + tollgate_id
                if not route_id in self.hist_att:
                    self.hist_att[route_id] = {}
                
                trace_start_time = line[2]
                trace_start_time = datetime.strptime(trace_start_time, "%Y-%m-%d %H:%M:%S")

                trace_date = trace_start_time.date()
                time_index = time_to_index(trace_start_time)

                if not trace_date in self.hist_att[route_id]:
                    self.hist_att[route_id][trace_date] = [0 for i in range(MAX_TIME_INDEX)]
                
                tt = float(line[-1]) # history travel time
                self.hist_att[route_id][trace_date][time_index] = tt
        return

    def smooth_hist_att_data(self):
        '''
        smooth history att data
        '''
        print 'smooth history att data'
        for route_id in self.hist_att.keys():
            for dt in self.hist_att[route_id]:
                self.hist_att[route_id][dt] = my_att_interpolation(self.hist_att[route_id][dt])
        return

    def calc_hist_att_of_win(self):
        '''
        calc history att of every time window
        '''
        print 'calc history att of every time window...'
        for route_id in self.hist_att.keys():
            self.hist_avg[route_id] = [0.0 for i in range(MAX_TIME_INDEX)]
        for route_id in self.hist_att.keys():
            tmp = np.zeros((MAX_TIME_INDEX, 2))
            for dt in self.hist_att[route_id]:
                for i in range(MAX_TIME_INDEX):
                    tmp[i] += [self.hist_att[route_id][dt][i], 1]
            for i in range(MAX_TIME_INDEX):
                try:
                    self.hist_avg[route_id][i] = float(tmp[i][0] / tmp[i][1])
                except ZeroDivisionError as zde:
                    self.hist_avg[route_id][i] = 0.0
                    print 'Warning! zero value of hist att data.'        
        return
    
    def write_hist_att(self, out_file='hist_att'):
        '''
        write all history att data to file
        '''
        out_file = '/'.join([self.result_dir, out_file+file_suffix])
        if not os.path.exists(self.result_dir):
            os.mkdir(self.result_dir)
        print 'Write avg travel time data to file:', out_file
        fw = open(out_file, 'w')
        outline = ','.join(['intersection_id','tollgate_id','time_window','avg_travel_time']) + '\n'
        fw.writelines(outline)
        for route_id in sorted(self.hist_att.keys()):
            [intersection_id, tollgate_id] = route_id.split('-')
            for dt in self.hist_att[route_id]: # date
                for ti in range(MAX_TIME_INDEX):
                    day_time = index_to_time(ti)
                    window_time = datetime(year=dt.year, month=dt.month, 
                        day=dt.day, hour=day_time.hour, minute=day_time.minute)
                    att = str(self.hist_att[route_id][dt][ti])
                    outline = ','.join([intersection_id, tollgate_id,
                        window_time.strftime(DATETIME_FORMAT), att]) + '\n'
                    fw.writelines(outline)
        fw.close()
        return out_file


    def write_hist_avg(self, out_file='hist_avg'):
        '''
        write hist att of time window
        '''
        # path exists ?
        if not os.path.exists(self.result_dir):
            os.mkdir(self.result_dir)
        out_file = '/'.join([self.result_dir , out_file+'.csv'])
        print 'Write hist avg to file:', out_file
        fw = open(out_file, 'w')
        outline = ','.join(['intersection_id','tollgate_id','time_window','avg_travel_time']) + '\n'
        fw.writelines([outline])
        for route_id in sorted(self.hist_avg.keys()):
            for ti in range(MAX_TIME_INDEX):
                # B,3,2017-10-01 00:00:00,102.09
                [intersection_id, tollgate_id] = route_id.split('-')
                avg_att = str(self.hist_avg[route_id][ti])

                outline = ','.join([intersection_id, tollgate_id, 
                    index_to_time(ti).strftime("%Y-%m-%d %H:%M:%S"), avg_att]) + '\n'
                fw.writelines(outline)
        fw.close()
        return out_file

    def load_hist_avg(self, in_file):
        '''
        load hist avg travel time from file
        '''
        self.hist_avg.clear()

        print 'load hist avg travel time from file:', in_file
        fr = open(in_file, 'r')
        fr.readline()
        hist_lines = fr.readlines()
        for i in range(len(hist_lines)):
            line = hist_lines[i].split(',')
            intersection_id = line[0]
            tollgate_id = line[1]
            route_id = intersection_id + '-' + tollgate_id
            if route_id not in self.hist_avg:
                self.hist_avg[route_id] = {}
            
            start_time = datetime.strptime(line[2], '%Y-%m-%d %H:%M:%S')
            time_index = time_to_index(start_time)
            if not time_index in self.hist_att[route_id]:
                self.hist_avg[route_id][time_index] = 0.0

            att = float(line[3])
            self.hist_avg[route_id][time_index] = att
        return
    
    def pre_process_testing_data(self, data_dir, context_dir, in_file):
        test_file_path = '/'.join([data_dir, context_dir, in_file])
        out_file_name = avgTravelTime(test_file_path)
        return out_file_name

    def read_testing_data(self, data_dir, context_dir, in_file):
        '''
        read testing data from file
        '''
        test_f = self.pre_process_testing_data(data_dir, context_dir, in_file=in_file)
        print 'read testing data from file'
        self.test_att.clear()
        fr = open(test_f, 'r')
        print fr.readline()  # skip the header
        window_data = fr.readlines()
        fr.close()
        for i in xrange(len(window_data)):
            line = window_data[i].replace('"', '').split(',')
            intersection_id = line[0]
            tollgate_id = line[1]
            route_id = intersection_id + '-' + tollgate_id
            if not route_id in self.test_att:
                self.test_att[route_id] = dict()

            window_start_time = line[2]
            window_start_time = datetime.strptime(window_start_time, "%Y-%m-%d %H:%M:%S")
            ti = time_to_index(window_start_time)
            
            dt = window_start_time.date()
            if not dt in self.test_days:
                self.test_days[dt] = 0
            
            if not dt in self.test_att[route_id]:
                self.test_att[route_id][dt] = [0 for i in range(MAX_TIME_INDEX)]
            att = float(line[3])
            self.test_att[route_id][dt][ti] = att

        return
    
    def do_prediction(self, pred_idx, out_file):
        '''
        do prediction of dates in self.test_days
        '''
        out_file = '/'.join([self.result_dir, out_file+file_suffix])
        print 'Do prediction, write to file:', out_file
        fw = open(out_file, 'w')
        outline = '"intersection_id","tollgate_id","time_window","avg_travel_time"' + '\n'
        fw.writelines(outline)
        for route_id in sorted(self.test_att.keys()):
            [intersection_id, tollgate_id] = route_id.split('-')
            for dt in sorted(self.test_days.keys()):
                for idx in pred_idx:
                    tm = index_to_time(idx)
                    dttm = datetime(year=dt.year, month=dt.month, day=dt.day, 
                        hour=tm.hour, minute=tm.minute)
                    endtm = dttm + timedelta(minutes=20)

                    pred_att = round(self.hist_avg[route_id][idx], 3)
                    
                    outline = ','.join([intersection_id, tollgate_id, 
                        '"[' + str(dttm) + ',' + str(endtm) + ')"', 
                        str(pred_att) ]) + '\n'
                    fw.writelines(outline)
        fw.close()
        return out_file
            

def test_att_predictor():
    ap = att_predictor(data_dir='dataSets', context_dir='training',
        raw_file='trajectories(table 5)_training', result_dir='../results')
    hist_att_f = ap.process_raw_file()
    ap.process_hist_file(hist_att_f)
    ap.smooth_hist_att_data()
    ap.calc_hist_att_of_win()
    hist_avg_f = ap.write_hist_avg('hist_att')

    ap.read_testing_data(data_dir='dataSets', context_dir='testing_phase1', in_file='trajectories(table 5)_test1')
    out_file = ap.do_prediction(pred_idx, 'pred_avg_travel_time_test')
    print 'Prediction written to', out_file

def main():
    test_att_predictor()

if __name__ == '__main__':
    main()
