class TriviaQuestion:
    def __init__(self, question):
        self.question = question["question"]
        self.correct_answer = question["correct_answer"]
        self.incorrect_answers = question["incorrect_answers"]
