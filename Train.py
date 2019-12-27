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

def get_model(maxlen):
    embed = BERTEmbedding('./Model/chinese_L-12_H-768_A-12',
                                task=kashgari.LABELING,
                                sequence_length=maxlen)
    model = BiLSTM_CRF_Model(embed)
    return model

if __name__ == '__main__':
    cf = ConfigParser()
    cf.read('./config.ini')
    data_path = cf.get('global', 'data_dir')
    model_path = cf.get('global', 'model_dir')

    train_x, train_y, valid_x, valid_y, test_x, test_y = read_data(data_path)
    # model = get_model(128)
    model = kashgari.utils.load_model(model_path)

    callbacks = [
                keras.callbacks.ModelCheckpoint('./Checkpoints/weights.{epoch:02d}-{val_loss:.2f}.h5', 
                    monitor='val_loss', 
                    verbose=0, 
                    save_best_only=False, 
                    save_weights_only=False,
                    mode='auto', 
                    period=1),
                keras.callbacks.TensorBoard(
                    log_dir='./Logs',
                    update_freq=200),
    ]
    
    model.compile_model()
    model.fit(train_x, train_y, valid_x, valid_y, batch_size=16, epochs=5, callbacks=callbacks)
    model.save('./Model/Bert_BiLSTM_CRF2')
    model.evaluate(test_x, test_y)
