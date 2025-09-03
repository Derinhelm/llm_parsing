from collections import Counter
import pandas as pd

def calc_sent_uas(g, p):
    g_dict = {t['id']: t['form'] for t in g}
    g_dict['0'] = 'root'
    p_dict = {t.id: t.form for t in p.normal} # TODO: >
    p_dict['0'] = 'root' # TODO: проверить, что нет линии с id=0
    #print(g_dict)
    #print(p_dict)
    g_edges = Counter([((t['form'], g_dict[t['parent_id']])
               if(t['parent_id'] in g_dict) else (t['form'], None)) for t in g])
    p_edges = Counter([((t.form, p_dict[t.parent_id])
               if(t.parent_id in p_dict) else (t.form, None)) for t in p.normal])

    #print(g_edges)
    return (g_edges & p_edges).total() / g_edges.total() # TODO: первое приближение

def calculate_uas(gold, pred):
    r = []
    assert len(gold) == len(pred)
    for i in range(len(gold)):
        r.append(calc_sent_uas(gold[i], pred[i]))
    r = pd.Series(r)
    return r

def compare_result(gold_res, pred_res):
    id_errors = {}
    form_errors = {}

    for s_i, gold_s in enumerate(gold_res):
        #assert all(line[0].isdigit() for line in pred_res[s_i].normal)
        gold_ids = Counter(t['id'] for t in gold_s)
        pred_ids = Counter(line.id
            for line in pred_res[s_i].normal if not line.errors)
        if gold_ids != pred_ids:
            id_errors[s_i] = (gold_ids - pred_ids, pred_ids - gold_ids)
        
        gold_forms = Counter(t['form'] for t in gold_s)
        pred_forms = Counter(line.form for line in pred_res[s_i].normal)
        if gold_forms != pred_forms:
            form_errors[s_i] = (gold_forms - pred_forms, pred_forms - gold_forms)
    return id_errors, form_errors
