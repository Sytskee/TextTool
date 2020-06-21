import os
import pickle

from datetime import datetime
from sklearn.datasets import load_files

from executors.ExecutorBase import ExecutorBase


class ApplyPickle(ExecutorBase):
    def __init__(self, data_files_path, pickle_path, output_path, status_report_queue=None):
        self.pickle_path = pickle_path

        self.data = None
        self.classifier = None

        output_file = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.txt'
        self.full_output_file_path = os.path.join(output_path, output_file)

        super().__init__(data_files_path, output_path, status_report_queue)

    def load_data(self):
        self.report_status('Loading data ...')

        self.data = load_files(self.data_files_path, encoding='utf-8')
        self.classifier = pickle.load(open(self.pickle_path, 'rb'))

        self.report_status('Data loaded')

    def predict(self):
        y_pred = self.classifier.predict(self.data.data)

        labels = None

        label_path = self.pickle_path.replace('.pkl', '.lbl')
        if os.path.isfile(label_path):
            labels = pickle.load(open(label_path, 'rb'))

        print_format = '{:100}  |  {:10}'
        header_line = print_format.format('File name', 'Label')

        with open(self.full_output_file_path, 'w', encoding='utf-8') as print_file:
            print(header_line, file=print_file)
            print('{}'.format('-' * len(header_line)), file=print_file)

            for i, y in enumerate(y_pred):
                if labels is not None:
                    print(print_format.format(os.path.basename(self.data.filenames[i]), labels[y]), file=print_file)
                else:
                    print(print_format.format(os.path.basename(self.data.filenames[i]), y), file=print_file)

        self.report_status('All done, see "{}" for output'.format(print_file.name))
