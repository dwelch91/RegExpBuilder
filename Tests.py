import unittest
from RegExpBuilder import RegExpBuilder

class Test(unittest.TestCase):
    def test_start_of_line(self):
        regex = RegExpBuilder()
        regex.start_of_line()
        regex.exactly(1).of("p")
        regex = regex.get_regexp()
    
        self.assertTrue(regex.match("p") is not None)
        self.assertTrue(regex.match("qp") is None)
  
    def test_end_of_line(self):
        regex = RegExpBuilder()
        regex.exactly(1).of("p")
        regex.end_of_line()
        regex = regex.get_regexp()
        
        self.assertTrue(regex.match("p") is not None)
        self.assertTrue(regex.match("pq") is None)
  
    def test_eitherLike_orLike(self):
        p1 = RegExpBuilder().exactly(1).of("p")
        p2 = RegExpBuilder().exactly(2).of("q")
        regex = RegExpBuilder()
        regex.start_of_line()
        regex.either([p1, p2])
        regex.end_of_line()
        regex = regex.get_regexp()
        
        self.assertTrue(regex.match("p") is not None)
        self.assertTrue(regex.match("qq") is not None)
        self.assertTrue(regex.match("pqq") is None)
        self.assertTrue(regex.match("qqp") is None)

    def test_orLike_chain(self):
        p1 = RegExpBuilder().exactly(1).of("p")
        p2 = RegExpBuilder().exactly(1).of("q")
        p3 = RegExpBuilder().exactly(1).of("r")
        regex = RegExpBuilder()
        regex.either([p1, p2, p3])
        regex = regex.get_regexp()

        self.assertTrue(regex.match("p") is not None)
        self.assertTrue(regex.match("q") is not None)
        self.assertTrue(regex.match("r") is not None)
        self.assertTrue(regex.match("s") is None)

    def test_orString(self):
        regex = RegExpBuilder()
        regex.either(["p", "q"])
        regex = regex.get_regexp()

        self.assertTrue(regex.match("p") is not None)
        self.assertTrue(regex.match("q") is not None)
        self.assertTrue(regex.match("r") is None)
  
    def test_exactly(self):
        regex = RegExpBuilder()
        regex.start_of_line()
        regex.exactly(3).of("p")
        regex.end_of_line()
        regex = regex.get_regexp()
        
        self.assertTrue(regex.match("ppp") is not None)
        self.assertTrue(regex.match("pp") is None)
        self.assertTrue(regex.match("pppp") is None) 
  
    def test_min(self):
        regex = RegExpBuilder()
        regex.start_of_line()
        regex.min(2).of("p")
        regex.end_of_line()
        regex = regex.get_regexp()
        
        self.assertTrue(regex.match("pp") is not None)
        self.assertTrue(regex.match("ppp") is not None)
        self.assertTrue(regex.match("ppppppp") is not None)
        self.assertTrue(regex.match("p") is None)
  
    def test_max(self):
        regex = RegExpBuilder()
        regex.start_of_line()
        regex.max(3).of("p")
        regex.end_of_line()
        regex = regex.get_regexp()
        
        self.assertTrue(regex.match("p") is not None)
        self.assertTrue(regex.match("pp") is not None)
        self.assertTrue(regex.match("ppp") is not None)
        self.assertTrue(regex.match("pppp") is None)
        self.assertTrue(regex.match("pppppppp") is None)
  
    def test_min_max(self):
        regex = RegExpBuilder()
        regex.start_of_line()
        regex.min(3).max(7).of("p")
        regex.end_of_line()
        regex = regex.get_regexp()
        
        self.assertTrue(regex.match("ppp") is not None)
        self.assertTrue(regex.match("ppppp") is not None)
        self.assertTrue(regex.match("ppppppp") is not None)
        self.assertTrue(regex.match("pp") is None)
        self.assertTrue(regex.match("p") is None)
        self.assertTrue(regex.match("pppppppp") is None)
        self.assertTrue(regex.match("pppppppppppp") is None)
  
    def test_of(self):
        regex = RegExpBuilder()
        regex.start_of_line()
        regex.exactly(2).of("p p p ")
        regex.end_of_line()
        regex = regex.get_regexp()
        
        self.assertTrue(regex.match("p p p p p p ") is not None)
        self.assertTrue(regex.match("p p p p pp") is None)
  
    def test_ofAny(self):
        regex = RegExpBuilder()
        regex.start_of_line()
        regex.exactly(3).of_any()
        regex.end_of_line()
        regex = regex.get_regexp()
        
        self.assertTrue(regex.match("pqr") is not None)

    def test_ofGroup(self):
        regex = RegExpBuilder()
        regex.start_of_line()
        regex.exactly(3).of("p").as_group()
        regex.exactly(1).of("q")
        regex.exactly(1).of_group(1)
        regex.end_of_line()
        regex = regex.get_regexp()
        
        self.assertTrue(regex.match("pppqppp") is not None)
  
    def test_fromClass(self):
        someLetters = ["p", "q", "r"]
        regex = RegExpBuilder()
        regex.start_of_line()
        regex.exactly(3).from_class(someLetters)
        regex.end_of_line()
        regex = regex.get_regexp()
        
        self.assertTrue(regex.match("ppp") is not None)
        self.assertTrue(regex.match("qqq") is not None)
        self.assertTrue(regex.match("ppq") is not None)
        self.assertTrue(regex.match("rqp") is not None)
        self.assertTrue(regex.match("pyy") is None)
  
    def test_notFromClass(self):
        someLetters = ["p", "q", "r"]
        regex = RegExpBuilder()
        regex.start_of_line()
        regex.exactly(3).not_from_class(someLetters)
        regex.end_of_line()
        regex = regex.get_regexp()
        
        self.assertTrue(regex.match("lmn") is not None)
        self.assertTrue(regex.match("mnq") is None)
  
    def test_like(self):
        pattern = RegExpBuilder().min(1).of("p").min(2).of("q")
        
        regex = RegExpBuilder()
        regex.start_of_line()
        regex.exactly(2).like(pattern)
        regex.end_of_line()
        regex = regex.get_regexp()
        
        self.assertTrue(regex.match("pqqpqq") is not None)
        self.assertTrue(regex.match("qppqpp") is None)
  
    def test_reluctantly(self):
        regex = RegExpBuilder()
        regex.exactly(2).of("p")
        regex.min(2).of_any().reluctantly()
        regex.exactly(2).of("p")
        regex = regex.get_regexp()
        
        self.assertTrue(regex.match("pprrrrpprrpp").group() == "pprrrrpp")
  
    def test_ahead(self):
        regex = RegExpBuilder()
        regex.exactly(1).of("dart")
        regex.ahead(RegExpBuilder().exactly(1).of("lang"))
        regex = regex.get_regexp()
        
        self.assertTrue(regex.match("dartlang").group() == "dart")
        self.assertTrue(regex.match("dartpqr") is None)
  
    def test_notAhead(self):
        regex = RegExpBuilder()
        regex.exactly(1).of("dart")
        regex.not_ahead(RegExpBuilder().exactly(1).of("pqr"))
        regex = regex.get_regexp()
        
        self.assertTrue(regex.match("dartlang") is not None)
        self.assertTrue(regex.match("dartpqr") is None)
  
    def test_asGroup(self):
        regex = RegExpBuilder()
        regex.min(1).max(3).of("p")
        regex.exactly(1).of("dart").as_group()
        regex.exactly(1).from_class(["p", "q", "r"])
        regex = regex.get_regexp()
        
        self.assertTrue(regex.match("pdartq").group(1) == "dart")

if __name__ == '__main__':
    unittest.main()
