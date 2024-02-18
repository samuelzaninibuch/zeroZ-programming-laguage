import sys

class Interpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}

    def execute(self, code):
        lines = code.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith('println'):
                self.println(line)
            elif ':' in line and '=' in line:
                if 'input(' in line and ')' in line:
                    self.input_variable(line)
                else:
                    self.assign_variable(line)
            elif line.startswith('function'):
                # Find the end of the function body
                body = []
                i += 1
                while i < len(lines) and not lines[i].startswith('}'):
                    body.append(lines[i])
                    i += 1
                body = '\n'.join(body)
                self.define_function(line, body)
            elif line.startswith('if'):
                # Find the end of the if block
                condition_body = []
                i += 1
                while i < len(lines) and not lines[i].startswith('}'):
                    condition_body.append(lines[i])
                    i += 1
                condition_body = '\n'.join(condition_body)
                if self.evaluate_if_else(line, condition_body):
                    # Skip the else and else if blocks if the if block was executed
                    while i < len(lines) and (lines[i].startswith('else if') or lines[i].startswith('else')):
                        i += 1
                        while i < len(lines) and not lines[i].startswith('}'):
                            i += 1
            elif line.startswith('else if'):
                # Find the end of the else if block
                condition_body = []
                i += 1
                while i < len(lines) and not lines[i].startswith('}'):
                    condition_body.append(lines[i])
                    i += 1
                condition_body = '\n'.join(condition_body)
                if self.evaluate_if_else(line, condition_body):
                    # Skip the else block if the else if block was executed
                    while i < len(lines) and lines[i].startswith('else'):
                        i += 1
                        while i < len(lines) and not lines[i].startswith('}'):
                            i += 1
            elif line.startswith('else'):
                # Find the end of the else block
                body = []
                i += 1
                while i < len(lines) and not lines[i].startswith('}'):
                    body.append(lines[i])
                    i += 1
                body = '\n'.join(body)
                self.execute(body)
            elif '(' in line and ')' in line:
                self.call_function(line)
            i += 1

    def evaluate_if_else(self, line, body):
        condition = line[line.find('(')+1:line.find(')')]
        # Replace variable names in the condition with their values
        for var_name, value in self.variables.items():
            condition = condition.replace(var_name, str(value) if isinstance(value, str) else repr(value))
        # Evaluate the condition
        if eval(condition):
            self.execute(body)
            return True
        return False

    def input_variable(self, line):
        name_type, _ = line.split('=')
        name, var_type = name_type.split(':')
        name = name.strip()
        var_type = var_type.strip()

        # Check if there is a prompt
        prompt = None
        if '(' in _ and ')' in _:
            prompt = _[_.find('(')+1:_.find(')')-1]  # -1 to remove the closing quote
            if prompt.startswith('"') and prompt.endswith('"'):
                prompt = prompt[1:-1]  # remove the quotes

        # Handle different types
        if var_type == 'int':
            self.variables[name] = int(input(prompt)) if prompt else int(input())
        elif var_type == 'char':
            self.variables[name] = str(input(prompt)) if prompt else str(input())
        elif var_type == 'string':
            self.variables[name] = str(input(prompt)) if prompt else str(input())
        elif var_type in ['float', 'double']:
            self.variables[name] = float(input(prompt)) if prompt else float(input())
        else:
            print(f"Error: Unknown type {var_type}")

    def println(self, line):
        # Remove 'println(' from the start and ')' from the end
        content = line.strip()[8:-1]
        # Check if content is a variable name
        if content in self.variables:
            print(self.variables[content])
        else:
            # It's a string, remove the quotes
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
            # Split the content into string literals and variable placeholders
            parts = content.split('{')
            for i in range(len(parts)):
                if '}' in parts[i]:
                    var_name, rest = parts[i].split('}', 1)
                    # Replace the variable placeholder with its value
                    if var_name in self.variables:
                        parts[i] = str(self.variables[var_name]) + rest
                    else:
                        print(f"Error: Variable {var_name} not found.")
            # Join the parts back together and print the result
            print(''.join(parts))

    def assign_variable(self, line):
        name_type, value = line.split('=')
        name, var_type = name_type.split(':')
        name = name.strip()
        var_type = var_type.strip()
        value = value.strip()

        # Handle different types
        if var_type == 'int':
            self.variables[name] = int(eval(value))
        elif var_type == 'char':
            self.variables[name] = str(value)
        elif var_type == 'string':
            self.variables[name] = str(value)
        elif var_type in ['float', 'double']:
            self.variables[name] = float(eval(value))
        else:
            print(f"Error: Unknown type {var_type}")


    def define_function(self, line, body):
        # Remove 'function ' from the start
        header = line[9:]
        name_args = header.split('(')
        name = name_args[0].strip()
        args = name_args[1][:-1].split(',')
        arg_names = [arg.split(':')[0].strip() if ':' in arg else arg.strip() for arg in args]
        arg_types = [arg.split(':')[1].strip() if ':' in arg else 'int' for arg in args]  # default to 'int' if no type specified
        # Remove the closing parenthesis from the last argument type
        if arg_types[-1].endswith(')'):
            arg_types[-1] = arg_types[-1][:-1]
        self.functions[name] = (arg_names, arg_types, body)

    def call_function(self, line):
        name_args = line.split('(')
        name = name_args[0].strip()
        args = [arg.strip() for arg in name_args[1][:-1].split(',')]
        if name in self.functions:
            arg_names, arg_types, body = self.functions[name]
            for i in range(len(args)):
                arg_type = arg_types[i]
                # Check if argument is a variable
                if args[i] in self.variables:
                # Use the variable's value instead of its name
                    args[i] = self.variables[args[i]]
                if arg_type == 'int':
                    self.variables[arg_names[i]] = int(args[i])
                elif arg_type == 'char':
                   self.variables[arg_names[i]] = str(args[i])
                elif arg_type == 'string':
                    self.variables[arg_names[i]] = str(args[i])
                elif arg_type in ['float', 'double']:
                    self.variables[arg_names[i]] = float(args[i])
                else:
                    print(f"Error: Unknown type {arg_type}")
            self.execute(body)
        elif name == 'println':
            self.println(line)
        else:
            print(f"Error: Function {name} not found.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py filename.zz")
    else:
        filename = sys.argv[1]
        if not filename.endswith('.zz'):
            print("Error: File does not have .zz extension.")
        else:
            try:
                code = open(filename, 'r').read()
                interpreter = Interpreter()
                interpreter.execute(code)
            except FileNotFoundError:
                print(f"Error: {filename} not found.")
            except Exception as e:
                print(f"Error: {e}")
