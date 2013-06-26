package main

import (
	"os"
    "fmt"
    "strings"
	"bufio"
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

func main() {
	if len(os.Args) == 2 {
		path := os.Args[1]
        newFName := path[:strings.Index(path, ".")] + ".asm"

}
