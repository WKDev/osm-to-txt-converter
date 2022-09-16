# 220906 chanhyeokson
# simple & colorful logger

import os
import time

class WKLogger:
    def __init__(self,target=os.path.basename(__file__) , log_path=None, log_level = 'verbose'):
        level = ['verbose','debug','info','warn','err', 'fatal']
        self.target = target
        self.log_path = log_path
        self.COLOR = {'black': '\033[0m', 'red':'\033[31m', 'yellow':'\033[33m','white':'\033[37m','green':'\033[32m', 'none':'\033[0m', 'blue':'\033[34m', 'cyan':'\033[46m'}
        self.log_level = level.index(log_level)

        # print(self.log_level)


    def get_filename(self):
        # 현재 날짜를 받아옵니다.
        curr_time = time.localtime()
        yr = str(curr_time.tm_year)

        # 날짜가 10보다 작은 경우, 앞에 0을 붙여줍니다.
        month = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_mon)
        d = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_mday)
        h = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_hour)
        _min = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_min)
        _sec = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_sec)

        ret = yr + month + d

        return ret

    def get_date_and_time(self):
        # 현재 날짜를 받아옵니다.
        curr_time = time.localtime()
        yr = str(curr_time.tm_year)[2:]

        # 날짜가 10보다 작은 경우, 앞에 0을 붙여줍니다.
        month = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_mon)
        d = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_mday)
        h = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_hour)
        _min = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_min)
        _sec = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_sec)

        ret = yr + month + d + '-' + h + ':' + _min + ':' + _sec

        return ret

    def add_data(self, data):
        if not os.path.isdir(os.path.join(self.log_path)):
            os.mkdir((os.path.join(self.log_path)))
        with open(os.path.join(self.log_path, self.get_filename()+'.txt'), 'a') as f:
            f.write(data + '\n')


    def verbose(self, contents='', c='green', write=True):
        raw_log = '[' + self.get_date_and_time() + ']' + '[' + self.target + '][VERBOSE] ' + str(contents)
        if write:
            self.add_data(data=raw_log)
        if self.log_level <= 0:
            print(raw_log)

    def debug(self, contents='', c='blue', write=True):
        raw_log = '[' + self.get_date_and_time() + ']' + '[' + self.target + '][DEBUG] ' + str(contents)
        colored_log = self.COLOR[c] + raw_log + '\033[0m'
        if write:
            self.add_data(data=raw_log)
        if self.log_level <= 1:
            print(colored_log)

    def info(self, contents='', c='green', write=True):
        raw_log = '[' + self.get_date_and_time() + ']' + '[' + self.target + '][INFO] ' + str(contents)
        colored_log = self.COLOR[c] + raw_log + '\033[0m'
        if write:
            self.add_data(data=raw_log)
        if self.log_level <= 2:
            print(colored_log)

    def warn(self, contents='', c='yellow', write=True):
        raw_log = '['+self.get_date_and_time()+']'+'['+self.target +'][WARN] ' + str(contents)
        colored_log = self.COLOR[c] +raw_log+'\033[0m'
        if write:
            self.add_data(data=raw_log)
        if self.log_level <= 3:
            print(colored_log)

    def err(self, contents='', c='red', write=True):
        raw_log = '['+self.get_date_and_time()+']'+'['+self.target +'][ERROR] ' + str(contents)
        colored_log = self.COLOR[c] + raw_log +'\033[0m'
        if write:
            self.add_data(data=raw_log)
        if self.log_level <= 4:
            print(colored_log)

if __name__ == '__main__':
    lg = WKLogger(log_path='./',)

    lg.verbose('verbose')
    lg.debug('debug')
    lg.info('info')
    lg.warn('warn')
    lg.err('err')

