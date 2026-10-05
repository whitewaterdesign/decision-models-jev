# System One models

Reinforcement learning from human feedback (RLHF) models such as ChatGPT and Claude are trained to say things that people
prefer [1], this works well when interacting with a chatbot, but when involved in decision making, scoring, it can
make confident-sounding hallucinations.  Reinforced learning for calibrated decisions (RLCD) instead trains the model to
return decisions and calibrated probabilities instead of generated text.  

Returns decisions and probabilities and confidence scores for it's answer, which enables more accurate decision making.

## State

This basically the input, all the information needed to make a decision.  Supporting information. The total context...but
not the question you want the model to evaluate.

Example:

```json
{
  "ticket": {
    "subject": "Duplicate charge",
    "messages": [
      {"from": "customer", "text": "I was charged twice for order A-104. Please refund the duplicate."},
      {"from": "support", "text": "We are checking the charges."}
    ]
  },
  "order": {
    "id": "A-104",
    "charges": [
      {"amount_usd": 49, "status": "captured"},
      {"amount_usd": 49, "status": "captured"}
    ]
  },
  "refund_policy": "Duplicate charges are eligible for a refund."
}
```

## Question

| Primitive type | What it answers         | Returns                                          | Examples                                           |
|----------------|-------------------------|--------------------------------------------------|----------------------------------------------------|
| Choice         | Which of these options? | `choice`, `probabilities`, `confidence`          | routing, classification                            |
| Score          | Which level?            | `score`, `legend`, `probabilities`, `confidence` | bug severity, top K (RAG), skill level             |
| Noul           | Is it true?             | `noul` (0 to 1)                                  | does contain PII? does mention distributed systems |


```python
questions = {
    "refund_requested": {
        "type": "noul",
        "instructions": "Does `ticket.messages[0].text` request a refund?",
    },
    "policy_supports_refund": {
        "type": "noul",
        "instructions": (
            "Does `refund_policy` support the refund requested "
            "in `ticket.messages[0].text`, given `order.charges`?"
        ),
    },
}
```

### Choice
You give the model a list of options and what they represent, the model will return the most likely option and the confidence score.

### Score
Rates content against ordered, descriptive levels, that are set on a spectrum.  Final score is a single value between 0 and n. 

###Noul**: A strict binary question, yes / no, will give a single number between 0 and 1 as to how confident the model is that the answer is **yes**.


## Example request flow

### State
```json
{
  "example_state": "Hi, I've been trying to connect my Stripe account for 3 days and the integration keeps failing. I'm losing sales. Please help ASAP."
}
```

### Questions
```json
{
  "department": {
    "type": "choice",
    "instructions": "Which team should handle this",
    "criteria": {
      "billing": "Payment or subscription issues",
      "technical": "Bugs or integration problems",
      "sales": "Pricing or account questions"
    }
  },
  "frustration": {
    "type": "score",
    "instructions": "How frustrated the customer appears",
    "criteria": [
      "Calm, just stating facts",
      "Frustrated but civil",
      "Very angry, strong language"
    ]
  },
  "is_urgent": {
    "type": "noul",
    "instructions": "The message conveys urgency or time-sensitivity"
  }
}

```

### Response

```json
{
  "model": "jev-1.13.0",
  "answers": {
    "department": {
      "type": "choice",
      "choice": "technical",
      "confidence": 0.76,
      "probabilities": {
        "technical": 0.84,
        "sales": 0,
        "billing": 0.16
      },
      "stats": {}
    },
    "frustration": {
      "type": "score",
      "score": 1,
      "legend": {
        "0": "Calm, just stating facts",
        "1": "Frustrated but civil",
        "2": "Very angry, strong language"
      },
      "confidence": 1,
      "probabilities": {
        "0": 0,
        "1": 1,
        "2": 0
      },
      "stats": {}
    },
    "is_urgent": {
      "type": "noul",
      "noul": 0.99,
      "stats": {}
    }
  },
  "usage": {
    "input_tokens": 432,
    "output_tokens": 73
  },
  "request_id": "playground_12ccea603c84f59438e927f55f6542c54c9",
  "evaluation_time_ms": 60.581227007787675
}
```

## Confidence

Score and Choice include multiple probabilities,

## Local models

- jaredpalmer/kev-9b (https://huggingface.co/jaredpalmer/kev-9b) 32GB Mac or 24GB GPU
- jaredpalmer/kev-4b (https://huggingface.co/jaredpalmer/kev-4b) 32GB Mac or 24GB GPU
https://github.com/jaredpalmer/kev
## Scorecard

| Entry                         | Index score | Calibration error |
|-------------------------------|------------:|------------------:|
| Jev 1.13                      |       57.91 |             0.074 |
| Surogate Rune 26B-A4B v3      |       57.44 |             0.120 |
| Decider chat with Gemma-4-31B |       57.33 |             0.047 |
| pplx-decider-v1-27b           |       56.40 |             0.018 |
| Decider 35B-A3B               |       47.11 |             0.023 |
| Bespoke Nimble 9B v2          |       39.57 |             0.024 |
| Kev-9B                        |       38.48 |             0.138 |
| Tev1-4B-experimental          |       29.24 |             0.104 |
| GLiNER2.5-Decide              |       11.21 |             0.088 |
| CLM-v0.1-8B                   |        7.40 |             0.323 |
| Laya                          |        6.04 |             0.140 |

## Possible use cases

- **Evaluation pipeline**, DeepEval allows you to use a SystemOne model to evaluate the quality of the response
- **Agentic routing**: if we have multiagent workflows, SystemOne model can choose which route to take
- **Local model**: we could host another SystemOne model locally,
- **Model routing**: decide how expensive a model to use 
- **RAG reranking**: given a list of RAG results and a question, rerank them to help LLM find the best answer
- **PII, log scanning**: could help in the previous PII experiment
- 

[[1] Machine Learning Primer, Typesafe AI, https://docs.typesafe.ai/introduction/machine-learning-primer](https://docs.typesafe.ai/introduction/machine-learning-primer])