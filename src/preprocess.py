import os
import subprocess
import sys
from tqdm import tqdm
import argparse

def clear(path):
    subprocess.run(["rm", "-rf", path])

def handle_retval(path_to_tmp, retval, call_location):
    if retval != 0:
        clear(path_to_tmp)
        print(f"Problem at {call_location}.")
        sys.exit(1)

def insert_spaces(code):
    newcode = ""
    insquote = False
    indquote = False
    for word in code:
        if word == '"' and not insquote:
            indquote = not indquote
        if word == "'" and not indquote:
            insquote = not insquote
        if word == " " and (insquote or indquote):
            newcode += "<seq2seq4repair_space>"
        else:
            newcode += word
    return newcode

def transform_code(path_to_preprocess, path_to_dataset, task, abcreation_err=subprocess.DEVNULL, tokenization_err=subprocess.DEVNULL, truncation_err=subprocess.DEVNULL, trunc=True):
    path_to_tmp = os.path.join(path_to_preprocess, "tmp/")
    path_to_tasks = os.path.join(path_to_dataset, "Tasks/")
    
    # Create tmp folder                    
    os.mkdir(path_to_tmp)

    # Create buggy file
    with open(os.path.join(path_to_tasks, task), 'r') as in_file:
        head1, head2, data_in = in_file.read().split('\n', 2)
    buggy_file_base_name = os.path.join(path_to_tmp, task.rstrip('.txt'))
    buggy_file_path = buggy_file_base_name + ".java"
    with open(buggy_file_path, 'w') as out_file:
        out_file.writelines(data_in)                                       

    # Get buggy line number
    path_to_sol = os.path.join(path_to_dataset, "Solutions/")
    path_to_sol = os.path.join(path_to_sol, task)
    buggy_line_number = int(open(path_to_sol, 'r').readlines()[0].strip())

    # Create Buggy Context Abstraction
    retval = subprocess.run(["java", "-jar", os.path.join(path_to_preprocess, "abstraction-1.0-SNAPSHOT-jar-with-dependencies.jar"), buggy_file_path, str(buggy_line_number), path_to_tmp], stdout=subprocess.DEVNULL, stderr=abcreation_err)
    if retval.returncode != 0:
        clear(path_to_tmp)
        return False, None, None 

    # Tokenizing                     
    retval = subprocess.run(["python3", os.path.join(path_to_preprocess, "tokenize.py"), buggy_file_base_name+"_abstract.java", buggy_file_base_name+"_abstract_tokenized.txt"], stdout=subprocess.DEVNULL, stderr=tokenization_err)
    #handle_retval(path_to_tmp, retval.returncode, "Tokenization")
    if retval.returncode != 0:
        clear(path_to_tmp)
        return False, None, None  

    # Replacing spaces with <seq2seq4repair_space> inside strings
    code = ""
    with open(buggy_file_base_name+"_abstract_tokenized.txt", 'r') as tokenized_file:
        code = tokenized_file.readlines()[0]
    newcode = insert_spaces(code)
    with open(buggy_file_base_name+"_abstract_tokenized_stringed.txt", 'w') as stringed_file:
        stringed_file.write(newcode)                    
    
    # Truncating
    t_t_a_b_c = ""
    if trunc:
        retval = subprocess.run(["perl", os.path.join(path_to_preprocess, "trimCon.pl"), buggy_file_base_name+"_abstract_tokenized_stringed.txt", buggy_file_base_name+"_abstract_tokenized_truncated.txt", "1000"], stdout=subprocess.DEVNULL, stderr=truncation_err)
        handle_retval(path_to_tmp, retval.returncode, "Truncation")

        # Get truncated tokenized abstract buggy context
        
        t_t_a_b_c = open(buggy_file_base_name+"_abstract_tokenized_truncated.txt", 'r').readlines()[0]
    else:
        t_t_a_b_c = newcode

    # Writing to final location
    clear(path_to_tmp)
    return True, task.strip('.txt')+"\n", t_t_a_b_c
    

