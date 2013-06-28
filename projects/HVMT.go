package main

import (
	"os"
    "fmt"
    "strings"
    "strconv"
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

/* We at least need this label counter to translate arith commands
 * but more generally, we may need to maintain state while translating
 * so we should probably make an object, a CommandTranslator, that takes in
 * the current command and translates into assembly.
 * So it should at least have a pointer to the current command, along with whatever
 * tools it needs to translate all commands. Also there should be a method, translate(),
 * which takes in a tokenized command and returns the ASM.
 *
 * But inside translate, we need to figure out what type of command it is. We also need
 * to pull apart the tokens to call the correct subroutine for translating each command.
 */

type CommandTranslator struct {
    currCommand *([]string)
    currCommandType int
    labelCount int
}

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

func (ct *CommandTranslator) translate(command []string) (string, bool) {
    ct.currCommand = &command
    ct.currCommandType = typeofCommand(command)
    asm := ""
    switch ct.currCommandType {
        case C_ARITHMETIC:
            asm = ct.translateArith(command[0])
        case C_PUSH:
            fallthrough
        case C_POP:
            // not sure if works :)
            asm = ct.translatePushPop(command[0], command[1], command[2])
        case C_LABEL:
            asm = ct.translateLabel(command[1])
        case C_GOTO:
            asm = ct.translateGoto(command[1])
        case C_IF:
            asm = ct.translateIf(command[1])
        default:
            fmt.Println("command unimplemented")
            return "", false
    }

    return asm, true
}

func (ct *CommandTranslator) translateLabel(symbol string) string {
    return "("+symbol+")"
}

func (ct *CommandTranslator) translateIf(symbol string) string {
    cmds := append(popstacktoD, "@"+symbol, "D;JNE")
    return strings.Join(cmds, "\n")
}

func (ct *CommandTranslator) translateGoto(symbol string) string {
    return strings.Join([]string{"@"+symbol, "0;JMP"}, "\n")
}

func (ct *CommandTranslator) translatePushPop(command, segment, index string) string {
    storeDinRN := func(n int) []string { return []string{"@R"+strconv.Itoa(n), "M=D"} }
    ldind := "@"+index

    reg := ""
    switch segment {
        case "local":
            reg = "@LCL"
        case "argument":
            reg = "@ARG"
        case "this":
            reg = "@THIS"
        case "that":
            reg = "@THAT"
        default:
            addr := 0
            if segment == "pointer" {
                addr = 3
            } else if segment == "temp" {
                addr = 5
            } else if segment == "static" {
                addr = 16
            }
            ind, _ := strconv.Atoi(index)
            reg = "@"+strconv.Itoa(addr + ind)
    }

    dedicated := map[string]bool{
        "local": true,
        "argument": true,
        "this": true,
        "that": true,
    }

    fixed := map[string]bool{
        "pointer": true,
        "temp": true,
        "static": true,
    }

    var retcmds []string
    if ct.currCommandType == C_PUSH {
        if segment == "constant" {
            retcmds = append([]string{ldind, "D=A"}, pushDtostack...)
        } else if dedicated[segment] {
            retcmds = append([]string{reg, "D=M", ldind, "A=A+D", "D=M"}, pushDtostack...)
        } else if fixed[segment] {
            retcmds = append([]string{reg, "D=M"}, pushDtostack...)
        }

    } else if ct.currCommandType == C_POP {
        if dedicated[segment] {
            retcmds = append(append(append(append(popstacktoD, storeDinRN(13)...),
            reg, "D=M", ldind, "D=D+A"),
            storeDinRN(14)...), "@R13", "D=M", "@R14", "A=M", "M=D")
        } else if fixed[segment] {
            retcmds = append(popstacktoD, reg, "M=D")
        }

    }

    return strings.Join(retcmds, "\n")

}

func (ct *CommandTranslator) translateArith(command string) string {
    switch command {
        case "add":
            fallthrough
        case "sub":
            fallthrough
        case "and":
            fallthrough
        case "or":
            return ct.translateArithBinary(command)
        case "eq":
            fallthrough
        case "lt":
            fallthrough
        case "gt":
            return ct.translateArithCompare(command)
        case "neg":
            fallthrough
        case "not":
            return ct.translateArithUnary(command)
        default:
            return ""
    }
}


func (ct *CommandTranslator) translateArithBinary(command string) string {
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

func (ct *CommandTranslator) translateArithCompare(command string) string {
    lab1 := "$LAB" + strconv.Itoa(ct.labelCount)
    lab2 := "$LAB"+strconv.Itoa(ct.labelCount+1)
    ct.labelCount += 2

    // I no longer recall what these do. lol?
    tmp := append(append(popstacktoD, "@R13", "M=D"), popstacktoD...)
    tmp = append(tmp, "@R13", "D=D-M", "@"+lab1, "D;J"+strings.ToUpper(command), "D=0")
    tmp = append(append(tmp, pushDtostack...), "@"+lab2, "0;JMP", "("+lab1+")", "D=-1")
    tmp = append(append(tmp, pushDtostack...), "("+lab2+")")
    return strings.Join(tmp, "\n")
}

func (ct *CommandTranslator) translateArithUnary(command string) string {
    lookup := map[string]string{
        "neg": "!D",
        "not": "-D",
    }

    return strings.Join(
        append(append(popstacktoD, "D="+lookup[command]), pushDtostack...),
        "\n")
}

func main() {
	if len(os.Args) == 2 {
		path := os.Args[1]
        newFName := path[:strings.Index(path, ".")] + ".asm"
		fo, _ := os.Create(newFName)
		writer := bufio.NewWriter(fo)

        translator := CommandTranslator{
            labelCount: 0,
        }

        cmdtoks := nand2tetris_lib.ReadAndTokenize(path, tokenizeLine)
        for i := range cmdtoks {
            fmt.Println(cmdtoks[i], typeofCommand(cmdtoks[i]))
            asm, success := translator.translate(cmdtoks[i])

            if success {
                if _, err := writer.WriteString(asm + "\n"); err != nil {
                    panic(err)
                }
            }
        }
		writer.Flush()
    }
}
