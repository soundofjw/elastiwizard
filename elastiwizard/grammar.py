class GrammarBuilder(object):
    """This will be used to build the grammar necessary for parsing"""

    def __init__(self, **options):
       self.grammar = """\
        question = metric sep field (sep delta)? (sep where)? (sep by sep group_by)?
        sep = ws
        ws = " "*
        metric = ~"[A-z]*"
        field = ~"[A-z]*"
        delta = ~"\w*\s\d*-\d*-\d."*
        where = ~"[A-z]"*
        group_by = ~"[A-z0-9 ,.'-/]"*
        by = "by"*
        """


