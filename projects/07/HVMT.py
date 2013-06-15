import sys, os

class TranslatorException(Exception):
    pass

labelcount = 0

C_ARITHMETIC, \
C_PUSH, \
C_POP, \
C_LABEL, \
C_GOTO, \
C_IF, \
C_FUNCTION, \
C_RETURN, \
C_CALL = [1,2,3,4,5,6,7,8,9]

class Parser:
    def __init__(self, src):
        self.f = open(src, 'r')
        self.currcmd = None

    def advance(self):
        print('inside advance!')
        line = self.f.readline()
        self.currcmd = self.tokenize_line(line)
        while(not self.currcmd):
            line = self.f.readline()

            if len(line) == 0:
                return False

            self.currcmd = self.tokenize_line(line)


        return True

    def commandType(self):
        cmd = self.currcmd[0]

        lookup = {
            'push': C_PUSH,
            'pop': C_POP,
            'label': C_LABEL,
            'goto': C_GOTO,
            'if': C_IF,
            'func': C_FUNCTION,
            'return': C_RETURN,
            'call': C_CALL
            }

        if cmd not in lookup:
            return C_ARITHMETIC
        else:
            return lookup[cmd]


    def arg1(self):
        if self.commandType() == C_ARITHMETIC:
            return self.currcmd[0]
        else:
            return self.currcmd[1]
        
    def arg2(self):
        return self.currcmd[2]

    def tokenize_line(self, line):
        tokens = []
        currtok = ''
        end = len(line) - 1

        if '//' in line:
            end = line.index('//')

        if len(line[:end]) > 0:
            return line[:end].split()
        else:
            return False


def translate_pushpop(cmd, arg1, arg2):
    pushDtostack = ['@SP', 'A=M', 'M=D', 'D=A+1', '@SP', 'M=D']
    popstacktoD  = ['@SP', 'D=M', 'AM=D-1', 'D=M']
    storeDinRN = lambda n: ['@R'+str(n), 'M=D']

    if (arg1 not in 
            ['argument', 'local', 'static', 'constant',
             'this', 'that', 'pointer', 'temp']):
        raise TranslatorException('Invalid segment')

    if not (arg2.isdigit() and int(arg2) >= 0 and int(arg2) <= 32767):
        raise TranslatorException('Invalid constant')


    ldind = '@'+arg2

    if arg1 == 'local':
        reg = '@LCL'
    elif arg1 == 'argument':
        reg = '@ARG'
    elif arg1 == 'this':
        reg = '@THIS'
    elif arg1 == 'that':
        reg = '@THAT'

    if arg1 == 'pointer':
        addr = 3
    elif arg1 == 'temp':
        addr = 5
    elif arg1 == 'static':
        addr = 16

    reglocs = ['local', 'argument', 'this', 'that']

    if cmd == C_PUSH:
        if arg1 == 'constant':
            return [ldind, 'D=A'] + pushDtostack

        elif arg1 in reglocs:
            return [reg, 'D=M', ldind, 'A=A+D', 'D=M'] + pushDtostack

        elif arg1 in ['pointer', 'temp', 'static']:
            addr = addr + int(arg2)
            return ['@'+str(addr), 'D=M'] + pushDtostack

    elif cmd == C_POP:
        if arg1 in reglocs:
            return (popstacktoD + storeDinRN(13)
            + [reg, 'D=M', ldind, 'D=D+A']
            + storeDinRN(14) + ['@R13', 'D=M', '@R14', 'A=M', 'M=D'])

        elif arg1 in ['pointer', 'temp', 'static']:
            addr = addr + int(arg2)
            return popstacktoD + ['@'+str(addr), 'M=D']


def translate_arith(cmd):
    global labelcount
    pushDtostack = ['@SP', 'A=M', 'M=D', 'D=A+1', '@SP', 'M=D']
    popstacktoD  = ['@SP', 'D=M', 'AM=D-1', 'D=M']

    if cmd in ['add', 'sub', 'and', 'or']:

        if cmd == 'add':
            maincomp = 'D+M'
        elif cmd == 'sub':
            maincomp = 'M-D'
        elif cmd == 'and':
            maincomp = 'D&M'
        elif cmd == 'or':
            maincomp = 'D|M'

        return popstacktoD + ['A=A-1', 'M='+maincomp, 'D=A+1', '@SP', 'M=D']

    elif cmd in ['eq', 'gt', 'lt']:

        lab1 = '$LAB'+str(labelcount)
        lab2 = '$LAB'+str(labelcount+1)
        labelcount += 2

        return (popstacktoD + ['@R13', 'M=D'] + popstacktoD 
                + ['@R13', 'D=D-M', '@'+lab1, 'D;J'+cmd.upper(), 'D=0']
                + pushDtostack + ['@'+lab2, '0;JMP', '('+lab1+')', 'D=-1']
                + pushDtostack + ['('+lab2+')'])

    elif cmd in ['neg', 'not']:

        if cmd == 'neg':
            maincomp = '!D'
        elif cmd == 'not':
            maincomp = '-D'

        return popstacktoD + ['D='+maincomp] + pushDtostack

    else:
        raise TranslatorException('Unimplemented or invalid!')


def doTheThings(path):
    fext = lambda s: s[s.index('.'):]
    # path is either a file name or a directory name
    if '.' in path:
        ext = fext(path)
        if  ext == '.vm':
            parser = Parser(path)
        else:
            raise TranslatorException('Unrecognized file extension "'+ext+'"')
#    else:
#        isdir = True
#        commands = []
#        for fname in os.listdir(path):
#            if fext(fname) == '.vm':
#                commands += read_and_tokenize(path+fname)

    assem_out = []
    print(path)
    print('--------------')

    while parser.advance():
        print('translating ', end='')
        print(parser.currcmd, end='...')

        cmdtype = parser.commandType()

        if cmdtype == C_ARITHMETIC:
            assem_out += translate_arith(parser.arg1())
        elif cmdtype in [C_PUSH, C_POP]:
            assem_out += translate_pushpop(cmdtype, parser.arg1(), parser.arg2())
        else:
            return "command unimplemented"

        print('done.')

    f = open(path[:path.index('.')] + '.asm', 'w')
    for ass in assem_out:
        f.write(ass + '\n')

    f.close()
                

if __name__ == "__main__":
    if len(sys.argv) == 2:
        doTheThings(sys.argv[1])

