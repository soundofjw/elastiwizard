from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor

class ElastiwizardParser(NodeVisitor):
    """
    Parses text based on given grammar by
    walking Nodetree
    """
    def __init__(self, grammar, text):
        self.question = {}
        ast = Grammar(grammar).parse(text)
        self.visit(ast)

    def visit_metric(self, n, vc):
        self.question['metric'] = n.text

    def visit_index(self, n, vc):
        self.question['index'] = n.text

    def visit_field(self, n, vc):
        self.question['field'] = n.text

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
