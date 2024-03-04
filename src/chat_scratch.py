import streamlit as st
from openai import OpenAI
import streamlit.components.v1 as components
from streamlit_pills import pills
import ast
import prompts

def connect_to_snowflake():
    conn = st.connection("snowflake")
    results = conn.query("SELECT * from EO_DATA.PUBLIC.EO_DATA_VIEW")
    st.dataframe(results)

def main():
    st.set_page_config(page_title="Chat with TEx", page_icon="🤠")
   
    st.title("Chat with Scratch 🤠")
    st.markdown("##### Your friendly neighborhood itcher")

    client = OpenAI(api_key=st.secrets.OPENAI_API_KEY)
   
   # Initialize the chat messages history with system prompt
    if "messages" not in st.session_state:
        # system prompt includes table information, rules, and prompts the LLM to produce
        # a welcome message to the user.
        st.session_state.messages = [{"role": "system", "content": prompts.GEN_SQL}]
        # st.session_state.messages = [{"role": "system", "content": "👋 Welcome to the chat! Ask me anything."}]


    # Prompt for user input and save to session messages
    if prompt := st.chat_input():        
        st.session_state.messages.append({"role": "user", "content": prompt})


    # If last message is from user, get OpenAI response
    if st.session_state.messages[-1]["role"] == "user":       
        
        response = ""
        for delta in client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        ):
            response += (delta.choices[0].delta.content or "")

        st.session_state.messages.append({"role": "system", "content": response})


    # display all prior messages in session state
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        if role == "system":
            with st.chat_message("assistant"):
                st.write(content)
        elif role == "user":
            with st.chat_message("user"):
                st.write(content)


    # Create list of suggested questions as pills and add to session messages
    optionList = client.chat.completions.create(
            model="gpt-3.5-turbo",
            # messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            messages=[{"role": "user", "content": f"Create a SINGLE python list of 3 suggested questions about the snowflake database table {prompts.table_context}. Do NOT number the questions, do not include a new line character: ['Question 1', 'Question 2', 'Question 3']"}],
            stream=False)
    # st.write(optionList)

    options = ast.literal_eval(optionList.choices[0].message.content)
    # st.write(options)
    st.session_state.messages.append({"role": "user", "content": pills("Suggestions", options,)})

    # st.write(prompts.GEN_SQL)
    # connect_to_snowflake()


if __name__ == "__main__":
    main()