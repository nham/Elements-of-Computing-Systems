// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[3], respectively.)

// Put your code here.


// set RAM[2] to 0
@2
M = 0

// load RAM[0] into D
@0
D=M

// if RAM[0] = 0, we can't multiply. so done
@END
D;JEQ

// if RAM[0] > 0, don't need to make it positive
@LOOP
D;JGT

@1
M=-M
@0
M=-M

(LOOP)
    // Add RAM[1] to RAM[2]
    @1
    D=M
    @2
    M=D+M

    // Decrement RAM[0]
    @0
    M=M-1

    D=M
    @LOOP
    D;JGT


(END)
