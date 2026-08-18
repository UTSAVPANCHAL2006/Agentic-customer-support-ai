import re

from app.agents.state import Agentstate
from app.common.custom_exception import CustomException
from app.common.logger import get_logger

logger = get_logger(__name__)

SUPPORT_KEYWORDS = [
    "order",
    "track",
    "tracking",
    "shipment",
    "shipping",
    "delivery",
    "deliver",
    "return",
    "refund",
    "billing",
    "payment",
    "invoice",
    "subscription",
    "ticket",
    "account",
    "login",
    "password",
    "access",
    "cancel",
    "status",
    "policy",
    "faq",
    "support",
    "help",
    "issue",
    "problem",
    "broken",
    "working",
    "late",
    "delay",
    "price",
    "cost",
    "amount",
    "hi",
    "hello",
    "hey",
    "thanks",
    "thank you",
]

INJECTION_PATTERNS = [
    r"ignore\s+(previous|all|prior)\s+instructions",
    r"you\s+are\s+now",
    r"pretend\s+(you\s+are|to\s+be)",
    r"jailbreak",
    r"dan\s+mode",
    r"system\s+prompt",
    r"forget\s+(everything|all)",
    r"act\s+as\s+(if\s+you\s+are|a)",
    r"new\s+instructions",
    r"override\s+(rules|instructions|system)",
]

# Customers often provide an ID as a follow-up after we ask for it (for example,
# "ORD-1013").  Treat that as a support message even when it has no keywords.
SUPPORT_ID_PATTERN = re.compile(r"\b(?:ORD|TRK|T)-\d+\b", re.IGNORECASE)

# These messages are handled by the classifier's `respond` action.  Blocking
# them prevents a normal conversation and makes the UI feel broken.
CONVERSATIONAL_PATTERN = re.compile(
    r"^(?:hi|hello|hey|thanks|thank you|how are you|how are u)[!?.\s]*$",
    re.IGNORECASE,
)

class GuardNode:

    def guard_node(self, state: Agentstate):
        try:
            message = state["ticket"].strip()
            normalized_message = message.lower()
            logger.info(f"GuardNode processing message: {message[:50]}...")

            if any(re.search(pattern, normalized_message) for pattern in INJECTION_PATTERNS):
                logger.info("GuardNode classification: injection")
                return {
                    "action": "blocked",
                    "response": "I'm unable to process that request.",
                }

            if (
                SUPPORT_ID_PATTERN.search(message)
                or CONVERSATIONAL_PATTERN.fullmatch(message)
                or any(keyword in normalized_message for keyword in SUPPORT_KEYWORDS)
            ):
                logger.info("GuardNode classification: support")
                return {}

            logger.info("GuardNode classification: blocked")
            return {
                "action": "blocked",
                "response": (
                    "I'm a customer support assistant. I can only help with "
                    "orders, shipments, returns, billing, tickets, or account issues. "
                    "Please ask a support-related question."
                ),
            }

        except Exception as e:
            logger.error(f"Error in GuardNode: {str(e)}")
            raise CustomException(f"GuardNode Failed", e)
