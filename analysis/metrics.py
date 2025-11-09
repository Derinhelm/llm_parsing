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
    
    extra_gold = list((las_g_edges - las_p_edges).elements())
    extra_parser = list((las_p_edges - las_g_edges).elements())
    both = list((las_p_edges & las_g_edges).elements())
    
    extra_gold_relations = Counter(r[2] for r in extra_gold)
    extra_parser_relations = Counter(r[2] for r in extra_parser if len(r) > 2)
    both_relations = Counter(r[2] for r in both)
    
    relations_stat = {"extra_gold": extra_gold_relations,
                      "extra_parser": extra_parser_relations,
                      "both": both_relations}
        
    #print(g_edges)
    return uas, las, relations_stat

def calculate_metrics(gold, pred):
    uas_list, las_list = [], []
    assert len(gold) == len(pred)
    relation_stat = {"extra_gold": Counter(),
                      "extra_parser": Counter(),
                      "both": Counter()}
    for i in range(len(gold)):
        uas_i, las_i, relations_stat_i = calc_sent_metrics(gold[i], pred[i])
        uas_list.append(uas_i)
        las_list.append(las_i)
        assert relation_stat.keys() == relations_stat_i.keys()
        for k in relation_stat:
            relation_stat[k] += relations_stat_i[k]
    uas_res = pd.Series(uas_list)
    las_res = pd.Series(las_list)
    return uas_res, las_res, relation_stat
