
class Question:

	def __init__(self, text, tag, children = [], parent = None):
		self.text = text
		self.tag = tag
		self.children = children
		for child in self.children:
			child.parent = self
		self.parent = parent


	def get_text_this_level(self):
		return(self.text)

	def is_atomic(self):
		return(False)

	def get_answers(self):
		qs = self.get_atomic_questions()
		answers = [q.answers for q in qs]
		if not answers:
			return
		else:
			first = answers[0]
			for a in answers:
				if a != first:
					raise(Exception("All atomic questions with the same ancestors must have the same answers"))
			return(first)

	def print_answers(self):
		qs = self.get_atomic_questions()
		answers = [q.answers for q in qs]
		if not answers:
			return
		else:
			first = answers[0]
			for a in answers:
				if a != first:
					raise(Exception("All atomic questions with the same ancestors must have the same answers"))
			qs[0].print_answers()
			return

	def get_atomic_questions(self):
		atomic = []
		for c in self.children:
			if c.is_atomic():
				atomic.append(c)
			else:
				for q in c.get_atomic_questions():
					atomic.append(q)
		return(atomic)

	def is_single_answer(self):
		a = self.get_answers()
		if a and len(a.keys()) == 1:
			return(True)
		else:
			return(False)

	def get_text_complete(self, sep = "..."):
		""" 
		Returns the complete parent text, down to this level.
		"""
		if self.parent:
			t = self.parent.get_text_complete(sep)
		else:
			t = ""
		return(t + sep + self.text)

	def pretty_print(self):
		print("{} ({})".format(self.text, self.tag))
		if not(self.parent):
			self.print_answers()

		for c in self.children:
			c.pretty_print()
		return


class AtomicQuestion(Question):

	def __init__(self, text, tag, answers, variable, maps_to_int, 
		         parent, exclude_from_analysis):
		self.text = text
		self.tag = tag
		# answers is int to string map
		self.answers = answers
		self.variable = variable
		self.maps_to_int = maps_to_int
		self.parent = parent
		self.children = []
		self.exclude_from_analysis = exclude_from_analysis

	def is_atomic(self):
		return(True)

	def provides_int(self):
		return(self.maps_to_int)

	def pretty_print(self):
		if self.is_single_answer() and self.exclude_from_analysis.keys() \
		== self.answers.keys():
		  	print("{} ({}) (X)".format(self.text, self.variable))
		else:
		  	print("{} ({})".format(self.text, self.variable))
		if not self.parent:
			self.print_answers()
		return

	def get_answers(self):
		return(self.answers)

	def print_answers(self):
		if len(self.answers.keys()) == 1:
			return
		a = []
		for k in sorted(self.answers.keys()):
			if k not in self.exclude_from_analysis:
				a.append("{} ({})".format(self.answers[k], k))
			else:
				a.append("{} (X)".format(self.answers[k]))
		print("Answers: {}".format(", ".join(a)))
