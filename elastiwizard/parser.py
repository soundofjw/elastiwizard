
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor

class ElastiwizardParser(NodeVisitor):
    def __init__(self, grammar, text):
        self.question = {}
        ast = Grammar(grammar).parse(text)
        self.visit(ast)

    def visit_metrics(self, n, vc):
        self.question['metrics'] = n.text

    def visit_index(self, n, vc):
        self.question['index'] = n.text

    def visit_delta(self, n, vc):
        self.question['delta'] = n.text

    def visit_where(self, n, vc):
        self.question['where'] = n.text

    def visit_group_by(self, n, vc):
        self.question['group_by'] = n.text

    def visit_order(self, n, vc):
        self.question['order'] = n.text

    def generic_visit(self, n, vc):
        pass


grammar = """\
question = metrics sep index (sep delta)? (sep where)? (sep group_by)? (sep order)?
sep = ws
ws = " "*
metrics = ~"[A-z]*"
index = ~"[A-z]*"
delta = ~"\w*\s\d*-\d*-\d."*
where = ~"[A-z\w=]"*
group_by = ~"[A-z]"*
order = ~"[A-z]"*
"""

goal = """\
count requests since 2015-07-07 where needs_license_research = 1 and researched_by = user/FJskoiw group_by researched_by order _count desc
"""

for line in text.splitlines():
    print ElastiwizardParser(grammar, goal).question