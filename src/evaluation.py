from ragas import evaluate
from ragas.metrics import Faithfulness, AnswerRelevancy
from datasets import Dataset


def evaluate_rag(question, answer, contexts):

    data = {
        "question": [question],
        "answer": [answer],
        "contexts": [contexts]
    }

    dataset = Dataset.from_dict(data)

    result = evaluate(
        dataset,
        metrics=[Faithfulness(), AnswerRelevancy()]
    )

    return result