import inspect
from typing import Any, Callable, Iterator, List, Optional
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables.utils import Output, Input
from langchain_core.runnables.config import RunnableConfig, merge_configs
from langchain_core.runnables.utils import ConfigurableFieldSpec
from langchain_core.chat_history import BaseChatMessageHistory


class CustomRunnableWithMessageHistory(RunnableWithMessageHistory):
    def __init__(self, 
                 chain,
                 get_session_history,
                 input_messages_key,
                 history_messages_key,
                 output_messages_key):

        history_factory_config = [
                ConfigurableFieldSpec(
                    id="session_id",
                    annotation=str,
                    name="Session ID",
                    description="Unique identifier for a session.",
                    default="",
                    is_shared=True,
                ),
                ConfigurableFieldSpec(
                    id="session_name",
                    annotation=str,
                    name="Session Name",
                    description="Human readable name for a session.",
                    default="",
                    is_shared=True,
                )
            ]
        super().__init__(chain, 
                         get_session_history,
                         input_messages_key=input_messages_key,
                         history_messages_key=history_messages_key,
                         output_messages_key=output_messages_key,
                         history_factory_config=history_factory_config)
    
    def run(self, input_data: dict, config: dict):
        session_id = config.get("configurable", {}).get("session_id")
        session_name = config.get("configurable", {}).get("session_name")

        # Fetch the chat history using both session_id and session_name
        chat_history = self.get_session_history(session_id, session_name)

        # Proceed with the chain using the retrieved chat history
        result = self.bound.invoke(input_data, history=chat_history.get_messages())

        return result
