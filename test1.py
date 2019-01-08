import gudhi
import pyodbc
from cfg.cfg import prod_SQL
import pandas as pd

"""
Todo TODAY
# get dataset.
# preproccess
# build simplical complexes

"""

labels_q = 'tda_ds2'


def get_dataset(q_str):
    conn = pyodbc.connect(prod_SQL)
    with conn.cursor() as crsr:
        crsr.execute(q_str)
        data = crsr.fetchall()
        keys = list(map(lambda x: x[0], crsr.description))
    conn.close()
    return data, keys


def table_to_df(qstr):
    data, keys = get_dataset(qstr)
    df = pd.DataFrame()
    for i, k in enumerate(keys):
        df[k] = list(map(lambda x: x[i], data))
    return df


def indices_to_one_hot(data):
    """Convert an iterable of indices to one-hot encoded labels."""
    ix = {x: i for i, x in enumerate(set(data))}
    ln = len(ix)
    return [ix[d] for d in data]


def prep_df(table, keys, one_hots, where=''):

    allk = keys + one_hots
    ky_str = ','.join(map(lambda x: '[{}]'.format(x), allk))
    q1 = "Select {} From [{}] {}".format(ky_str, table, where)
    print(q1)
    df = pd.DataFrame()
    dt = get_dataset(q1)
    for i, k in enumerate(allk):
        df[k] = list(map(lambda x: x[i], dt))
        # if k in one_hots:
            # df[k] = indices_to_one_hot(df[k].values)
    return df


def pd_to_tree(dim_keys, df):
    st = gudhi.SimplexTree()
    for vls in zip(*(df[k].values for k in dim_keys)):
        st.insert(list(vls))
    return st


def stat_st(stree):
    print('dim: {}, verts: {}, simps: {}'.format(
        stree.dimension(), stree.num_vertices(), stree.num_simplices(), )
    )


def preprocess():
    """
    dimensions - original value, change_amount

    amounts normed to either 1 or line item amount


    :param data:
    :return:
    """
    _table = 'ChangeOrderPotentialLineItem'
    _keys = ['extended_amount']
    _one_hots = ['cost_code_sortable_code']

    df = prep_df(_table, _keys, _one_hots)
    st = pd_to_tree(_keys + _one_hots, df)
    return df, st


def sc_overtime(**kwargs):
    """
    create views by timeperiod of evolution of simplical complex
    :param data:
    :return:
    """
    pass


def build_graph_no_scale(data, keys):
    """
    2 options
        - 1 Graph with just total amounts
        - 2 (summary) Metanodes with the state, with labeled edges for instance items
        - 3

    """
    import networkx as nx
    G = nx.DiGraph()

    for line in data:
        pass

    return G





def run():
    q_str = "Select [amount] From [ChangeOrderRequest]"

