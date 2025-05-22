import re

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)})'


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None
        self.keywords = {'if': 'IF', 'else': 'ELSE', 'while': 'WHILE', 'for': 'FOR', 'print': 'PRINT'}  # Store keywords as uppercase

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def id(self):
        result = ''
        while self.current_char is not None and re.match(r'[a-zA-Z_]', self.current_char):
            result += self.current_char
            self.advance()
        token_type = self.keywords.get(result.lower())  # Case-insensitive keyword check
        if token_type:
            return Token(token_type)
        return Token('IDENTIFIER', result)

    def number(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return Token('NUMBER', int(result))

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isalpha():
                return self.id()

            if self.current_char.isdigit():
                return self.number()

            # Multi-character operators
            if self.current_char == '=' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token('EQ')
            if self.current_char == '!' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token('NE')
            if self.current_char == '<' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token('LE')
            if self.current_char == '>' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token('GE')

            # Single-character operators
            if self.current_char == '=':
                self.advance()
                return Token('EQUALS')
            if self.current_char == '<':
                self.advance()
                return Token('LT')
            if self.current_char == '>':
                self.advance()
                return Token('GT')
            if self.current_char == '+':
                self.advance()
                return Token('PLUS')
            if self.current_char == '-':
                self.advance()
                return Token('MINUS')
            if self.current_char == '*':
                self.advance()
                return Token('MULTIPLY')
            if self.current_char == '/':
                self.advance()
                return Token('DIVIDE')
            if self.current_char == '(':
                self.advance()
                return Token('LPAREN')
            if self.current_char == ')':
                self.advance()
                return Token('RPAREN')
            if self.current_char == '{':
                self.advance()
                return Token('LBRACE')
            if self.current_char == '}':
                self.advance()
                return Token('RBRACE')
            if self.current_char == ';':
                self.advance()
                return Token('SEMI')

            self.error()

        return Token('EOF')



class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self, message="Invalid syntax"):  # Added a default message
        raise Exception(message)

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected {token_type}, but got {self.current_token.type}")  # Provide more context

    def parse(self):
        statements = []
        while self.current_token.type != 'EOF':
            statements.append(self.statement())
        return statements

    def statement(self):
        if self.current_token.type == 'IF':
            return self.if_stmt()
        elif self.current_token.type == 'WHILE':
            return self.while_stmt()
        elif self.current_token.type == 'FOR':
            return self.for_stmt()
        elif self.current_token.type == 'IDENTIFIER':
            return self.assign_stmt()
        elif self.current_token.type == 'PRINT':
            return self.print_stmt()
        else:
            return self.expression() # Changed this to expression. A statement can be an expression.

    def if_stmt(self):
        self.eat('IF')
        self.eat('LPAREN')
        condition = self.expression()
        self.eat('RPAREN')
        self.eat('LBRACE')
        body = self.statements()
        self.eat('RBRACE')
        else_body = None
        if self.current_token.type == 'ELSE':
            self.eat('ELSE')
            self.eat('LBRACE')
            else_body = self.statements()
            self.eat('RBRACE')
        return {'type': 'IF', 'condition': condition, 'body': body, 'else_body': else_body}

    def while_stmt(self):
        self.eat('WHILE')
        self.eat('LPAREN')
        condition = self.expression()
        self.eat('RPAREN')
        self.eat('LBRACE')
        body = self.statements()
        self.eat('RBRACE')
        return {'type': 'WHILE', 'condition': condition, 'body': body}

    def for_stmt(self):
        self.eat('FOR')
        self.eat('LPAREN')
        init = self.assign_stmt()  # Corrected: for loop initialization is an assignment
        condition = self.expression()
        self.eat('SEMI')
        update = self.assign_stmt() # Corrected: for loop update is an assignment
        self.eat('RPAREN')
        self.eat('LBRACE')
        body = self.statements()
        self.eat('RBRACE')
        return {'type': 'FOR', 'init': init, 'condition': condition, 'update': update, 'body': body}

    def assign_stmt(self):
        var_name = self.current_token.value
        self.eat('IDENTIFIER')
        self.eat('EQUALS')
        value = self.expression()
        self.eat('SEMI')
        return {'type': 'ASSIGN', 'var_name': var_name, 'value': value}

    def print_stmt(self):
        self.eat('PRINT')
        self.eat('LPAREN')
        expr = self.expression()
        self.eat('RPAREN')
        self.eat('SEMI')
        return {'type': 'PRINT', 'expr': expr}

    def statements(self):
        stmts = []
        # Modified condition to stop at 'RBRACE'
        while self.current_token.type != 'RBRACE':
            stmts.append(self.statement())
        return stmts

    def expression(self):
        return self.comparison() # Start with lowest precedence

    def comparison(self):
        left = self.arithmetic() # Renamed from term to arithmetic, the next level in PEMDAS
        while self.current_token.type in ('EQ', 'NE', 'LT', 'GT', 'LE', 'GE'):
            op = self.current_token
            self.eat(op.type)
            right = self.arithmetic()
            left = {'type': 'BINOP', 'left': left, 'op': op, 'right': right}
        return left

    def arithmetic(self):
        left = self.term()
        while self.current_token.type in ('PLUS', 'MINUS'):
            op = self.current_token
            self.eat(op.type)
            right = self.term()
            left = {'type': 'BINOP', 'left': left, 'op': op, 'right': right}
        return left

    def term(self):
        left = self.factor()
        while self.current_token.type in ('MULTIPLY', 'DIVIDE'):
            op = self.current_token
            self.eat(op.type)
            right = self.factor()
            left = {'type': 'BINOP', 'left': left, 'op': op, 'right': right}
        return left

    def factor(self):
        token = self.current_token
        if token.type == 'NUMBER':
            self.eat('NUMBER')
            return {'type': 'NUMBER', 'value': token.value}
        elif token.type == 'IDENTIFIER':
            self.eat('IDENTIFIER')
            return {'type': 'IDENTIFIER', 'value': token.value}
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            expr = self.expression()
            self.eat('RPAREN')
            return expr
        elif token.type == 'MINUS': #handle unary minus
            self.eat('MINUS')
            return {'type': 'UNARYOP', 'op': 'MINUS', 'expr': self.factor()} #factor handles the next operand
        elif token.type == 'PLUS': #handle unary plus.
            self.eat('PLUS')
            return {'type': 'UNARYOP', 'op': 'PLUS', 'expr': self.factor()}
        else:
            self.error("Invalid factor") # Improved error message

