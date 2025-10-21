def print_file(filename):
    with open(filename, "r") as fptr:
        for line in fptr.readlines():
            print(line.rstrip("\n"))
