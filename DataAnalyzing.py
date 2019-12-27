from configparser import ConfigParser
from Dictionary import *
import pprint
import re
from TextPreprocessing import switch_after_cut
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
plt.rcParams['font.family'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False
sns.set(font='Microsoft YaHei')


cf = ConfigParser()
cf.read('./config.ini')
data_path = cf.get('global', 'data_dir')
analysis_dir = cf.get('global', 'analysis_dir')


# 存数据
# from kashgari.corpus import DataReader
# def read_data(dir_path):
#     train_x, train_y = DataReader().read_conll_format_file(dir_path + '/time.train')
#     valid_x, valid_y = DataReader().read_conll_format_file(dir_path + '/time.dev')
#     test_x, test_y = DataReader().read_conll_format_file(dir_path + '/time.test')
#     all_x = train_x + valid_x + test_x
#     all_y = train_y + valid_y + test_y
#     time_word_list = list()
#     time_word = ''
#     for char_list, tag_list in zip(all_x, all_y):
#         for char, tag in zip(char_list, tag_list):
#             if tag != 'O':
#                 time_word += char
#             elif time_word != '':
#                 time_word_list.append(time_word)
#                 time_word = ''
#     print(f'sentence_num: {len(time_word_list)}')
#     return time_word_list
# time_word_set = read_data(data_path)
# with open(analysis_dir + '/raw_time_words.txt', 'w') as f:
#     for time_word in time_word_set:
#         f.write(time_word + '\n')


time_word_set = list()
with open(analysis_dir + '/raw_time_words.txt', 'r') as f:
    while True:
        word = f.readline()
        if word == '':
            break
        word = switch_after_cut(word.strip(), isAnalysis=True)
        time_word_set.append(word)

print(f'time_word_num: {len(time_word_set)}')

rule_list = [rule for rule in rule_dict.keys()]
cnt_dict = dict()
word_tag = dict()
unmatch_word = set()

flag = False
for word in time_word_set:
    word_tag[word] = list()
    for index, rule in enumerate(rule_list):
        pattern = re.compile(rule)
        match = pattern.search(word)
        if match is not None:
            word_tag[word].append(rule_dict[rule])
            if rule_dict[rule] not in cnt_dict.keys():
                cnt_dict[rule_dict[rule]] = 0
            cnt_dict[rule_dict[rule]] += 1
            flag = True
    if not flag:
        unmatch_word.add(word)
    flag = False


# 未考虑到的词
with open(analysis_dir + '/unmatch_time_words.txt', 'w') as f:
    for time_word in unmatch_word:
        f.write(time_word + '\n')



# 描述复杂程度分布
# tag_freqDict = sorted(word_tag.items(), key=lambda obj: len(obj[1]), reverse=True)
# pprint.pprint(tag_freqDict[:20])
# tag_num_dict = {'tag_num': [len(obj) for obj in word_tag.values()]}
# df = pd.DataFrame(tag_num_dict)
# sns.countplot(x='tag_num', data=df)
# plt.xticks(rotation=30)
# plt.show()


# 事件描述方式分析
# cnt_dict['unmatch'] = len(unmatch_word)
# freqDict = sorted(cnt_dict.items(), key=lambda obj: obj[1], reverse=True)

# top_df = pd.DataFrame(freqDict[:20])
# top_df.columns=["Time_word", "Freq"]
# sns.barplot(x="Time_word", y="Freq", data=top_df)
# plt.xticks(rotation=30)
# plt.show()

# 时间的准确、模糊、相对描述占比
# category_num = {'label': ['accurate', 'fuzzy', 'relative'], 'num': [0, 0, 0]}
# for word in time_word_set:
#     for index, (label, rule_list) in enumerate(rule_block_dict.items()):
#         for rule in rule_list:
#             pattern = re.compile(rule)
#             match = pattern.search(word)
#             if match is not None:
#                 category_num['num'][index] += 1
#                 break

# df = pd.DataFrame(category_num)
# plt.pie(df.num, labels=df.label, autopct='%1.2f%%')
# plt.show()



# 存句子
from kashgari.corpus import DataReader

def read_sentence(dir_path):
    train_x, train_y = DataReader().read_conll_format_file(dir_path + '/time.train')
    valid_x, valid_y = DataReader().read_conll_format_file(dir_path + '/time.dev')
    test_x, test_y = DataReader().read_conll_format_file(dir_path + '/time.test')
    all_x = train_x + valid_x + test_x
    all_y = train_y + valid_y + test_y
    sentence_list = list()
    sen_tag_list = list()
    for char_list, tag_list in zip(all_x, all_y):
        sentence_list.append("".join(char_list))
        sen_tag_list.append(" ".join(tag_list))
    return sentence_list, sen_tag_list

sentence_list, sen_tag_list = read_sentence(data_path)
with open(analysis_dir + '/sentences.txt', 'w') as f:
    for sentence in sentence_list:
        f.write(sentence + '\n')
with open(analysis_dir + '/sentences_tag.txt', 'w') as f:
    for sen_tag in sen_tag_list:
        f.write(sen_tag + '\n')



sentence_list = list()
sen_tag_list = list()
with open(analysis_dir + '/sentences.txt', 'r') as f:
    while True:
        sentence = f.readline()
        if sentence != '':
            sentence_list.append(sentence.strip())
        else:
            break
with open(analysis_dir + '/sentences_tag.txt', 'r') as f:
    while True:
        sen_tag = f.readline()
        if sen_tag != '':
            sen_tag_list.append(sen_tag.strip())
        else:
            break

# 起始位置分析
# index_num = list()
# begin_index = list()

# for _id, sen_tag in enumerate(sen_tag_list):
#     sen_tag = sen_tag.split(" ")
#     if 'B-TIME' not in sen_tag:
#         continue
#     index = sen_tag.index('B-TIME')
#     begin_index.append(index/(len(sen_tag) - 1))
#     index_num.append(_id)

# plt.scatter(x=begin_index, y=index_num, marker='.')
# plt.xlim(0, 1)
# plt.show()

# 长度&位置分析
# index_num = list()
# begin_index = list()
# for _id, sen_tag in enumerate(sen_tag_list):
#     a, b = None, None
#     sen_tag = sen_tag.split(" ")
#     if 'B-TIME' not in sen_tag:
#         continue
#     a = sen_tag.index('B-TIME')
#     for i in range(a + 1, len(sen_tag)):
#         if sen_tag[i] == 'O':
#             b = i - 1
#             break
#     x = np.arange(a/(len(sen_tag) - 1), b/(len(sen_tag) - 1), 0.1)
#     y = np.array([_id for _ in range(len(x))])
#     plt.plot(x, y)
# plt.show()


# 查看时间词前后的词性分布
# import nltk
# import jieba.posseg as pseg
# import jieba
# import re

# with open(analysis_dir + '/jieba_new_dict.txt', 'w', encoding='utf-8') as nf:
#     with open(analysis_dir + '/raw_time_words.txt', 'r') as f:
#         while True:
#             word = f.readline()
#             if word == '':
#                 break
#             nf.write(word.strip()+' '+'300'+' '+'t'+'\n')

# jieba.load_userdict(analysis_dir + '/jieba_new_dict.txt')

# tag_pairs = list()
# for text in sentence_list:
#     text = re.sub(r'[，、；！？。,!?.;]', "", text)
#     posseg_list = pseg.cut(text)
#     tag_list = ['head']
#     for _, tag in posseg_list:
#         tag_list.append(tag)
#     tag_list.append('tail')
#     tag_pairs += nltk.bigrams(tag_list)

# # 时间词之前
# # print("时间词之前：")
# # noun_preceders = [a for a, b in tag_pairs if b == 't']
# # fdist = nltk.FreqDist(noun_preceders).most_common(10)
# # df = pd.DataFrame(fdist)
# # df.columns=["前一个词性", "Freq"]
# # sns.barplot(x="前一个词性", y="Freq", data=df)
# # plt.show()

# # 时间词之后
# # print("时间词之后：")
# # noun_preceders = [b for a, b in tag_pairs if a == 't']
# # fdist = nltk.FreqDist(noun_preceders).most_common(10)
# # df = pd.DataFrame(fdist)
# # df.columns=["后一个词性", "Freq"]
# # sns.barplot(x="后一个词性", y="Freq", data=df)
# # plt.show()



# 统计字数和各标记数目
# from kashgari.corpus import DataReader
# train_x, train_y = DataReader().read_conll_format_file(data_path + '/time.train')
# valid_x, valid_y = DataReader().read_conll_format_file(data_path + '/time.dev')
# test_x, test_y = DataReader().read_conll_format_file(data_path + '/time.test')

# a = 0
# b = 0
# c = 0
# for tag_list in train_y:
#     for tag in tag_list:
#         if tag == 'B-TIME':
#             a += 1
#         elif tag == 'I-TIME':
#             b += 1
#         else:
#             c += 1
# print("训练集：")
# print(f"B-TIME:{a}  I-TIME:{b} O:{c} 总计:{a+b+c}")
# a = 0
# b = 0
# c = 0
# for tag_list in valid_y:
#     for tag in tag_list:
#         if tag == 'B-TIME':
#             a += 1
#         elif tag == 'I-TIME':
#             b += 1
#         else:
#             c += 1
# print("验证集：")
# print(f"B-TIME:{a}  I-TIME:{b} O:{c} 总计:{a+b+c}")
# a = 0
# b = 0
# c = 0
# for tag_list in test_y:
#     for tag in tag_list:
#         if tag == 'B-TIME':
#             a += 1
#         elif tag == 'I-TIME':
#             b += 1
#         else:
#             c += 1
# print("测试集：")
# print(f"B-TIME:{a}  I-TIME:{b} O:{c} 总计:{a+b+c}")