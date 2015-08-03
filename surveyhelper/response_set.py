import pandas as pd

class ResponseSet:

    @staticmethod
    def get_data(response_file, skiprows = [1]):
        return(pd.read_csv(response_file , skiprows=skiprows, encoding="utf8"))

    @staticmethod
    def get_grouped_data(df, grouping_question):
        groups = df.groupby(grouping_question.tag)
        
