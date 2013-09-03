import re




class RegExpBuilder:
    def __init__(self):
        self.inside_char_class_pattern = re.compile(r"([\^\-\]])")
        self.outside_char_class_pattern = re.compile(r"([.\^$*+?()\[{])")
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


    def _flush_state(self):
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


    def get_literal(self):
        self._flush_state()
        return self._literal


    def get_regexp(self, flags=0):
        self._flush_state()
        if self._ignoreCase:
            flags |= re.IGNORECASE
        if self._multiLine:
            flags |= re.MULTILINE
        return re.compile(self._literal, flags)


    def ignore_case(self):
        self._ignoreCase = True
        return self


    def multi_line(self):
        self._multiLine = True
        return self


    def start_of_input(self):
        self._literal += "(?:^)"
        return self


    def start_of_line(self):
        self.multi_line()
        return self.start_of_input()


    def end_of_input(self):
        self._flush_state()
        self._literal += "(?:$)"
        return self


    def end_of_line(self):
        self.multi_line()
        return self.end_of_input()


    def either(self, s):
        firstElement = s[0]
        if isinstance(firstElement, basestring):
            self._either_like(RegExpBuilder().exactly(1).of(firstElement))
        else:
            self._either_like(firstElement)
        for element in s[1:]:
            if isinstance(element, basestring):
                self._or_like(RegExpBuilder().exactly(1).of(element))
            else:
                self._or_like(element)


    def _either_like(self, r):
        if not isinstance(r, RegExpBuilder):
            raise ValueError
        self._flush_state()
        self._either = r.get_literal()
        return self


    def _or_like(self, r):
        if not isinstance(r, RegExpBuilder):
            raise ValueError
        eitherLike = self._either
        orLike = r.get_literal()
        if not eitherLike: # == "":
            self._literal = "{}|(?:{}))".format(self._literal[:-1], orLike)
        else:
            self._literal += "(?:(?:{})|(?:{}))".format(self._either, orLike)
        self._clear()
        return self


    def exactly(self, n):
        if not isinstance(n, int):
            raise ValueError
        self._flush_state()
        self._min = self._max = n
        return self


    def min(self, n):
        if not isinstance(n, int):
            raise ValueError
        self._flush_state()
        self._min = n
        return self


    def max(self, n):
        if not isinstance(n, int):
            raise ValueError
        self._flush_state()
        self._max = n
        return self


    def of(self, s):
        if not isinstance(s, basestring):
            raise ValueError
        self._of = self.outside_char_class_pattern.sub(r"\\\1", s)
        return self


    def of_any(self):
        self._ofAny = True
        return self


    def of_group(self, n):
        if not isinstance(n, int) or self._ofGroup is not None:
            raise ValueError
        self._ofGroup = n
        return self


    def from_class(self, s):
        if not isinstance(s, (list, set)):
            raise ValueError
        self._from = self.inside_char_class_pattern.sub(r"\\\1", ''.join(s))
        return self


    def not_from_class(self, s):
        if not isinstance(s, (list, set)):
            raise ValueError
        self._notFrom = self.inside_char_class_pattern.sub(r"\\\1", ''.join(s))
        return self


    def like(self, r):
        if not isinstance(r, RegExpBuilder):
            raise ValueError
        self._like = r.get_literal()
        return self


    def reluctantly(self):
        self._reluctant = True
        return self

    nonGreedy = nonGreedily = reluctantly


    def ahead(self, r):
        if not isinstance(r, RegExpBuilder):
            raise ValueError
        self._flush_state()
        self._literal += "(?={})".format(r.get_literal())
        return self


    def not_ahead(self, r):
        if not isinstance(r, RegExpBuilder):
            raise ValueError
        self._flush_state()
        self._literal += "(?!{})".format(r.get_literal())
        return self


    def as_group(self, name=""):
        if not isinstance(name, basestring):
            raise ValueError
        self._capture = True
        self._capture_name = name
        return self

    capture = as_group


    def then(self, s):
        return self.exactly(1).of(s)


    def some(self, s):
        return self.min(1).from_class(s)


    def maybe_some(self, s):
        return self.min(0).from_class(s)


    def maybe(self, s):
        return self.max(1).of(s)


    def something(self):
        return self.min(1).of_any()


    def anything(self):
        return self.min(0).of_any()


    def any(self):
        return self.exactly(1).of_any()


    def line_break(self):
        return self.either(["\r\n", "\r", "\n"])


    def line_breaks(self):
        return self.like(RegExpBuilder().line_break())


    def whitespace(self):
        if self._min == -1 and self._max == -1:
            return self.exactly(1).of("\s")
        self._like = "\s"
        return self


    def not_whitespace(self):
        if self._min == -1 and self._max == -1:
            return self.exactly(1).of("\S")
        self._like = "\S"
        return self


    def tab(self):
        return self.exactly(1).of("\t")


    def tabs(self):
        return self.like(RegExpBuilder().tab())


    def digit(self):
        return self.exactly(1).of("\d")


    def not_digit(self):
        return self.exactly(1).of("\D")


    def digits(self):
        return self.like(RegExpBuilder().digit())


    def not_digits(self):
        return self.like(RegExpBuilder().not_digit())


    def letter(self):
        self.exactly(1)
        self._from = "A-Za-z"
        return self


    def not_letter(self):
        self.exactly(1)
        self._notFrom = "A-Za-z"
        return self


    def letters(self):
        self._from = "A-Za-z"
        return self


    def not_letters(self):
        self._not_from = "A-Za-z"
        return self

    def lower_case_letter(self):
        self.exactly(1)
        self._from = "a-z"
        return self


    def lower_case_letters(self):
        self._from = "a-z"
        return self


    def upper_case_letter(self):
        self.exactly(1)
        self._from = "A-Z"
        return self


    def upper_case_letters(self):
        self._from = "A-Z"
        return self


    def append(self, r):
        if not isinstance(r, RegExpBuilder):
            raise ValueError
        self.exactly(1)
        self._like = r.get_literal()
        return self


    def optional(self, r):
        if not isinstance(r, RegExpBuilder):
            raise ValueError
        self.max(1)
        self._like = r.get_literal()
        return self

