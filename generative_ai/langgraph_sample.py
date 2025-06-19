from langgraph.graph import StateGraph, END
from typing import TypedDict
import matplotlib.pyplot as plt

# Create Analysis Pipeline
def create_analysis_pipeline(ai_connection: object, db_connection: object, view_information: str):
    graph = StateGraph(State)
        
    graph.add_node("fix_sql_llm", fix_sql_llm_graph)
    graph.add_node("get_sql_llm", get_sql_llm_graph)
    graph.add_node("test_sql_llm", test_sql_llm_graph)
    graph.add_node("check_data_ready", check_data_ready)
    graph.add_node("get_data_snowflake_version", get_data_graph)
    graph.add_node("get_chart_suggestions", get_chart_suggestions_graph)
    
    graph.add_edge("get_sql_llm", "test_sql_llm")
    graph.add_edge("fix_sql_llm", "test_sql_llm")
    graph.add_edge("get_chart_suggestions", END)
    
    graph.add_conditional_edges(
        "test_sql_llm",
        should_end,
        {
            True: "get_data_snowflake_version",
            False: "fix_sql_llm"
        }
    )
    
    graph.add_conditional_edges(
        "get_data_snowflake_version",
        test_is_chart_ready,
        {
            True: "get_chart_suggestions",
            False: END
        }
    )
    
    graph.set_entry_point("get_sql_llm")
    
    return graph.compile()
