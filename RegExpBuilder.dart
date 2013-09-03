class RegExpBuilder {
  
  List<String> _literal;
  bool _ignoreCase;
  bool _multiLine;
  HashSet<String> _specialCharactersInsideCharacterClass;
  HashSet<String> _specialCharactersOutsideCharacterClass;
  List<String> _escapedString;
  int _min;
  int _max;
  String _of;
  bool _ofAny;
  int _ofGroup;
  String _from;
  String _notFrom;
  String _like;
  String _either;
  bool _reluctant;
  bool _capture;
  
  RegExpBuilder() {
    _literal = [];
    _specialCharactersInsideCharacterClass = new HashSet.from([@"^", @"-", @"]"]);
    _specialCharactersOutsideCharacterClass = new HashSet.from([@".", @"^", @"$", @"*", @"+", @"?", @"(", @")", @"[", @"{"]);
    _escapedString = [];
    _clear();
  }
  
  void _clear() {
    _ignoreCase = false;
    _multiLine = false;
    _min = -1;
    _max = -1;
    _of = "";
    _ofAny = false;
    _ofGroup = -1;
    _from = "";
    _notFrom = "";
    _like = "";
    _either = "";
    _reluctant = false;
    _capture = false;
  }
  
  void _flushState() {
    if (_of != "" || _ofAny || _ofGroup > 0 || _from != "" || _notFrom != "" || _like != "") {
      var captureLiteral = _capture ? "" : "?:";
      var quantityLiteral = _getQuantityLiteral();
      var characterLiteral = _getCharacterLiteral();
      var reluctantLiteral = _reluctant ? "?" : "";
      _literal.add("($captureLiteral(?:$characterLiteral)$quantityLiteral$reluctantLiteral)");
      _clear();
    }
  }
  
  String _getQuantityLiteral() {
    if (_min != -1) {
      if (_max != -1) {
        return "{$_min,$_max}";
      }
      return "{$_min,}";
    }
    return "{0,$_max}";
  }
  
  String _getCharacterLiteral() {
    if (_of != "") {
      return _of;
    }
    if (_ofAny) {
      return ".";
    }
    if (_ofGroup > 0) {
      return "\\$_ofGroup";
    }
    if (_from != "") {
      return "[$_from]";
    }
    if (_notFrom != "") {
      return "[^$_notFrom]";
    }
    if (_like != "") {
      return _like;
    }
  }
  
  String getLiteral() {
    _flushState();
    return Strings.concatAll(_literal);
  }
  
  RegExp getRegExp() {
    return new RegExp(getLiteral(), _ignoreCase, _multiLine);
  }
  
  RegExpBuilder ignoreCase() {
    _ignoreCase = true;
    return this;
  }
  
  RegExpBuilder multiLine() {
    _multiLine = true;
    return this;
  }
  
  RegExpBuilder startOfInput() {
    _literal.add("(?:^)");
    return this;
  }
  
  RegExpBuilder startOfLine() {
    multiLine();
    return startOfInput();
  }
  
  RegExpBuilder endOfInput() {
    _flushState();
    _literal.add(@"(?:$)");
    return this;
  }
  
  RegExpBuilder endOfLine() {
    multiLine();
    return endOfInput();
  }
  
  RegExpBuilder either(Dynamic r) {
    if (r is String) {
      return this._eitherLike(new RegExpBuilder().exactly(1).of(r));
    }
    else {
      return this._eitherLike(r);
    }
  }
  
  RegExpBuilder _eitherLike(RegExpBuilder r) {
    _flushState();
    _either = r.getLiteral();
    return this;
  }
  
  RegExpBuilder or(Dynamic r) {
    if (r is String) {
      return this._orLike(new RegExpBuilder().exactly(1).of(r));
    }
    else {
      return this._orLike(r);
    }
  }
  
  RegExpBuilder _orLike(RegExpBuilder r) {
    var either = _either;
    var or = r.getLiteral();
    if (either == "") {
      var lastOr = _literal.last();
      _literal[_literal.length - 1] = lastOr.substring(0, lastOr.length - 1);
      _literal.add("|(?:$or))");
    }
    else {
      _literal.add("(?:(?:$either)|(?:$or))");
    }
    _clear();
    return this;
  }
  
  RegExpBuilder exactly(int n) {
    _flushState();
    _min = n;
    _max = n;
    return this;
  }
  
  RegExpBuilder min(int n) {
    _flushState();
    _min = n;
    return this;
  }
  
  RegExpBuilder max(int n) {
    _flushState();
    _max = n;
    return this;
  }
  
  RegExpBuilder of(String s) {
    _of = _escapeOutsideCharacterClass(s);
    return this;
  }
  
  RegExpBuilder ofAny() {
    _ofAny = true;
    return this;
  }
  
  RegExpBuilder ofGroup(int n) {
    _ofGroup = n;
    return this;
  }
  
  RegExpBuilder from(List<String> s) {
    _from = _escapeInsideCharacterClass(Strings.concatAll(s));
    return this;
  }
  
  RegExpBuilder notFrom(List<String> s) {
    _notFrom = _escapeInsideCharacterClass(Strings.concatAll(s));
    return this;
  }
  
  RegExpBuilder like(RegExpBuilder r) {
    _like = r.getLiteral();
    return this;
  }
  
  RegExpBuilder reluctantly() {
    _reluctant = true;
    return this;
  }
  
  RegExpBuilder ahead(RegExpBuilder r) {
    _flushState();
    _literal.add("(?=${r.getLiteral()})");
    return this;
  }
  
  RegExpBuilder notAhead(RegExpBuilder r) {
    _flushState();
    _literal.add("(?!${r.getLiteral()})");
    return this;
  }
  
  RegExpBuilder asGroup() {
    _capture = true;
    return this;
  }
  
  RegExpBuilder then(String s) {
    return exactly(1).of(s);
  }
  
  RegExpBuilder some(List<String> s) {
    return min(1).from(s);
  }
  
  RegExpBuilder maybeSome(List<String> s) {
    return min(0).from(s);
  }
  
  RegExpBuilder maybe(String s) {
    return max(1).of(s);
  }
  
  RegExpBuilder something() {
    return min(1).ofAny();
  }
  
  RegExpBuilder anything() {
    return min(0).ofAny();
  }
  
  RegExpBuilder any() {
    return exactly(1).ofAny();
  }
  
  RegExpBuilder lineBreak() {
    return either("\r\n").or("\r").or("\n");
  }
  
  RegExpBuilder lineBreaks() {
    return like(new RegExpBuilder().lineBreak());
  }
  
  RegExpBuilder whitespace() {
    if (_min == -1 && _max == -1) {
      return exactly(1).of("\s");
    }
    _like = "\s";
    return this;
  }
  
  RegExpBuilder notWhitespace() {
    if (_min == -1 && _max == -1) {
      return exactly(1).of("\S");
    }
    _like = "\S";
    return this;
  }
  
  RegExpBuilder tab() {
    return exactly(1).of("\t");
  }
  
  RegExpBuilder tabs() {
    return like(new RegExpBuilder().tab());
  }
  
  RegExpBuilder digit() {
    return exactly(1).of("\d");
  }
  
  RegExpBuilder notDigit() {
    return exactly(1).of("\D");
  }
  
  RegExpBuilder digits() {
    return like(new RegExpBuilder().digit());
  }
  
  RegExpBuilder notDigits() {
    return like(new RegExpBuilder().notDigit());
  }
  
  RegExpBuilder letter() {
    exactly(1);
    _from = "A-Za-z";
    return this;
  }
  
  RegExpBuilder notLetter() {
    exactly(1);
    _notFrom = "A-Za-z";
    return this;
  }
  
  RegExpBuilder letters() {
    _from = "A-Za-z";
    return this;
  }
  
  RegExpBuilder notLetters() {
    _notFrom = "A-Za-z";
    return this;
  }
  
  RegExpBuilder lowerCaseLetter() {
    exactly(1);
    _from = "a-z";
    return this;
  }
  
  RegExpBuilder lowerCaseLetters() {
    _from = "a-z";
    return this;
  }
  
  RegExpBuilder upperCaseLetter() {
    exactly(1);
    _from = "A-Z";
    return this;
  }
  
  RegExpBuilder upperCaseLetters() {
    _from = "A-Z";
    return this;
  }
  
  RegExpBuilder append(RegExpBuilder r) {
    exactly(1);
    _like = r.getLiteral();
    return this;
  }
  
  RegExpBuilder optional(RegExpBuilder r) {
    max(1);
    _like = r.getLiteral();
    return this;
  }
  
  String _escapeInsideCharacterClass(String s) {
    return _escapeSpecialCharacters(s, _specialCharactersInsideCharacterClass);
  }

  String _escapeOutsideCharacterClass(String s) {
    return _escapeSpecialCharacters(s, _specialCharactersOutsideCharacterClass);
  }
  
  String _escapeSpecialCharacters(String s, Set<String> specialCharacters) {
    _escapedString.clear();
    for (var i = 0; i < s.length; i++) {
      var character = s[i];
      if (specialCharacters.contains(character)) {
        _escapedString.add("\\$character");
      }
      else {
        _escapedString.add(character);
      }
    }
    return Strings.concatAll(_escapedString);
  }
}
