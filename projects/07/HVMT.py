import sys, os

class TranslatorException(Exception):
    pass

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
            'if-goto': C_IF,
            'function': C_FUNCTION,
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


class CodeWriter:
    pushDtostack = ['@SP', 'A=M', 'M=D', 'D=A+1', '@SP', 'M=D']
    popstacktoD  = ['@SP', 'D=M', 'AM=D-1', 'D=M']

    def __init__(self, path):
        self.f = open(path, 'w')
        self.labelcount = 0


    def translate_pushpop(self, cmd, segment, index):
        storeDinRN = lambda n: ['@R'+str(n), 'M=D']
        pushDtostack = CodeWriter.pushDtostack
        popstacktoD = CodeWriter.popstacktoD

        if (segment not in 
                ['argument', 'local', 'static', 'constant',
                 'this', 'that', 'pointer', 'temp']):
            raise TranslatorException('Invalid segment')

        if not (index.isdigit() and int(index) >= 0 and int(index) <= 32767):
            raise TranslatorException('Invalid constant')


        ldind = '@'+index

        if segment == 'local':
            reg = '@LCL'
        elif segment == 'argument':
            reg = '@ARG'
        elif segment == 'this':
            reg = '@THIS'
        elif segment == 'that':
            reg = '@THAT'
        elif segment != 'constant':
            if segment == 'pointer':
                addr = 3
            elif segment == 'temp':
                addr = 5
            elif segment == 'static':
                addr = 16

            addr = '@'+str(addr + int(index))

        dedicated = ['local', 'argument', 'this', 'that']
        fixed = ['pointer', 'temp', 'static']

        if cmd == C_PUSH:
            if segment == 'constant':
                return [ldind, 'D=A'] + pushDtostack

            elif segment in dedicated:
                return [reg, 'D=M', ldind, 'A=A+D', 'D=M'] + pushDtostack

            elif segment in fixed:
                return [addr, 'D=M'] + pushDtostack

        elif cmd == C_POP:
            if segment in dedicated:
                return (popstacktoD + storeDinRN(13)
                + [reg, 'D=M', ldind, 'D=D+A']
                + storeDinRN(14) + ['@R13', 'D=M', '@R14', 'A=M', 'M=D'])

            elif segment in fixed:
                return popstacktoD + [addr, 'M=D']


    def translate_arith(self, cmd):
        pushDtostack = CodeWriter.pushDtostack
        popstacktoD = CodeWriter.popstacktoD

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

            lab1 = '$LAB'+str(self.labelcount)
            lab2 = '$LAB'+str(self.labelcount+1)
            self.labelcount += 2

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


    def translate_if(self, arg1):
        return CodeWriter.popstacktoD + ['@'+arg1, 'D;JNE']


    def write_pushpop(self, command, segment, index):
        assembly = self.translate_pushpop(command, segment, index)
        self.f.write('\n'.join(assembly)+'\n')

    def write_arith(self, command):
        assembly = self.translate_arith(command)
        self.f.write('\n'.join(assembly)+'\n')

    def write_if(self, label):
        assembly = self.translate_if(label)
        self.f.write('\n'.join(assembly)+'\n')

    def write_label(self, label):
        assembly = '('+label+')'
        self.f.write(assembly+'\n')

    def write_goto(self, label):
        assembly = ['@'+label, '0;JMP']
        self.f.write('\n'.join(assembly)+'\n')


def doTheThings(path):
    fext = lambda s: s[s.index('.'):]

    if '.' not in path or fext(path) != ".vm":
        raise TranslatorException('Bad file name')

    parser = Parser(path)
    writer = CodeWriter(path[:path.index('.')] + '.asm')
    print(path)
    print('--------------')

    while parser.advance():
        print('translating ', end='')
        print(parser.currcmd, end='...')
        cmdtype = parser.commandType()

        if cmdtype == C_ARITHMETIC:
            writer.write_arith(parser.arg1())
        elif cmdtype in [C_PUSH, C_POP]:
            writer.write_pushpop(cmdtype, parser.arg1(), parser.arg2())
        elif cmdtype == C_LABEL:
            writer.write_label(parser.arg1())
        elif cmdtype == C_GOTO:
            writer.write_goto(parser.arg1())
        elif cmdtype == C_IF:
            writer.write_if(parser.arg1())
        else:
            return "command unimplemented"

        print('done.')
                

if __name__ == "__main__":
    if len(sys.argv) == 2:
        doTheThings(sys.argv[1])

