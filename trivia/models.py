class TriviaQuestion:
    def __init__(self, question):
        self.question = question["question"]
        correct_answer = question["correct_answer"]
        incorrect_answers = question["incorrect_answers"]
        self.answers = incorrect_answers.append(correct_answer)
