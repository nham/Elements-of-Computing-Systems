package main

import (
    "fmt"
    "os"
    "io/ioutil"
    "strings"
)

type SymbolTable struct {
    table map[string]uint
}

func (st *SymbolTable) setEntry(symbol string, address uint) {
    st.table[symbol] = address
}

func (st *SymbolTable) getAddress(symbol string) uint {
    return st.table[symbol]
}

func (st *SymbolTable) contains(symbol string) bool {
    _, ok := st.table[symbol]
    return ok
}

func initSymbolTable() SymbolTable {
    return SymbolTable{
        table: map[string]uint{
            "SP":     0,
            "LCL":    1,
            "ARG":    2,
            "THIS":   3,
            "THAT":   4,
            "R0":     0,
            "R1":     1,
            "R2":     2,
            "R3":     3,
            "R4":     4,
            "R5":     5,
            "R6":     6,
            "R7":     7,
            "R8":     8,
            "R9":     9,
            "R10":   10,
            "R11":   11,
            "R12":   12,
            "R13":   13,
            "R14":   14,
            "R15":   15,
            "SCREEN": 16384,
            "kbd": 24576,
        },
    }
}

func tokenizeLine(line string) []string {
    punct := [...]string{"@", "=", ";", "(", ")"}
    whitespace := [...]string{" ", "\t"}

    end := len(line) - 1
    commentPos := strings.Index(line, "//")
    if commentPos > -1 {
        end = commentPos
    }

    var start int
    var tokens []string

    for i, c := range line[:end] {
        skip := false
        for _, v := range whitespace {
            if string(c) == v {
                if start < i {
                    tokens = append(tokens, line[start:i])
                }

                start = i + 1
                skip = true
                break
            }
        }

        if skip == true {
            break
        }

        for _, v := range punct {
            if string(c) == v {
                if start < i {
                    tokens = append(tokens, line[start:i])
                }

                tokens = append(tokens, string(c))
                start = i + 1
                break
            }
        }

    }

    if start < end {
        tokens = append(tokens, line[start:end])
    }

    return tokens

}

const (
    A_COMMAND int = iota
    C_COMMAND int = iota
    L_COMMAND int = iota
)

type HackCommand struct {
    cmdType int
    tokens []string
}

func (hc HackCommand) symbol() string {
    if hc.cmdType == C_COMMAND {
        // error or something
        return ""
    }
    return hc.tokens[1]
}

func (hc HackCommand) dest() string {
    if hc.cmdType != C_COMMAND {
        // error or something
        return ""
    }
    return hc.tokens[0]
}

func (hc HackCommand) comp() string {
    if hc.cmdType != C_COMMAND {
        // error or something
        return ""
    }
    return hc.tokens[2]
}

func (hc HackCommand) jump() string {
    if hc.cmdType != C_COMMAND {
        // error or something
        return ""
    }
    return hc.tokens[4]
}

func createHCFromTokens(tokens []string) *HackCommand {
    var cmdType int

    switch tokens[0] {
        case "@":
            cmdType = A_COMMAND
        case "(":
            cmdType = L_COMMAND
        default:
            cmdType = C_COMMAND
    }

    return &HackCommand{
        cmdType: cmdType,
        tokens: tokens,
    }
}


// Reads commands from the input file, each line corresponding to a
// command. The lines are tokenized into a slice
// Comments and blank lines are filtered out.
func readAndTokenize(fname string) [][]string {
    content, _ := ioutil.ReadFile(fname)
    lines := strings.Split(string(content), "\n")

    var tokenizedCmds [][]string

    for i := range lines {
        if len(lines[i]) > 0 {
            tokenizedCmds = append(tokenizedCmds, tokenizeLine(lines[i]))
        }
    }

    return tokenizedCmds
}

func doTheThings(fname string) {
    symtab := initSymbolTable()
    commands := readAndTokenize(fname)

    for i := range commands {
        cmd := createHCFromTokens(commands[i])
        fmt.Println(cmd)
    }

}

func main() {
    if len(os.Args) == 2 {
        doTheThings(os.Args[1])
    }
}