def main():
    ## PARAMETERS
    input_folder_name = "Datasets"
    output_folder_name = "New_datasets"

    path_to_preprocess = os.path.abspath(os.path.dirname(__file__))
    path_to_tmp = os.path.join(path_to_preprocess, "tmp/")
    if os.path.exists(path_to_tmp):
        clear(path_to_tmp)
    path_to_datasets = os.path.join(path_to_preprocess, "../" + input_folder_name + "/")
    path_to_outputs = os.path.join(path_to_preprocess, "../" + output_folder_name + "/")    
    abcreation_err = open(os.path.join(path_to_preprocess, "abccreation.out"), 'w')
    tokenization_err = open(os.path.join(path_to_preprocess, "tokenization.out"), 'w')
    truncation_err = open(os.path.join(path_to_preprocess, "truncation.out"), 'w')
    for dataset_dir in os.listdir(path_to_datasets):
        path_to_dataset = os.path.join(path_to_datasets, dataset_dir)
        if(os.path.isdir(path_to_dataset)):
            path_to_output = os.path.join(path_to_outputs, dataset_dir, "abstractions.txt")
            final_abstraction_file = open(path_to_output, 'a')
            path_to_indexes = os.path.join(path_to_outputs, dataset_dir, "indexes.txt")
            final_indexes_file = open(path_to_indexes, 'a')
            for task in tqdm(os.listdir(path_to_tasks)):
                if(task.endswith(".txt")):
                    ok, idx, t_t_a_b_c = transform_code(path_to_preprocess, path_to_dataset, task, abcreation_err, tokenization_err, truncation_err)
                    if ok:
                        final_abstraction_file.write(t_t_a_b_c)
                        final_indexes_file.write(idx)

            final_abstraction_file.close()
            final_indexes_file.close()
    sys.exit()

def rebuild_list():
    path_to_preprocess = os.path.abspath(os.path.dirname(__file__))
    path_to_datasets = os.path.join(path_to_preprocess, "../Datasets/")
    path_to_list = os.path.join(path_to_preprocess, "../train-val-test-tocompare/")
    path_to_outputs = os.path.join(path_to_preprocess, "../train-val-test_touse/")
    path_to_tmp = os.path.join(path_to_preprocess, "tmp/")
    if os.path.exists(path_to_tmp):
        clear(path_to_tmp)
    files = ["train", "val", "test"]
    for file in files:
        file_name = "src-" + file + "_idx_rebuilt.txt"
        list = []
        with open(os.path.join(path_to_list, file_name), 'r') as list_file:
            list = list_file.readlines()    
        path_to_output = os.path.join(path_to_outputs, file + ".txt")
        out = open(path_to_output, 'a')    
        for line in tqdm(list):
            dataset, task = line.split(" - ")
            task = task.strip() + ".txt"
            path_to_dataset = os.path.join(path_to_datasets, dataset)
            ok, idx, t_t_a_b_c = transform_code(path_to_preprocess, path_to_dataset, task, trunc=False)
            if ok:
                out.write(t_t_a_b_c)
        out.close()
    sys.exit()    

def trunc_list():
    path_to_preprocess = os.path.abspath(os.path.dirname(__file__))
    path_to_inputs = os.path.join(path_to_preprocess, "../train-val-test_touse/")
    path_to_outputs = os.path.join(path_to_preprocess, "../train-val-test_touse/truncated/")
    path_to_tmp = os.path.join(path_to_preprocess, "tmp/")
    if os.path.exists(path_to_tmp):
        clear(path_to_tmp)
    files = ["train", "val", "test"]
    for file in files:
        file_name = "src-" + file + ".txt"
        lines = []
        with open(os.path.join(path_to_inputs, file_name), 'r') as file_in:
            lines = file_in.readlines()
        os.mkdir(path_to_tmp)
        out_file_name = os.path.join(path_to_outputs, file_name)
        out_file = open(out_file_name, 'a')
        for line in tqdm(lines):
            untrunc_file = os.path.join(path_to_tmp, "tmp.txt")
            trunc_file = os.path.join(path_to_tmp, "tmp_trunc.txt")
            if os.path.exists(untrunc_file):
                clear(untrunc_file)
            if os.path.exists(trunc_file):
                clear(trunc_file)
            with open(untrunc_file, 'w') as file_out_1:
                file_out_1.write(line)
            retval = subprocess.run(["perl", os.path.join(path_to_preprocess, "trimCon.pl"), untrunc_file, trunc_file, "1000"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            handle_retval(path_to_tmp, retval.returncode, "Truncation")
            with open(trunc_file) as file_in_final:
                toRead = file_in_final.readlines()[0]
                out_file.write(toRead)
        out_file.close()
        clear(path_to_tmp)
            


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", default=False, action="store_true")
    parser.add_argument("-t", default=False, action="store_true")
    args = parser.parse_args()
    if args.r:
        rebuild_list()
    elif args.t:
        trunc_list()
    else:
        main()