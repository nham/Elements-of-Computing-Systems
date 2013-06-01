import sys, re

class AssemblerException(Exception):
    pass

#lookups

destlookup = {
        'M':   '001',
        'D':   '010',
        'MD':  '011',
        'A':   '100',
        'AM':  '101',
        'AD':  '110',
        'AMD': '111'}

complookup = {
    '0':   '0101010',
    '1':   '0111111',
    '-1':  '0111010',
    'D':   '0001100',
    'A':   '0110000',
    'M':   '1110000',
    '!D':  '0001101',
    '!A':  '0110001',
    '!M':  '1110001',
    '-D':  '0001111',
    '-A':  '0110011',
    '-M':  '0110011',
    'D+1': '0011111',
    'A+1': '0110111',
    'M+1': '1110111',
    'D-1': '0001110',
    'A-1': '0110010',
    'M-1': '1110010',
    'D+A': '0000010',
    'D+M': '1000010',
    'D-A': '0010011',
    'D-M': '1010011',
    'A-D': '0000111',
    'M-D': '1000111',
    'D&A': '0000000',
    'D&M': '1000000',
    'D|A': '0010101',
    'D|M': '1010101'}

jumplookup = {
        'JGT': '001',
        'JEQ': '010',
        'JGE': '011',
        'JLT': '100',
        'JNE': '101',
        'JLE': '110',
        'JMP': '111'}


symbol_table = {
    'SP':     0,
    'LCL':    1,
    'ARG':    2,
    'THIS':   3,
    'THAT':   4,
    'R0':     0,
    'R1':     1,
    'R2':     2,
    'R3':     3,
    'R4':     4,
    'R5':     5,
    'R6':     6,
    'R7':     7,
    'R8':     8,
    'R9':     9,
    'R10':   10,
    'R11':   11,
    'R12':   12,
    'R13':   13,
    'R14':   14,
    'R15':   15,
    'SCREEN': 16384,
    'KBD': 24576}


varsym_mem = 16


def is_symbol(string):
    return re.match('[a-zA-Z_.$][a-zA-Z0-9_.$]*', string) != None


def tokenize_line(line):
    tokens = []
    nexttok = ''
    if len(line) > 1 and line[0:2] == '//':
        return False
        

    for c in line:
        if c in [' ', '\t', '\n']:
            pass

        elif c == '/':
            if nexttok == '/':
                nexttok = ''
                break
            elif nexttok != '':
                tokens.append(nexttok)
                nexttok = c

        elif c in ['@', '=', ';', '(', ')']:
            if nexttok != '':
                tokens.append(nexttok)

            tokens.append(c)
            nexttok = ''

        else:
            nexttok += c

    if nexttok != '':
        tokens.append(nexttok)

    if len(tokens) == 0:
        return False

    print(tokens)
    return tokens

def translate_A(mnem):
    global varsym_mem

    if len(mnem) != 2:
        raise AssemblerException('Invalid A-instruction')


    if mnem[1].isdigit():
        constant = int(mnem[1])
        if constant < 0:
            raise AssemblerException('Constant cannot be negative')
        addr = constant

    else:
        if mnem[1] in symbol_table:
            addr = symbol_table[mnem[1]]
        else:
            addr = varsym_mem
            symbol_table[mnem[1]] = addr
            varsym_mem += 1

    return "{0:016b}".format(addr)


def translate_C(mnem):
    tokoff = 0

    #translate destination
    if '=' in mnem:
        if mnem[1] != '=' or '=' in mnem[2:]:
            raise AssemblerException('"=" is misplaced')

        try:
            dest = destlookup[ mnem[0] ]
        except KeyError:
            raise AssemblerException('invalid destination')

        tokoff = 2

    else:
        dest = '000'


    #translate computation
    try:
        comptoken = mnem[tokoff]

    except IndexError:
        raise AssemblerException('Missing computation section')

    try:
        comp = complookup[comptoken]
    except ValueError:
        raise AssemblerException('Invalid computation')


    # translate jump
    if len(mnem) > tokoff+1:
        if mnem[tokoff+1] != ';':
            raise AssemblerException('Invalid mnemonic following computation')

        jumptoken = mnem[tokoff+2]

        try:
            jump = jumplookup[jumptoken]
        except KeyError:
            raise AssemblerException('invalid jump')
    else:
        jump = '000'


    return '111'+comp+dest+jump



def translate(mnem):
    tokoff = 0

    if len(mnem) > 5:
        raise AssemblerException('Mnemonic too long: it can\'t exceed 5 tokens')

    try:
        if mnem[0] == '@':
            binary = translate_A(mnem)
        else:
            binary = translate_C(mnem)
    except AssemblerException as e:
        raise e


    return binary

def is_label_sym_def(parse):
    if len(parse) == 3:
        if parse[0] == '(' and parse[2] == ')':
            if is_symbol(parse[1]):
                return True
    return False

def parse_file(fname):
    f = open(fname, 'r')
    commands = []
    icount = -1
    for line in f:
        parse = tokenize_line(line)
        if parse != False:
            if is_label_sym_def(parse):
                if parse[1] not in symbol_table:
                    symbol_table[parse[1]] = -1
                else:
                    raise AssemblerException('Trying to define label twice')

            else:
                icount += 1
                commands.append(parse)

                for sym in symbol_table:
                    if symbol_table[sym] == -1:
                        symbol_table[sym] = icount
    f.close()


    icount = 0

    f = open(fname[:fname.index('.')] + '.hack', 'w')
    for cmd in commands:
        try:
            tr = translate(cmd)
            f.write(tr + '\n')
            #print(tr)
            icount += 1
        except AssemblerException as e:
            print('\nTranslation error on instruction '+str(icount)+': \n'+str(e))
            break

    f.close()

    return



if __name__ == "__main__":
    if len(sys.argv) == 2:
        parse_file(sys.argv[1])

# The full process should be:
#  1. tokenize
#  2. pull out label symbols into table
