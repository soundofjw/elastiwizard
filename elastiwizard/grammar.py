class GrammarBuilder(object):
    """This will be used to build the grammar necessary for parsing"""

    def __init__(self, **options):
       self.grammar = """\
       question = metric space (the space field space of space)? (index) (space where)? (space by space group_by)? (space delta)?

        space = ~"\s*"
        string = ~"[A-z,]"
        number = ~"[0-9]"
        date = ~"[A-z0-9,.'-/]"
        value = (string / number / date)

        metric = "count" / "how many" / "sum" / "average" / "max" / "min" / "best" / "worst"
        index = string*
        field = string*
        delta = deltastring space date* (space deltastring space date*)?
        deltastring = "since" / "from" / "to" / "each"
        where = string*
        values = value+
        group_by = values*
        by = "by"+
        the = "the"+
        of = "of"+
        """


