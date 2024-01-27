import unittest
from parameterized import parameterized
from spacytest import question_to_statement  # Make sure to import your function from the script

class QuestionToStatementTest(unittest.TestCase):

    @parameterized.expand([
        ("Will at least 3 months of third party safety evaluations be conducted on Gemini before its deployment?", 
         "50%", 
         "There is a 50% chance that at least 3 months of third party safety evaluations will be conducted on Gemini before its deployment according to Metaculus prediction community."),
        ("Will one of the first AGI claim to be conscious?",
         "45%",
         "There is a 45% chance that one of the first AGI will claim to be conscious according to Metaculus prediction community.")
        # Add more test cases here as tuples (question, prediction_info, expected_result)
    ])
    def test_question_to_statement(self, question, prediction_info, expected_result):
        result = question_to_statement(question, prediction_info)
        self.assertEqual(result, expected_result)

if __name__ == "__main__":
    unittest.main()
