import nltk
import jieba.posseg as pseg
import re


def word_label(_str):
    '''使用jieba进行词性标注
    '''
    _str = re.sub(r'[，、；！？。,!?.;]', " ", _str)
    posseg_list = pseg.cut(_str)
    word_list = list()
    tag_list = list()
    for word, tag in posseg_list:
        word_list.append(word)
        tag_list.append("n" if tag == "eng" else tag)
    return word_list, tag_list


def get_action_list_old(_str):
    '''根据词性把不同事务分开，每件事物以动词或介词(v、p)开始，以动词或者名词(v、n)结束
    '''
    word_list, tag_list = word_label(_str + " ")
    things_list = list()
    thing = list()
    thing_tag = list()
    # print(word_list)
    # print(tag_list)
    flag = 0
    for index, tag in enumerate(tag_list):
        if word_list[index] == ' ':
            # 以动词或者名词(v、n)结束
            for tag in reversed(thing_tag):
                suffix_list = ['v', 'n', 'vn']
                if tag not in suffix_list:
                    thing.pop()
                    continue
                break
            if len(thing) != 0:
                things_list.append("".join(thing))
            thing = list()
            thing_tag = list()
            flag = 0
        elif word_list[index] == '我':
            thing = list()
            thing_tag = list()
            flag = 0
        else:
            # 以动词或介词(v、p)开始
            if flag == 1 or tag == 'v' or tag == 'p':
                thing.append(word_list[index])
                thing_tag.append(tag_list[index])
                if flag != 1:
                    flag = 1
    return things_list


def grammar_words(_str):
    '''动态生成文法 和 关键词列表
    '''
    _str = re.sub(r'[，、；！？。,!?.; ]', "_", _str)
    posseg_list = pseg.cut(_str)
    word_list = list()
    tag_list = list()
    grammar_string = """VP -> VP2 | VP1 \nVP2 -> PP VP1S \nVP1 -> V VP1 | V NP | V \nNP -> Det N | N N | N \nPP -> P NP """
    v_cnt = 0
    for word, tag in posseg_list:
        if tag == 'v' or tag == 'vn':
            word_list.append(word)
            grammar_string += f"\nV -> '{word}'"
            v_cnt += 1
        elif tag == 'n' or tag == 'nr' or tag == 'ns' or tag == 'eng':
            word_list.append(word)
            grammar_string += f"\nN -> '{word}'"
        elif tag == 'p':
            word_list.append(word)
            grammar_string += f"\nP -> '{word}'"
        elif tag == 'm':
            word_list.append(word)
            grammar_string += f"\nDet -> '{word}'"
    grammar_string = f'VPS -> ' + ' | '.join(['VP ' * i for i in range(1, v_cnt + 1)]) + '\n' + grammar_string
    grammar_string += f'\nVP1S -> ' + ' | '.join(['VP1 ' * i for i in range(v_cnt, 0, -1)])
    # print(grammar_string)
    return nltk.CFG.fromstring(grammar_string), word_list


def getVP(parent):
    res = list()
    for node in parent:
        if node.label() == 'VP':
            node = node[0]
            leaves = node.leaves()
            if node[0].label() == 'PP':
                PP = ''.join(node[0].leaves())
                VPS = '、'.join([''.join(VP.leaves()) for VP in node[1]])
                res.append(PP + VPS)
            else:
                res.append(''.join(leaves))
    return res

def get_action_list(text):
    '''根据句法分析把不同事务分开
    '''
    grammar, sent = grammar_words(text)
    rd_parser = nltk.RecursiveDescentParser(grammar)
    try:
        tree = next(rd_parser.parse(sent))
        return getVP(tree)
    except Exception as err:
        print(err)
        return get_action_list_old(text)

if __name__ == '__main__':
    while True:
        text = input('input > ')
        grammar, sent = grammar_words(text)
        rd_parser = nltk.RecursiveDescentParser(grammar)
        tree = next(rd_parser.parse(sent))
        tree.draw()
        print(f'output > {getVP(tree)}')
        print('\n')