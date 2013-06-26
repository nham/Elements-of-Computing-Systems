package main

import (
	"os"
    "fmt"
    "strings"
	//"bufio"
    "wabbo.org/nand2tetris_lib"
)

const (
	C_ARITHMETIC int = iota
	C_PUSH int = iota
	C_POP int = iota
    C_LABEL int = iota
    C_GOTO int = iota
    C_IF int = iota
    C_FUNCTION int = iota
    C_RETURN int = iota
    C_CALL int = iota
)

func tokenizeLine(line string) []string {
	end := len(line) - 1
	commentPos := strings.Index(line, "//")
	if commentPos > -1 {
		end = commentPos
	}

    if end > 0 {
        return strings.Split(line[:end], " ")
    } else {
        return make([]string, 0)
    }
}

func typeofCommand(tokens []string) int {
    cmd := tokens[0]

    lookup := map[string]int{
        "push": C_PUSH,
        "pop": C_POP,
        "label": C_LABEL,
        "goto": C_GOTO,
        "if-goto": C_IF,
        "function": C_FUNCTION,
        "return": C_RETURN,
        "call": C_CALL,
        }

    if v, in := lookup[cmd]; in == false {
        return C_ARITHMETIC
    } else {
        return v
    }
}


func main() {
	if len(os.Args) == 2 {
		path := os.Args[1]
        newFName := path[:strings.Index(path, ".")] + ".asm"
        fmt.Println(newFName)

        cmdtoks := nand2tetris_lib.ReadAndTokenize(path, tokenizeLine)
        for i := range cmdtoks {
            fmt.Println(cmdtoks[i], typeofCommand(cmdtoks[i]))

            switch typeofCommand(cmdtoks[i]) {
                case C_ARITHMETIC:
                    //writer.write_arith(parser.arg1())
                case C_PUSH:
                    fallthrough
                case C_POP:
                    //writer.write_pushpop(cmdtype, parser.arg1(), parser.arg2())
                case C_LABEL:
                    //writer.write_label(parser.arg1())
                case C_GOTO:
                    //writer.write_goto(parser.arg1())
                case C_IF:
                    //writer.write_if(parser.arg1())
                default:
                    //fmt.Println("command unimplemented")
            }
        }
    }
}
