from enum import Enum
import pandas as pd
import math
from datetime import datetime
import os
import re
from korean_romanizer.romanizer import Romanizer

class Static:
    input_df = pd.DataFrame()
    output_df = pd.DataFrame(dtype=str)
    symbol_table = dict()
    lookup_table = dict()
    table_default = "tables/"

    def reset_static():
        Static.input_df = pd.DataFrame()
        Static.output_df = pd.DataFrame(dtype=str)
        Static.symbol_table = dict()
        Static.lookup_table = dict()

    def get_numerical(listed):
        listed = listed.lower()
        value = 0
        for digit in range(0, len(listed)):
            currentdigitmult = int(math.pow(26, len(listed)-digit-1))
            value += (ord(listed[digit])-96) * currentdigitmult
        return value

    def get_character(num):
        if num <= 0:
            return ""
        elif num <= 26:
            return chr(96 + num)
        else:
            return Static.get_character(int( (num - 1) / 26)) + chr(97 + (num - 1) % 26)


class Command(Enum):
    ERROR = 0
    WRITE = 1
    READ = 2
    LET = 3
    GET = 4
    TABLE_LOAD = 5
    TABLE_SEARCH = 6
    CONCAT = 7
    PRIMITIVE = 8
    TIME = 9
    OPER = 10
    REPLACE = 11
    ROMANIZE = 12
    NAMEFLIP = 13
    CUT = 14


class CommandTree:
    left = None
    right = None
    instruction = Command.ERROR

    def execute(self, row_num: int):
        print("generic error, failed runtime.")
        exit(1)

    def is_returning(self):
        return False


# WRITE <CELLROW> <DATA>
class CommandWrite(CommandTree):
    cell_column = None
    instruction = Command.WRITE

    def __init__(self, cell, data):
        self.cell_column = cell
        self.right = data

    def is_returning(self):
        return False

    def execute(self, row_num: int):
        data_collaged = self.right.execute(row_num)

        column_max = len(Static.output_df.columns)+1
        if column_max <= Static.get_numerical(self.cell_column):
            column_needed = Static.get_numerical(self.cell_column) - column_max
            for counted in range (column_max-1 , column_needed+column_max-1):
                Static.output_df.at[row_num, Static.get_character(counted+1).upper()] = None

        Static.output_df.at[row_num, self.cell_column] = data_collaged
        return None


# READ <CELLROW>
class CommandRead(CommandTree):
    cell_column = None
    instruction = Command.READ

    def __init__(self, cell):
        self.cell_column = cell

    def is_returning(self):
        return True

    def execute(self, row_num: int):
        numerical = Static.get_numerical(self.cell_column)-1
        receval = Static.input_df.iloc[row_num, numerical]
        return str(receval)


# LET <VAR> <DATA>
class CommandLet(CommandTree):
    variable = None
    instruction = Command.LET

    def __init__(self, variable, data):
        self.variable = variable
        self.right = data

    def is_returning(self):
        return False

    def execute(self, row_num: int):
        data_collaged = self.right.execute(row_num)
        Static.symbol_table[self.variable] = data_collaged


# GET <VAR>
class CommandGet(CommandTree):
    variable = None
    instruction = Command.GET

    def __init__(self, variable):
        self.variable = variable

    def is_returning(self):
        return True

    def execute(self, row_num: int):
        return Static.symbol_table[self.variable]


# LOAD <TABLE_NAME>
class CommandTableLoad(CommandTree):
    table_name = None
    instruction = Command.TABLE_LOAD

    def __init__(self, table_name):
        self.table_name = table_name

    def is_returning(self):
        return False

    def execute(self, row_num: int):
        true_default = Static.table_default + self.table_name + ".csv"
        new_table = None
        if os.path.exists(true_default):
            new_table = pd.read_csv(true_default, encoding='utf8')
        elif os.path.exists(Static.table_default + self.table_name + ".xlsx"):
            new_table = pd.read_excel(Static.table_default + self.table_name + ".xlsx")

        dictionary = dict()
        counter = 0
        for ind in range(len(new_table)):
            cell1 = new_table.loc[ind, 'key']
            cell2 = new_table.loc[ind, 'value']
            dictionary[cell1] = cell2

        Static.lookup_table[self.table_name] = dictionary
        return None


# SEARCH <TABLE_NAME> <KEY>
# Note, if no match, it returns the key.
# TODO: make if statement to make ignore possible
class CommandTableSearch(CommandTree):
    table_name = None
    table_key = None
    instruction = Command.TABLE_SEARCH

    def __init__(self, table_name, key):
        self.table_name = table_name
        self.table_key = key

    def is_returning(self):
        return True

    def execute(self, row_num: int):
        table_in_question = Static.lookup_table[self.table_name]
        executed_results = self.table_key.execute(row_num)
        key = executed_results.strip()
        answer = None
        if key in table_in_question:
            answer = table_in_question[key]
        else:
            answer = key
        return answer


