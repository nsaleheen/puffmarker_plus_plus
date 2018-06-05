# import datetime, time
from typing import List
from datetime import datetime, timedelta
import pytz
import os
import numpy as np
from puffmarker.domain.datapoint import DataPoint
from puffmarker.input.export_streamprocessor import *
from puffmarker.input.import_stream_processor_inputs import load_data, \
    load_data_offset

data_dir = '/home/nsaleheen/data/rice_ema_puffmarker_activity_loc/'
data_dir = '/home/nsaleheen/data/RICE_data/without_raw_data/'

smoking_self_report_file = 'SMOKING+SELF_REPORT+PHONE.csv'
activity_type_file = 'ACTIVITY_TYPE+PHONE.csv'
puffmarker_smoking_epi_cloud_file = 'PUFFMARKER_SMOKING_EPISODE+PHONE.csv'

streamprocessor_puffmarker_smoking_epi_file = 'streamprocessor.puffMarker.smoking.episode.rip.wrist.combine.csv'
streamprocessor_puffmarker_smoking_epi_file = 'org.md2k.streamprocessor+PUFFMARKER_SMOKING_EPISODE+PHONE.csv'
# streamprocessor_puffmarker_smoking_epi_file = 'puffmarker_streamprocessor.csv'

ema_random_file = 'EMA+RANDOM_EMA+PHONE.csv'
ema_smoking_file = 'EMA+SMOKING_EMA+PHONE.csv'
ema_end_of_day_file = 'EMA+END_OF_DAY_EMA+PHONE.csv'
ema_stressed_file = 'EMA+STRESS_EMA+PHONE.csv'

tz = pytz.timezone('US/Central')
print(tz)


# unix time to '2017-11-01 15:52:00'
def unixtime_to_datetime_pre(timestamp):
    timestamp = timestamp / 1000
    dt = datetime.fromtimestamp(timestamp, tz).strftime('%m-%d-%Y %H:%M:%S')
    return dt


def unixtime_to_datetime(timestamp):
    timestamp = timestamp / 1000
    dt = datetime.fromtimestamp(timestamp, tz).strftime('%m/%d %H:%M:%S')
    return dt


# unix time to  '2017-11-01 15:52:00' -> '2017-11-01'
def unixtime_to_date(timestamp):
    dt = unixtime_to_datetime(timestamp)
    return dt.split(' ')[0]


# unix time to  '2017-11-01 15:52:00' -> '15:52:00'
def unixtime_to_time(timestamp):
    dt = unixtime_to_datetime(timestamp)
    return dt.split(' ')[1]


# unix time to '15*52' in minutes
def unixtime_to_timeOfDay(timestamp):
    tm = unixtime_to_time(timestamp)
    toks = tm.split(':')
    h = int(toks[0])
    m = int(toks[1])
    timeOfday = h * 60 + m
    return timeOfday


ut = 1512506705814  # 1386181800

print(unixtime_to_datetime(ut))
print(unixtime_to_date(ut))
print(unixtime_to_time(ut))
print(unixtime_to_timeOfDay(ut))

# timezone = datetime.timezone(datetime.timedelta(milliseconds=offset))
# ts = datetime.datetime.fromtimestamp(ts, timezone)

import json


def get_fileName(cur_dir, file_sufix):
    filenames = [name for name in os.listdir(cur_dir) if
                 name.endswith(file_sufix)]
    # print(file_sufix + ':' + str(filenames))
    if len(filenames) > 0:
        return filenames[0]
    else:
        return None


def get_EMA_data(cur_dir, filename):
    if filename is None:
        return []

    fp = open(cur_dir + filename)
    file_content = fp.read()
    fp.close()

    lines = file_content.splitlines()
    data = []
    for line in lines:
        if len(line) > 1:
            ts, offset, sample = line.split(',', 2)
            # start_time = int(ts)
            start_time = int(float(ts)) / 1000.0
            start_time = datetime.fromtimestamp(start_time, tz)
            offset = int(offset)
            sample = sample[1:-1]
            data.append([start_time, offset, sample])
    return data


