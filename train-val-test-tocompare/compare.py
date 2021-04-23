import sys 
import argparse
import os

def main(args):
    src_files = []
    src_lens = []
    for src_file in args.src:
        src = open(src_file, "r")
        tmp = src.readlines()
        src_files.append(tmp)
        src_lens.append(len(tmp))
        src.close()

    rebuilt_files = []
    idx_files = []
    for reb_file in args.rebuilt:
        rebuilt = open(reb_file, "r")
        tmp = rebuilt.readlines()
        rebuilt_files += tmp
        rebuilt.close()
        idx_rebuilt = open(reb_file.rstrip('abstractions.txt')+"indexes.txt", 'r')
        tmp_idx = [reb_file + " - " + id for id in idx_rebuilt.readlines()]
        idx_rebuilt.close()
        idx_files += tmp_idx
        

    rebuilt_files = {x.strip():i for i, x in enumerate(rebuilt_files)}

    matches = [0 for i in range(len(src_lens))]
    for index_file in range(len(src_files)):
        file = src_files[index_file]
        idx_out_file = None
        abc_out_file = None
        if args.write:
            name = args.src[index_file].rsplit('/', 1)[1]
            idx_out_file = open(name.rsplit('.', 1)[0]+"_idx_rebuilt.txt", 'w')
            abc_out_file = open(name.rsplit('.', 1)[0]+"_rebuilt.txt", 'w')
        for index_line in range(len(file)):
            line = file[index_line]
            stripped_line = line.strip()
            if len(line) > 0:
                if stripped_line in rebuilt_files:
                    matches[index_file] += 1
                    if args.write:
                        abc_out_file.write(line)
                        idx_out_file.write(idx_files[rebuilt_files[stripped_line]])
        if args.write:
            idx_out_file.close()
            abc_out_file.close()
    for index in range(len(args.src)):
        print(f"We recovered {matches[index]}/{src_lens[index]} ({round((float(matches[index])/float(src_lens[index]))*100, 2)}%) of {args.src[index].rsplit('/', 1)[1]})")

def compare_tgt():
    path_to_here = os.path.abspath(os.path.dirname(__file__))
    path_to_seq = os.path.join(path_to_here, "../SequenceR-datasets/")
    files = ["train", "val", "test"]
    for file in files:
        score = 0
        tot = 0
        ## SEQ 
        # src
        path_to_seq_src = os.path.join(path_to_seq, "src-" + file + ".txt")
        seq_src = []
        with open(path_to_seq_src, 'r') as seq_src_file:
            seq_src = {line.strip():i for i,line in enumerate(seq_src_file.readlines())}
        # tgt
        path_to_seq_tgt = os.path.join(path_to_seq, "tgt-" + file + ".txt")
        seq_tgt = []
        with open(path_to_seq_tgt, 'r') as seq_tgt_file:
            seq_tgt = [line.strip() for line in seq_tgt_file.readlines()]

        ## REBUILT
        #src
        path_to_rebuilt_src = os.path.join(path_to_here, "src-" + file + "_rebuilt.txt")
        rebuilt_src = []
        with open(path_to_rebuilt_src, 'r') as rebuilt_src_file:
            rebuilt_src = [line.strip() for line in rebuilt_src_file.readlines()]
        #tgt
        path_to_rebuilt_tgt = os.path.join(path_to_here, "tgt-" + file + ".txt")
        rebuilt_tgt = []
        with open(path_to_rebuilt_tgt, 'r') as rebuilt_tgt_file:
            rebuilt_tgt = [line.strip() for line in rebuilt_tgt_file.readlines()]

        ## OUTPUT for new tgt
        path_to_new_tgt = os.path.join(path_to_here, "../train-val-test_touse/","tgt-" + file + "_new.txt")
        out = open(path_to_new_tgt, 'a')

        for tgt_line_idx in range(len(rebuilt_tgt)):
            tot += 1
            tgt_line = rebuilt_tgt[tgt_line_idx]
            src_line = rebuilt_src[tgt_line_idx]
            if src_line in seq_src:
                out.write(seq_tgt[seq_src[src_line]].strip()+"\n")
                if seq_tgt[seq_src[src_line]].strip() == tgt_line.strip():
                    score += 1
            else:
                print("how did this code get in the final rebuilt dataset ?")
                continue
        print(f"{score}/{tot} lines of tgt match for file {file}")
        out.close()


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", nargs="+")
    parser.add_argument("--rebuilt", nargs="+")
    parser.add_argument("--write", default=False)
    parser.add_argument("-tgt", default=False, action="store_true")
    args = parser.parse_args()
    if args.tgt:
        compare_tgt()
    else:
        main(args)