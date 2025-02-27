from inspect_ai import Task, task
from inspect_ai.solver import generate, prompt_template, system_message, TaskState
from inspect_ai.scorer import (
    CORRECT,
    INCORRECT,
    PARTIAL,
    NOANSWER,
    Score,
    accuracy,
    stderr,
    Scorer,
    scorer,
    Target,
)
from typing import Callable, Optional
import random
import cvc5

import re
from checker import EquivalenceChecker
from sample_samples import variable_dataset_sample

def equivalence_scorer(checker: Callable[[str, str], tuple[str, Optional[cvc5.Result]]]) -> Scorer:
    """
    Translates an optional cvc5 result into a score.
    The checker should return None only if parsing fails, and otherwise the cvc5 result.
    A result of unsatisfiable is interpreted as a correct answer, on the assumption that a check on equality is made by an attempt to prove inequality.
    And, with this a result of satisfaible is interpreted as an incorrect answer.
    Any other result (i.e. unknown) due to resource limits or insufficient heuristics is marked as partial.
    """
    async def score(state: TaskState, target: Target) -> Score:
        answer: str | None = None
        for value in target:
            answer, result = checker(state.output.completion, value)
            if result is None:
                return Score(value=NOANSWER, answer=answer, explanation=state.output.completion)
            elif cvc5.Result.isUnsat(result):
                return Score(value=CORRECT, answer=answer, explanation=state.output.completion)
            elif cvc5.Result.isSat(result):
                return Score(value=INCORRECT, answer=answer, explanation=state.output.completion)
            elif cvc5.Result.isUnknown(result):
                return Score(value=PARTIAL, answer=answer, explanation=state.output.completion)


    return score


@scorer(metrics=[accuracy(), stderr()])
def equivalence_check() -> Scorer:
    """
    Checks a response where the last line is of the form:

        ANSWER: $ANSWER

    $ANSWER is parsed as a formula and is compared to a known formula answering the question.
    Specifically, cvc5 attempts to prove the two formulas are distinct and if this fails the given formula is equivalent to the known formula.
    """

    def check(value: str, target: str) -> tuple[str, cvc5.Result]:
        for line in value.split("\n"):

            # TODO: Build a slightly more complex regex or use a markdown parser to remove markdown like this.
            if line[:2] == "**":
                line = line[2:-2]

            answer_match = re.search("ANSWER: (.*)", line)
            if answer_match:
                to_check: str = answer_match.group(1)

                checker = EquivalenceChecker()
                print(f"Checking '{to_check}' against '{target}'")
                result: Optional[cvc5.Result] = checker.check(to_check, target)
                print(f"\tResult: '{result}'")

                return [to_check, result]

        return ["NO_ANSWER", None]

    return equivalence_scorer(check)


# The template is almost identical to the gsm8k template.
# The primary difference is hints regarding a formula, and the omission of repeat instructions on the format of the answer (as testing established these were unnecessary).
MATH_FUNCTION_PROMPT_TEMPLATE = """
Please solve the following problem with a formula.
You do not need to rewrite or simplify your answer.
Write your answer as "ANSWER: $ANSWER" (without quotes) where $ANSWER is a formla which uses the same variables as found in the problem.

{prompt}
""".strip()


def simple_sample_to_fewshot(sample):
    """
    Translates a simple sample for fewshot learning by concatenating the problem with the answer.
    Note, as the samples do not contain reasoning, fewshot training likely only helps the model identify the use of variables and expected output format.
    """
    return f"{sample.input}\n\nANSWER: {sample.target}"

@task
def gsm8k_variable(fewshot=10, fewshot_seed=42):
    """
    An example task using a fragment of the gsm8k dataset adapted to use variables in place of specific values.
    The model is expected to produce a formula, and the example is evaluated by proving it is equivalent to a known answer formula.
    In cases of a failure to parse the formula, no answer is recorded, and in the (very unlikely) case of a failed proof partial credit is given.

    By default, ten samples are used for fewshot training to help align the model with the output required for parsing.
    """

    dataset = variable_dataset_sample
    random.shuffle(dataset)

    solver = [prompt_template(MATH_FUNCTION_PROMPT_TEMPLATE), generate()]
    if fewshot:
        fewshot_msg = system_message(
            "\n\n".join(
                [simple_sample_to_fewshot(sample) for sample in dataset[:fewshot]]
            )
        )

        solver.insert(0, fewshot_msg)

    # define task
    return Task(
        dataset[fewshot:],
        solver=solver,
        scorer=equivalence_check(),
    )