import re

# ... (Token, Lexer, Parser classes unchanged)

class Interpreter:
    def __init__(self, parser, global_scope=None):
        self.parser = parser
        self.global_scope = global_scope if global_scope is not None else {}

    def interpret(self):
        tree = self.parser.parse()
        for stmt in tree:
            self.visit(stmt)

    def visit(self, node):
        if not node:
            return None
        method_name = f'visit_{node["type"].lower()}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        raise Exception(f'No visit_{node["type"].lower()} method for {node}')

    def visit_if(self, node):
        condition_value = self.visit(node['condition'])
        if condition_value:
            for stmt in node['body']:
                self.visit(stmt)
        elif node['else_body']:
            for stmt in node['else_body']:
                self.visit(stmt)

    def visit_while(self, node):
        while self.visit(node['condition']):
            for stmt in node['body']:
                self.visit(stmt)

    def visit_for(self, node):
        self.visit(node['init'])
        while self.visit(node['condition']):
            for stmt in node['body']:
                self.visit(stmt)
            self.visit(node['update'])

    def visit_assign(self, node):
        var_name = node['var_name']
        value = self.visit(node['value'])
        self.global_scope[var_name] = value

    def visit_print(self, node):
        value = self.visit(node['expr'])
        print(value)

    def visit_binop(self, node):
        left = self.visit(node['left'])
        right = self.visit(node['right'])
        op_type = node['op'].type
        if op_type == 'PLUS':
            return left + right
        elif op_type == 'MINUS':
            return left - right
        elif op_type == 'MULTIPLY':
            return left * right
        elif op_type == 'DIVIDE':
            if right == 0:
                raise ZeroDivisionError("Division by zero")
            return left / right
        elif op_type == 'EQ':
            return left == right
        elif op_type == 'NE':
            return left != right
        elif op_type == 'LT':
            return left < right
        elif op_type == 'GT':
            return left > right
        elif op_type == 'LE':
            return left <= right
        elif op_type == 'GE':
            return left >= right
        else:
            raise Exception(f"Unsupported binary operator: {op_type}")

    def visit_unaryop(self, node):
        expr_value = self.visit(node['expr'])
        if node['op'] == 'MINUS':
            return -expr_value
        elif node['op'] == 'PLUS':
            return +expr_value
        else:
            raise Exception(f"Unsupported unary operator: {node['op']}")

    def visit_number(self, node):
        return node['value']

    def visit_identifier(self, node):
        var_name = node['value']
        if var_name in self.global_scope:
            return self.global_scope[var_name]
        else:
            raise NameError(f"Variable '{var_name}' is not defined")

# Main REPL loop with persistent global_scope
def main():
    global_scope = {}
    while True:
        try:
            lines = []
            open_braces = 0
            while True:
                text = input("? ")
                if text.strip().lower() == "exit":
                    return
                lines.append(text)
                open_braces += text.count('{') - text.count('}')
                # If all opened braces are closed, break (or if no braces were used)
                if open_braces <= 0 and (not lines[-1].strip() or lines[-1].strip().endswith(';') or lines[-1].strip() == '}'):
                    break
            code = '\n'.join(lines)
            if not code.strip():
                continue
            lexer = Lexer(code)
            parser = Parser(lexer)
            interpreter = Interpreter(parser, global_scope)
            interpreter.interpret()
            global_scope = interpreter.global_scope
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()


