import os
import pickle

from sklearn.datasets import load_files
from sklearn.metrics import classification_report


class ApplyPickle():
    def __init__(self, data_files_path, pickle_path, output_path, status_report_queue=None):
        self.pickle_path = pickle_path
        self.data = None

        super().__init__(data_files_path, output_path, status_report_queue)

    def load_data(self):
        self.report_status('Loading data ...')

        self.data = load_files(self.data_files_path, encoding='utf-8')

        self.report_status('Data loaded')


'''
    #data_set_path = r'C:\Users\Sytske\Desktop\Ingrid\Dataset\ThinkingTestLevel3'
    data_set_path = r'C:\Users\Sytske\Desktop\Ingrid\Dataset\Thinking 2'
    #data_set_path = r'C:\Users\Sytske\Desktop\Ingrid\Dataset\ThinkingTest'
    #pickle_path = r'C:\Users\Sytske\Documents\GitHub\TextTool\output\2017-10-15_14-31-22_1.pkl'
    pickle_path = r'C:\Users\Sytske\Documents\GitHub\TextTool\output\2017-12-03_21-34-41_1.pkl'

    data = load_files(data_set_path, encoding='utf-8')     # The path to and encoding of the input dataset

    classifier = pickle.load(open(pickle_path, 'rb'))
    y_pred = classifier.predict(data.data)

    labels = None

    label_path = pickle_path.replace('.pkl', '.lbl')
    if os.path.isfile(label_path):
        labels = pickle.load(open(label_path, 'rb'))

    print_format = '{:100}  |  {:10}'
    header_line = print_format.format('File name', 'Label')

    with open(r'C:\Users\Sytske\Desktop\Ingrid\Dataset\Thinking 2\output.txt', 'w', encoding='utf-8') as print_file:
        print(header_line, file=print_file)
        print('{}'.format('-' * len(header_line)), file=print_file)

        for i, y in enumerate(y_pred):
            if labels is not None:
                print(print_format.format(os.path.basename(data.filenames[i]), labels[y]), file=print_file)
            else:
                print(print_format.format(os.path.basename(data.filenames[i]), y), file=print_file)

    print('All done, see "{}" for output'.format(print_file.name))
'''