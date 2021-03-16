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
    path_to_datasets = os.path.join(path_to_preprocess, "../Datasets/")
    path_to_outputs = os.path.join(path_to_preprocess, "../Truncated_Abstract_buggy_contexts/")    
    for dataset_dir in os.listdir(path_to_datasets):
        path_to_dataset = os.path.join(path_to_datasets, dataset_dir)
        if(os.path.isdir(path_to_dataset)):
            path_to_tasks = os.path.join(path_to_dataset, "Tasks/")
            for task in tqdm(os.listdir(path_to_tasks)):
                if(task.endswith(".txt")):

                    # Create tmp folder
                    path_to_tmp = os.path.join(path_to_preprocess, "tmp/")
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
                    retval = subprocess.run(["java", "-jar", os.path.join(path_to_preprocess, "abstraction-1.0-SNAPSHOT-jar-with-dependencies.jar"), buggy_file_path, str(buggy_line_number), path_to_tmp], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    if retval.returncode != 0:
                        clear(path_to_tmp)
                        continue 

                    # Tokenizing                     
                    retval = subprocess.run(["python3", os.path.join(path_to_preprocess, "tokenize.py"), buggy_file_base_name+"_abstract.java", buggy_file_base_name+"_abstract_tokenized.txt"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    #handle_retval(path_to_tmp, retval.returncode, "Tokenization")
                    if retval.returncode != 0:
                        clear(path_to_tmp)
                        continue 

                    # Truncating
                    retval = subprocess.run(["perl", os.path.join(path_to_preprocess, "trimCon.pl"), buggy_file_base_name+"_abstract_tokenized.txt", buggy_file_base_name+"_abstract_tokenized_truncated.txt", "1000"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    handle_retval(path_to_tmp, retval.returncode, "Truncation")

                    # Get truncated tokenized abstract buggy context
                    t_t_a_b_c = open(buggy_file_base_name+"_abstract_tokenized_truncated.txt", 'r').readlines()[0]

                    # Writing to final location
                    path_to_output = os.path.join(path_to_outputs, dataset_dir, "abstractions.txt")
                    with open(path_to_output, 'a') as f:
                        f.write(t_t_a_b_c)
                    clear(path_to_tmp)
    sys.exit()



if __name__=="__main__":
    main()