import sys
import fileinput
import os

path = ""
for filePath in os.listdir(path):

    # replace all occurrences of 'sit' with 'SIT' and insert a line after the 5th
    for line in (fileinput.input(os.path.join(path,filePath), inplace=1)):
        # sys.stdout.write(line.replace('sit', 'SIT'))  # replace 'sit' and write
        # if i == 4: sys.stdout.write('\n')  # write a blank line after the 5th line
        if line[0] == "2":
            sys.stdout.write(line.replace(line[0], '5', 1))
        elif line[0] == "5":
            sys.stdout.write(line.replace(line[0], '2', 1))
        else:
            sys.stdout.write(line)

