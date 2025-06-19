```mermaid
flowchart TD
    __start__["__start__"]
    fix_sql_llm["fix_sql_llm"]
    get_sql_llm["get_sql_llm"]
    test_sql_llm["test_sql_llm"]
    get_data_snowflake_version["get_data_snowflake_version"]
    get_chart_suggestions["get_chart_suggestions"]
    __end__["__end__"]

    __start__ --> get_sql_llm
    fix_sql_llm --> test_sql_llm
    get_chart_suggestions --> __end__
    get_sql_llm --> test_sql_llm
    test_sql_llm -- True --> get_data_snowflake_version
    test_sql_llm -- False --> fix_sql_llm
    get_data_snowflake_version -- True --> get_chart_suggestions
    get_data_snowflake_version -- False --> __end__
```
