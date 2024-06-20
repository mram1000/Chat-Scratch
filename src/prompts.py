import streamlit as st
from streamlit_pills import pills

SCHEMA_PATH = st.secrets.get("SCHEMA_PATH", "EO_DATA.PUBLIC")
QUALIFIED_TABLE_NAME = f"{SCHEMA_PATH}.EO_DATA_VIEW"
TABLE_DESCRIPTION = """
This table has various metrics for excess inventory broken out by ODM, BU (Business Unit), and the INTEL_MONTH_YR.
"""
# This query is optional if running Frosty on your own table, especially a wide table.
# Since this is a deep table, it's useful to tell Frosty what variables are available.
# Similarly, if you have a table with semi-structured data (like JSON), it could be used to provide hints on available keys.
# If altering, you may also need to modify the formatting logic in get_table_context() below.
# METADATA_QUERY = f"SELECT VARIABLE_NAME, DEFINITION FROM {SCHEMA_PATH}.EO_DATA_VIEW;"
COLUMNS = """
ODM_NAME, BU_NAME, INTEL_MONTH_YR,  CALC_EXCESS_FULL_HOR_DOLLARS, BOH_DOLLARS, OPO_DOLLARS, TOTAL_DEMAND_FULL_HOR_DOLLARS, ODM_RPTD_EXCESS_DOLLARS,INV_BOH_PLUS_PO_FULL_HOR_DOLLARS, IOI_DOLLARS, CALC_BOH_EXCESS_DOLLARS, CALC_OPO_EXCESS_DOLLARS, CURRENT_LIABILITY_DOLLARS, TOTAL_EXPOSURE_DOLLARS, DEMAND_CONTRACT_HOR_DOLLARS, CUSTOM_BOH_DOLLARS, CUSTOM_OPO_DOLLARS, CUSTOM_OPO_NCNR_DOLLARS, CUSTOM_DEMAND_CONTR_HOR_DOLLARS , DEMAND_CONTRACT_HOR_DAYS, OPO_NCNR_DOLLARS, IOI_QTY, BOH_AGING_LT_90_QTY, BOH_AGING_BETWEEN_90_180_QTY , BOH_AGING_BETWEEN_180_270_QTY, BOH_AGING_GT_270_QTY, SUBCON_ID
"""

table_context = f"""
Here is the table name: {QUALIFIED_TABLE_NAME}.
These are the available columns: {COLUMNS} .
"""

GEN_SQL = """
You will be acting as an AI Turnkey Excess Inventory reporting helper. Your goal is to give correct, executable SQL queries to users.
You do not need to provide the actual answer - only the SQL query. The user will ask questions, for each question you should respond and include a SQL query based on the question.

{context}
Create an sql query based on the user's question based on the table name and columns above.

Here are critical rules for the interaction you must abide:
<rules>
1. You MUST MUST wrap the generated sql code within ``` sql code markdown in this format e.g
```sql
(select 1) union (select 2)
```
2. Always generate a sql query in response to the user's question.
3. You should only use the table columns given in <columns>, and the table given in <tableName>, you MUST NOT hallucinate about the table or column names
</rules>

Now to get started, please briefly introduce yourself, describe the table at a high level


"""




@st.cache_data(show_spinner="Loading Tex's context...")
def get_table_context(table_name: str, table_description: str, metadata_query: str = None):
    table = table_name.split(".")
    conn = st.connection("snowflake")
    columns = conn.query(f"""
        SELECT COLUMN_NAME, DATA_TYPE FROM {table[0].upper()}.INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{table[1].upper()}' AND TABLE_NAME = '{table[2].upper()}'
        """, show_spinner=False,
    )
    columns = "\n".join(
        [
            f"- **{columns['COLUMN_NAME'][i]}**: {columns['DATA_TYPE'][i]}"
            for i in range(len(columns["COLUMN_NAME"]))
        ]
    )
    context = f"""
Here is the table name <tableName> {'.'.join(table)} </tableName>

<tableDescription>{table_description}</tableDescription>

Here are the columns of the {'.'.join(table)}

<columns>\n\n{columns}\n\n</columns>
    """
    if metadata_query:
        metadata = conn.query(metadata_query, show_spinner=False)
        metadata = "\n".join(
            [
                f"- **{metadata['VARIABLE_NAME'][i]}**: {metadata['DEFINITION'][i]}"
                for i in range(len(metadata["VARIABLE_NAME"]))
            ]
        )
        context = context + f"\n\nAvailable variables by VARIABLE_NAME:\n\n{metadata}"
    return context

def get_system_prompt():
    table_context = get_table_context(
        table_name=QUALIFIED_TABLE_NAME,
        table_description=TABLE_DESCRIPTION
        #metadata_query=METADATA_QUERY
    )      

    return GEN_SQL.format(context=table_context)

# do `streamlit run prompts.py` to view the initial system prompt in a Streamlit app
if __name__ == "__main__":
    st.header("System prompt for TEx")
    st.markdown(get_system_prompt())