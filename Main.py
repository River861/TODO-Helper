import kashgari
import Predict
import ThingsDividing
import TextPreprocessing
import TimeParsing
import pprint
import arrow
import re
from configparser import ConfigParser


class TimeNer():

    def __init__(self, path):
        self.__model = kashgari.utils.load_model(path)


    def __cut(self, text, tag_list):
        '''根据tag把时间和事务分开，可以认为时间总在事务前说
        '''
        tag_list.append('B-TIME')
        text += ' '
        time_text_list = list()
        things_text_list = list()
        time_text = ''
        things_text = ''
        for index, tag in enumerate(tag_list):
            if tag == 'B-TIME':
                if time_text != '' and things_text != '':
                    time_text_list.append(time_text)
                    things_text_list.append(things_text)
                time_text = text[index]
                things_text = ''
            elif tag == 'I-TIME':
                time_text += text[index]
            else:
                things_text += text[index]
        return time_text_list, things_text_list


    def get_schedule(self, text):
        # 进入模型
        tag_list = Predict.predict(self.__model, text.strip())
        # 分离时间语句
        time_text_list, things_text_list = self.__cut(text, tag_list[0])
        # print(time_text_list, things_text_list)

        scheduler_table = dict()
        doubt_table = dict()
        baseTime = arrow.now() 
        for time_text, things_text in zip(time_text_list, things_text_list):
            # 换数字、标点、消歧义
            time_text = TextPreprocessing.switch_after_cut(time_text)
            # 生成任务表
            action_list = ThingsDividing.get_action_list(things_text)

            # 处理时间段类型
            rule = "(.+)[至到~](.+)"
            pattern = re.compile(rule)
            match = pattern.search(time_text)
            if match is not None:
                start_time = match.group(1)
                end_time = match.group(2)
                baseTime, Y, M, D, h, m = TimeParsing.parse(start_time, baseTime)
                if baseTime is None: # 正则识别失败
                    baseTime = arrow.get(Y, M, D, h, m)
                    doubt_table[f'{start_time} ~ {end_time}'] = action_list
                else:
                    if h is None and m is None:
                        start_time = "%d/%02d/%02d" % (Y, M, D)
                    else:
                        start_time = "%d/%02d/%02d %02d:%02d" % (Y, M, D, h, m)

                    baseTime, Y, M, D, h, m = TimeParsing.parse(end_time, baseTime)
                    if baseTime is None: # 正则识别失败
                        baseTime = arrow.get(Y, M, D, h, m)
                        doubt_table[f'{start_time} ~ {end_time}'] = action_list
                    else:
                        if h is None and m is None:
                            end_time = "%d/%02d/%02d" % (Y, M, D)
                        else:
                            end_time = "%d/%02d/%02d %02d:%02d" % (Y, M, D, h, m)
                        scheduler_table[f'{start_time} ~ {end_time}'] = action_list
                
            else:
                # 解析时间(baseTime要更新)
                baseTime, Y, M, D, h, m = TimeParsing.parse(time_text, baseTime)
                if baseTime is None: # 正则识别失败
                    baseTime = arrow.get(Y, M, D, h, m)
                    doubt_table[time_text] = action_list
                else:
                    if h is None and m is None:
                        do_time = "%d/%02d/%02d" % (Y, M, D)
                    else:
                        do_time = "%d/%02d/%02d %02d:%02d" % (Y, M, D, h, m)
                    scheduler_table[do_time] = action_list

        return scheduler_table, doubt_table




if __name__ == '__main__':
    import logging
    import jieba
    import arrow
    jieba.setLogLevel(logging.INFO)
    cf = ConfigParser()
    cf.read('./config.ini')
    model_path = cf.get('global', 'model_dir')

    model = TimeNer(model_path)
    curTime = arrow.now()
    while True:
        text = input('>输入:\n')
        print(f'\n>当前时间:\n {"%d/%02d/%02d %02d:%02d" % (curTime.year, curTime.month, curTime.day, curTime.hour, curTime.minute)}')
        scheduler_table = model.get_schedule(text)
        print('\n>输出任务时间表:')
        pprint.pprint(scheduler_table[0])
        print('\n')
