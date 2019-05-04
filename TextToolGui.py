import os
import nltk
import sys
import csv

import tkinter
import tkinter.ttk as ttk

from tkinter import messagebox
from tkinter import filedialog

from datetime import datetime
from multiprocessing import Process, freeze_support, SimpleQueue

# Fix for placing helper files in the same folder
PACKAGE_PARENT = '..'

if getattr(sys, 'frozen', False):
    # frozen
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    # unfrozen
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

#SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from classifier.TextClassifier import TextClassifier
from classifier.TextClassifier import pipeline_and_parameters as pipeline_and_parameters

class TextToolGui(object):
    def __init__(self, window):
        # Set path to Main folder with dataset on your computer that contains the categorized subfolders (see README file for more information).
        # To test the script on the 20 Newsgroups dataset, use: file_path = 'fetch_20newsgroups'
        #self.file_path = tkinter.StringVar(value='C:/Users/Sytske/Desktop/Anoniem_Geknipt_PatientSpeech')
        #self.file_path = tkinter.StringVar(value="fetch_20newsgroups")
        self.file_path = tkinter.StringVar(value='C:/your/data/set')

        if os.path.isdir(self.file_path.get()):
            dirs = [os.path.join(self.file_path.get(), o) for o in os.listdir(self.file_path.get()) if
                    os.path.isdir(os.path.join(self.file_path.get(), o))]
            self.number_of_classes = tkinter.StringVar(value=dirs.__len__())
        else:
            self.number_of_classes = tkinter.StringVar(value=-1)

        self.text_classification_process = None
        self.status_report_queue = SimpleQueue()

        self.window = window
        self.create_window()

        self.window.after(100, self.periodical_runner)

    def periodical_runner(self):
        while not self.status_report_queue.empty():
            self.output_text.config(state='normal')
            self.output_text.insert(tkinter.END, self.status_report_queue.get() + '\n')
            self.output_text.see(tkinter.END)
            self.output_text.config(state='disabled')

        self.window.after(100, self.periodical_runner)

    def create_window(self):
        row_counter = 0

        self.window.wm_title("Text classification tool")
        self.window.resizable(0, 0)

        tkinter.Label(self.window, text="Step 1:").grid(row=row_counter, column=0, sticky=tkinter.W)
        self.select_dir_button = tkinter.Button(self.window, text="Select directory", command=self.select_directory)
        self.select_dir_button.grid(row=row_counter, column=1, sticky=tkinter.W)

        row_counter += 1

        tkinter.Label(self.window, text="Selected directory:").grid(row=row_counter, column=0, sticky=tkinter.W)
        tkinter.Label(self.window, textvariable=self.file_path, height=1, width=75, anchor=tkinter.W, justify=tkinter.LEFT).grid(row=row_counter, column=2, sticky=tkinter.W)

        row_counter += 1

        tkinter.Label(self.window, text="Number of classes found:").grid(row=row_counter, column=0, sticky=tkinter.W)
        tkinter.Label(self.window, textvariable=self.number_of_classes, height=1, width=75, anchor=tkinter.W,
                      justify=tkinter.LEFT).grid(row=row_counter, column=2, sticky=tkinter.W)

        row_counter += 1
        self.generate_output_button_row = row_counter
        tkinter.Label(self.window, text="Step 2:").grid(row=row_counter, column=0, sticky=tkinter.W)
        self.generate_output_button = tkinter.Button(self.window, text="Start text classification", command=self.start_text_classification)
        self.generate_output_button.grid(row=row_counter, column=1, sticky=tkinter.W)

        row_counter += 1

        tkinter.Label(self.window, text="Step 3:").grid(row=row_counter, column=0, sticky=tkinter.W)
        self.open_output_button = tkinter.Button(self.window, text="Open the generated output file", command=self.open_output, state="disabled")
        self.open_output_button.grid(row=row_counter, column=1, sticky=tkinter.W)

        row_counter += 1

        self.output_text = tkinter.Text(self.window, height=20, state='disabled')
        self.output_text.grid(row=row_counter, column=0, columnspan=4)
        scrollbar = tkinter.Scrollbar(self.window)
        scrollbar.grid(row=row_counter, column=4, stick=tkinter.NS)

        scrollbar.config(command=self.output_text.yview)
        self.output_text.config(yscrollcommand=scrollbar.set)

        row_counter += 1

        tkinter.Label(self.window, text="S.Wiegersma@utwente.nl", anchor=tkinter.E, justify=tkinter.RIGHT).grid(row=row_counter, column=0, columnspan=5, sticky=tkinter.E)

    def select_directory(self):
        try:
            self.file_path.set(filedialog.askdirectory(title="Choose the directory that contains the dataset"))

            dirs = [os.path.join(self.file_path.get(), o) for o in os.listdir(self.file_path.get()) if os.path.isdir(os.path.join(self.file_path.get(), o))]
            self.number_of_classes.set(dirs.__len__())

            self.window.update()
        except Exception as exception:
            print("Unexpected error:", sys.exc_info()[0])
            messagebox.showinfo("Something went wrong", exception, parent=self.window)
            raise

    def start_text_classification(self):
        self.select_dir_button.config(state="disabled")

        self.generate_output_frame = ttk.Frame(self.window)
        self.generate_output_frame.grid(row=self.generate_output_button_row, column=2, sticky=tkinter.NSEW)
        generate_output_progress = ttk.Progressbar(self.generate_output_frame, orient='horizontal', mode='indeterminate')
        generate_output_progress.pack(expand=True, fill=tkinter.BOTH, side=tkinter.TOP)
        generate_output_progress.start(50)

        self.generate_output_button.config(text="Stop text classification...", command=self.stop_text_classification_button)

        self.window.update()

        # Set variable to language of dataset, e.g. 'dutch', 'english' or any other language supported by NLTK
        language = 'dutch'

        error = None

        try:
            # Create the classifier with the language and dataset:
            text_classifier = TextClassifier(language, self.file_path.get(), self.status_report_queue)
            number_of_groups = text_classifier.get_groups_counter()

            for i in range(number_of_groups):
                self.status_report_queue.put('{}: {} outer loops, start fitting {}'.format(datetime.now().strftime('%H:%M:%S'), number_of_groups, i + 1))

                text_classifier.set_next_group_data(i)

                # Different scoring metrics can be used:
                if self.number_of_classes == 2:
                    # For binary classifiers: ['accuracy', 'precision', 'recall', 'f1']
                    scorings = ['f1']
                else:
                    # For multiclass classifiers: ['accuracy', 'precision_weighted', 'recall_weighted', 'f1_weighted'] or
                    #                             ['accuracy', 'precision_micro', 'recall_micro', 'f1_micro'] or
                    #                             ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']
                    scorings = ['f1_weighted']

                # Apply pipeline and parameters:
                for scoring in scorings:
                    pipeline_and_parameters(text_classifier,
                                            scoring,
                                            [result_scoring for result_scoring in scorings if result_scoring is not scoring],
                                            text_classifier.development_filenames,
                                            self.file_path.get())

                    self.text_classification_process = Process(target=text_classifier.train_and_predict)
                    self.text_classification_process.start()

                    while self.text_classification_process.is_alive():
                        self.text_classification_process.join(0.1)
                        self.window.update()
                        sys.stdout.flush()
        except Exception as exception:
            print("Unexpected error:", sys.exc_info()[0])
            messagebox.showinfo("Something went wrong", exception, parent=self.window)
            error = exception

        # All done
        self.status_report_queue.put('{}: All done!'.format(datetime.now().strftime('%H:%M:%S')))
        self.text_classification_process = None
        self.stop_text_classification()

        if error is not None:
            raise error


    def stop_text_classification_button(self):
        if messagebox.askokcancel("Stop", "Do you want to stop the text classification??"):
            self.stop_text_classification()

    def stop_text_classification(self):
        if self.text_classification_process is not None:
            if self.text_classification_process.is_alive():
                self.text_classification_process.terminate()
                self.text_classification_process.join()

            self.text_classification_process = None

        self.generate_output_frame.destroy()

        self.select_dir_button.config(state="normal")
        self.generate_output_button.config(text="Start text classification", command=self.start_text_classification)
        self.window.update()

    def generate_output(self):
        title_row = ["Word", "Category", "Total"]
        sorted_text_categories = sorted(self.texts_per_class)

        words_new_sorted = sorted(self.word_objects)

        for text_category in sorted_text_categories:
            title_row.append(text_category)

        with open(self.dataset_directory_name.get().replace(".csv", ".output.csv"), "w", newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=";", quotechar="\"", quoting=csv.QUOTE_MINIMAL)
            writer.writerow(title_row)

            for key in words_new_sorted:
                value = self.word_objects[key]
                row_to_write = [key, value["category"], value["count_total"]]

                for text_category in sorted_text_categories:
                    row_to_write.append(value["count_" + text_category])

                writer.writerow(row_to_write)

    def feature_selection(self):
        len_class = dict()
        len_class["total"] = 0

        for text_class in self.texts_per_class:
            len_class[text_class] = 0

        # get only the keywords and count the total number of keywords
        word_objects_only_keywords = dict()

        for word in self.word_objects:
            if self.word_objects[word]["category"] == self.word_categories[3]:
                word_objects_only_keywords[word] = self.word_objects[word]
                len_class["total"] += self.word_objects[word]["count_total"]

                for text_class in self.texts_per_class:
                    len_class[text_class] += self.word_objects[word]["count_" + text_class]

        # calculate the 'not' count
        for word in word_objects_only_keywords:
            word_objects_only_keywords[word]["not_count_total"] = 0

            for text_class in self.texts_per_class:
                word_objects_only_keywords[word]["not_count_" + text_class] = len_class[text_class] - word_objects_only_keywords[word]["count_" + text_class]
                word_objects_only_keywords[word]["not_count_total"] += word_objects_only_keywords[word]["not_count_" + text_class]

    def open_output(self):
        try:
            nltk.os.startfile(self.dataset_directory_name.get().replace(".csv", ".output.csv"))
        except Exception as exception:
            print("Unexpected error:", sys.exc_info()[0])
            messagebox.showinfo('Something went wrong', exception, parent=self.window)
            raise

    def on_closing(self):
        if self.text_classification_process is not None:
            if self.text_classification_process.is_alive():
                self.text_classification_process.terminate()
                self.text_classification_process.join()

if __name__ == '__main__':
    freeze_support()

    tk_window = tkinter.Tk()
    text_tool = TextToolGui(tk_window)

    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if text_tool is not None:
                text_tool.on_closing()

            tk_window.destroy()

    tk_window.protocol("WM_DELETE_WINDOW", on_closing)
    tk_window.mainloop()