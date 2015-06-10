SurveyHelper
------------

SurveyHelper is currently under development. It will be a package for 
analyzing survey data. It is initially geared at reading surveys in from 
Qualtrics and providing methods to display and analyze survey results.

Example usage:

	>>> from surveyhelper.codebook import Codebook
	>>> from surveyhelper.qsf_parser import QsfParser
	>>> p = QsfParser('Sample_Survey.qsf')
	>>> c = p.create_codebook()
	>>> c.pretty_print()