@0
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
@SP
D=M
AM=D-1
D=M
@R13
M=D
@LCL
D=M
@0
D=D+A
@R14
M=D
@R13
D=M
@R14
A=M
M=D
(LOOP_START)
@ARG
D=M
@0
A=A+D
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
@LCL
D=M
@0
A=A+D
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
@SP
D=M
AM=D-1
D=M
A=A-1
M=D+M
D=A+1
@SP
M=D
@SP
D=M
AM=D-1
D=M
@R13
M=D
@LCL
D=M
@0	
D=D+A
@R14
M=D
@R13
D=M
@R14
A=M
M=D
@ARG
D=M
@0
A=A+D
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
@1
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
@SP
D=M
AM=D-1
D=M
A=A-1
M=M-D
D=A+1
@SP
M=D
@SP
D=M
AM=D-1
D=M
@R13
M=D
@ARG
D=M
@0
D=D+A
@R14
M=D
@R13
D=M
@R14
A=M
M=D
@ARG
D=M
@0
A=A+D
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
@SP
D=M
AM=D-1
D=M
@LOOP_START
D;JNE
@LCL
D=M
@0
A=A+D
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
