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
    user_goal = input("Please provide which step you want to do:\n\t(A) Convert .TextGrids to .txt files for G2P.\n\t(B) Use the X-SAMPA output .csvs from the WebMAUS G2P and combine them into one lexicon.\n\t")

    if user_goal == "A":
        input_tg_dir = "D:\\OneDrive - Radboud Universiteit\\Letterster-annotations\\WebMAUS Aligner\\004_All round 1 data alignment with LEX\\Input Files"
        prepare_txt_files_for_G2P(input_tg_dir)

    elif user_goal == "B":
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
        curr_file_trans_df = pd.read_csv(file, header=None)
        curr_file_trans_df.columns = ["orth/X-SAMPA"]
        # Apply the fix_single_consonants function here to simplify the consonants
        curr_file_trans_df = fix_single_consonants(curr_file_trans_df)
        
        LEX_df = pd.concat([LEX_df, curr_file_trans_df], ignore_index=True)
    LEX_df = LEX_df.drop_duplicates()
    return LEX_df

def simplify_consonants(row):
    consonant_transcription_map = {
        'E s s e: h a:':'s x',
        'b e:': 'b',
        's e:': 's',
        'd e:': 'd',
        'E f': 'f',
        'G e:': 'x',
        'h a:': 'h',
        'j e:': 'j',
        'k a:': 'k',
        'E l': 'l',
        'E m': 'm',
        'E n': 'n',
        'p e:': 'p',
        'k y': 'k',
        'E r': 'r',
        'E s': 's',
        't e:': 't',
        'v e:': 'v',
        'w e:': 'w',
        'I k s': 'k',
        'z E t': 'z'
    }

    orth_xsampa = row.split(';')
    
    if len(orth_xsampa) == 2:
        orth = orth_xsampa[0]
        transcription = orth_xsampa[1]
        
        # Rule for simplifying consonants
        for extended, simple in consonant_transcription_map.items():
            for consonant in simple.split():
                # Find consonants that are flanked by hyphens in orthography (orth)
                hyphen_pattern = f'-{consonant}-'
                if hyphen_pattern in orth or orth.startswith(f'{consonant}-') or orth.endswith(f'-{consonant}'):
                    # Perform the replacement in the transcription
                    transcription = transcription.replace(extended, simple)

        consonants = "bcdfghjklmnpqrstvwxz"
        
        # Check if 'u' is surrounded by consonants or followed by a hyphen
        for i, char in enumerate(orth):
            if char == 'u':
                is_surrounded_by_consonants = (
                    (i > 0 and orth[i-1] in consonants) and 
                    (i < len(orth)-1 and orth[i+1] in consonants)
                )
                is_followed_by_hyphen = (i < len(orth)-1 and orth[i+1] == '-')
                
                # If either condition is true, replace 'u' with 'Y' in the transcription
                if is_surrounded_by_consonants or is_followed_by_hyphen:
                    transcription = transcription.replace('u', 'Y', 1)
                    
        return orth + ';' + transcription

    return row

def fix_single_consonants(trans_df):
    # Apply simplify_consonants to each row in the dataframe
    trans_df['orth/X-SAMPA'] = trans_df['orth/X-SAMPA'].apply(simplify_consonants)
    trans_df['orth/X-SAMPA'] = trans_df['orth/X-SAMPA'].replace('Yi', 'ui', regex=True)
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