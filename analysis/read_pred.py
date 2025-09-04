import itertools
import re
import string

def split_merged_id_form(split_line):
# Обработка строк со "слипшимися id и form" ("5ранний")
    if (len(split_line) > 0) and split_line[0][0].isdigit() and \
            ((len(split_line) == 9 and split_line[1] == "_") or
             (len(split_line) == 10 and set(split_line[1:6]) <= {"_", "__"})): # TODO
        digits = ''.join(list(itertools.takewhile(
            lambda x: x.isdigit(), split_line[0])))
        other = split_line[0][len(digits):]
        if all([symb.isalpha() or symb in string.punctuation or symb in {"«", "»"}
                for symb in other]):
            split_line = [digits, other] + split_line[1:]
    return split_line

class LineResult:
    def __init__(self, line):
        self.line = line
        self.id, self.form, self.parent_id, self.relation = None, None, None, None
        self.errors = []
        self.warnings = []
        split_line = re.split(r'\s+', line)
        split_line = [line for line in split_line if len(line) > 0]
        split_line = split_merged_id_form(split_line) # TODO: rename
        if len(split_line) > 10 and set(split_line[2:-4]) <= {"_", "__"}:
            split_line = split_line[:2] + ["_"] * 4 + split_line[-4:]
            # Удаление лишних "_" в середине
        if len(split_line) == 10:
            if not split_line[0].isdigit():
                self.errors.append(("Not digit id", line))
            elif split_line[1] == "_":
                self.errors.append(("Wrong form", line)) # TODO: Более понятное описание
            elif not split_line[6].isdigit():
                self.errors.append(("Not digit parent_id", line))
            elif not split_line[7].isalpha():
                self.errors.append(("Wrong relation", line))
            else:
                self.id = split_line[0] # str as in gold
                self.form = split_line[1]
                self.parent_id = split_line[6]
                self.relation = split_line[7]
        else:
            self.errors.append(("Wrong len", line))

    def __str__(self):
        return f"{self.id}_{self.form}"

class ParserSentResult:
    def __init__(self, s):
        self.original_s = s # TODO: rename
        self.full = s.strip().split('\n')
        self.splitted = [ LineResult(line) for line in self.full ]
        self.normal = [ line for line in self.splitted if len(line.errors) == 0]
        
    def __str__(self):
        return ', '.join(str(t) for t in self.normal)        

def parse_results(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = f.read()
    data = data.strip().split("===========================")
    data = [ ParserSentResult(s) for s in data if len(s) > 0]
    return data
