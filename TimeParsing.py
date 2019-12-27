import re
import arrow

def get_year(text):
    rule = "[0-9]{2,4}(?=年)"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        if int(match.group()) > 100:
            return int(match.group())
        return 2000 + int(match.group())


def get_month(text):
    rule = "(?<!\d)(10|11|12|[1-9])(?=月)"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        return int(match.group())

def get_day(text):
    rule = "(?<!\d)([0-3][0-9]|[1-9])(?=(日|号))"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        return int(match.group())

def get_hour(text):
    h = None
    rule = "([0-2]?[0-9])(?=(点|时))" # 注意防止 周1 3点
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        h = int(match.group(1))

    rule = "凌晨"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        if h is None:  # 增加对没有明确时间点，只写了“凌晨”这种情况的处理
            h = 0
        elif h >= 12 and h <= 23:
            h -= 12
        elif h == 0:
            h = 12

    rule = "(早上|早晨|早间|晨间|今早|明早|早|清晨)"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        if h is None:
            h = 6
        elif h >= 12 and h <= 23:
            h -= 12
        elif h == 0:
            h = 12

    rule = "(上午|am|AM)"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        if h is None:
            h = 9
        elif h >= 12 and h <= 23:
            h -= 12
        elif h == 0:
            h = 12

    rule = "(中午|午间|白天)"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        if h is None:
            h = 12
        elif h >= 0 and h <= 4:
            h += 12


    rule = "(下午|午后|pm|PM)"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        if h is None:
            h = 15
        elif h >= 0 and h <= 11:
            h += 12

    rule = "(晚上|夜间|夜里|今晚|明晚|晚|夜里)"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        if h is None:
            h = 21
        elif h >= 0 and h <= 11:
            h += 12
        elif h == 12:
            h = 0

    return h

def get_minute(text):
    m = None
    rule = "([0-5]?[0-9](?=分(?!钟)))"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        m = int(match.group())

    # 加对一刻，半，3刻的正确识别（1刻为15分，半为30分，3刻为45分）
    rule = "(?<=[点时])1刻(?!钟)"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        m= 15

    rule = "(?<=[点时])半"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        m = 30

    rule = "(?<=[点时])3刻(?!钟)"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        m = 45

    return m


def get_colonType(text):

    # 给周1等后加空格，防止错误识别 周1XX:XX
    def addsuffix(matched):
        return matched.group() + ' '
    rule = "(周|星期|礼拜)([1-7])"
    pattern = re.compile(rule)
    text = re.sub(pattern, addsuffix, text)

    h = None
    m = None
    rule = "(晚上|夜间|夜里|今晚|明晚|晚|夜里|下午|午后)([0-2]?[0-9]):([0-5]?[0-9])" # 晚上XX:XX
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        h = int(match.group(2))
        m = int(match.group(3))
        if 0 <= h <= 11:
            h += 12


    if match is None:
        rule = "([0-2]?[0-9]):([0-5]?[0-9])(PM|pm|p.m)" # XX:XX pm
        pattern = re.compile(rule)
        match = pattern.search(text)
        if match is not None:
            h = int(match.group(1))
            m = int(match.group(2))
            if 0 <= h <= 11:
                h += 12


    if match is None:
        rule = "([0-2]?[0-9]):([0-5]?[0-9])" # XX:XX
        pattern = re.compile(rule)
        match = pattern.search(text)
        if match is not None:
            h = int(match.group(1))
            m = int(match.group(2))

    Y = None
    M = None
    D = None
    # 年月日的简易表达
    rule = "([0-9]{2,4})([-./])(10|11|12|[1-9])([-./])([0-3][0-9]|[1-9])"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        Y = int(match.group(1)) if int(match.group(1)) > 100 else (2000 + int(match.group(1)))
        M = int(match.group(3))
        D = int(match.group(5))

    else:
        # 月日的简易表达
        rule = "(10|11|12|[1-9])([-./])([0-3][0-9]|[1-9])"
        pattern = re.compile(rule)
        match = pattern.search(text)
        if match is not None:
            M = int(match.group(1))
            D = int(match.group(3))

    return Y, M, D, h, m


