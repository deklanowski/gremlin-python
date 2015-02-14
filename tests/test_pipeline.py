# Test scenarios based on http://gremlindocs.com/

from nose.tools import nottest
from gremthon import Gremthon

#Java imports
from com.tinkerpop.blueprints.impls.tg import TinkerGraphFactory

graph = TinkerGraphFactory.createTinkerGraph()
g = Gremthon(graph)


def test_both():
    assert set([v.id for v in g.v(4).both()]) == {'1', '5', '3'}
    assert [v.id for v in g.v(4).both('knows')] == ['1']
    assert set([v.id for v in g.v(4).both('knows', 'created')]) == {'1', '5', '3'}
    assert [v.id for v in g.v(4).both(1, 'knows', 'created')] == ['1']


def test_both_e():
    assert set([e.id for e in g.v(4).both_e()]) == {'8', '10', '11'}
    assert [e.id for e in g.v(4).both_e('knows')] == ['8']
    assert set([e.id for e in g.v(4).both_e('knows', 'created')]) == {'8', '10', '11'}
    assert [e.id for e in g.v(4).both_e(1, 'knows', 'created')] == ['8']


def test_both_v():
    assert [v.id for v in g.e(12).in_v()] == ['3']
    assert [v.id for v in g.e(12).out_v()] == ['6']
    assert [v.id for v in g.e(12).both_v()] == ['6', '3']


def test_graph_edge_iterator():
    assert set([e.id for e in g.E]) == {'10', '7', '9', '8', '11', '12'}


def test_get_adjacent_vertices():
    assert [v.id for v in g.v(4).in_()] == ['1']
    assert [v.id for v in g.v(4).in_e().out_v()] == ['1']
    assert set([v.id for v in g.v(3).in_('created')]) == {'1', '4', '6'}
    assert set([v.id for v in g.v(3).in_(2, 'created')]) < {'1', '4', '6'}
    assert set([v.id for v in g.v(3).in_e('created').out_v()]) == {'1', '4', '6'}
    assert set([v.id for v in g.v(3).in_e(2, 'created').out_v()]) < {'1', '4', '6'}


def test_properties():
    assert g.v(3).name == 'lop'
    assert list(g.v(3))[0].name == 'lop'
    assert list(g.v(3))[0]['name'] == 'lop'
    assert list(g.v(3))[0].get_property('name') == 'lop'


def test_labels():
    assert list(g.v(6).out_e())[0].label == 'created'
    assert [e.id for e in g.v(1).out_e().filter(lambda it: it.label == 'created')] == ['9']
    assert [e.id for e in g.v(1).out_e().has('label','created')] == ['9']


@nottest
def test_link_both_in_out():
    #TODO: see why except doesn't seem to be working as expected
    # marko = g.v(1)
    # g.V.except_([marko])
    pass


def test_map():
    assert list(g.v(1).map())[0] == {'age': 29, 'name': 'marko'}
    actual_items = list(g.V.map('id','age'))
    expected_items = [
        {'id': '3', 'age': None},
        {'id': '2', 'age': 27},
        {'id': '1', 'age': 29},
        {'id': '6', 'age': 35},
        {'id': '5', 'age': None},
        {'id': '4', 'age': 32}
    ]
    assert len(actual_items) == len(expected_items)
    for expected_item in expected_items:
        assert expected_item in actual_items
    assert list(g.v(1).map('id','age'))[0] == {'id': '1', 'age': 29}


def test_memoize():
    assert set([v.id for v in g.V.out().out().memoize(1)]) == {'5', '3'}
    assert set([v.id for v in g.V.out().as_('here').out().memoize('here')]) == {'5', '3'}
    m = {}
    g.V.out().out().memoize(1, m)
    # assert [v.id for v in m[list(g.v(4))[0].vertex]] == ['5', '3']


def test_order():
    #TODO: implement tests for order
    pass


