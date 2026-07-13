from app.agents.nodes.tool_node import ToolNode

from app.agents.tools.order_tool import OrderTool, orders
from app.agents.tools.ticket_tool import TicketTool, tickets
from app.agents.tools.user_tool import UserTool, users


def test_tool_node():

    order_tool = OrderTool(orders)
    ticket_tool = TicketTool(tickets)
    user_tool = UserTool(users)

    tool_node = ToolNode(
        order_tool=order_tool,
        ticket_tool=ticket_tool,
        user_tool=user_tool
    )

    samples = [

        {
            "tool_name": "track_order",
            "order_id": "ORD-1005",
            "ticket_id": None,
            "user_id": None
        },

        {
            "tool_name": "cancel_order",
            "order_id": "ORD-1002",
            "ticket_id": None,
            "user_id": None
        },

        {
            "tool_name": "check_return_eligibility",
            "order_id": "ORD-1008",
            "ticket_id": None,
            "user_id": None
        },

        {
            "tool_name": "check_ticket_status",
            "order_id": None,
            "ticket_id": "T-3001",
            "user_id": None
        },

        {
            "tool_name": "get_ticket",
            "order_id": None,
            "ticket_id": "T-3001",
            "user_id": None
        },

        {
            "tool_name": "get_user",
            "order_id": None,
            "ticket_id": None,
            "user_id": "user_7"
        }
    ]

    for state in samples:

        result = tool_node.tool_node(state)

        print("=" * 60)
        print("Tool :", state["tool_name"])
        print(result)


if __name__ == "__main__":
    test_tool_node()