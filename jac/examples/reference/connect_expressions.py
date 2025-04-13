from __future__ import annotations
from jaclang.plugin.builtin import *
from jaclang import JacFeature as _


class node_a(_.Node):
    value: int


class Creator(_.Walker):
    @_.entry
    def create(self, here: _.Root) -> None:
        end = here
        i = 0
        while i < 7:
            if i % 2 == 0:
                _.conn(end, (end := node_a(value=i)))
            else:
                _.conn(
                    end,
                    (end := node_a(value=i + 10)),
                    edge=MyEdge,
                    conn_assign=(("val",), (i,)),
                )
            i += 1

    @_.entry
    def travel(self, here: _.Root | node_a) -> None:
        for i in _.refs(here, MyEdge, lambda edge: edge.val <= 6):
            print(i.value)
        _.visit(self, _.refs(here))


class MyEdge(_.Edge):
    val: int = 5


if __name__ == "__main__":
    _.spawn(_.root(), Creator())
