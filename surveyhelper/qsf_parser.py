"""
Parses a Qualtrics .qsf file and creates a codebook from it.
"""

import json
import re
import logging
from pprint import pprint
from bs4 import BeautifulSoup
from surveyhelper import SelectOneQuestion, SelectMultipleQuestion, \
SelectOneMatrixQuestion, SelectMultipleMatrixQuestion, Codebook

class QsfParser:

    def __init__(self, qsf_filename, options = {'exclude_trash': True}):
        with open(qsf_filename) as qsf_file:
            qsf = json.load(qsf_file)
        self.qsf = qsf
        self.options = options

    @staticmethod
    def remove_html(text):
        soup = BeautifulSoup(text)
        [s.extract() for s in soup('style')]
        return(soup.get_text().strip())

    def create_codebook(self, title = None):
        q = self.create_questions()
        if title == None:
            title = self.get_survey_title()
        return(Codebook(title, q))

    def get_survey_title(self):
        return(self.qsf['SurveyEntry']['SurveyName'])

    def pretty_print(self):
        pprint(self.qsf)
        return

    def get_block_order(self):
        """
        Return a list of block ids in the order they appear in the
        survey
        """
        flow_info = [e['Payload']['Flow'] 
                     for e in self.qsf['SurveyElements']
                     if e['Element'] == 'FL']
        if len(flow_info) != 1:
            raise(Exception("Invalid flow specification"))
        block_order = [e['ID'] for e in flow_info[0]
                       if e['Type'] in ['Standard', 'Block']]
        return(block_order)

    def get_block_dict(self):
        """
        Returns a dictionary mapping block id to the dictionary
        containing all the block info
        """
        block_info = [e['Payload'] for e in self.qsf['SurveyElements']
                      if e['Element'] == 'BL']
        if len(block_info) != 1:
            raise(Exception("Invalid block specification"))
        blocks = block_info[0]
        blocks_by_id = {}

        # It appears that sometimes blocks is a list containing one
        # or more dicts, and sometimes it's already a dict at this point
        if type(blocks) == list:
            for block_dict in blocks:
                blocks_by_id[block_dict['ID']] = block_dict

        else:
            for k, v in blocks.items():
                blocks_by_id[v['ID']] = v

        return(blocks_by_id)

    def get_question_order(self):
        """
        Returns a list of question ids, in the same order they 
        appear in the survey
        """
        block_order = self.get_block_order()
        blocks_by_id = self.get_block_dict()
        exclude_trash = self.options['exclude_trash']

        ordered_qids = []
        for k in block_order:
            data = blocks_by_id[k]
            if ((data['Type'] == 'Trash' and exclude_trash) or 
            'BlockElements' not in data):
                continue
            qids = [e['QuestionID'] for e in data['BlockElements']
                    if e['Type'] == 'Question']
            ordered_qids += qids
        return(ordered_qids)

    def get_question_json(self, qids):
        """
        Given a list of Qualtrics question ids, extract the 
        corresponding parsed JSON. Returns a dict, mapping QID to to
        parsed JSON dict
        """
        q = [e for e in self.qsf['SurveyElements'] 
             if e['Element'] == 'SQ' 
             and e['Payload']['QuestionID'] in qids]
        questions = {}
        for i in q:
            questions[i['Payload']['QuestionID']] = i
        return(questions)

    def create_questions(self):
        """
        From what I can tell about the qsf format, the question types we
        want to extract are the ones where "QuestionType" == "MC",
        "Matrix", "TE" (text entry), or "SBS" (side by side)
        """
        
        qids = self.get_question_order()
        qid_to_json = self.get_question_json(qids)

        questions = []
        for id in qids:
            json = qid_to_json[id]['Payload']
            if (json['QuestionType'] == 'MC' and 
            json['Selector'] in ['SAVR', 'SAHR']):
                questions.append(self.build_sqsr(json))
            elif (json['QuestionType'] == 'MC' and 
            json['Selector'] in ['MACOL', 'MAVR']):
                questions.append(self.build_sqmr(json))
            elif (json['QuestionType'] == 'Matrix' and
            json['Selector'] == 'Likert' and json['SubSelector'] ==
            'SingleAnswer'):
                questions.append(self.build_mqsr(json))
            elif (json['QuestionType'] == 'Matrix' and
            json['Selector'] == 'Likert' and json['SubSelector'] ==
            'MultipleAnswer'):
                questions.append(self.build_mqmr(json))
            else:
                txt = json['QuestionText']
                qtype = json['QuestionType']
                select = json['Selector']
                logging.info("Skipping question {}\n\nType: {}\nSelector: {}")
        return(questions)

    def _recode_exclusions(self, exclusions, recode):
        exclusions_rcd = {}
        for k, v in exclusions.items():
            if v != "No":
                continue
            elif k in recode:
                exclusions_rcd[int(recode[k])] = True
            else:
                exclusions_rcd[int(k)] = True
        return(exclusions_rcd)

    def _parse_recode_values(self, json):
        if 'RecodeValues' in json:
            recode = json['RecodeValues']
        else:
            recode = {}
        return(recode)

    def _parse_analyze_choices(self, json):
        if 'AnalyzeChoices' in json:
            exclude = json['AnalyzeChoices']
        else:
            exclude = {}
        return(exclude)   


    def build_sr_question(self, text, label, choices, recode, var,
        provides_int, exclusions):
        """
        """
        txt_cln = QsfParser.remove_html(text)
        choices_cln = dict([(k, QsfParser.remove_html(v['Display'])) 
                           for k, v in choices.items()])
        choices_rcd = {}
        for k, v in recode.items():
            choices_rcd[int(v)] = choices_cln[k]
        for k in choices_cln.keys() - recode.keys():
            choices_rcd[int(k)] = choices_cln[k]
        exclusions_rcd = self._recode_exclusions(exclusions, recode)

        choices_text = []
        values = []
        for k in sorted(choices_rcd.keys()):
            values.append(k)
            choices_text.append(choices_rcd[k])
        exclude = []
        for v in values:
            if v in exclusions_rcd:
                exclude.append(True)
            else:
                exclude.append(False)
        return(SelectOneQuestion(txt_cln, var, choices_text, label, 
               values, exclude))

    def build_sqsr(self, json):
        recode = self._parse_recode_values(json)
        exclude = self._parse_analyze_choices(json)
        q = self.build_sr_question(json['QuestionText'], 
            json['DataExportTag'], json['Choices'], recode, 
            json['DataExportTag'], True, exclude)
        return(q)

    def build_mqsr(self, json):
        stem_text = QsfParser.remove_html(json['QuestionText'])
        tag = json['DataExportTag']
        recode = self._parse_recode_values(json)
        exclude = self._parse_analyze_choices(json)

        questions = []
        for k in json['ChoiceOrder']:
            text = json['Choices'][str(k)]['Display']
            if 'ChoiceDataExportTags' in json and json['ChoiceDataExportTags']:
                var = json['ChoiceDataExportTags'][str(k)]
            else:
                var = "{}_{}".format(tag, k)
            q = self.build_sr_question(text, tag, json['Answers'], 
                recode, var, True, exclude)
            questions.append(q)
        return(SelectOneMatrixQuestion(stem_text, tag, questions))

    def build_mr_question(self, text, label, choices, recode, var_base,
        provides_int, exclusions):
        """
        """
        text = QsfParser.remove_html(text)
        choices_cln = dict([(k, QsfParser.remove_html(v['Display'])) 
                           for k, v in choices.items()])
        choices_rcd = {}
        recode_inverse = {}
        for k, v in recode.items():
            choices_rcd[int(v)] = choices_cln[k]
            recode_inverse[int(v)] = int(k)
        for k in choices_cln.keys() - recode.keys():
            choices_rcd[int(k)] = choices_cln[k]
            recode_inverse[int(k)] = int(k)

        exclusions_rcd = self._recode_exclusions(exclusions, recode)
        ans_choices = []
        variables = []
        exclude = []
        for c in sorted(choices_rcd.keys()):
            ans_choices.append(choices_rcd[c])
            orig_pos = recode_inverse[c]
            variables.append("{}_{}".format(var_base, orig_pos))
            if c in exclusions_rcd:
                exclude.append(True)
            else:
                exclude.append(False)
        return(SelectMultipleQuestion(text, variables, ans_choices,
            label, exclude))


    def build_sqmr(self, json):
        recode = self._parse_recode_values(json)
        exclude = self._parse_analyze_choices(json)
        q = self.build_mr_question(json['QuestionText'], 
            json['DataExportTag'], json['Choices'], recode, 
            json['DataExportTag'], True, exclude)
        return(q)

    def build_mqmr(self, json):
        stem_text = QsfParser.remove_html(json['QuestionText'])
        tag = json['DataExportTag']
        recode = self._parse_recode_values(json)
        exclude = self._parse_analyze_choices(json)

        children = []
        for k in json['ChoiceOrder']:
            text = json['Choices'][str(k)]['Display']
            if 'ChoiceDataExportTags' in json and json['ChoiceDataExportTags']:
                var = json['ChoiceDataExportTags'][str(k)]
            else:
                var = "{}_{}".format(tag, k)
            q = self.build_mr_question(text, var, json['Answers'], 
                recode, var, True, exclude)
            children.append(q)
        return(SelectMultipleMatrixQuestion(stem_text, tag, children))

                