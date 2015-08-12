from itertools import compress

class QuestionScale():

    @staticmethod
    def create_scale(type, choices, exclude_from_analysis, values=None, 
                     midpoint=None):
        if type=='nominal':
            return(NominalScale(choices, exclude_from_analysis))
        elif type =='ordinal':
            return(OrdinalScale(choices, exclude_from_analysis, values))
        elif type =='likert':
            return(LikertScale(choices, exclude_from_analysis, values, midpoint))
        else:
            raise(Exception("Invalid scale type: {}".format(type)))

    def __init__(self, choices, exclude_from_analysis):
        self.choices = choices
        self.exclude_from_analysis = exclude_from_analysis

    def __eq__(self, other): 
        return (self.choices == other.choices and 
                self.exclude_from_analysis == other.exclude_from_analysis)

    @staticmethod
    def change_scale(oldscale, new_type, new_values=None, new_midpoint=None):
        if hasattr(oldscale, 'values') and new_values==None:
            new_values = oldscale.values
        if hasattr(oldscale, 'midpoint') and new_midpoint==None:
            new_midpoint = oldscale.midpoint
        return(QuestionScale.create_scale(new_type, oldscale.choices, 
            oldscale.exclude_from_analysis, new_values, new_midpoint))


    def reverse_choices(self):
        self.choices.reverse()
        self.exclude_from_analysis.reverse()

    def get_choices(self, remove_exclusions=True):
        choices = self.choices
        if remove_exclusions:
            choices = list(compress(choices, 
                      [not x for x in self.exclude_from_analysis]))
        return(choices)

    def exclude_choices_from_analysis(self, choices):
        new_excl = []
        for c, e in zip(self.choices, self.exclude_from_analysis):
            if c in choices:
                new_excl.append(True)
            else:
                new_excl.append(e)
        self.exclude_from_analysis = new_excl

class NominalScale(QuestionScale):

    def __init__(self, choices, exclude_from_analysis):
        super().__init__(choices, exclude_from_analysis)

    def excluded_choices(self):
        x = list(compress(self.choices, 
                      [x for x in self.exclude_from_analysis]))
        return(x)

class OrdinalScale(QuestionScale):

    def __init__(self, choices, exclude_from_analysis, values):
        super().__init__(choices, exclude_from_analysis)
        self.values = values

    def __eq__(self, other):
        if super().__eq__(other):
            return(self.values == other.values)
        else:
            return(False)

    def reverse_choices(self):
        super().reverse_choices()
        self.values.reverse()

    def get_values(self, remove_exclusions=True):
        values = self.values
        if remove_exclusions:
            values = list(compress(values, 
                      [not x for x in self.exclude_from_analysis]))
        return(values)

    def choices_to_str(self, remove_exclusions=False, show_values=True):
        choices = self.get_choices(remove_exclusions)
        values = self.get_values(remove_exclusions)
        if show_values:
            new_choices = []
            for c, v, x in zip(choices, values, self.exclude_from_analysis):
                if x:
                    new_choices.append("{} (X)".format(c))
                else:
                    new_choices.append("{} ({})".format(c, v))
            choices = new_choices
        return(choices)


class LikertScale(OrdinalScale):

    def __init__(self, choices, exclude_from_analysis, values, midpoint=None):
        super().__init__(choices, exclude_from_analysis, values)
        ct = len(self.exclude_from_analysis) - sum(self.exclude_from_analysis)
        if not midpoint:
            self.midpoint = ct/2
        else:
            if midpoint > ct or midpoint < 0:
                raise(
                    Exception("Invalid midpoint {} for {} point scale".format(midpoint, ct
                    ))
                )
            else:
                self.midpoint = midpoint

    def __eq__(self, other):
        if super().__eq__(other):
            return(self.midpoint == other.midpoint)
        else:
            return(False)

