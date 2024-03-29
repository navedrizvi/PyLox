from typing import List
from token_ import Token
from token_type import TokenType, keyword_token_map


class Scanner:
    '''Responsible for scanning input characters from source file to tokens parsed by the interpreter.
    
    In: raw user source code
    Out: call scan_tokens() returns list of tokens understood by interpreter
    '''
    def __init__(self, source: str):
        self.source = source
        self.tokens = []

        # Current position tracking
        self.line = 1  # Current line number
        self.starts_at = 0  # First char offset in current lexeme being scanned
        self.current = 0  # Current char being scanned

    def scan_tokens(self) -> List[Token]:
        ''' Core of scanner. Consumes source code characters in a loop

           :return: a list of tokens that are fed to TODO 
         '''
        # Each turn of the loop scans a single token
        while not self._is_at_end():
            self.starts_at = self.current
            self._scan_token()
        final_token = Token('EOF', '', None, self.line)
        self.tokens.append(final_token)

        return self.tokens

    def _advance(self) -> str:
        ''' Returns current characater being consumed'''
        self.current += 1
        return self.source[self.current - 1]

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _is_next_char_in_source(self, expected: chr) -> bool:
        if self._is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def _scan_token(self) -> bool:
        '''Figures out lexeme of the source code character by consuming it 
         and any following chars part of that lexeme. Emits a token ypon reaching end of the lexeme'''

        # Inner-function used as dict dispatcher (alternative for switch-case)
        def stdtoken_switcher(char):
            switcher = {
                #Single char tokens
                '(':
                lambda: self._add_token('LEFT_PAREN'),
                ')':
                lambda: self._add_token('RIGHT_PAREN'),
                '{':
                lambda: self._add_token('LEFT_BRACE'),
                '}':
                lambda: self._add_token('RIGHT_BRACE'),
                ',':
                lambda: self._add_token('COMMA'),
                '.':
                lambda: self._add_token('DOT'),
                '+':
                lambda: self._add_token('PLUS'),
                ';':
                lambda: self._add_token('SEMICOLON'),
                '/':
                lambda: self._add_token('SLASH'),
                '*':
                lambda: self._add_token('STAR'),

                #Handle operators- One or two char tokens
                '!':
                lambda: self._add_token('BANG_EQUAL'
                                        if self._is_next_char_in_source('=')
                                        else 'BANG'),
                "=":
                lambda: self._add_token('EQUAL_EQUAL'
                                        if self._is_next_char_in_source('=')
                                        else 'EQUAL'),
                ">":
                lambda: self._add_token('GREATER_EQUAL'
                                        if self._is_next_char_in_source('=')
                                        else 'GREATER'),
                '<':
                lambda: self._add_token('LESS_EQUAL'
                                        if self._is_next_char_in_source('=')
                                        else 'LESS'),

                #Edge cases
                '/':
                lambda: self._handle_slash_case(),
                '\n':
                lambda: self._incr_line(),
                '"':
                lambda: self._add_string_token(),

                #Ignore white spaces
                ' ':
                lambda: None,
                '\r':
                lambda: None,
                '\t':
                lambda: None,
            }
            try:
                switcher[char]()
                return True
            except KeyError:
                return False

        c = self._advance()
        stdtoken_present = stdtoken_switcher(c)
        if not stdtoken_present:
            digits_present = self._getnumber(c)
            if not digits_present:
                self._getalphanumerics(
                )  # default type for an undientified token is IDENTIFER

    def _getnumber(self, char: str) -> bool:
        if char.isnumeric():
            self._add_number_token()
            return True
        else:
            return False

    def _add_number_token(self):
        ''' Stores integer and floating points '''
        while self._peek().isnumeric():  # consume number digits
            self._advance()

        found_decimal: bool = self._peek() == '.' and self._peek_next(
        ).isnumeric()

        if found_decimal:
            self._advance()  # skip '.'
            while self._peek_next().isnumeric():  # consume decimal digits
                self._advance()
            self._advance()  # consume last decimal digit

        number_str = self.source[self.starts_at:self.current]
        self._add_token('NUMBER', float(number_str))

    def _peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def _add_token(self, token_type, literal=None):
        text = self.source[self.starts_at:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    def _getalphanumerics(self):
        while self._peek().isalnum():
            self._advance()
        text = self.source[self.starts_at:self.current]
        type_ = keyword_token_map.get(text, 'IDENTIFIER')
        self._add_token(type_)

    def _incr_line(self):
        self.line += 1

    def _handle_slash_case(self):
        if self._is_next_char_in_source("/"):
            while (self._peek() != '\n' and not self._is_at_end()):
                self._advance()
        else:
            self._add_token('SLASH')

    def _add_string_token(self):
        ''' Adds the string token present between opening and closing quotes (string literals) '''
        #Consumes characters till ending double quote is reached
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == '\n':
                self.line += 1
            self._advance()

        if self._is_at_end():
            self._Lox_error("Unterminated string.")
            return

        # Creates the Token (string literal) that is interpretable by interpreter
        self._advance()

        first_char_idx = self.starts_at + 1
        last_char_idx = self.current - 1
        value = self.source[first_char_idx:last_char_idx]

        self._add_token('STRING', value)

    def _peek(self) -> str:
        if self._is_at_end():
            return '\0'
        return self.source[self.current]

    def _Lox_error(self, message):
        from lox import Lox
        Lox.error_line(self.line, message)