# random ema + stressed EMA
# sample = (#smoked, from_time, to_time); eg: "2 hrs - 4 hrs" one cig smoked (1, 2*60*60*1000, 4*60*60*1000)
def get_random_EMA(cur_dir, filename) -> List[DataPoint]:
    emas = get_EMA_data(cur_dir, filename)
    data = []
    for ema in emas:
        d = ema[2]
        jsn_file = json.loads(d)
        status = jsn_file['status']
        # print(d)
        if status == 'COMPLETED':
            is_smoked = jsn_file['question_answers'][39]['response'][0]
            # print(is_smoked, status)
            if is_smoked.lower() == 'yes':
                nSmoked = jsn_file['question_answers'][40]['response'][0]
                if int(nSmoked) == 1:
                    nQI = 41
                else:
                    nQI = 42
                # options: ["0 - 2 hrs", "2 hrs - 4 hrs", "4 hrs - 6 hrs", "6 hrs - 8 hrs", "8 hrs - 10 hrs", "10 hrs - 12 hrs", "More than 12 hrs"]
                howlong_ago = jsn_file['question_answers'][nQI]['response']
                if howlong_ago is None:
                    howlong_ago = jsn_file['question_answers'][nQI+1]['response']

                sample = [int(nSmoked)]
                # print(howlong_ago, nSmoked)
                for hla in howlong_ago:
                    hla = str(hla)
                    if hla in ["More than 12 hrs"]:
                        sample.extend(
                            [12 * 60 * 60 * 1000, 24 * 60 * 60 * 1000])
                        continue
                    st = hla.split('-')[0]
                    et = hla.split('-')[1]
                    st = st.split(' ')[0]
                    st = int(st.strip()) * 60 * 60 * 1000
                    et = et.strip().split(' ')[0]
                    et = int(et.strip()) * 60 * 60 * 1000
                    sample.extend([st, et])

                # print([ema[0], ema[1], nSmoked, howlong_ago, sample])
                # data.append([ema[0], ema[1], int(nSmoked)])
                if len(sample) > 3:
                    print('great than 1 timeslots', len(sample)/2)
                data.append(
                    DataPoint(start_time=ema[0], offset=ema[1], sample=sample))
            else:
                data.append(
                    DataPoint(start_time=ema[0], offset=ema[1], sample=[0]))
    return data


def get_smoking_self_report(cur_dir, filename) -> List[DataPoint]:
    emas = get_EMA_data(cur_dir, filename)
    data = []
    for ema in emas:
        d = ema[2]
        jsn_file = json.loads(d)
        status = jsn_file['message']
        if 'YES' in status:
            #             print(status)
            data.append(DataPoint(start_time=ema[0], offset=ema[1], sample=1))
            # print(ema)
            # data.append([ema[0], ema[1], status])
    return data


cur_dir = data_dir + '2007/'


# emas = get_smoking_self_report(cur_dir, get_fileName(cur_dir, smoking_self_report_file))
# print(emas)

# emas = get_smoking_EMA(cur_dir, get_fileName(cur_dir, ema_smoking_file))
# print(emas)
# emas = get_random_EMA(cur_dir, get_fileName(cur_dir, ema_stressed_file))
# print(emas)
# emas = get_random_EMA(cur_dir, get_fileName(cur_dir, ema_random_file))
# print(emas)


