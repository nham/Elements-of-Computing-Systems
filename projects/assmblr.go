package main

import (
	"bufio"
	"fmt"
	"io/ioutil"
	"os"
	"strconv"
	"strings"
)

var destLookup map[string]string = map[string]string{
	"null": "000",
	"M":    "001",
	"D":    "010",
	"MD":   "011",
	"A":    "100",
	"AM":   "101",
	"AD":   "110",
	"AMD":  "111",
}

var compLookup map[string]string = map[string]string{
	"0":   "0101010",
	"1":   "0111111",
	"-1":  "0111010",
	"D":   "0001100",
	"A":   "0110000",
	"M":   "1110000",
	"!D":  "0001101",
	"!A":  "0110001",
	"!M":  "1110001",
	"-D":  "0001111",
	"-A":  "0110011",
	"-M":  "0110011",
	"D+1": "0011111",
	"A+1": "0110111",
	"M+1": "1110111",
	"D-1": "0001110",
	"A-1": "0110010",
	"M-1": "1110010",
	"D+A": "0000010",
	"D+M": "1000010",
	"D-A": "0010011",
	"D-M": "1010011",
	"A-D": "0000111",
	"M-D": "1000111",
	"D&A": "0000000",
	"D&M": "1000000",
	"D|A": "0010101",
	"D|M": "1010101",
}

var jumpLookup map[string]string = map[string]string{
	"null": "000",
	"JGT":  "001",
	"JEQ":  "010",
	"JGE":  "011",
	"JLT":  "100",
	"JNE":  "101",
	"JLE":  "110",
	"JMP":  "111",
}

func C_CMDToBin(hc *HackCommand) string {
	dest, comp, jump := "", "", ""
	compOff := 0

	if hc.tokens[1] == "=" {
		dest = destLookup[hc.tokens[0]]
		compOff = 2
	} else {
		dest = destLookup["null"]
	}

	comp = compLookup[hc.tokens[compOff]]

	if len(hc.tokens) > compOff+1 {
		jump = jumpLookup[hc.tokens[compOff+2]]
	} else {
		jump = jumpLookup["null"]
	}

	return "111" + comp + dest + jump
}

func L_CMDToBin(hc *HackCommand, st *SymbolTable, i uint) {
	symbol := hc.tokens[1]

	if !st.contains(symbol) {
		st.setEntry(symbol, i)
	} else {
		// error, I assume, trying to redefine the label.
	}
}

func A_CMDToBin(hc *HackCommand, st *SymbolTable, counter func() int) string {
	// its either a digit, so parse it directly
	// or a symbol, so look up in the symbol table
	symbol := hc.tokens[1]
	i, err := strconv.ParseInt(symbol, 10, 0)

	if err != nil {
		if st.contains(symbol) {
			i = int64(st.table[symbol])
		} else {
			newi := counter()
			st.setEntry(symbol, uint(newi))
			i = int64(newi)
		}
	}

	return fmt.Sprintf("%016v", strconv.FormatInt(i, 2))
}

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
			"R10":    10,
			"R11":    11,
			"R12":    12,
			"R13":    13,
			"R14":    14,
			"R15":    15,
			"SCREEN": 16384,
			"kbd":    24576,
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
			continue
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
	tokens  []string
}

func createHC(tokens []string) *HackCommand {
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
		tokens:  tokens,
	}
}

// Reads commands from the input file, each line corresponding to a
// command. The lines are tokenized into a slice
// Comments and blank lines are filtered out.
func readAndTokenize(fname string, tokenizer func(line string) []string) [][]string {
	content, _ := ioutil.ReadFile(fname)
	lines := strings.Split(string(content), "\n")

	var tokenizedCmds [][]string

	for i := range lines {
		if len(lines[i]) > 0 {
			tmp := tokenizer(lines[i])
			if len(tmp) > 0 {
				tokenizedCmds = append(tokenizedCmds, tmp)
			}
		}
	}

	return tokenizedCmds
}

func makeCounter(start, inc int) func() int {
	start -= 1
	return func() int {
		start += inc
		return start
	}
}

func createHCs(cmds [][]string) [](*HackCommand) {
	hcs := make([](*HackCommand), len(cmds))
	for i := 0; i < len(cmds); i++ {
		hcs[i] = createHC(cmds[i])
	}

	return hcs
}

func main() {
	if len(os.Args) == 2 {
		fname := os.Args[1]
		symtab := initSymbolTable()
		commands := createHCs(readAndTokenize(fname, tokenizeLine))

		var icount uint = 0 // the index of the *next* command

		// pass 1: add labels to symbol table
		for i := range commands {
			cmd := commands[i]

			if commands[i].cmdType == L_COMMAND {
				L_CMDToBin(cmd, &symtab, icount)
			} else {
				icount += 1
			}
		}

		varCounter := makeCounter(16, 1)
		icount = 0
		newFName := fname[:strings.Index(fname, ".")] + ".hack"
		fo, _ := os.Create(newFName)

		write := bufio.NewWriter(fo)

		for i := range commands {
			cmd := commands[i]

			bin := ""
			switch cmd.cmdType {
			case A_COMMAND:
				bin = A_CMDToBin(cmd, &symtab, varCounter)
				icount += 1
			case C_COMMAND:
				bin = C_CMDToBin(cmd)
				icount += 1
			}

			if bin != "" {
				if _, err := write.WriteString(bin + "\n"); err != nil {
					panic(err)
				}

			}
		}

		write.Flush()
	}
}
