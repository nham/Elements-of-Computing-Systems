import qualified Data.Map as Map

-- lookups
dests = Map.fromList [("null", "000"), ("M", "001"), ("D", "010"), ("MD", "011"),
                      ("A", "100"), ("AM", "101"), ("AD", "110"), ("AMD", "111")]

comps = Map.fromList [("0", "0101010"), ("1", "0111111"), ("-1", "0111010"),
                      ("D", "0001100"), ("A", "0110000"), ("M", "1110000"),
                      ("!D", "0001101"), ("!A", "0110001"), ("!M", "1110001"),
                      ("-D", "0001111"), ("-A", "0110011"), ("-M", "0110011"), 
                      ("D+1", "0011111"), ("A+1", "0110111"), ("M+1", "1110111"),
                      ("D-1", "0001110"), ("A-1", "0110010"), ("M-1", "1110010"),
                      ("D+A", "0000010"), ("D+M", "1000010"), ("D-A", "0010011"), 
                      ("D-M", "1010011"), ("A-D", "0000111"), ("M-D", "1000111"),
                      ("D&A", "0000000"), ("D&M", "1000000"), ("D|A", "0010101"),
                      ("D|M", "1010101")]

jumps = Map.fromList [("null", "000"), ("JGT", "001"), ("JEQ", "010"),
                          ("JGE", "011"), ("JLT", "100"), ("JNE", "101"),
                          ("JLE", "110"), ("JMP", "111")]

-- end lookups

data HackInstruction = A { value :: String} 
                     | C { comp :: String, dest :: String, jump :: String}
type SymbolTable = Map.Map String Int

symTable :: SymbolTable
symTable = Map.fromList [("SP", 0), ("LCL", 1), ("ARG", 2),
                         ("THIS", 3), ("THAT", 4),
                         ("R0", 0), ("R1", 1), ("R2", 2),
                         ("R3", 3), ("R4", 4), ("R5", 5),
                         ("R6", 6), ("R7", 7), ("R8", 8),
                         ("R9", 9), ("R10", 10), ("R11", 11),
                         ("R12", 12), ("R13", 13), ("R14", 14),
                         ("R15", 15), ("SCREEN", 16384), ("kbd", 24576)]

decToBin :: String -> String
decToBin x = reverse $ f x
    where f x = let d = read x :: Int
                    q = show $ d `div` 2
                    r = show $ d `mod` 2
                in if (d == 0) || (d == 1)
                      then x
                      else r ++ (f q)

padStr :: String -> Int -> Char -> String
padStr s n padchar = (take (n - length s) $ repeat padchar) ++ s

-- determines if the string
isNat :: String -> Bool
isNat [] = False
isNat xs = all (`elem` ['0'..'9']) xs

-- doesnt handle translating A-instructions with symbols
toBinary :: HackInstruction -> SymbolTable -> String
toBinary (A v) st = if (isNat v) 
                        then padStr (decToBin v) 16 '0'
                        else let (Just n) = Map.lookup v st
                             in show n

toBinary (C c d j) _ = let Just cStr = Map.lookup c comps 
                           Just dStr = Map.lookup d dests
                           Just jStr = Map.lookup j jumps
                       in "111" ++ cStr ++ dStr ++ jStr