# CONCAT <FRONT> <BACK>
class CommandConcat(CommandTree):
    var_name = None
    instruction = Command.CONCAT

    def __init__(self, front, back):
        self.left = front
        self.right = back

    def is_returning(self):
        return True

    def execute(self, row_num: int):
        front_reader = self.left.execute(row_num)
        back_reader = self.right.execute(row_num)
        return str(front_reader+back_reader)


# PRIMITIVE <STRING>
class CommandPrimitive(CommandTree):
    data = None
    instruction = Command.PRIMITIVE

    def __init__(self, data):
        self.data = data

    def is_returning(self):
        return True

    def execute(self, row_num: int):
        return str(self.data)


# TIME <TIMEFORMAT>
class CommandTime(CommandTree):
    time_format = None
    instruction = Command.TIME

    def __init__(self, time_format):
        self.time_format = time_format

    def is_returning(self):
        return True

    def execute(self, row_num: int):
        return datetime.now().strftime(self.time_format)


# OPER <OPERATION> <FRONT> <BACK>
class CommandOperation(CommandTree):
    instruction = Command.OPER
    operation = None

    def __init__(self, front, back, operation):
        self.left = front
        self.right = back
        self.operation = operation

    def is_returning(self):
        return True

    def execute(self, row_num: int):
        front_res = self.left.execute(row_num)
        back_res = self.right.execute(row_num)
        front_ans = None
        back_ans = None
        try:
            front_ans = float(front_res)
        except ValueError:
            print("Runtime Error: "+front_res+" cannot be converted to int")
            exit(3)
        try:
            back_ans = float(back_res)
        except ValueError:
            print("Runtime Error: "+back_res+" cannot be converted to int")
            exit(3)

        if self.operation == '+':
            return front_ans + back_ans
        elif self.operation == '-':
            return front_ans - back_ans
        elif self.operation == '*':
            return front_ans * back_ans
        elif self.operation == "/":
            return front_ans / back_ans
        else:
            print("Runtime Error: " + self.operation + " operator is not implemented")
            exit(3)


# REPLACE <FROM> <TO> <ORIGIN>
class CommandReplace(CommandTree):
    instruction = Command.REPLACE
    origin = None

    def __init__(self, search, to, origin):
        self.left = search
        self.right = to
        self.origin = origin

    def is_returning(self):
        return True

    def execute(self, row_num: int):
        front_res = self.left.execute(row_num)
        back_res = self.right.execute(row_num)
        origin_res = self.origin.execute(row_num)
        origin_res = re.sub(pattern=front_res, repl=back_res, string=origin_res)
        return origin_res


# ROMANIZE <KOREAN>
class CommandRomanize(CommandTree):
    instruction = Command.ROMANIZE

    def __init__(self, korean):
        self.right = korean

    def is_returning(self):
        return True

    def execute(self, row_num: int):
        back_res = self.right.execute(row_num)
        romanizer = Romanizer(back_res)
        origin_res = romanizer.romanize()
        return origin_res

# NAMEFLIP <NAME>
class CommandNameFlip(CommandTree):
    instruction = Command.NAMEFLIP

    def __init__(self, name):
        self.right = name

    def is_returning(self):
        return True

    def execute(self, row_num: int):
        back_res = self.right.execute(row_num)
        regexp = re.compile("[a-zA-Z]")
        if regexp.search(back_res):
            return back_res
        split = back_res.split()
        origin_res = split.pop()
        separate = " "

        addun_res = separate.join(split)
        origin_res = origin_res + addun_res

        return origin_res


# CUT <IndexCutoutStart> <IndexCutoutEnd> <ORIGIN>
class CommandCut(CommandTree):
    instruction = Command.CUT

    startInd = None
    endInd = None

    def __init__(self, start, end, origin):
        self.startInd = int(start)
        self.endInd = int(end)
        self.right = origin

        if self.startInd is not int or self.endInd is not int:
            print("Runtime Error: Cut command needs numerical values for limits")
            exit(3)

    def is_returning(self):
        return True

    def execute(self, row_num: int):

        string_in_question = self.right.execute(row_num)
        if self.startInd < 0:
            self.startInd = 0
        if self.endInd >= len(string_in_question):
            self.endInd = len(string_in_question) - 1

        string_answer = string_in_question[self.startInd:self.endInd]

        return string_answer