def get_relative(baseTime, text):
    '''相对时间 只需要考虑“之后”
    '''
    ansTime = arrow.get(baseTime)


    rule = "\d+(?=多?天[以之过]?后)"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        ansTime = ansTime.shift(days=int(match.group()))


    rule = "\d+(?=多?个?(周|星期|礼拜)[以之过]?后)"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        ansTime = ansTime.shift(weeks=int(match.group()))


    rule = "\d+(?=多?个?月[以之过]?后)"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        ansTime = ansTime.shift(months=int(match.group()))


    rule = "\d+(?=多?年[以之过]?后)"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        ansTime = ansTime.shift(years=int(match.group()))


    rule = "\d+(?=多?个?多?(小时|钟|钟头|时辰)[以之过]?后)"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        ansTime = ansTime.shift(hours=int(match.group()))


    rule = "半(?=个?多?(小时|钟|钟头|时辰)[以之过]?后)"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        ansTime = ansTime.shift(minutes=30)


    rule = "\d+(?=多?分钟[以之过]?后)"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        ansTime = ansTime.shift(minutes=int(match.group()))


    rule = "半(?=分钟[以之过]?后)"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        ansTime = ansTime.shift(seconds=30)


    rule = "\d+(?=刻钟[以之过]?后)"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        ansTime = ansTime.shift(minutes=15*int(match.group()))

    # -----短的相对时间------

    rule = "明年"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        ansTime = ansTime.shift(years=1)

    rule = "后年"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        ansTime = ansTime.shift(years=2)


    rule = "下+个?月"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        match = re.compile("下").findall(text)
        ansTime = ansTime.shift(months=len(match))


    rule = "明天?(?!年)"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        ansTime = ansTime.shift(days=1)


    rule = "(?<!大)后天"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        ansTime = ansTime.shift(days=2)

    rule = "大+后天"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        match = re.compile("大").findall(text)
        ansTime = ansTime.shift(days=len(match))


    rule = "(下*个?(周|星期|礼拜))([1-7]?)"
    pattern = re.compile(rule)
    match = pattern.search(text)
    if match is not None:
        a = match.group(1)
        b = match.group(3)
        a = re.compile("下").findall(a)
        b = 1 if b == "" else int(b)
        ansTime = ansTime.shift(weeks=len(a), days=b-ansTime.weekday()-1)

    return ansTime.year, ansTime.month, ansTime.day, ansTime.hour, ansTime.minute



def parse(text, curTime):
    '''解析时间 总入口
    '''
    # print(f'raw-text: {text}')
    Y, M, D, h, m = get_relative(curTime, text)
    # print(f'Y={Y} M={M} D={D} h={h} m={m}')
    nY1 = get_year(text)
    nM1 = get_month(text)
    nD1 = get_day(text)  
    nh1 = get_hour(text)
    nm1 = get_minute(text)
    # print(f'Y={nY1} M={nM1} D={nD1} h={nh1} m={nm1}')
    nY2, nM2, nD2, nh2, nm2 = get_colonType(text)
    # print(f'Y={nY2} M={nM2} D={nD2} h={nh2} m={nm2}')
    Y = nY1 if nY1 is not None else Y
    M = nM1 if nM1 is not None else M
    D = nD1 if nD1 is not None else D
    h = nh1 if nh1 is not None else h
    m = nm1 if nm1 is not None else m
    Y = nY2 if nY2 is not None else Y
    M = nM2 if nM2 is not None else M
    D = nD2 if nD2 is not None else D
    h = nh2 if nh2 is not None else h
    m = nm2 if nm2 is not None else m
    ansTime = arrow.get(Y, M, D, h, m)
    # 没有提取到任何时间
    if (Y, M, D, h, m) == (curTime.year, curTime.month, curTime.day, curTime.hour, curTime.minute):
        return None, ansTime.year, ansTime.month, ansTime.day, ansTime.hour, ansTime.minute

    # 消歧义2(月份问题)
    if (Y, M, D) < (curTime.year, curTime.month, curTime.day):
        if M == curTime.month:
            ansTime = ansTime.shift(months=1)
        elif M < curTime.month:
            ansTime = ansTime.shift(years=1)


    # 消歧义3(早、晚问题)
    elif (Y, M, D, h, m) < (curTime.year, curTime.month, curTime.day, curTime.hour, curTime.minute):
        ansTime = ansTime.shift(days=1)

    if (h, m) == (curTime.hour, curTime.minute):
        return ansTime, ansTime.year, ansTime.month, ansTime.day, None, None
    return ansTime, ansTime.year, ansTime.month, ansTime.day, ansTime.hour, ansTime.minute


if __name__ == '__main__':
    baseTime = arrow.now()
    # test='今天晚上8:15' 
    # test = '12月3日下午3点1刻'  
    # test = '2019.12.3'
    # test = '1号8:00pm'  
    # test = '周3之前'
    while True:
        test = input(f'input > ')
        bY, bM, bD, bh, bm = baseTime.year, baseTime.month, baseTime.day, baseTime.hour, baseTime.minute
        ansTime, Y, M, D, h, m = parse(test, baseTime)
        print(f'当前时间 > {"%d/%02d/%02d %02d:%02d" % (bY, bM, bD, bh, bm)}')
        if h is None or m is None:
            print(f'解析结果 > {"%d/%02d/%02d" % (Y, M, D)}')
        else:
            print(f'解析结果 > {"%d/%02d/%02d %02d:%02d" % (Y, M, D, h, m)}')
        print('\n')
