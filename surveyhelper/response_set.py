import pandas as pd
import numpy as np

class ResponseSet:

    @staticmethod
    def get_data(response_file, codebook, skiprows = [1], encoding="utf8"):
        df = pd.read_csv(response_file , skiprows=skiprows, encoding=encoding)
        # go through each variable in the codebook and make sure the corresponding 
        # column is integer coded
        matched_questions = []
        for q in codebook.get_questions():
            matched = True
            for v in q.get_variable_names():
                if v not in df:
                    print("Warning: Expected variable {} not found in data file {}".format(v, response_file))
                    matched = False
                elif df[v].dtype not in [np.int64, np.float64]:
                    print("Converting variable {} to integer from {}".format(v, df[v].dtype))
                    df[v] = df[v].convert_objects(convert_numeric=True)
            if matched: matched_questions.append(q)
        return(df, matched_questions)



    @staticmethod
    def get_grouped_data(df, grouping_question):
        groups = df.groupby(grouping_question.tag)
        
