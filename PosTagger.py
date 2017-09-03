from collections import OrderedDict
from nltk.data import load
from nltk.tag.perceptron import PerceptronTagger
from nltk.tokenize import word_tokenize
from os import listdir
from os.path import join, isfile, split

if __name__ == '__main__':
    tagger_pickle_path = 'C:\\Users\\Sytske\\Desktop\\Anoniem_Geknipt_PatientSpeech\\TaggerPickle'

    # This may take a few minutes. (But once loaded, the tagger is really fast!)
    tagger = PerceptronTagger(load=False)
    tagger.load(join(tagger_pickle_path, 'model.perc.dutch_tagger_small.pickle'))

    sent_tokenizer = load('tokenizers/punkt/dutch.pickle')

    def tokenize(text):
        for sentence in sent_tokenizer.tokenize(text):
            yield word_tokenize(sentence)

    base_path = 'C:\\Users\\Sytske\\Desktop\\Anoniem_Geknipt_PatientSpeech'
    text_files_paths = [join(base_path, 'Hotspots'),
                        join(base_path, 'NonHotspots')]

    for text_files_path in text_files_paths:
        text_file_paths = [f for f in listdir(text_files_path) if isfile(join(text_files_path, f))]

        header_line = '\t'.join(['Filename'] + sorted(tagger.classes))
        lines = [header_line]

        for text_file_path in text_file_paths:
            text = open(join(text_files_path, text_file_path), 'r').read()
            sentences = tokenize(text)
            tag_counts = OrderedDict.fromkeys(sorted(tagger.classes), 0)

            for sentence in sentences:
                tagged_sentence = tagger.tag(sentence)
                #print(tagged_sentence)

                for tagged_word in tagged_sentence:
                    tag_counts[tagged_word[1]] += 1

            line = '\t'.join([text_file_path] + list(map(str, tag_counts.values())))
            lines.append(line)

        output_file = open(join(base_path, 'PosTagCounts_' + split(text_files_path)[1] + '.csv'), 'w')
        output_file.writelines([x + '\n' for x in lines])
        output_file.close()