import kashgari
from kashgari.corpus import DataReader
from kashgari.embeddings import BERTEmbedding
from kashgari.tasks.labeling import BiLSTM_CRF_Model
import keras
from configparser import ConfigParser

def read_data(dir_path):
    train_x, train_y = DataReader().read_conll_format_file(dir_path + '/time.train')
    valid_x, valid_y = DataReader().read_conll_format_file(dir_path + '/time.dev')
    test_x, test_y = DataReader().read_conll_format_file(dir_path + '/time.test')
    return train_x, train_y, valid_x, valid_y, test_x, test_y

if __name__ == '__main__':
    cf = ConfigParser()
    cf.read('./config.ini')
    data_path = cf.get('global', 'data_dir')
    model_path = cf.get('global', 'model_dir')

    train_x, train_y, valid_x, valid_y, test_x, test_y = read_data(data_path)
    model = kashgari.utils.load_model(model_path)
    model.evaluate(test_x, test_y)
