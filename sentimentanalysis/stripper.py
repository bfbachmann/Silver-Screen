input_file = open('lexicon.txt', 'r')
output_file = open('lexicon_done.txt', 'w')

for line in input_file:
    output_file.write(line.rsplit('\t', 2)[0])
    output_file.write('\t')
    output_file.write('\n')

output_file.close()
