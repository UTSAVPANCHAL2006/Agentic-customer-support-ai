from app.agents.graph import AgentGraph

from app.rag.retriever import Retriever
from app.rag.generate import Generator
from app.rag.llm import LLM

from app.agents.tools.order_tool import OrderTool
from app.agents.tools.ticket_tool import TicketTool
from app.agents.tools.user_tool import UserTool

from app.agents import Classifier   # <-- apne project ke hisab se import change karna


def main():

    # LLM
    llm = LLM()

    # Components
    retriever = Retriever()
    generator = Generator(llm)
    classify = Classifier(llm)

    # Tools
    order_tool = OrderTool()
    ticket_tool = TicketTool()
    user_tool = UserTool()

    # Graph
    agent = AgentGraph(
        retriever=retriever,
        generator=generator,
        classify=classify,
        llm=llm,
        order_tool=order_tool,
        ticket_tool=ticket_tool,
        user_tool=user_tool,
    )

    test_queries = [

        # ---------- RAG ----------
        "What is your refund policy?",

        # ---------- Tool ----------
        "Track my order ORD-1005",

        "Cancel my order ORD-1005",

        "Check return eligibility for order ORD-1005",

        "Check ticket TICK-100",

        "Get user USER-10",

        # ---------- Clarify ----------
        "Track my order",

        # ---------- Escalate ----------
        "I want to file a legal complaint."
    ]

    for query in test_queries:

        print("\n" + "=" * 70)
        print("QUERY")
        print(query)

        result = agent.run(query)

        print("\nFINAL STATE")
        print(result)

        print("\nFINAL RESPONSE")
        print(result["response"])

        print("=" * 70)


if __name__ == "__main__":
    main()