import re

inside_pattern = re.compile(r"([\^\-\]])")
outside_pattern = re.compile(r"([.\^$*+?()\[{])")


class RegExpBuilder:
    def __init__(self):
        self._literal = ""
        self._clear()


    def _clear(self):
        self._ignoreCase = False
        self._multiLine = False
        self._min = -1
        self._max = -1
        self._of = ""
        self._ofAny = False
        self._ofGroup = None
        self._from = ""
        self._notFrom = ""
        self._like = ""
        self._either = ""
        self._reluctant = False
        self._capture = False
        self._capture_name = ""


    def _flushState(self):
        if self._of or self._ofAny or self._ofGroup or self._from or self._notFrom or self._like:
            if self._min != -1:
                if self._max != -1:
                    quantity = "{{{},{}}}".format(self._min, self._max)
                else:
                    quantity = "{{{},}}".format(self._min)
            elif self._max != -1:
                quantity = "{{0,{}}}".format(self._max)
            else:
                quantity = ""

            if self._of:
                char = self._of
            elif self._ofAny:
                char = "."
            elif self._ofGroup:
                char = "\\{}".format(self._ofGroup)
            elif self._from:
                char = "[{}]".format(self._from)
            elif self._notFrom:
                char = "[^{}]".format(self._notFrom)
            elif self._like:
                char = self._like

            capture_name = "?P<{}>".format(self._capture_name) if self._capture_name else ""

            self._literal += "(" + (capture_name if self._capture else "?:") + "(?:" + char + ")" + quantity + ("?" if self._reluctant else "") + ")"
            self._clear()


    def getLiteral(self):
        self._flushState()
        return self._literal


    def getRegExp(self, flags=0):
        self._flushState()
        if self._ignoreCase:
            flags |= re.IGNORECASE
        if self._multiLine:
            flags |= re.MULTILINE
        return re.compile(self._literal, flags)


    def ignoreCase(self):
        self._ignoreCase = True
        return self


    def multiLine(self):
        self._multiLine = True
        return self


    def startOfInput(self):
        self._literal += "(?:^)"
        return self


    def startOfLine(self):
        self.multiLine()
        return self.startOfInput()


    def endOfInput(self):
        self._flushState()
        self._literal += "(?:$)"
        return self


    def endOfLine(self):
        self.multiLine()
        return self.endOfInput()


    def eitherLike(self, r):
        if not isinstance(r, RegExpBuilder):
            raise ValueError
        self._flushState()
        self._either = r.getLiteral()
        return self


    def eitherString(self, s):
        return self.eitherLike(RegExpBuilder().exactly(1).of(s))


    def orLike(self, r):
        if not isinstance(r, RegExpBuilder):
            raise ValueError
        if not self._either:
            self._literal = "{}|(?:{}))".format(self._literal[:-1], r.getLiteral())
        else:
            self._literal += "(?:(?:{})|(?:{}))".format(self._either, r.getLiteral())
        self._clear()
        return self


    def orString(self, s):
        return self.orLike(RegExpBuilder().exactly(1).of(s))


    def exactly(self, n):
        if not isinstance(n, int):
            raise ValueError
        self._flushState()
        self._min, self._max = n, n
        return self


    def min(self, n):
        if not isinstance(n, int):
            raise ValueError
        self._flushState()
        self._min = n
        return self


    def max(self, n):
        if not isinstance(n, int):
            raise ValueError
        self._flushState()
        self._max = n
        return self


    def of(self, s):
        if not isinstance(s, basestring):
            raise ValueError
        self._of = outside_pattern.sub(r"\\\1", s)
        return self


    def ofAny(self):
        self._ofAny = True
        return self


    def ofGroup(self, n):
        if not isinstance(n, int) or self._ofGroup is not None:
            raise ValueError
        self._ofGroup = n
        return self


    def fromClass(self, s):
        if not isinstance(s, (list, set)):
            raise ValueError
        self._from = inside_pattern.sub(r"\\\1", ''.join(s))
        return self


    def notFromClass(self, s):
        if not isinstance(s, (list, set)):
            raise ValueError
        self._notFrom = inside_pattern.sub(r"\\\1", ''.join(s))
        return self


    def like(self, r):
        if not isinstance(r, RegExpBuilder):
            raise ValueError
        self._like = r.getLiteral()
        return self


    def reluctantly(self):
        self._reluctant = True
        return self

    nonGreedy = nonGreedily = reluctantly


    def ahead(self, r):
        if not isinstance(r, RegExpBuilder):
            raise ValueError
        self._flushState()
        self._literal += "(?={})".format(r.getLiteral())
        return self


    def notAhead(self, r):
        if not isinstance(r, RegExpBuilder):
            raise ValueError
        self._flushState()
        self._literal += "(?!{})".format(r.getLiteral())
        return self


    def asGroup(self, name=""):
        if not isinstance(name, basestring):
            raise ValueError
        self._capture = True
        self._capture_name = name
        return self

    capture = asGroup


    def then(self, s):
        return self.exactly(1).of(s)


    def some(self, s):
        return self.min(1).fromClass(s)


    def maybeSome(self, s):
        return self.min(0).fromClass(s)


    def maybe(self, s):
        return self.max(1).of(s)


    def anything(self):
        return self.min(1).ofAny()


    def lineBreak(self):
        return self.eitherString("\r\n").orString("\r").orString("\n")


    def lineBreaks(self):
        return self.like(RegExpBuilder().lineBreak())


    def whitespace(self):
        if self._min == -1 and self._max == -1:
            return self.exactly(1).of("\s")
        self._like = "\s"
        return self


    def tab(self):
        return self.exactly(1).of("\t")


    def tabs(self):
        return self.like(RegExpBuilder().tab())


    def digit(self):
        return self.exactly(1).of("\d")


    def digits(self):
        return self.like(RegExpBuilder().digit())


    def letter(self):
        self.exactly(1)
        self._from = "A-Za-z"
        return self


    def letters(self):
        self._from = "A-Za-z"
        return self


    def lowerCaseLetter(self):
        self.exactly(1)
        self._from = "a-z"
        return self


    def lowerCaseLetters(self):
        self._from = "a-z"
        return self


    def upperCaseLetter(self):
        self.exactly(1)
        self._from = "A-Z"
        return self


    def upperCaseLetters(self):
        self._from = "A-Z"
        return self


    def append(self, r):
        if not isinstance(r, RegExpBuilder):
            raise ValueError
        self.exactly(1)
        self._like = r.getLiteral()
        return self


    def optional(self, r):
        if not isinstance(r, RegExpBuilder):
            raise ValueError
        self.max(1)
        self._like = r.getLiteral()
        return self


if __name__ == "__main__":
    pass


