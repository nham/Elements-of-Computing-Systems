import sys, os

class TranslatorException(Exception):
    pass

arith_commands = ['add', 'sub', 'neg', 'eq',
                  'gt', 'lt', 'and', 'or', 'not']

memaccess_commands = ['push', 'pop']

segments = {
    'argument': 0,
    'local': 0,
    'static': 0,
    'constant': 0,
    'this': 0,
    'that': 0,
    'pointer': 0,
    'temp': 0}

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


def translate(command):
    tokoff = 0
    pushDtostack = ['@SP', 'A=M', 'M=D', 'D=A+1', '@SP', 'M=D']
    popstacktoD  = ['@SP', 'D=M', 'AM=D-1', 'D=M']

    if len(command) > 3:
        raise TranslatorException('Invalid command: too long')

    if command[0] == 'push' and command[1] == 'constant':
        if (
            command[2].isdigit() and 
            int(command[2]) >= 0 and 
            int(command[2]) <= 32767
           ):
            return ['@'+command[2], 'D=A'] + pushDtostack
        else:
            raise TranslatorException('Invalid constant')
    elif command[0] == 'add' and len(command) == 1:
        # maybe we should push D=D+m and then pushDtostack
        return popstacktoD + ['A=A-1', 'M=D+M', 'D=A+1', '@SP', 'M=D']
    else:
        raise TranslatorException('Unimplemented or invalid!')



def assembly_init():
    return ['@256', 'D=A', '@SP', 'M=D']

def doTheThings(path):
    fext = lambda s: s[s.index('.'):]
    # path is either a file name or a directory name
    if '.' in path:
        ext = fext(path)
        if  ext == '.vm':
            commands = read_and_tokenize(path)
        else:
            raise TranslatorException('Unrecognized file extension "'+ext+'"')
    else:
        isdir = True
        commands = []
        for fname in os.listdir(path):
            if fext(fname) == '.vm':
                commands += read_and_tokenize(path+fname)

    if len(commands) > 0:
        assem_out = assembly_init()
        print(path)
        print('--------------')

        for cmd in commands:
            assem_out += translate(cmd)
            print(cmd)
            print(assem_out)
            print('--------------')

            
        f = open(path[:path.index('.')] + '.asm', 'w')
        for ass in assem_out:
            f.write(ass + '\n')

        f.close()
                


if __name__ == "__main__":
    if len(sys.argv) == 2:
        doTheThings(sys.argv[1])

