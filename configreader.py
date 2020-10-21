import command
import pandas as pd

special_words = ['WRITE', 'READ', 'LET', 'GET', 'LOAD', 'SEARCH', 'CONCAT', 'PRIMITIVE', 'TIME', 'OPER']
returning_words = ['READ', 'GET', 'SEARCH', 'CONCAT', 'PRIMITIVE', 'TIME', 'OPER']

def read_configuration(filename):
    counter = 0
    sq_list = list()
    with open(filename, encoding="utf-8") as file:
        for line in file:
            if line[0] == '#':
                continue
            elif line == "":
                continue
            counter += 1
            line = line.replace("\n", "")
            sq_list.append(line_splitification(counter, line))
    return sq_list


def read_configuration_command(command):
    counter = 0
    sq_list = list()
    sp_list = command.split('\n')
    for line in sp_list:
        counter += 1
        sq_list.append(line_splitification(counter, line))
    return sq_list


def split_chars(word):
    return [char for char in word]


def custom_space_split(line):
    words = list()
    next_word = ""
    in_quotes = False
    in_slap = False
    for character in line:
        if in_quotes:
            if character == '\"':
                in_quotes = False
                next_word += character
                words.append(next_word)
                next_word = ""
                continue
            else:
                next_word += character
        elif in_slap:
            if character == ']':
                in_slap = False
                next_word += character
                words.append(next_word)
                next_word = ""
                continue
            else:
                next_word += character
        else:
            if character == " ":
                if next_word != "":
                    words.append(next_word)
                    next_word = ""
                continue
            elif character == "\"":
                in_quotes = True
                next_word += character
                continue
            elif character == "[":
                in_slap = True
                next_word += character
                continue
            else:
                next_word += character
    if next_word != "":
        words.append(next_word)
    return words



def line_splitification (line_num, line):
    splited_words = custom_space_split(line)

    point_counter = len(splited_words)-1

    stack = list()
    data_tree = None
    cell_column = None
    variable_name = None
    table_name = None
    table_key = None
    string = None


    while point_counter >= 0:
        checking_current = splited_words[point_counter]

        if checking_current in special_words:
            if checking_current == 'WRITE':
                cell_column = stack.pop()
                data_tree = stack.pop()
                if not data_tree.is_returning():
                    print(str(data_tree.instruction) + " does not return value for WRITE in line "+ str(line_num))
                    exit(1)
                stack.append(command.CommandWrite(cell_column, data_tree))
            elif checking_current == 'READ':
                cell_column = stack.pop()
                stack.append(command.CommandRead(cell_column))
            elif checking_current == 'LET':
                variable_name = stack.pop()
                data_tree = stack.pop()
                if not data_tree.is_returning():
                    print(str(data_tree.instruction) + " does not return value for LET in line " + str(line_num))
                    exit(1)
                stack.append(command.CommandLet(variable_name, data_tree))
            elif checking_current == 'GET':
                variable_name = stack.pop()
                stack.append(command.CommandGet(variable_name))
            elif checking_current == 'LOAD':
                table_name = stack.pop()
                stack.append(command.CommandTableLoad(table_name))
            elif checking_current == 'SEARCH':
                table_name = stack.pop()
                table_key = stack.pop()
                stack.append(command.CommandTableSearch(table_name, table_key))
            elif checking_current == 'CONCAT':
                left_side = stack.pop()
                right_side = stack.pop()
                stack.append(command.CommandConcat(left_side, right_side))
            elif checking_current == 'PRIMITIVE':
                string = stack.pop()
                if string[0] != "\"" or string[len(string)-1] != "\"":
                    print("no quotation mark for PRIMITIVE, line "+line_num)
                    exit(1)
                string = string[1:]
                string = string[:len(string)-1]
                stack.append(command.CommandPrimitive(string))
            elif checking_current == 'TIME':
                string = stack.pop()
                if string[0] != "[" or string[len(string) - 1] != "]":
                    print("no [] for timeframe in TIME, line " + line_num)
                    exit(1)
                string = string[1:]
                string = string[:len(string) - 1]
                stack.append(command.CommandTime(string))
            elif checking_current == 'OPER':
                operation = stack.pop()
                left_side = stack.pop()
                right_side = stack.pop()

                stack.append(command.CommandOperation(left_side, right_side, operation))
        else:
            stack.append(checking_current)

        point_counter -= 1

    return stack[0]

def load_csv_direct(file_name):
    df = pd.read_csv(file_name, keep_default_na=False, dtype=str)
    df.astype('string')
    command.Static.reset_static()
    command.Static.input_df = df

def load_excel_direct(file_name):
    df = pd.read_excel(file_name, keep_default_na=False, dtype=str)
    df.astype('string')
    command.Static.reset_static()
    command.Static.input_df = df


def run_cfr(config_path, data_path):
    cong = read_configuration(config_path)

    if data_path.endswith(".csv"):
        load_csv_direct(data_path)
    elif data_path.endswith(".xlsx"):
        load_excel_direct(data_path)
    else:
        exit(2)


    for rownum in range(0, len(command.Static.input_df)):
        for i in range(0, len(cong)):
            cong[i].execute(rownum)
    return command.Static.output_df
