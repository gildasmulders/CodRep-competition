import sys 
import argparse

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
        tmp_idx = idx_rebuilt.readlines()
        idx_files += tmp_idx
        idx_rebuilt.close()

    rebuilt_files = [x.strip() for x in rebuilt_files]

    matches = [0 for i in range(len(src_lens))]
    for index_file in range(len(src_files)):
        file = src_files[index_file]
        idx_out_file = None
        abc_out_file = None
        if args.write:
            name = args.src[index_file].rsplit('/', 1)[1]
            idx_out_file = open(name.rstrip('.txt')+"_idx_rebuilt.txt", 'w')
            abc_out_file = open(name.rstrip('.txt')+"_rebuilt.txt", 'w')
        for index_line in range(len(file)):
            line = file[index_line]
            stripped_line = line.strip()
            if len(line) > 0:
                if stripped_line in rebuilt_files:
                    matches[index_file] += 1
                    if args.write:
                        abc_out_file.write(line)
                        idx_out_file.write(idx_files[rebuilt_files.index(stripped_line)])
        if args.write:
            idx_out_file.close()
            abc_out_file.close()
    for index in range(len(args.src)):
        print(f"We recovered {matches[index]}/{src_lens[index]} ({round((float(matches[index])/float(src_lens[index]))*100, 2)}%) of {args.src[index].rsplit('/', 1)[1]})")



if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", nargs="+")
    parser.add_argument("--rebuilt", nargs="+")
    parser.add_argument("--write", default=False)
    args = parser.parse_args()
    main(args)