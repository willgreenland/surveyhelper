"""
FrequencyReport
--------
Provides utilities for producing a survey frequency report.
"""

from jinja2 import Environment, FileSystemLoader
import yaml
from unidecode import unidecode

class FrequencyReport:

    def __init__(self, response_set, config_file):
        with open(config_file, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)

        self.template_dir = cfg['output']['template_dir']
        self.freq_template = cfg['output']['template_file']
        self.report_file = cfg['output']['report_file']
        self.cut_var = cfg['analysis']['cut_variable']
        self.report_title = cfg['report_data']['title']
        self.response_set = response_set

    def create_report(self):
        env = Environment(loader=FileSystemLoader(self.template_dir),
                  extensions=['jinja2.ext.with_'])
        template = env.get_template(self.freq_template)
        outfile = open(self.report_file, 'w+')
        
        questions = []
        for q in self.response_set.matched_questions:
            scale = q.get_scale()
            if scale and hasattr(scale, 'midpoint'):
                midpoint = scale.midpoint
            else:
                midpoint = None
            questions.append((
                            q.text,
                            q.freq_table_to_json(self.response_set.data),
                            [q.freq_table_to_json(self.response_set.data)],
                            q.questions_to_json(),
                            ['all'],
                            q.graph_type(),
                            midpoint
                            ))
        t = template.render(count=len(self.response_set.data),
                                      survey_title=self.report_title,
                                      questions=questions)
        outfile.write(unidecode(t))

