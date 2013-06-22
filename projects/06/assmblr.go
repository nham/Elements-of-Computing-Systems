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

func readAndTokenize(fname string) [][]string {
    content, _ := ioutil.ReadFile(fname)
    lines := strings.Split(string(content), "\n")

    for i := range lines {
        if len(lines[i]) > 0 {
            tokens := tokenizeLine(lines[i])
            fmt.Println(tokens)
        }
    }

    return make([][]string, 5)

}

func doTheThings(fname string) {
    symtab := initSymbolTable()
    fmt.Println(symtab)

    fmt.Println(readAndTokenize(fname))

}

func main() {
    if len(os.Args) == 2 {
        doTheThings(os.Args[1])
    }

}
