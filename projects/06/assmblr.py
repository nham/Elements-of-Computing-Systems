import sys

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

    tokens.append(nexttok)

    if len(tokens) == 0:
        return False

    print(tokens)
    return tokens


def translate(mnem):
    binary = ''
    tokoff = 0

    if len(mnem) > 5:
        raise Exception('Mnemonic too long: it can\'t exceed 5 tokens')

    if mnem[0] == '@':
        binary = "{0:016b}".format(int(''.join(mnem[1:])))
    else:
        if '=' in mnem:
            if mnem[1] != '=' or '=' in mnem[2:]:
                raise Exception('"=" is misplaced')

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
                raise Exception('invalid destination')

            tokoff = 2

        else:
            dest = '000'

        try:
            comptoken = mnem[tokoff]
        except IndexError:
            raise Exception('Missing computation section')

        print(' -- '+dest)



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
            except Exception as e:
                print('\nTranslation error on line '+str(ln)+': \n'+str(e))
                break

        ln += 1



if __name__ == "__main__":
    if len(sys.argv) == 2:
        parse_file(sys.argv[1])
