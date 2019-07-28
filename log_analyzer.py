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

from collections import namedtuple
from datetime import datetime
import argparse
import os
import json


def parse_path():
    parser = argparse.ArgumentParser()  # argument_default='./log_analyzer_config'
    parser.add_argument('--config_path')
    args = parser.parse_args()
    # print(type(args.config_path))
    print(args.config_path)
    return args.config_path


def read_log_analyzer_config(path):
    if not os.path.exists(path):
        raise FileNotFoundError('No file: {}'.format(path))

    with open(path) as log_analyzer_config:
        return json.load(log_analyzer_config)


def merge_config(default_config, ext_config):
    default_config.update(ext_config)
    return default_config


def find_last_file(path):
    return open('./log/nginx-access-ui.log-20170630')


def read_line():
    pass


def read_log():
    pass


def main():
    default_config = {
        "REPORT_SIZE": 1000,
        "REPORT_DIR": "./reports",
        "LOG_DIR": "./log",
        "SUCCESSFUL_PERCENT": 0.95
    }

    path = parse_path()
    ext_config = read_log_analyzer_config(path)
    config = merge_config(default_config, ext_config)
    log_file = find_last_file(config.get("LOG_DIR"))

    # потом сделать более красивую функцию

    lines = [line.rstrip() for line in log_file]
    lines = [line.split() for line in lines]

    print(lines[0])



if __name__ == "__main__":
    main()
