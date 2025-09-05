from collections import Counter
import pandas as pd

def calc_f(g_edges, p_edges):
    if p_edges.total() != 0:
        precision = (g_edges & p_edges).total() / p_edges.total()
    else:
        precision = 0
    if g_edges.total() != 0:
        recall = (g_edges & p_edges).total() / g_edges.total()
    else:
        recall = 0
    if precision + recall == 0:
        return 0 # TODO
    f_score = (2 * precision * recall) / (precision + recall)
    return f_score

def calc_sent_metrics(g, p):
    g_dict = {t['id']: t['form'] for t in g}
    g_dict['0'] = 'root'
    p_dict = {t.id: t.form for t in p.normal} # TODO: >
    p_dict['0'] = 'root' # TODO: проверить, что нет линии с id=0

    uas_g_edges = Counter([((t['form'], g_dict[t['parent_id']])
               if(t['parent_id'] in g_dict) else (t['form'], None)) for t in g])
    uas_p_edges = Counter([((t.form, p_dict[t.parent_id])
               if(t.parent_id in p_dict) else (t.form, None)) for t in p.normal])
    uas = calc_f(uas_g_edges, uas_p_edges)

    las_g_edges = Counter([((t['form'], g_dict[t['parent_id']], t['relation'])
               if(t['parent_id'] in g_dict) else (t['form'], None)) for t in g])
    las_p_edges = Counter([((t.form, p_dict[t.parent_id], t.relation)
               if(t.parent_id in p_dict) else (t.form, None)) for t in p.normal])
    las = calc_f(las_g_edges, las_p_edges)

    #print(g_edges)
    return uas, las

def calculate_metrics(gold, pred):
    uas_list, las_list = [], []
    assert len(gold) == len(pred)
    for i in range(len(gold)):
        uas_i, las_i = calc_sent_metrics(gold[i], pred[i])
        uas_list.append(uas_i)
        las_list.append(las_i)
    uas_res = pd.Series(uas_list)
    las_res = pd.Series(las_list)
    return uas_res, las_res

def compare_result(gold_res, pred_res):
    for s_i, gold_s in enumerate(gold_res):
        #assert all(line[0].isdigit() for line in pred_res[s_i].normal)
        gold_ids = Counter(t['id'] for t in gold_s)
        pred_ids = Counter(line.id
            for line in pred_res[s_i].normal if not line.errors)
        if gold_ids != pred_ids:
            pred_res[s_i].errors.add(("id error",
                (tuple((gold_ids - pred_ids).elements()),
                tuple((pred_ids - gold_ids).elements()))))
        
        gold_forms = Counter(t['form'] for t in gold_s)
        pred_forms = Counter(line.form for line in pred_res[s_i].normal)
        if gold_forms != pred_forms:
            pred_res[s_i].errors.add(("form error",
                (tuple((gold_forms - pred_forms).elements()),
                 tuple((pred_forms - gold_forms).elements()))))
