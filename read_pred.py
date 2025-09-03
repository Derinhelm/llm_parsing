import re

class LineResult:
    def __init__(self, line):
        self.line = line
        self.id, self.form, self.parent_id, self.relation = None, None, None, None
        self.errors = []
        split_line = re.split(r'\s+', line)
        split_line = [line for line in split_line if len(line) > 0]
        if len(split_line) == 10: # TODO: Обработка строк со "слипшимися id и form"
            if not split_line[0].isdigit():
                self.errors.append(("Not digit id", line))
            elif split_line[1] == "_":
                self.errors.append(("Wrong form", line)) # TODO: Более понятное описание
            elif not split_line[6].isdigit():
                self.errors.append(("Not digit parent_id", line))
            elif not split_line[7].isalpha():
                self.errors.append(("Wrong relation", line))
            else:
                self.id = int(split_line[0])
                self.form = split_line[1]
                self.parent_id = int(split_line[6])
                self.relation = split_line[7]
        else:
            self.errors.append(("Wrong len", line))

class ParserSentResult:
    def __init__(self, s):
        self.original_s = s # TODO: rename
        self.full = s.strip().split('\n')
        self.splitted = [ LineResult(line) for line in self.full ]
        self.normal = [ line for line in self.splitted if len(line.errors) == 0]
        
        #re.split(r'\s+', s)

def parse_results(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = f.read()
    data = data.strip().split("===========================")
    data = [ ParserSentResult(s) for s in data if len(s) > 0]
    return data
