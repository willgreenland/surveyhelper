"""
Codebook
--------
Represents information about all the questions in a survey and
their possible responses.
"""

from collections import OrderedDict

class Codebook:

    def __init__(self, survey_title, questions_list):
        """
        store all of the questions in an OrderedDict
        """
        self.survey_title = survey_title
        self.questions = OrderedDict()
        for q in questions_list:
            self.questions[q.tag] = q

    def get_question(self, qname):
        if qname in self.questions:
            return(self.questions[qname])
        else:
            raise KeyError("Question not found: {}".format(qname))

    def get_questions(self):
        return([v for k, v in self.questions.items()])

    def pretty_print(self):
        print("Survey: {}".format(self.survey_title))
        for k, v in self.questions.items():
            v.pretty_print()
            print()
        return
