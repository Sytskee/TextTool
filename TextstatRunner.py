from os import listdir, linesep
from os.path import isfile, join, split
from textstat.textstat import textstat

if __name__ == '__main__':
    base_path = 'C:\\Users\\Sytske\\Desktop\\Anoniem_Geknipt_PatientSpeech'
    text_files_paths = [join(base_path, 'Hotspots'),
                        join(base_path, 'NonHotspots')]

    for text_files_path in text_files_paths:
        text_file_paths = [f for f in listdir(text_files_path) if isfile(join(text_files_path, f))]

        header_line = '\t'.join(['Filename',
                                 'avg_letter_per_word',
                                 'avg_sentence_length',
                                 'avg_syllables_per_word',
                                 'char_count',
                                 'lexicon_count',
                                 'sentence_count',
                                 'syllable_count',
                                 'avg_sentence_per_word',
                                 'flesch_reading_ease',
                                 'smog_index',
                                 'flesch_kincaid_grade',
                                 'coleman_liau_index',
                                 'automated_readability_index',
                                 'dale_chall_readability_score',
                                 'difficult_words',
                                 'linsear_write_formula',
                                 'gunning_fog',
                                 'text_standard'])
        lines = [header_line]

        for text_file_path in text_file_paths:
            text = open(join(text_files_path, text_file_path), 'r').read()

            line = '\t'.join([text_file_path,
                              str(textstat.avg_letter_per_word(text)),
                              str(textstat.avg_sentence_length(text)),
                              str(textstat.avg_syllables_per_word(text)),
                              str(textstat.char_count(text)),
                              str(textstat.lexicon_count(text)),
                              str(textstat.sentence_count(text)),
                              str(textstat.syllable_count(text)),
                              str(textstat.avg_sentence_per_word(text)),
                              str(textstat.flesch_reading_ease(text)),
                              str(textstat.smog_index(text)),
                              str(textstat.flesch_kincaid_grade(text)),
                              str(textstat.coleman_liau_index(text)),
                              str(textstat.automated_readability_index(text)),
                              str(textstat.dale_chall_readability_score(text)),
                              str(textstat.difficult_words(text)),
                              str(textstat.linsear_write_formula(text)),
                              str(textstat.gunning_fog(text)),
                              textstat.text_standard(text)])
            lines.append(line)

        output_file = open(join(base_path, 'Textstat_' + split(text_files_path)[1] + '.csv'), 'w')
        output_file.writelines([x + '\n' for x in lines])
        output_file.close()