import qualified Data.Map as Map
import Control.Applicative

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
                       deriving(Show)
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
toBinary :: SymbolTable -> HackInstruction -> String
toBinary st (A v) = if (isNat v) 
                        then padStr (decToBin v) 16 '0'
                        else let (Just n) = Map.lookup v st
                             in show n

toBinary _ (C c d j) = let Just cStr = Map.lookup c comps 
                           Just dStr = Map.lookup d dests
                           Just jStr = Map.lookup j jumps
                       in "111" ++ cStr ++ dStr ++ jStr


translate :: [HackInstruction] -> [String]
translate = map (toBinary symTable)


-- Parsing! --

newtype Parser a = P (String -> [(a, String)])

instance Functor Parser where
    fmap f (P v) = P (\s -> [(f x, s') | (x, s') <- v s])

instance Applicative Parser where
    pure x = P (\s -> [(x, s)])

    (P g) <*> (P h) = P (\s -> [(f a, rest) 
                                | (f, rem) <- g s
                                , (a, rest) <- h rem
                                ])

instance Alternative Parser where
    empty = P (const [])
    (P j) <|> (P k) = P (\s -> j s ++ k s)


unP :: Parser a -> (String -> [(a, String)])
unP (P f) = f

-- takes a Parser and runs it n times in a row.
-- TODO: What is the meaning of running a parser zero times?
parseN :: Int -> Parser a -> Parser [a]
parseN 1 p = (:[]) <$> p
parseN n p = (:) <$> p <*> parseN (n-1) p



getIfTrue :: (Char -> Bool) -> Parser Char
getIfTrue p = P (\s -> case s of
                            [] -> []
                            (x:xs) -> if p x
                                        then [(x, xs)]
                                        else [])

getIfTrueN :: Int -> (Char -> Bool) -> Parser String
getIfTrueN n p = parseN n $ getIfTrue p

{-
getIfTrueN p 1 = (\c -> [c]) <$> getIfTrue p
getIfTrueN p n = (:) <$> (getIfTrue p) <*> (getIfTrueN p (n-1))
    where z = getIfTrue p
-}


getOneOfSet :: String -> Parser Char
getOneOfSet cs = getIfTrue (`elem` cs)

getC :: Char -> Parser Char
getC x = getIfTrue (== x)

getCN :: Int -> Char -> Parser String
getCN n x = parseN n $ getC x


getDigit :: Parser Char
getDigit = getOneOfSet ['0'..'9']
getLower = getOneOfSet ['a'..'z']
getUpper = getOneOfSet ['A'..'Z']
getSpecial = getOneOfSet ['_', '.', '$', ':']

getNonDigit = getLower <|> getUpper <|> getSpecial
getSymbolChar = getNonDigit <|> getDigit

getSymbol = (:) <$> getNonDigit <*> many getSymbolChar

getConstant = many getDigit

-- same as regex's ".*". It matches any string.
getDot :: Parser Char
getDot = getIfTrue (const True)

getDotStar :: Parser String
getDotStar = many getDot


getComment = (++) <$> (getCN 2 '/') <*> getDotStar
    where f s t = s:t:""


parseACmd :: Parser HackInstruction
parseACmd = A <$> (getC '@' *> (getSymbol <|> getConstant))
