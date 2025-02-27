# Prototype evaluations of abstract reasoning

Custom evaluation methods for [Inspect AI](https://inspect.ai-safety-institute.org.uk) API using [cvc5](http://cvc5.github.io) and a custom parser to evalute whether a LLM correctly identifies some formula which solves a math problem.

Included are 20 samples, derived from the [GSM8K](https://github.com/openai/grade-school-math) dataset by replacing specific values with variables.

For example, a prompt may read:

```text
Richard lives in an apartment building with FLOOR floors. Each floor contains UNIT units, and 3/4 of the building is occupied. What's the total number of unoccupied units In the building?
```

The given (slightly long-winded) target is `(FLOOR * UNIT) - ((3 * FLOOR * UNIT) / 4)` and responses such as `(FLOOR × UNIT) / 4` are marked as correct/

## Evaluation overview

Responses are evaluated as follows:

- Correct, if the LLM identifies any formula equivalent to a target answer.
- Incorrect, if the LLM identifies any formula which is not equivalent to a target answer.
- Partial, if equivalence cannot be determined either way within some resource limit.
- No Answer, otherwise.

The evaluations rely on the base level competency of the LLM to:

- Write an answer on the final line of the output with the prefix `ANSWER:`
- Use the same variables as in the problem statement.

The parser is written with [tree-sitter](https://tree-sitter.github.io/tree-sitter/) and contains some limitations, though is reasonably robust.
For example, division and integer division are supported, and the answer may written in natural langauge or though TeX markup.[^1]

[^1]: Though, of note is that the current release of tree-sitter fails to correctly determine precedence within dollar signs.

## Informal overview

The GSM8K dataset contains

``` text
James decides to run 3 sprints 3 times a week.  He runs 60 meters each sprint.  How many total meters does he run a week?
```

Answers contain some reasoning, and the expected solution.

``` text
He sprints 3*3=9 times
So he runs 9*60=540 meters

540
```

Specific answers are useful, but most samples in the GSM8K dataset amount:

1. Identifying an abstract formula.
2. Selecting the appropriate values to instantiate in that formula
3. Calculating the result.

In the above example, a formula is:

``` text
SPRINTS_EACH_TIME * TIMES_PER_WEEK * METERS_PER_SPRINT
```

Alternative formulas may permute the order, or change things up.
Another formula, with some redundancy, is:

``` text
((METERS_PER_SPRINT / SPRINTS_EACH_TIME) * TIMES_PER_WEEK) * SPRINTS_EACH_TIME
```

Evaluating whether a LLM is able to identify an appropriate formula is of interest for a few reasons.
To give two examples:

- If the model correctly identifies a formula it is likely the formula is (or could have) been used in a specific instance of reasoning and so can provide confidence in specific answers.
- If the model correctly identifies a formula, calculating instances of the formula can be passed to some other more efficient process, and freeing the LLM for other tasks.

Still, evaluating formulas presents a slight challenge.

The example reasoning used something close to the first formula, though could have used the second.
And, generally speaking, as the formulas are equivalent there's no reason to prefer one over the other.

So, a simple comparison of the formula identified to a target formula is unlikely to provide a suitable evaluation.

The same issue is present in specific examples.
For example, 540 answers the example question, as does (1080 / 2), as does 6 * 9 * 10.
Still, there is a strong expectation to present specific numerical answers in their simplified form (as a single number).
A similar expectation of simplicity exists for formulas -- these shouldn't contain clear redundancy, as in the second example --- but the expectation itself is far more complex and may shift from person to person.
Pedantic though it may be, grouping the variables to clarify their connection is more simple, if some sense of the word:

``` text
METERS_PER_SPRINT * SPRINTS_EACH_TIME * TIMES_PER_WEEK
```

Regardless, this is only a slight challenge.

Equality of formulas such as the above with a target is mostly trivial for SMT solvers such as z3 or cvc5.
All that's required is to encode both the formula and the target as an inequality, and if the solver manages to find instances for the variables such that the inequality holds, the formulas are not equal.
For example, with a little reasoning it is clear that all the formula mentioned so far are equivalent, just as it's clear that by settting `METERS_PER_SPRINT = 50`, `SPRINTS_EACH_TIME = 3`, and `TIMES_PER_WEEK = 3`, the following does not hold:

``` text
(METERS_PER_SPRINT * SPRINTS_EACH_TIME * TIMES_PER_WEEK) != ((10 * SPRINTS_EACH_TIME + 10 * TIMES_PER_WEEK) * SPRINTS_EACH_TIME * TIMES_PER_WEEK)
```

These evaluations check the answer of a LLM against some known formula using cvc5.

## Examples

The default prompt reads:

``` text
Please solve the following problem with a formula.
You do not need to rewrite or simplify your answer.
Write your answer as \"ANSWER: $ANSWER\" (without quotes) where $ANSWER is a formla which uses the same variables as found in the problem.
```


Examples are taken from a local instance of [DeepSeek-R1-Distill-Llama-8B-F16](https://huggingface.co/bartowski/DeepSeek-R1-Distill-Llama-8B-GGUF), with:

- A token limit of 6,144.
- Temperature of 0.7
- Fewshot training on ten examples.

### A Correct Response

Problem statement:

``` text
Eliza's rate per hour for the first TIME hours she works each week is $RATE. She also receives an overtime pay of 1.2 times her regular hourly rate. If Eliza worked for OVERTIME > TIME hours this week, how much are her earnings for this week?
```

Target:

``` text
(TIME * RATE) + (1.2 * RATE * (OVERTIME - TIME))
```

Response (in full):

``` text
<think>
Okay, let me try to figure out Eliza's earnings for the week. So, from what I understand, she works for a certain number of hours each week, called TIME. Her regular hourly rate is RATE per hour. But if she works more than TIME hours, which they call OVERTIME, she gets overtime pay at 1.2 times her regular rate.

First, let's break down the earnings into two parts: the regular hours and the overtime hours.

The regular hours are when she works up to TIME hours each week. So, for these TIME hours, she earns RATE per hour. That part would be RATE multiplied by TIME.

Then there's the overtime. Overtime is any time she works beyond TIME, which is OVERTIME minus TIME hours. For that extra time, instead of her regular rate, she gets 1.2 times RATE as overtime pay. So, that would be 1.2 * RATE multiplied by (OVERTIME - TIME).

To find the total earnings, I think I need to add both parts together. So, that's (RATE * TIME) + (1.2 * RATE * (OVERTIME - TIME)).

Hmm, let me write this out as a formula:

Total Earnings = Regular Pay + Overtime Pay
= RATE × TIME + 1.2 × RATE × (OVERTIME − TIME)

I should make sure I'm not mixing up the variables here. The problem says she works for OVERTIME hours, which is more than TIME. So, yes, overtime is only for the extra hours beyond TIME.

Let me double-check if this makes sense. Suppose TIME is 40 hours a week and she worked 45 hours (so OVERTIME = 45). Her regular pay would be RATE * 40, and overtime would be 1.2 * RATE * (5), since she worked 5 extra hours. That seems right.

So, the formula should correctly represent her total earnings from both regular and overtime pay.
</think>

To determine Eliza's total weekly earnings, we consider both her regular hours worked and her overtime hours. Her regular pay is calculated at her standard hourly rate, while her overtime pay is 1.2 times that rate for any hours exceeding the designated TIME.

**Formula:**
Total Earnings = Regular Pay + Overtime Pay
= RATE × TIME + 1.2 × RATE × (OVERTIME − TIME)

ANSWER: RATE * TIME + 1.2 * RATE * (OVERTIME - TIME)
```

There are (at least) three things of note.

- The LLM does not reason about the standard semantic content of TIME and OVERTIME and correctly identifies OVERTIME refers to the total time worked by Eliza.
- The LLM considers instantiating the TIME and OVERTIME variables to verify their reasoning.
- The LLM seems to be matching the setup against the broader formula of `Total Earnings = Regular Pay + Overtime Pay`.

### An Incorrect Response

Problem statement:

``` text
A new program had DOWNLOADS downloads in the first month. The number of downloads in the second month was SECOND times as many as the downloads in the first month, but then reduced by 30% in the third month. How many downloads did the program have total over the three months?
```

Target:

``` text
((SIZE / SPEED) * 1.4) + TIME
```

Response (in full):

``` text
<think>
Okay, let's try to figure out how long it takes Carla to download the file. So, she starts downloading a SIZE GB file at a speed of SPEED GB per minute. That sounds straightforward. Normally, without any interruptions, the time should just be SIZE divided by SPEED, right? But then, something happens.

Forty percent of the way through the download, which means she's downloaded 0.4 * SIZE GB, Windows forces a restart. This interruption takes TIME minutes. So, during those TIME minutes, she can't download anything else; the download has to pause. After that, she has to restart the download from the beginning.

So, first part: She downloads 40% of the file before the interruption. Let me calculate how long that takes. If her speed is SPEED GB per minute, then time taken for 0.4 * SIZE would be (0.4 * SIZE) / SPEED minutes.

Then, she spends TIME minutes restarting and installing updates.

After that, she has to start over from 0% again. So, the remaining 60% of the file needs to be downloaded at her usual speed. Time for that part would be (0.6 * SIZE) / SPEED minutes.

So, adding all these up: time for first part + TIME minutes + time for second part.

Let me write this out step by step:

1. First download segment: 40% of the file.
- Time = (0.4 * SIZE) / SPEED

2. Restart and update time:
- Time = TIME minutes

3. Second download segment: 60% of the file.
- Time = (0.6 * SIZE) / SPEED

Total time = (0.4 * SIZE)/SPEED + TIME + (0.6 * SIZE)/SPEED

I can combine the first and third terms because they both have SIZE/SPEED.

So, 0.4*SIZE/SPEED + 0.6*SIZE/SPEED = (1.0 * SIZE)/SPEED

Therefore, total time is (SIZE / SPEED) + TIME minutes.

Wait, does that make sense? Let me double-check. Normally, without interruption, it's SIZE/SPEED. But with the interruption, she loses 40% and has to download again from scratch. So, effectively, she ends up doing two full downloads: first 40%, then another 100%. Without the interruption, it would have been just one download.

So yes, that means her total time is (SIZE/SPEED)*1 + TIME.

Alternatively, maybe I can think of it as two separate downloads. The first download gets her to 40%, which takes (0.4*SIZE)/SPEED minutes. Then she stops and restarts after TIME minutes. Then she starts again from 0% and downloads the remaining 60%, which is another (0.6*SIZE)/SPEED.

Adding these together, as I did before, gives SIZE/SPEED + TIME. So that seems correct.

I don't think there's any overlap or anything else to consider here because once Windows restarts, she has to start from zero again. There's no partial download that can be continued; it's a complete interruption.

So yeah, the total time is (SIZE divided by SPEED) plus TIME minutes.
</think>


Carla initially downloads 40% of the file before the interruption, then spends TIME minutes waiting, and finally restarts to download the remaining 60%. The total download time is the sum of these three parts.

ANSWER: ((0.4 * SIZE) / SPEED) + TIME + ((0.6 * SIZE) / SPEED)

Which simplifies to:

SIZE/SPEED + TIME

But since the question says \"how long does it take,\" and the answer should be expressed in terms of the variables given, I'll keep it as:

((0.4 * SIZE) / SPEED) + TIME + ((0.6 * SIZE) / SPEED)

Or written as:

(SIZE/SPEED) + TIME

But to match the original breakdown, let's write it with the 40% and 60%.

So the formula is:

( (0.4 * SIZE)/SPEED ) + TIME + ( (0.6 * SIZE)/SPEED )

Combine the two terms with SIZE/SPEED:

( (1.0 * SIZE)/SPEED ) + TIME

Which can be written as:

(SIZE / SPEED) + TIME

But in case they want it broken down, I'll present both versions.

ANSWER: ((0.4 * SIZE) / SPEED) + TIME + ((0.6 * SIZE) / SPEED)

Alternatively:

ANSWER: (SIZE / SPEED) + TIME
```

The target answer is `((SIZE / SPEED) * 1.4) + TIME`, and the mistake in reasoning happens early when the LLM writes '… she has to start over from 0% again. So, the remaining 60% of the file needs to be downloaded'.
