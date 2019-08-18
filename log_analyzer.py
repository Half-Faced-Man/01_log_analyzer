    #!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';


config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "SUCCESSFUL_PERCENT": 0.95
}

from collections import namedtuple, defaultdict
from datetime import datetime
import argparse
import os
import json
import logging
import re
import gzip
import statistics


last_log = namedtuple('last_log', ['date', 'path'])


def parse_path():
    parser = argparse.ArgumentParser()  # argument_default='./log_analyzer_config'
    parser.add_argument('--config_path', default='./log_analyzer_config')
    args = parser.parse_args()
    # print(type(args.config_path))
    # print(args.config_path)
    return args.config_path


def read_log_analyzer_config(path):
    if not os.path.exists(path):
        raise FileNotFoundError('No file: {}'.format(path))

    with open(path) as log_analyzer_config:
        return json.load(log_analyzer_config)


def merge_config(default_config, ext_config):
    default_config.update(ext_config)
    return default_config


def init_logging(config):
    loging_path = config.get('LOGGING_FILE')

    logging.basicConfig(
        format='[%(asctime)s] %(levelname).1s %(message)s',
        level=logging.DEBUG,
        datefmt='%Y.%m.%d %H:%M:%S',
        filename=loging_path
    )


def find_last_file(config):
    pattern = re.compile(r'^nginx-access-ui\.log-(?P<date>\d{8})(\.gz)?$')
    root_dir = config.get("LOG_DIR")
    last_file = None
    date_last_file = None
    for path, dirs, files in os.walk(root_dir):
        for filename in files:
            match_file = re.match(pattern, filename)
            date = match_file.group(1)
            date = datetime.strptime(date, "%Y%m%d")

            if not last_file or date_last_file < date:
                last_file = os.path.join(path, filename)
                date_last_file = date

    logging.info('Found last log. Date: {}, Name: {}'.format(date_last_file, last_file))
    return last_log(date_last_file, last_file)
    #return open('./log/nginx-access-ui.log-20170630')


def report(date, cfg):
    date = datetime.strftime(date, '%Y.%m.%d')
    report_path = os.path.join(cfg.get('REPORT_DIR'), 'report_{}'.format(date))
    if os.path.exists(report_path):
        FileExistsError('report at {} exist'.format(report_path))

    return report_path

def split_line(line):
    try:
        data = line.split(' ')
        #url, request_time = line[7].strip(), float(line[-1].strip())
        return {'url': data[7], 'request_time': data[-1]}
    except Exception:
        logging.debug(f"Error while split line: \n\t {line}")
        return None


def reader_log_file(path, cfg):
    with gzip.open(path, 'rb') if path.endswith('.gz') else open(path) as file:
        lines = [line.rstrip() for line in file]
        count_lines = len(lines)
        succ_count_lines = 0
        for line in lines:
            data = split_line(line)
            #print(type(data))
            if not data:
               continue

            yield data
            succ_count_lines += 1
            #print(succ_count_lines)

        curr_succ_pers = succ_count_lines / count_lines
        print(curr_succ_pers)
        logging.info("successful percent = {}".format(curr_succ_pers))


        #lines = [line.split()  for line in lines]
        #print(lines[0:2])

        if curr_succ_pers < cfg.get('SUCCESSFUL_PERCENT'):
            raise RuntimeError('Too many incorrect data')


def calculate_statistics(lines_gen, cfg):
    full_request_time = 0
    full_url_count = 0
    data = defaultdict(list)
    for i in lines_gen:
        url, req_time = i['url'], float(i['request_time'])
        #print(url)

        data[url].append(req_time)
        full_request_time += req_time
        full_url_count += 1

    stat = []
    for k, v in data.items():
        stat.append({
            'url': k,
            'count': len(v),
            'count_perc': 100 * len(v) / full_url_count,
            'time_sum': sum(v),
            'time_perc': 100 * sum(v) / full_request_time,
            'time_avg': sum(v) / len(v),
            'time_max': max(v),
            'time_med': statistics.median(v)
        })

    sorted_stat = (sorted(stat, key=lambda k: k["time_sum"], reverse=True) )[:cfg['REPORT_SIZE']]

    return json.dumps(sorted_stat)


def write_report(stat, path):
    with open(path, mode='tw', encoding='utf-8') as report:
        report.write(stat)


def main():
    default_config = {
        "REPORT_SIZE": 1000,
        "REPORT_DIR": "./reports",
        "LOG_DIR": "./log",
        "SUCCESSFUL_PERCENT": 0.95,
        "LOGGING_FILE": "./logging_file"
    }

    init_logging(default_config)
    path = parse_path()
    ext_config = read_log_analyzer_config(path)
    config = merge_config(default_config, ext_config)
    #init_logging(config)

    log_file = find_last_file(config)
    report_path = report(log_file.date, config)
    lines = reader_log_file(log_file.path, config)
    stat = calculate_statistics(lines, config)
    write_report(stat, report_path)


if __name__ == "__main__":
    main()