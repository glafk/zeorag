import json
from typing import Sequence

from langchain_postgres import PostgresChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict
import psycopg

class CustomChatMessageHistory(PostgresChatMessageHistory):
    @classmethod
    def create_custom_table(cls, connection, table_name):
        with connection.cursor() as cursor:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    session_id UUID NOT NULL,
                    session_name TEXT,
                    message JSONB NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            connection.commit()

    def __init__(self, 
                 table_name: str,
                 session_id: str,
                 session_name: str,
                 sync_connection: psycopg.Connection):
        self.table_name = table_name
        self.session_name = session_name
        super().__init__(table_name, str(session_id), sync_connection=sync_connection)

    def add_messages(self, messages: Sequence[BaseMessage]):
        """Add messages to the chat message history."""
        if self._connection is None:
            raise ValueError(
                "Please initialize the CustomChatMessageHistory "
                "with a sync connection or use the aadd_messages method instead."
            )

        values = [
            (self._session_id, self.session_name, json.dumps(message_to_dict(message)))
            for message in messages
        ]


        query = f"""
            INSERT INTO {self.table_name} (session_id, session_name, message)
            VALUES (%s, %s, %s)
        """

        with self._connection.cursor() as cursor:
            cursor.executemany(query, values)
        self._connection.commit()