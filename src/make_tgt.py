import os
import subprocess
import javalang
from tqdm import tqdm
from preprocess import insert_spaces

def main():
    path_to_here = os.path.abspath(os.path.dirname(__file__))
    path_to_datasets = os.path.join(path_to_here, "../Datasets/")
    path_to_list = os.path.join(path_to_here, "../train-val-test-tocompare/")
    files = ["train", "val", "test"]
    for file in files:
        file_name = "src-" + file + "_idx_rebuilt.txt"
        tasklist = []
        with open(os.path.join(path_to_list, file_name), 'r') as list_file:
            tasklist = list_file.readlines()    
        path_to_output = os.path.join(path_to_list, "tgt-" + file + ".txt")
        out = open(path_to_output, 'a') 
        for line in tasklist:

            ## getting tgt line
            dataset, task = line.split(" - ")
            task = task.strip() + ".txt"
            path_to_task = os.path.join(path_to_datasets, dataset, "Tasks", task)
            tgt_line = ""
            with open(path_to_task, 'r') as in_file:
                tgt_line, thrash1, thrash2 = in_file.read().split('\n', 2)

            ## tokenizing
            try:
                tokens = list(javalang.tokenizer.tokenize(tgt_line))
                tokenized_line = ""
                for token in tokens:
                    tokenized_line += token.value + " "
                tokenized_line = tokenized_line.strip() + "\n"
            except:
                print(tgt_line)
                continue

            ## inserting special char for spaces in strings
            final_code = insert_spaces(tokenized_line)

            out.write(final_code)

        out.close()


if __name__=="__main__":
    main()