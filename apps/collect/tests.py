import unittest

class TestCollectFunctions(unittest.TestCase):

    def setUp(self):
        self.incident_str = ""

    def test_nogeofix(self):
        #If google returns invalid data or None when geocoding an incident, deal with it accordingly and gracefully
        pass 
    
    def test_parse(self):
        # make sure the shuffled sequence does not lose any elements
        random.shuffle(self.seq)
        self.seq.sort()
        self.assertEqual(self.seq, range(10))

        # should raise an exception for an immutable sequence
        self.assertRaises(TypeError, random.shuffle, (1,2,3))

    def test_choice(self):
        element = random.choice(self.seq)
        self.assertTrue(element in self.seq)