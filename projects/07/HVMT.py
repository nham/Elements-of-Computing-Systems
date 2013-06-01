import sys, os

def tokenize_line(line):
    tokens = []
    currtok = ''
    end = len(line) - 1

    if '//' in line:
        end = line.index('//')

    if len(line[:end]) > 0:
        return line[:end].split()
    else:
        return False

def read_and_tokenize(fname):
    f = open(fname, 'r')
    commands = []
    i = -1
    for line in f:
        tokens = tokenize_line(line)
        if tokens != False:
            i += 1
            commands.append(tokens)

    f.close()
    return commands


def doTheThings(path):
    fext = lambda s: s[s.index('.'):]
    # path is either a file name or a directory name
    if '.' in path:
        ext = fext(path)
        if  ext == '.vm':
            commands = read_and_tokenize(path)
            print(path)
            print('--------------')
            print(commands)
        else:
            raise TranslatorException('Unrecognized file extension "'+ext+'"')
    else:
        # drectory
        for fname in os.listdir(path):
            if fext(fname) == '.vm':
                commands = read_and_tokenize(path+fname)
                print(path)
                print('--------------')
                print(commands)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        doTheThings(sys.argv[1])

