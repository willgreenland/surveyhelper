SurveyHelper
------------

SurveyHelper is a Python 3 package currently under development. It will 
provide utilities for analyzing and visualizing survey data. It is 
initially geared at reading surveys in from Qualtrics by parsing a .qsf 
file and a response file. At present, it creates html frequency reports
using d3.js.

Example usage::

	from surveyhelper.codebook import Codebook
	from surveyhelper.qsf_parser import QsfParser
	p = QsfParser('Sample_Survey.qsf')
	c = p.create_codebook()
	c.pretty_print()

	import surveyhelper as sh

    p = sh.QsfParser("my_qualtrics_file.qsf")
    c = p.create_codebook()

    for label in ['Q1', 'Q2', 'Q3']:
		c.questions[label].exclude_choices_from_analysis(['Not applicable'])

    for label in ['Q2', 'Q3']:
		c.questions[label].change_scale('ordinal')

	c.questions['Q1'].reverse_choices()
    c.questions['Q1'].change_midpoint(2)

    # Remove initial numbering from question text
    for label, q in c.questions.items():
		q.text = re.sub(r'[0-9]\. ','', q.text)


	r = sh.ResponseSet("my_qualtrics_responses.csv", c)
	f = sh.FrequencyReport(r, 'config.yml')
	f.create_report()