import os
import subprocess
import sys
from tqdm import tqdm

def clear(path):
    subprocess.run(["rm", "-rf", path])

def handle_retval(path_to_tmp, retval, call_location):
    if retval != 0:
        clear(path_to_tmp)
        print(f"Problem at {call_location}.")
        sys.exit(1)

def main():
    path_to_preprocess = os.path.abspath(os.path.dirname(__file__))
    path_to_tmp = os.path.join(path_to_preprocess, "tmp/")
    if os.path.exists(path_to_tmp):
        clear(path_to_tmp)
    path_to_datasets = os.path.join(path_to_preprocess, "../Datasets/")
    path_to_outputs = os.path.join(path_to_preprocess, "../New_datasets/")    
    abcreation_err = open(os.path.join(path_to_preprocess, "abccreation.out"), 'w')
    tokenization_err = open(os.path.join(path_to_preprocess, "tokenization.out"), 'w')
    truncation_err = open(os.path.join(path_to_preprocess, "truncation.out"), 'w')
    for dataset_dir in os.listdir(path_to_datasets):
        path_to_dataset = os.path.join(path_to_datasets, dataset_dir)
        if(os.path.isdir(path_to_dataset)):
            path_to_tasks = os.path.join(path_to_dataset, "Tasks/")
            path_to_output = os.path.join(path_to_outputs, dataset_dir, "abstractions.txt")
            final_abstraction_file = open(path_to_output, 'a')
            path_to_indexes = os.path.join(path_to_outputs, dataset_dir, "indexes.txt")
            final_indexes_file = open(path_to_indexes, 'a')
            for task in tqdm(os.listdir(path_to_tasks)):
                if(task.endswith(".txt")):

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
                        continue 

                    # Tokenizing                     
                    retval = subprocess.run(["python3", os.path.join(path_to_preprocess, "tokenize.py"), buggy_file_base_name+"_abstract.java", buggy_file_base_name+"_abstract_tokenized.txt"], stdout=subprocess.DEVNULL, stderr=tokenization_err)
                    #handle_retval(path_to_tmp, retval.returncode, "Tokenization")
                    if retval.returncode != 0:
                        clear(path_to_tmp)
                        continue 

                    # Replacing spaces with <seq2seq4repair_space> inside strings
                    code = ""
                    with open(buggy_file_base_name+"_abstract_tokenized.txt", 'r') as tokenized_file:
                        code = tokenized_file.readlines()[0]
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
                    with open(buggy_file_base_name+"_abstract_tokenized_stringed.txt", 'w') as stringed_file:
                        stringed_file.write(newcode)                    
                    
                    # Truncating
                    retval = subprocess.run(["perl", os.path.join(path_to_preprocess, "trimCon.pl"), buggy_file_base_name+"_abstract_tokenized_stringed.txt", buggy_file_base_name+"_abstract_tokenized_truncated.txt", "1000"], stdout=subprocess.DEVNULL, stderr=truncation_err)
                    handle_retval(path_to_tmp, retval.returncode, "Truncation")

                    # Get truncated tokenized abstract buggy context
                    t_t_a_b_c = open(buggy_file_base_name+"_abstract_tokenized_truncated.txt", 'r').readlines()[0]

                    # Writing to final location
                    final_abstraction_file.write(t_t_a_b_c)
                    final_indexes_file.write(task.strip('.txt')+"\n")
                    clear(path_to_tmp)
            final_abstraction_file.close()
            final_indexes_file.close()
    sys.exit()



if __name__=="__main__":
    main()