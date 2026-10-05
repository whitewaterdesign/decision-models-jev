from typesafe_sdk import Score, TypeSafeClient, Noul, Choice
from dotenv import load_dotenv

load_dotenv()
REFUND_TICKET = (
    "I was charged twice for order A-104 ($49 each). "
    "Please refund the duplicate charge."
)
REFUND_POLICY = "Duplicate charges are eligible for a full refund within 5 business days."

with TypeSafeClient() as client:
    state = {
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
      "refund_policy": "Duplicate charges are eligible for a refund.",
      "response": (
        "Sorry about that! I can see two $49 charges on order A-104. "
        "I've refunded the duplicate and it should reach your account "
        "within 5 business days."
      )
    }
    response = client.system_one(
        state=state,
        questions={
            "does_response_agree_to_refund": Noul(instructions="Does the response agree to refund the duplicate charge?"),
            "is_consistent": Noul(instructions="Is the response consistent with the refund policy?"),
            "is_duplicate": Noul(instructions="Has a duplicate charge been made on the order?"),
            "response_helpfulness": Score(
                instructions="How helpful and courteous is the response as a reply to the customer's message?",
                criteria=[
                    "Unhelpful or rude",
                    "Partially helpful",
                    "Helpful and polite",
                ],
            ),
            "which_team": Choice(
                instructions="Which team should own this ticket?",
                criteria={"billing": "Charges, invoices, payment problems", "technical": "Bugs or integration problems", "sales": "Pricing or account questions"},
            ),
        },
    )

    print(f"Does the response agree to refund the duplicate charge? {response.answers['does_response_agree_to_refund']}")
    print(f"Is the response consistent with the refund policy? {response.answers['is_consistent']}")
    print(f"Has a duplicate charge been made on the order? {response.answers['is_duplicate']}")
    print(f"How helpful and courteous is the response? {response.answers['response_helpfulness']}")
    print(f"Which team should own this ticket? {response.answers['which_team']}")


    """
    Does the response agree to refund the duplicate charge? type='noul' noul=0.99
    Is the response consistent with the refund policy? type='noul' noul=0.98
    Has a duplicate charge been made on the order? type='noul' noul=0.98
    How helpful and courteous is the response? type='score' score=2.0 confidence=1.0 legend={0: 'Unhelpful or rude', 1: 'Partially helpful', 2: 'Helpful and polite'} probabilities={0: 0.0, 1: 0.0, 2: 1.0}
    Which team should own this ticket? type='choice' choice='billing' confidence=1.0 probabilities={'billing': 1.0, 'sales': 0.0, 'technical': 0.0}
    """