def test_path():
    expected_items = [
        ['1', '2'],
        ['1', '4'],
        ['1', '3']
    ]
    actual_items = [[pair[0].id, pair[1].id] for pair in g.v(1).out().path()]
    assert len(actual_items) == len(expected_items)
    for expected_item in expected_items:
        assert expected_item in actual_items

    actual_items = [p for p in g.v(1).out().path(lambda it: it.id)]
    assert len(actual_items) == len(expected_items)
    for expected_item in expected_items:
        assert expected_item in actual_items

    expected_items = [
        ['1', 'vadas'],
        ['1', 'josh'],
        ['1', 'lop']
    ]

    actual_items = [p for p in g.v(1).out().path(lambda it: it.id, lambda it: it.name)]
    assert len(actual_items) == len(expected_items)
    for expected_item in expected_items:
        assert expected_item in actual_items

    expected_items = [
        ['1', '7', '2'],
        ['1', '8', '4'],
        ['1', '9', '3'],
    ]

    actual_items = [[p[0].id, p[1].id, p[2].id] for p in g.v(1).out_e().in_v().path()]
    assert len(actual_items) == len(expected_items)
    for expected_item in expected_items:
        assert expected_item in actual_items


def test_gather_scatter():
    assert set([v.id for v in list(g.v(1).out().gather(lambda it: it[1:]))[0]]) < {'4', '3', '2'}
    assert set([v.id for v in list(g.v(1).out().gather(lambda it: it[1:]).scatter())]) < {'4', '3', '2'}


def test_select():
    assert [[x[0].id, x[1].id] for x in list(g.v(1).as_('x').out('knows').as_('y').select())] == [['1', '2'], ['1', '4']]
    assert [x[0].id for x in list(g.v(1).as_('x').out('knows').as_('y').select(["y"]))] == ['2', '4']
    assert [x[0] for x in list(g.v(1).as_('x').out('knows').as_('y').select(["y"], lambda it: it.name))] == ['vadas', 'josh']


def test_shuffle():
    shuffled_items = list(g.v(1).out().shuffle())
    out_items = list(g.v(1).out())
    assert len(shuffled_items) == len(out_items)
    for item in shuffled_items:
        assert item in out_items


def test_vertex_iteration():
    assert set([v.id for v in g.V]) == {'3', '2', '1', '6', '5', '4'}
    assert [v.id for v in g.vertices("name", "marko")] == ['1']
    assert g.vertices("name", "marko").name == 'marko'


def test_index_filter():
    assert set([v.id for v in g.V[2:4]]) < {'3', '2', '1', '6', '5', '4'}
    assert len([v.id for v in g.V[2:4]]) == 2
    assert set([v.id for v in g.V.out()[:2]]) < {'3', '2', '1', '6', '5', '4'}
    assert len([v.id for v in g.V.out()[:2]]) == 2
    assert set([v.id for v in g.V.out()[4:]]) < {'3', '2', '1', '6', '5', '4'}
    assert len([v.id for v in g.V.out()[4:]]) == 2
    assert [v.id for v in g.V.out()[4]] == ['5']


def test_dedup():
    assert set([v.id for v in g.v(1).out().in_()]) == {'1', '1', '1', '4', '6'}
    assert set([v.id for v in g.v(1).out().in_().dedup()]) == {'1', '4', '6'}


def test_filter():
    assert set([v.name for v in g.V.filter(lambda it: it.age > 29)]) == {'peter', 'josh'}


def test_interval():
    assert set([e.weight for e in g.E.interval("weight", 0.3, 0.9)]) == {0.5, 0.4000000059604645, 0.4000000059604645}


def test_random():
    random_objects = list(g.V.random(0.5))
    all_objects = list(g.V)
    for obj in random_objects:
        assert obj in all_objects


#TODO: keep testing!

@nottest
def test_retain():
    pass


def test_simple_path():
    assert [v.id for v in g.v(1).out().in_().simple_path()] == ['4', '6']


@nottest
def test_aggregate():
    pass


@nottest
def test_group_by():
    pass


@nottest
def test_group_count():
    pass


@nottest
def test_optional():
    pass


@nottest
def test_side_effect():
    pass


@nottest
def test_store():
    pass

@nottest
def test_table():
    pass


@nottest
def test_tree():
    pass


@nottest
def test_copy_split():
    pass


@nottest
def test_exhaust_merge():
    pass


@nottest
def test_fair_merge():
    pass


@nottest
def test_loop():
    pass


@nottest
def test_keys():
    pass


@nottest
def test_remove():
    pass


@nottest
def test_value():
    pass


@nottest
def test_add_edge():
    pass


@nottest
def test_add_vertex():
    pass


@nottest
def test_index():
    pass


@nottest
def test_fill():
    pass

