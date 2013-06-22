package main

import (
    "fmt"
    "os"
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

func doTheThings(args string) {
    symtab := initSymbolTable()
    fmt.Println(symtab)
}

func main() {
    if len(os.Args) == 2 {
        doTheThings(os.Args[1])
    }

}
