def read_gold_treebank(filepath):
    with open(filepath, 'r', encoding='utf-8') as fh:
        sents = []
        sent = []
        for line in fh:
            tok = line.strip().split('\t')
            if not tok or line.strip() == '': # empty line, add sentence to list
                if len(sent) > 0:
                    sents.append(sent)
                sent = []
            else:
                if not(line[0] == '#' or '-' in tok[0]): # a comment line
                    tok_dict = { 'id': tok[0], 'form': tok[1],
                        'parent_id': tok[6], 'relation': tok[7] }
                    if "." not in tok_dict['id']: # Токены для эллипсиса, не учитываем их
                        sent.append(tok_dict)
    return sents
