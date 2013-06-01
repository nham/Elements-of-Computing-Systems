import sys

class AssemblerException(Exception):
    pass

def tokenize_line(line):
    tokens = []
    nexttok = ''
    if len(line) > 1 and line[0:2] == '//':
        return False
        

    for c in line:
        if c in [' ', '\t', '\n']:
            pass

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


def translate(mnem):
    binary = ''
    tokoff = 0

    if len(mnem) > 5:
        raise AssemblerException('Mnemonic too long: it can\'t exceed 5 tokens')

    if mnem[0] == '@':
        binary = "{0:016b}".format(int(''.join(mnem[1:])))
    else:
        if '=' in mnem:
            if mnem[1] != '=' or '=' in mnem[2:]:
                raise AssemblerException('"=" is misplaced')

            # so theres a destination. translate it
            destlookup = {
                    'M':   '001',
                    'D':   '010',
                    'MD':  '011',
                    'A':   '100',
                    'AM':  '101',
                    'AD':  '110',
                    'AMD': '111'}
            try:
                dest = destlookup[ mnem[0] ]
            except KeyError:
                raise AssemblerException('invalid destination')

            tokoff = 2

        else:
            dest = '000'

        try:
            comptoken = mnem[tokoff]

        except IndexError:
            raise AssemblerException('Missing computation section')

        try:
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
            comp = complookup[comptoken]
        except ValueError:
            raise AssemblerException('Invalid computation')

        if len(mnem) > tokoff+1:
            if mnem[tokoff+1] != ';':
                raise AssemblerException('Invalid mnemonic following computation')

            jumptoken = mnem[tokoff+2]

            jumplookup = {
                    'JGT': '001',
                    'JEQ': '010',
                    'JGE': '011',
                    'JLT': '100',
                    'JNE': '101',
                    'JLE': '110',
                    'JMP': '111'}
            try:
                jump = jumplookup[jumptoken]
            except KeyError:
                raise AssemblerException('invalid jump')
        else:
            jump = '000'


        binary = '111'+comp+dest+jump



    return binary

def parse_file(fname):
    f = open(fname, 'r')
    bininsts = []
    ln = 1
    for line in f:
        parse = tokenize_line(line)
        if parse != False:
            try:
                tr = translate(parse)
                bininsts.append(tr)
                print(tr)
            except AssemblerException as e:
                print('\nTranslation error on line '+str(ln)+': \n'+str(e))
                break

        ln += 1

    f.close()

    print(fname.index('.'))
    f = open(fname[:fname.index('.')] + '.hack', 'w')
    f.write('\n'.join(bininsts) + '\n')
    f.close()

    return bininsts



if __name__ == "__main__":
    if len(sys.argv) == 2:
        parse_file(sys.argv[1])
