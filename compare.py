from sys import argv
import ast
import re 
import argparse

class MyTransformer(ast.NodeTransformer):
    __varables = []
    __def = []

    def get_def(self):
        return self.__def
    
    def get_varables(self):
        return self.__varables

    def clean_def(self):
        self.__def = []

    def clean_varables(self):
        self.__varables = []


    def visit_FunctionDef(self, node: ast.FunctionDef) -> any:
        self.__def.append(node.name)
        node.name='Function'
        for i in range(len(node.args.args)):
            self.__args.append(node.args.args[i].arg)
            node.args.args[i].arg = 'arg'
        
        return node
    def visit_Str(self, node): 
        return ast.Str('str: ' + node.s) 
    
    def visit_Assign(self, node: ast.Assign) -> any:
        self.__varables.append(node.targets[0].id)
        (node.targets[0].id)='var'
        return node

    def visit_Name(self, node: ast.Name) -> any:
        if node.id in self.__varables:
            node.id = 'var'
        return node

def parse(string):
    lst = []
    end_words = ['{','(','[',',']
    new_word=''
    for i in range(len(string)):
        if string[i] not in end_words:
            new_word+=string[i]
        else:
            lst.append(new_word)
            new_word = ''
    return lst

def changefunctions(commands, object1, object2):
    try:
        pattern = re.compile(f"Call(func=Name(id='{object1}'")
        commands = pattern.subn(object2,commands)
    except Exception:
        pass

def changevarables(commands, object1, object2):
    try:
        pattern = re.compile(f"Name(id='{object1}'")
        commands = pattern.subn(object2,commands)
    except Exception:
        pass

def maximum_length(first_string: str, second_string: str) -> int:
    first_length = len(first_string)
    second_length = len(second_string)
    if first_length<second_length:
        first_length, second_length = second_length, first_length
    return first_length

def Levenshtein(first_string: list, second_string: list) -> int:
    first_length = len(first_string)
    second_length = len(second_string)
    if first_length>second_length:
        first_string, second_string = second_string, first_string
        first_length, second_length = second_length, first_length
    current_row = range(first_length+1)
    for i in range(1, second_length+1):
        previous_row, current_row = current_row, [i]+[0]*first_length
        for j in range(1,first_length+1):
            add, delete, change = previous_row[j] + 1, current_row[j-1] + 1, previous_row[j - 1]
            if first_string[j - 1] != second_string[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)
    return current_row[first_length]

def main():
    transformer = MyTransformer()

    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="file with names of files that shold be compared")
    parser.add_argument("output_file", help="output file saves result of the analysis")
    args = parser.parse_args()  
    input_file = open(args.input_file)
    output_file = open(args.output_file)

    while True:
        first_file, second_file= map(str,input_file.readline().split())
        first_code=open(first_file)
        second_code=open(second_file)
        first_string = ast.parse(first_code.read())
        second_string = ast.parse(second_code.read())

        first_string = ast.dump(transformer.visit(first_string))
        varables = transformer.get_varables()
        functions = transformer.get_def()
        for var in varables:
            changevarables(first_string, var, 'var')
        for func in functions:
            changefunctions(first_string, func, 'Function')
        transformer.clean_def()
        transformer.clean_varables()
        second_string = ast.dump(transformer.visit(second_string))
        varables = transformer.get_varables()
        functions = transformer.get_def()
        for var in varables:
            changevarables(second_string, var, 'var')
        for func in functions:
            changefunctions(second_string, func, 'Function')


        output_file.write(str(1-(Levenshtein(parse(first_string),
                    parse(second_string))/maximum_length(first_string,second_string))))

    first_code.close()
    second_code.close()
    output_file.close()
    input_file.close()

if __name__ == '__main__':
    main()