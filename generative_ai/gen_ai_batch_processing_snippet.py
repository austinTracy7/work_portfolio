from snowflake.snowpark.functions import sql_expr

# Batch processing Generative AI with Snowflake Cortex
enriched_df = more_testing_df.with_column(
    "ENRICHMENT",
    sql_expr("""parse_and_validate_llm_response(SNOWFLAKE.CORTEX.COMPLETE(
    'claude-3-5-sonnet',
    [{
    'role': 'user',
    'content': 'Using the contextual information provided return just enrichment or cleaned/corrected data for the flagged columns (under fixes in the input with false values). Leave everything else alone unless it is flagged with null and needs to be changed for coherence. 
      Input Data Record: ' || OBJECT_CONSTRUCT(*)::VARCHAR || '
    ...""")
    )
