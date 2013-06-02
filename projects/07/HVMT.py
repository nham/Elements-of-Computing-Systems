import sys, os

class TranslatorException(Exception):
    pass

labelcount = 0

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
    global labelcount
    pushDtostack = ['@SP', 'A=M', 'M=D', 'D=A+1', '@SP', 'M=D']
    popstacktoD  = ['@SP', 'D=M', 'AM=D-1', 'D=M']
    storeDinRN = lambda n: ['@R'+str(n), 'M=D']

    if len(command) > 3:
        raise TranslatorException('Invalid command: too long')

    vmcmd = command[0]

    if vmcmd in ['push', 'pop']:
        seg = command[1]

    if vmcmd == 'push':
        if seg == 'constant':
            if (
                command[2].isdigit() and 
                int(command[2]) >= 0 and 
                int(command[2]) <= 32767
               ):
                return ['@'+command[2], 'D=A'] + pushDtostack
            else:
                raise TranslatorException('Invalid constant')

        elif seg in ['local', 'argument', 'this', 'that']:
            pass

    elif vmcmd == 'pop' and seg in ['local', 'argument', 'this', 'that']:
        if seg == 'local':
            reg = '@LCL'
        elif seg == 'argument':
            reg = '@ARG'
        elif seg == 'this':
            reg = '@THIS'
        elif seg == 'that':
            reg = '@THAT'

        return (popstacktoD + storeDinRN(13)
        + [reg, 'D=M', '@'+command[2], 'D=D+A']
        + storeDinRN(14) + ['@R13', 'D=M', '@R14', 'A=M', 'M=D'])

    elif vmcmd == 'pop' and seg in ['pointer', 'temp']:
        if seg == 'pointer':
            addr = 3
        else:
            addr = 5

        addr = addr + int(command[2])

        x = popstacktoD + ['@'+str(addr), 'M=D']
        return x

    elif (vmcmd in ['add', 'sub', 'and', 'or'] 
            and len(command) == 1):

        if vmcmd == 'add':
            maincomp = 'D+M'
        elif vmcmd == 'sub':
            maincomp = 'M-D'
        elif vmcmd == 'and':
            maincomp = 'D&M'
        elif vmcmd == 'or':
            maincomp = 'D|M'

        return popstacktoD + ['A=A-1', 'M='+maincomp, 'D=A+1', '@SP', 'M=D']

    elif vmcmd in ['eq', 'gt', 'lt']  and len(command) == 1:

        lab1 = 'LAB'+str(labelcount)
        lab2 = 'LAB'+str(labelcount+1)
        labelcount += 2

        return (popstacktoD + ['@R13', 'M=D'] + popstacktoD 
                + ['@R13', 'D=D-M', '@'+lab1, 'D;J'+vmcmd.upper(), 'D=0']
                + pushDtostack + ['@'+lab2, '0;JMP', '('+lab1+')', 'D=-1']
                + pushDtostack + ['('+lab2+')'])

    elif vmcmd in ['neg', 'not'] and len(command) == 1:

        if vmcmd == 'neg':
            maincomp = '!D'
        elif vmcmd == 'not':
            maincomp = '-D'

        return popstacktoD + ['D='+maincomp] + pushDtostack

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

            
        f = open(path[:path.index('.')] + '.asm', 'w')
        for ass in assem_out:
            f.write(ass + '\n')

        f.close()
                


if __name__ == "__main__":
    if len(sys.argv) == 2:
        doTheThings(sys.argv[1])

