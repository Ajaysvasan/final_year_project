import sqlite3
from typing import List

import numpy as np
from snapShotNodes import SnapShotNode

from config import Config


class ConversationVectorManager:
    def __init__(self) -> None:
        self.conn = sqlite3.connect(Config.CONVERSATION_SNAPSHOT_DB)
        self.cursor = self.conn.cursor()

        self.conn.execute("PRAGMA foreign_keys = ON")
        self.__create_snapshot_table()
        self.__create_vector_ids_table()
        self.__create_cummulative_summary_vector_id_table()

    def __create_snapshot_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_snapshots (
                snapshot_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                topic_id TEXT NOT NULL,
                conversation_id TEXT NOT NULL,
                timestamp DATETIME,
                size_of_the_summary INTEGER NOT NULL,
                len_of_the_summary INTEGER NOT NULL,
                cummulative_summary_vector_id INTEGER NOT NULL
                FOREIGN KEY (snapshot_id) REFERENCES cummulative_summary_vector_ids(snapshot_id)
            )
            """)
        self.conn.commit()

    def __create_cummulative_summary_vector_id_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS cummulative_summary_vector_ids (
            snapshot_id TEXT PRIMARY KEY,
            cummulative_summary_vector_id INTEGER NOT NULL,
            FOREIGN KEY (snapshot_id) REFERENCES conversation_snapshots(snapshot_id)
            file_offset INTEGER NOT NULL
        )
        """)
        self.conn.commit()

    def __insert_cummulative_summary_vector_id(
        self, snapshot: SnapShotNode, file_offset: int
    ):
        self.cursor.execute(
            """
            INSERT INTO cummulative_summary_vector_ids (snapshot_id, cummulative_summary_vector_id, file_offset) VALUES (?, ?, ?)
            """,
            (snapshot.snapshot_id, snapshot.cummulative_summary_vector_id, file_offset),
        )
        self.conn.commit()

    def __select_cummulative_summary_vector_id(self, snapshot_id: str):
        self.cursor.execute(
            """
            SELECT cummulative_summary_vector_id FROM cummulative_summary_vector_ids WHERE snapshot_id = ?
            """,
            (snapshot_id,),
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def __select_file_offset(self, snapshot_id: str):
        self.cursor.execute(
            """
            SELECT file_offset FROM cummulative_summary_vector_ids WHERE snapshot_id = ?
            """,
            (snapshot_id,),
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def __create_vector_ids_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS snapshot_vector_ids (
            snapshot_id TEXT NOT NULL,
            vector_ids TEXT NOT NULL,
            FOREIGN KEY (snapshot_id) REFERENCES conversation_snapshots(snapshot_id)
        )
        """)
        self.conn.commit()

    def __insert_snapshot_metadata(
        self, snapshot_node: SnapShotNode, topic_id: str, project_id: str
    ):
        self.cursor.execute(
            """
            INSERT INTO conversation_snapshots (
                project_id, topic_id, conversation_id, timestamp,
                size_of_the_summary, len_of_the_summary, cummulative_summary_vector_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot_node.snapshot_id,
                project_id,
                topic_id,
                snapshot_node.conversation_id,
                snapshot_node.time_of_snap_shot,
                snapshot_node.size_of_the_summary,
                snapshot_node.len_of_the_summary,
                snapshot_node.cummulative_summary_vector_id,
            ),
        )
        self.conn.commit()

    def __select_snapshot_metadata(self, conversation_id: str):
        self.cursor.execute(
            """
            SELECT * FROM conversation_snapshots WHERE conversation_id = ?
            """,
            (conversation_id,),
        )
        return self.cursor.fetchall()

    def __insert_vector_ids(self, snapshot_id: str, vector_ids: List[np.uint32]):
        ids = ""
        for id in vector_ids:
            ids += str(id) + " "

        ids = ids.strip()
        self.cursor.execute(
            """INSERT INTO "snapshot_vector_ids (snapshot_id , vector_ids) VALUES(? , ?); """,
            (snapshot_id, ids),
        )

        self.conn.commit()

    def __select_vector_ids(self, snapshot_id: str) -> List[np.uint32]:
        self.cursor.execute(
            """
            SELECT vector_id FROM snapshot_vector_ids WHERE snapshot_id = ?
            """,
            (snapshot_id,),
        )

        return [np.uint32(row[0]) for row in self.cursor.fetchall()]

    def insert_cummulative_summary_vector_id(
        self, snapshot: SnapShotNode, file_offset: int
    ):
        self.__insert_cummulative_summary_vector_id(snapshot, file_offset)

    def insert_vector_ids(self, snapshot_id: str, vector_ids: List[np.uint32]):
        self.__insert_vector_ids(snapshot_id, vector_ids)

    def load_snap_shot_objects(self, conversation_id: str) -> List[SnapShotNode]:
        # return me all the snapshots for that id as list
        # then using that construct the snapshot objects and return me the list
        snapshots_meta_data = self.__select_snapshot_metadata(conversation_id)
        snapshots: List[SnapShotNode] = []
        for snapshot in snapshots_meta_data:
            snapshot_node = SnapShotNode(
                snapshot_id=snapshot[0],
                time_of_snap_shot=snapshot[4],
                size_of_the_summary=snapshot[5],
                len_of_the_summary=snapshot[6],
                summary_vector_ids=self.__select_vector_ids(snapshot[0]),
                conversation_id=snapshot[3],
                cummulative_summary_vector_id=snapshot[7],
            )
            snapshots.append(snapshot_node)
        return snapshots

    def insert_snapshot(
        self, snapshot_node: SnapShotNode, topic_id: str, project_id: str
    ):
        self.__insert_snapshot_metadata(snapshot_node, topic_id, project_id)

    def get_snapshot_metadata(self, conversation_id: str):
        return self.__select_snapshot_metadata(conversation_id)

    def get_cummulative_summary_vector_id(self, conversation_id: str):
        snapshot_metadata = self.__select_snapshot_metadata(conversation_id)
        if snapshot_metadata:
            return snapshot_metadata[0][7]  # Return the cummulative_summary_vector_id

    def get_file_offset(self, snapshot_id: str):
        return self.__select_file_offset(snapshot_id)

    def close(self):
        self.conn.close()
