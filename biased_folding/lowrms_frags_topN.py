# ""
# Run script as:
# lowrms_frags_topN.py -frag_qual frag_qual3.dat -ntop 3 -fullmer 00001.200.9mers -out 00001.3t200.9mers
# lowrms_frags_topN.py -frag_qual frag_qual9.dat -ntop 3 -fullmer 00001.200.3mers -out 00001.3t200.3mers
#
# Fragment quality input files are obtained by running the r_frag_quality app calculating the rmsd between picked fragments and the input structure.
# r_frag_quality.default.linuxgccrelease -in:file:native input.pdb -f  input.200.3mers -out:qual frag_qual3.dat
#
# Output files with the selected fragments are those used as inputs in standard Rosetta ab initio structure prediction calculations.
#
# ""

from argparse import ArgumentParser

# we need the fragment quality for the 3mers too.
parser = ArgumentParser(description='Get the lowest rms fragments among top N')
parser.add_argument('-frag_qual', type=str,
                    help='frag quality file where rms and score ranking')
parser.add_argument('-nbest_fragments', type=int,
                    default=200, help='fragments among top N')
parser.add_argument('-fullmer', type=str, help='fragment file')
parser.add_argument('-out', type=str, help='output fragment file')
parser.add_argument('-ntop', type=int, default=3,
                    help='how many fragments of lowest rmsd to take')
args = parser.parse_args()

frag_qual_file = args.frag_qual
fullmer = args.fullmer
outfile = args.out
ntop = args.ntop
nbest_fragments = args.nbest_fragments

with open(frag_qual_file, 'r') as f:
    dic = {}
    nfrag = 0
    for line in f.readlines():
        if line.startswith('#'):
            nfrag = 0  # 重置
            continue
        nfrag += 1  # 改window内的第一个frag id.
        pos = int(line.split()[0])
        rmsd = float(line.split()[-3])
        if nfrag == 1:
            dic[pos] = {}
        if nfrag <= nbest_fragments:
            dic[pos][nfrag] = rmsd


# find N lowest rmsd fragments
dic_top = {}
for pos in dic.keys():
    frag_list = dic[pos].items()
    frag_list = (sorted(frag_list, key=lambda t: t[1]))
    top_n_list = frag_list[:ntop]
    # top_n_list =  [(86, 0.13), (83, 0.16), (132, 0.17)]
    dic_top[pos] = [i[0] for i in top_n_list]

# Take best N fragments from 00001.200.9mers
filein = open(fullmer)
fileout = open(outfile, 'w')
for line in filein:
    if 'position' in line:
        pos = int(line.split()[1])
        if pos > 1:
            fileout.write('\n')
        line2 = line.replace('200', '%3i' % (ntop))
        fileout.write(line2)
        prev_frag = 0
        count = 0
        nfrag = 0
    elif line == '\n':
        nfrag += 1

    # and ( line[85]=='P' and line[90]=='F' ): # fragment line
    elif len(line.split()) > 1:
        if nfrag in dic_top[pos]:
            this_frag = nfrag
            if this_frag != prev_frag:
                count += 1
                fileout.write('\n')
                prev_frag = this_frag
            fileout.write(line)
