package main

import (
	"os"
    "fmt"
    "strings"
	"bufio"
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

var popstacktoD []string = []string{"@SP", "D=M", "AM=D-1", "D=M"}
var pushDtostack []string = []string{"@SP", "A=M", "M=D", "D=A+1", "@SP", "M=D"}

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

func translateCommand(command []string) (string, bool) {
    asm := ""
    switch typeofCommand(command) {
        case C_ARITHMETIC:
            asm = translateArith(command[0])
        case C_PUSH:
            fallthrough
        case C_POP:
            // not sure if works :)
            asm = translatePushPop(command[0], command[1], command[2])
        case C_LABEL:
            asm = translateLabel(command[1])
        case C_GOTO:
            asm = translateGoto(command[1])
        case C_IF:
            asm = translateIf(command[1])
        default:
            fmt.Println("command unimplemented")
            return "", false
    }

    return asm, true
}

func translateLabel(symbol string) string {
    return "("+symbol+")"
}

func translateIf(symbol string) string {
    cmds := append(popstacktoD, "@"+symbol, "D;JNE")
    return strings.Join(cmds, "\n")
}

func translateGoto(symbol string) string {
    return strings.Join([]string{"@"+symbol, "0;JMP"}, "\n")
}

func translateArith(command string) string {
    switch command {
        case "add":
            fallthrough
        case "sub":
            fallthrough
        case "and":
            fallthrough
        case "or":
            return translateArithBinary(command)
        case "eq":
            fallthrough
        case "lt":
            fallthrough
        case "gt":
            return translateArithCompare(command)
        case "neg":
            fallthrough
        case "not":
            return translateArithUnary(command)
        default:
            return ""
    }
}


func translateArithBinary(command string) string {
    lookup := map[string]string{
        "add": "D+M",
        "sub": "M-D",
        "and": "D&M",
        "or" : "D|M",
    }

    return strings.Join(
        append(popstacktoD, "A=A-1", "M="+lookup[command], "D=A+1", "@SP", "M=D"),
        "\n")
}

func translateArithCompare(command string) string {
    /*
            lab1 = '$LAB'+str(self.labelcount)
            lab2 = '$LAB'+str(self.labelcount+1)
            self.labelcount += 2

            return (popstacktoD + ['@R13', 'M=D'] + popstacktoD 
                    + ['@R13', 'D=D-M', '@'+lab1, 'D;J'+cmd.upper(), 'D=0']
                    + pushDtostack + ['@'+lab2, '0;JMP', '('+lab1+')', 'D=-1']
                    + pushDtostack + ['('+lab2+')'])
                    */
    return ""
}

func translateArithUnary(command string) string {
    lookup := map[string]string{
        "neg": "!D",
        "not": "-D",
    }

    return strings.Join(
        append(append(popstacktoD, "D="+lookup[command]), pushDtostack...),
        "\n")
}

func translatePushPop(command, segment, index string) string {
    return ""
}


func main() {
	if len(os.Args) == 2 {
		path := os.Args[1]
        newFName := path[:strings.Index(path, ".")] + ".asm"
		fo, _ := os.Create(newFName)
		writer := bufio.NewWriter(fo)

        cmdtoks := nand2tetris_lib.ReadAndTokenize(path, tokenizeLine)
        for i := range cmdtoks {
            fmt.Println(cmdtoks[i], typeofCommand(cmdtoks[i]))
            asm, success := translateCommand(cmdtoks[i])

            if success {
                if _, err := writer.WriteString(asm + "\n"); err != nil {
                    panic(err)
                }
            }
        }
    }
}
