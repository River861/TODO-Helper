import kashgari
from configparser import ConfigParser

def predict(model, text):
    '''预测
    输入句子，返回时间标记列表
    '''
    text = text.replace(" ", "，")
    tag_list = model.predict([[char for char in text]])
    return tag_list


if __name__ == '__main__':
    cf = ConfigParser()
    cf.read('./config.ini')
    model_path = cf.get('global', 'model_dir')

    model = kashgari.utils.load_model(model_path)
    while True:
        text = input('Sentence: ')
        tag_list = predict(model, text)
        print(' '.join(tag_list[0]))
