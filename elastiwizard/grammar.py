class GrammarBuilder(object):
    """This will be used to build the grammar necessary for parsing"""

    def __init__(self, **options):
       self.grammar = """\
       question = metric space index (space delta)? (space where)? (space by space group_by)?

        space = ~"\s*"
        string = ~"[A-z]"
        number = ~"[0-9]"
        date = ~"[A-z0-9,.'-/]"
        value = (string / number / date)

        metric = string*
        index = string*
        delta = deltastring space date* (space deltastring space date*)?
        deltastring = "since" / "from" / "to" / "each"
        where = string*
        values = value+
        group_by = values*
        by = "by"*
        """


