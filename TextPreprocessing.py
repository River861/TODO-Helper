from Dictionary import word2num, holiday2date, punc_lower, solar2data
import arrow
import re

# def switch_before_predict(text):
#     '''[换节日] 在进入神经网络之前就转换
#     '''
#     for key, val in holiday2date.items():
#         text = text.replace(key, val)
#     return text


def switch_after_cut(time_text, isAnalysis=False):
    '''[换节日、换节气、数字、标点、消歧义] 时间段才进来转换，事务段不要进来
    '''
    YEAR = arrow.now().year
    for key, val in holiday2date.items():
        time_text = time_text.replace(key, val)
    for key, data in solar2data.items():
        # 通式寿星公式——[Y×D+C]-L
        # Y=年代数的后2位、D=0.2422、L=闰年数、C取决于节气和年份。
        Y = YEAR % 100
        D = 0.2422
        L = (Y - 1) / 4
        C = float(data[1])
        day = int(Y * D + C) - int(L)
        day = '0' + str(day) if day < 10 else str(day)
        time_text = time_text.replace(key, f'{data[0]}-{day}')
    for key, val in word2num.items():
        time_text = time_text.replace(key, val)
    for key, val in punc_lower.items():
        time_text = time_text.replace(key, val)
    if isAnalysis:
        return time_text

    # 消歧义1(下周、这周问题)
    def addPrefix(matched):
        return '下'+matched
    rule = "(?<!下)(周|星期|礼拜)([1-7])"
    pattern = re.compile(rule)
    match = pattern.search(time_text)
    if match is not None and int(match.group(2)) <= arrow.now().weekday() + 1:
        time_text = re.sub(pattern, addPrefix, time_text)
    return time_text

if __name__ == '__main__':
    time_text = '春分 惊蛰 冬至'
    print(switch_after_cut(time_text, isAnalysis=True))