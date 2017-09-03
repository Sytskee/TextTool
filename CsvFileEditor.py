import math
import csv
from os.path import join, split, splitext

if __name__ == '__main__':
    base_path = 'C:\\Users\\Sytske\\Desktop\\Data\csv'
    base_csv_path = join(base_path, 'Hotspots_Merged.csv')

    base_csvs = [join(base_path, 'Hotspots_Merged.csv'),
                 join(base_path, 'NonHotspots_Merged.csv')]

    for base_csv_path in base_csvs:
        csv_dict = {}

        with open(base_csv_path, newline='') as csvfile:
            csv_dict = csv.DictReader(csvfile, delimiter='\t', quoting=csv.QUOTE_NONE)

            new_file_name = splitext(split(base_csv_path)[1])[0]
            new_file_name += '_generated.csv'

            with open(join(base_path, new_file_name), 'w', newline='\n', encoding='utf-8') as csvfile:
                header_set = False
                colomns_to_remove = ['Stat_lexicon_count',
                                     'LIWC_WC']

                for row in csv_dict:
                    round_number_of_digits = 3

                    row['Stat_Brunet'] = round(math.pow(float(row['Stat_N_tokens']), math.pow(float(row['Stat_N_types']), -0.165)), round_number_of_digits)
                    row['Stat_PNR'] = round((float(row['POS_pronadv']) +
                                             float(row['POS_prondemo']) +
                                             float(row['POS_pronindef']) +
                                             float(row['POS_pronpers']) +
                                             float(row['POS_pronposs']) +
                                             float(row['POS_pronquest']) +
                                             float(row['POS_pronrefl']) +
                                             float(row['POS_pronrel'])) / (float(row['POS_nounpl']) +
                                                                           float(row['POS_nounprop']) +
                                                                           float(row['POS_nounsg'])), round_number_of_digits)

                    fixed_row_devider = float(row['LIWC_WC'])
                    row['Extra_Fragments'] = round((float(row['Extra_Fragments']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['Extra_Confusion'] = round((float(row['Extra_Confusion']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_conjcoord'] = round((float(row['POS_conjcoord']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_conjsubo'] = round((float(row['POS_conjsubo']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_det__art'] = round((float(row['POS_det__art']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_det__demo'] = round((float(row['POS_det__demo']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_nounpl'] = round((float(row['POS_nounpl']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_nounprop'] = round((float(row['POS_nounprop']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_nounsg'] = round((float(row['POS_nounsg']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_partte'] = round((float(row['POS_partte']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_prep'] = round((float(row['POS_prep']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_pronadv'] = round((float(row['POS_pronadv']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_prondemo'] = round((float(row['POS_prondemo']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_pronindef'] = round((float(row['POS_pronindef']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_pronpers'] = round((float(row['POS_pronpers']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_pronposs'] = round((float(row['POS_pronposs']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_pronquest'] = round((float(row['POS_pronquest']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_pronrefl'] = round((float(row['POS_pronrefl']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_pronrel'] = round((float(row['POS_pronrel']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_verbinf'] = round((float(row['POS_verbinf']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_verbpapa'] = round((float(row['POS_verbpapa']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_verbpastpl'] = round((float(row['POS_verbpastpl']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_verbpastsg'] = round((float(row['POS_verbpastsg']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_verbpresp'] = round((float(row['POS_verbpresp']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_verbprespl'] = round((float(row['POS_verbprespl']) / fixed_row_devider) * 100, round_number_of_digits)
                    row['POS_verbpressg'] = round((float(row['POS_verbpressg']) / fixed_row_devider) * 100, round_number_of_digits)

                    for colomn_to_remove in colomns_to_remove:
                        del row[colomn_to_remove]

                    if not header_set:
                        writer = csv.DictWriter(csvfile, fieldnames=row.keys(), delimiter='\t', quoting=csv.QUOTE_NONE)
                        writer.writeheader()
                        header_set = True

                    for key, value in row.items():
                        if key != 'Filename' and float(value) < 0:
                            row[key] = 0

                    writer.writerow(row)