def get_RICE_PILOT_EMAs_New(pid):
    cur_dir = data_dir + pid + '/'

    # smoking_epis = load_data(cur_dir + get_fileName(cur_dir, streamprocessor_puffmarker_smoking_epi_file))
    smoking_epi_filename = get_fileName(cur_dir,streamprocessor_puffmarker_smoking_epi_file)

    if smoking_epi_filename is not None:
        smoking_epis = load_data_offset(cur_dir + smoking_epi_filename)
    else:
        smoking_epis = []

    smoking_selfreport = get_smoking_self_report(cur_dir, get_fileName(cur_dir,
                                                                       smoking_self_report_file))

    smoking_emas = get_random_EMA(cur_dir,
                                  get_fileName(cur_dir, ema_smoking_file))
    random_emas = get_random_EMA(cur_dir,
                                 get_fileName(cur_dir, ema_random_file))
    stressed_emas = get_random_EMA(cur_dir,
                                   get_fileName(cur_dir, ema_stressed_file))

    # all_emas = np.array(smoking_emas) + np.array(random_emas) + np.array(stressed_emas)
    all_emas = smoking_emas + random_emas + stressed_emas
    all_emas.sort(key=lambda x: x.start_time)

    sup_sr = [0] * len(smoking_epis)
    sup_time_ema = [0] * len(smoking_epis)
    sup_ema = [0] * len(smoking_epis)

    for i, epi in enumerate(smoking_epis):
        for sr in smoking_selfreport:
            time_diff = (sr.start_time - epi.start_time).total_seconds()
            if (time_diff > -1800 and time_diff < 1800):
                sup_sr[i] = 1
                break
        for re in all_emas:
            if len(re.sample) <= 1:
                continue
            st = re.start_time - timedelta(milliseconds=re.sample[2])
            et = re.start_time - timedelta(milliseconds=re.sample[1])
            if (epi.start_time >= st and epi.start_time <= et):
                sup_time_ema[i] = 1
                break
    for i, ema in enumerate(all_emas):
        if len(ema.sample) <= 1:
            continue
        if i > 0:
            for j, epi in enumerate(smoking_epis):
                if epi.start_time > all_emas[i-1].start_time and epi.start_time < ema.start_time:
                    sup_ema[j] = 1

    sup = [sup_sr[i] * 100 + sup_time_ema[i]*10 + sup_ema[i] for i in
           range(len(sup_time_ema))]

    support_filename = 'RICE_smoking_episodes_with_support.csv'
    # append_to_file(support_filename, 'pid,datetime,unix_timestamp,EMA_support_with_time,EMA_support')
    for i, dp in enumerate(smoking_epis):
        txt = pid + ',' + str(dp.start_time) + ',' + str(dp.start_time.timestamp()) + ',' + str(sup_time_ema[i]) + ',' + str(sup_ema[i])
        print(txt)
        append_to_file(support_filename, txt)


    non_sup = len([v for v in sup if v == 0])
    print(
        'Supported : Not supported = ' + str(len(sup) - non_sup) + ' : ' + str(
            non_sup))

def get_RICE_PILOT_EMAs(pid):
    cur_dir = data_dir + pid + '/'

    # smoking_epis = load_data(cur_dir + get_fileName(cur_dir, streamprocessor_puffmarker_smoking_epi_file))
    smoking_epi_filename = get_fileName(cur_dir,streamprocessor_puffmarker_smoking_epi_file)

    if smoking_epi_filename is not None:
        smoking_epis = load_data_offset(cur_dir + smoking_epi_filename)
    else:
        smoking_epis = []

    smoking_selfreport = get_smoking_self_report(cur_dir, get_fileName(cur_dir,
                                                                       smoking_self_report_file))

    smoking_emas = get_random_EMA(cur_dir,
                                  get_fileName(cur_dir, ema_smoking_file))
    random_emas = get_random_EMA(cur_dir,
                                 get_fileName(cur_dir, ema_random_file))
    stressed_emas = get_random_EMA(cur_dir,
                                   get_fileName(cur_dir, ema_stressed_file))

    sup_sr = [0] * len(smoking_epis)
    sup_cr = [0] * len(smoking_epis)
    sup_ema = [0] * len(smoking_epis)

    for i, epi in enumerate(smoking_epis):
        for sr in smoking_selfreport:
            time_diff = (sr.start_time - epi.start_time).total_seconds()
            if (time_diff > -1800 and time_diff < 1800):
                sup_sr[i] = 1
                break
        for sr in smoking_emas:
            if len(sr.sample) <= 1:
                continue
            time_diff = (sr.start_time - epi.start_time).total_seconds()
            if (time_diff > -600 and time_diff < 1800):
                sup_cr[i] = 1
                break

        for re in smoking_emas:
            if len(re.sample) <= 1:
                continue
            st = re.start_time - timedelta(milliseconds=re.sample[2])
            et = re.start_time - timedelta(milliseconds=re.sample[1])
            if (epi.start_time >= st and epi.start_time <= et):
                sup_ema[i] = 1
                break
        for re in random_emas:
            if len(re.sample) <= 1:
                continue
            st = re.start_time - timedelta(milliseconds=re.sample[2])
            et = re.start_time - timedelta(milliseconds=re.sample[1])
            if (epi.start_time >= st and epi.start_time <= et):
                sup_ema[i] = 1
                break
        for re in stressed_emas:
            if len(re.sample) <= 1:
                continue
            st = re.start_time - timedelta(milliseconds=re.sample[2])
            et = re.start_time - timedelta(milliseconds=re.sample[1])
            if (epi.start_time >= st and epi.start_time <= et):
                sup_ema[i] = 1
                break

    sup = [sup_sr[i] * 100 + sup_cr[i] * 10 + sup_ema[i] for i in
           range(len(sup_ema))]

    print('se=' + str(len(smoking_epis)) + ' : sup sr = ' + str(
        sum(sup_sr)) + "/" + str(
        len(smoking_selfreport)) + ' : sup cr = ' + str(
        sum(sup_cr)) + "/" + str(len(smoking_emas)) + ' : sup ema = ' + str(
        sum(sup_ema)) + "/" + str(len(stressed_emas) + len(smoking_emas) + len(random_emas)))

    non_sup = len([v for v in sup if v == 0])
    print(
        'Supported : Not supported = ' + str(len(sup) - non_sup) + ' : ' + str(
            non_sup))
    # print(sup)
    # print(len(smoking_selfreport))
    # print(len(smoking_emas))
    # print(len(random_emas))
    # print(len(stressed_emas))

    # print(smoking_epis)
    # print(smoking_emas)
    # print(smoking_selfreport)
    # print(random_emas)
    # print(stressed_emas)
    #


