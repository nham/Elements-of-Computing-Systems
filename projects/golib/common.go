package nand2tetris_lib

import (
	"io/ioutil"
	"strings"
)

// Reads commands from the input file, each line corresponding to a
// command. It also takes a tokenizer function, which splits up each line
// into a slice of strings, each string corresponding to a token
//
// The obvious problem is that it reads the whole file into memory at once
// and returns the entire tokenized output in one slice.
func ReadAndTokenize(fname string, tokenizer func(line string) []string) [][]string {
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
