import textgrid
import glob
import pandas as pd


# 1: Read in textgrids, fix <> issues, output as .txt (run prepare_txt_files__for_G2P())
# 2: Obtain G2P .csv files with X-SAMPA using output .txts: https://clarin.phonetik.uni-muenchen.de/BASWebServices/interface/Grapheme2Phoneme.
#       - tab as output format.
#       - keep annotation markers = yes.
# 3: Modify .csvs to fix single consonant issue (see readme) and export entire lexicon into single .csv.
# 4: Align using Pipeline without ASR (https://clarin.phonetik.uni-muenchen.de/BASWebServices/interface/Pipeline).
#   - The lexicon needs to be used as the exception dictionary.

def main():
    input_tg_dir = "D:\\OneDrive - Radboud Universiteit\\Letterster-annotations\\WebMAUS Aligner\\004_All round 1 data with LEX\\Input Files" # .txts of orthographic transcriptions
    prepare_txt_files_for_G2P(input_tg_dir)


    input_csv_XSAMPA_dir = "D:\\OneDrive - Radboud Universiteit\\Letterster-annotations\\WebMAUS Aligner\\004_All round 1 data alignment with LEX\\Letterster Lexicon" # .csvs containing X-SAMPA
    # # Combining the output files from BAS G2P into a lexicon (.csv files)
    SAMPA_csv_files = get_files_csv(input_csv_XSAMPA_dir)
    print(f"\nNumber of files\t: {len(SAMPA_csv_files)}")

    LEX_df = pd.DataFrame(columns=["orth/X-SAMPA"])

    LEX_df = process_files(SAMPA_csv_files, LEX_df)
    print(LEX_df)

    output_LEX_file = "D:\\OneDrive - Radboud Universiteit\\Letterster-annotations\\WebMAUS Aligner\\004_All round 1 data alignment with LEX\\Letterster Lexicon\\Full Lexicon\\Letterster_LEX.csv"
    export_LEX(LEX_df, output_LEX_file)



def export_LEX(LEX_df, output_LEX_file):
    LEX_df.to_csv(output_LEX_file, index=False, header=None)

def process_files(files, LEX_df):
    for file in files:
        curr_file_trans_df = pd.read_csv(file, header = None)
        curr_file_trans_df.columns = ["orth/X-SAMPA"]
        curr_file_trans_df = fix_single_consonants(curr_file_trans_df)


        LEX_df = pd.concat([LEX_df, curr_file_trans_df], ignore_index=True)
    return(LEX_df)

def simplify_consonants(row):
    # 's x' was added.
    consonant_transcription_map = {
    'E s s e: h a:':'s x','b e:': 'b', 's e:': 's', 'd e:': 'd', 'E f': 'f', 'G e:': 'g', 'h a:': 'h', 'j e:': 'j', 'k a:': 'k',
    'E l': 'l', 'E m': 'm', 'E n': 'n', 'p e:': 'p', 'k y': 'k', 'E r': 'r', 'E s': 's', 't e:': 't',
    'v e:': 'v', 'w e:': 'w', 'I k s': 'k', 'z E t': 'z'
    }
    orth_xsampa = row.split(';')
    if len(orth_xsampa) == 2:
        transcription = orth_xsampa[1]
        for extended, simple in consonant_transcription_map.items():
            transcription = transcription.replace(extended, simple)
        return orth_xsampa[0] + ';' + transcription
    return row
    

def fix_single_consonants(trans_df):
    trans_df['orth/X-SAMPA'] = trans_df['orth/X-SAMPA'].apply(simplify_consonants)

    return trans_df



def get_files_csv(input_csv_XSAMPA_dir):
    file_dir = input_csv_XSAMPA_dir
    files = glob.glob(f"{file_dir}\\*.csv")
    return files

def fix_angulars(orth_trans):
    orth_trans = orth_trans.replace('<', '').replace('>', '')
    orth_trans = orth_trans.replace("ggg", "<ggg>")
    orth_trans = orth_trans.replace("xxx", "<xxx>")

    return orth_trans


def get_files_tg(input_tg_dir):
    file_dir = input_tg_dir
    files = glob.glob(f"{file_dir}\\*.TextGrid")
    return files


def prepare_txt_files_for_G2P(input_tg_dir):
    tg_files = get_files_tg(input_tg_dir)
    print(len(tg_files))

    for file in tg_files:
        tg = textgrid.TextGrid.fromFile(file)
        output_file = file.replace("_checked.TextGrid", ".txt")
    
        tg_orth_trans = tg[0][0].mark
        tg_orth_trans = fix_angulars(tg_orth_trans)
    
        with open(output_file, 'w') as file:
            file.write(tg_orth_trans)

main()