pid_all = ["3001", "3002", "3003",
           "3004", "3005", "3006", "3007", "3008", "3010", "3013", "3014",
           "3015", "3016", "3017", "3018", "3022", "3023", "3024", "3025",
           "3026", "3028", "3029", "3030", "3031", "3032", "3033", "3034",
           "3035", "3036", "3037", "3038", "3039", "3040", "3041", "3042",
           "3043", "3044", "3045", "3046", "3047", "3048", "3049", "3050",
           "3051", "3052", "3053", "3054", "3055"]

# , "2008", "2010", "2011", "2012"
pids = ["2006", "2007", "2009", "2013", "2014", "2015", "2016", "2017"]
support_filename = 'RICE_smoking_episodes_with_support.csv'
append_to_file(support_filename, 'pid,datetime,unix_timestamp,EMA_support_with_time,EMA_support')
for pid in pid_all:
    print('-----------' + pid + '---------------------------')
    # get_RICE_PILOT_EMAs(pid)
    get_RICE_PILOT_EMAs_New(pid)

# get_RICE_PILOT_EMAs('3044')
#
# -----------2006---------------------------
# se=25 : sup sr = 19 : sup cr = 18 : sup ema = 4
# Supported : Not supported = 21 : 4
# -----------2007---------------------------
# se=6 : sup sr = 5 : sup cr = 6 : sup ema = 0
# Supported : Not supported = 6 : 0
# -----------2009---------------------------
# se=32 : sup sr = 14 : sup cr = 30 : sup ema = 10
# Supported : Not supported = 30 : 2
# -----------2013---------------------------
# se=113 : sup sr = 72 : sup cr = 108 : sup ema = 49
# Supported : Not supported = 113 : 0
# -----------2014---------------------------
# se=44 : sup sr = 6 : sup cr = 43 : sup ema = 23
# Supported : Not supported = 44 : 0
# -----------2015---------------------------
# se=0 : sup sr = 0 : sup cr = 0 : sup ema = 0
# Supported : Not supported = 0 : 0
# -----------2016---------------------------
# se=0 : sup sr = 0 : sup cr = 0 : sup ema = 0
# Supported : Not supported = 0 : 0
# -----------2017---------------------------
# se=8 : sup sr = 0 : sup cr = 5 : sup ema = 2
# Supported : Not supported = 5 : 3
