from collections import Counter

from metrics import compare_result, calculate_uas
from read_gold import read_gold_treebank
from read_pred import LineResult, ParserSentResult, parse_results


treebank_names = ['gsd', 'pud', 'taiga', 'poetry', 'syntagrus']
parser_names = [ 'qwen4', 'ruadapt4' ]
prompt_range = range(1, 11)
experiments = [(tr, prompt_i, parser) for tr in treebank_names
               for prompt_i in prompt_range
               for parser in parser_names ]
gold_treebanks = {}
for tr in treebank_names:
    gold_treebanks[tr] = read_gold_treebank(f'treebanks/ru_{tr}-ud-test.conllu')

pred_results = {}
for tr, prompt_i, parser in experiments:
    pred_results[(tr, prompt_i, parser)] = \
        parse_results(f'results/{parser}/{tr}/{parser}_{tr}_2_{prompt_i}.txt')

'''id_errors = {}
form_errors = {}
for tr, prompt_i, parser in experiments:
    id_errors[(tr, prompt_i, parser)], form_errors[(tr, prompt_i, parser)] = \
            compare_result(gold_treebanks[tr], pred_results[(tr, prompt_i, parser)])
    #print(tr, prompt_i, parser, len(id_errors[(tr, prompt_i, parser)]),
    #          len(form_errors[(tr, prompt_i, parser)]))
'''
uas = {}
for tr, prompt_i, parser in experiments:
    uas[(tr, prompt_i, parser)] = \
                calculate_uas(gold_treebanks[tr], pred_results[(tr, prompt_i, parser)])
    #print(tr, prompt_i, parser, res[(tr, prompt_i, parser)].mean())

'''
print("Line errors")
for tr, prompt_i, parser in experiments:
    print(tr, prompt_i, parser, Counter([line.errors[0][0]
        for sent in pred_results[(tr, prompt_i, parser)]
        for line in sent.splitted if len(line.errors) > 0]))
'''

for tr in treebank_names:
    for parser in parser_names:
        u_stat = [uas[(tr, prompt_i, parser)].mean().round(2)
                  for prompt_i in prompt_range]
        order_i = sorted(list(prompt_range),
                         key=lambda x: u_stat[x - 1])
        print(tr, parser, min(u_stat), max(u_stat), order_i)
