import os
import sqlite3
from typing import List, Optional, Union

import numpy as np

try:
    from .snapShotNodes import SnapShotNode
except ImportError:
    from snapShotNodes import SnapShotNode

from config import Config, get_logger

logger = get_logger(__name__)


class ConversationVectorMetaDataManager:
    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = db_path or Config.CONVERSATION_SNAPSHOT_DB
        # Ensure the parent directory of the database exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        logger.info(f"Initializing ConversationVectorMetaDataManager with DB: '{self.db_path}'")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.__create_snapshot_table()
        self.__create_vector_ids_table()
        self.__create_cumulative_summary_offset_table()
        logger.debug("ConversationVectorMetaDataManager SQLite schema verified.")

    def __create_snapshot_table(self) -> None:
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_snapshots (
                row_id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id TEXT UNIQUE NOT NULL,
                project_id TEXT NOT NULL,
                topic_id TEXT NOT NULL,
                conversation_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                
                size_of_the_summary INTEGER NOT NULL,
                len_of_the_summary INTEGER NOT NULL,
                cumulative_summary_vector_id INTEGER NOT NULL
            )
            """)
        self.conn.commit()

    def __create_vector_ids_table(self) -> None:
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshot_vector_ids (
                snapshot_id TEXT NOT NULL,
                vector_id INTEGER NOT NULL,
                vector_position INTEGER NOT NULL,
                PRIMARY KEY (snapshot_id, vector_position),
                FOREIGN KEY (snapshot_id) REFERENCES conversation_snapshots(snapshot_id) ON DELETE CASCADE
            )
            """)
        self.conn.commit()

    def __create_cumulative_summary_offset_table(self) -> None:
        # Renamed table and removed duplicate cumulative_summary_vector_id column
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cumulative_summary_offsets (
                snapshot_id TEXT PRIMARY KEY,
                file_offset INTEGER NOT NULL,
                FOREIGN KEY (snapshot_id) REFERENCES conversation_snapshots(snapshot_id) ON DELETE CASCADE
            )
            """)
        self.conn.commit()

    def __insert_snapshot_metadata(
        self, snapshot_node: SnapShotNode, topic_id: str, project_id: str
    ) -> str:
        # Use plain INSERT to fail loudly on uniqueness conflict and avoid ON DELETE CASCADE side-effects
        self.cursor.execute(
            """
            INSERT INTO conversation_snapshots (
                snapshot_id, project_id, topic_id, conversation_id, timestamp,
                size_of_the_summary, len_of_the_summary, cumulative_summary_vector_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot_node.snapshot_id,
                project_id,
                topic_id,
                snapshot_node.conversation_id,
                snapshot_node.time_of_snap_shot,
                int(snapshot_node.size_of_the_summary),
                int(snapshot_node.len_of_the_summary),
                int(snapshot_node.cumulative_summary_vector_id),
            ),
        )
        self.conn.commit()

        # Automatically insert vector IDs if they exist in the node
        if snapshot_node.summary_vector_ids:
            self.__insert_vector_ids(
                snapshot_node.snapshot_id, snapshot_node.summary_vector_ids
            )

        return snapshot_node.snapshot_id

    def __select_snapshot_metadata(self, conversation_id: str) -> List[tuple]:
        # Ordered deterministically by row_id (insertion order)
        self.cursor.execute(
            """
            SELECT snapshot_id, project_id, topic_id, conversation_id, timestamp,
                   size_of_the_summary, len_of_the_summary, cumulative_summary_vector_id
            FROM conversation_snapshots
            WHERE conversation_id = ?
            ORDER BY row_id ASC
            """,
            (conversation_id,),
        )
        return self.cursor.fetchall()

    def __insert_vector_ids(
        self, snapshot_id: str, vector_ids: List[np.uint32]
    ) -> None:
        # Delete existing vector IDs first to support clean replacement/updates
        self.cursor.execute(
            "DELETE FROM snapshot_vector_ids WHERE snapshot_id = ?", (snapshot_id,)
        )
        # Store vector_position explicitly to preserve ordering
        self.cursor.executemany(
            """
            INSERT INTO snapshot_vector_ids (snapshot_id, vector_id, vector_position)
            VALUES (?, ?, ?)
            """,
            [(snapshot_id, int(vid), pos) for pos, vid in enumerate(vector_ids)],
        )
        self.conn.commit()

    def __select_vector_ids(self, snapshot_id: str) -> List[np.uint32]:
        # Ordered explicitly by position to preserve conversational context order
        self.cursor.execute(
            """
            SELECT vector_id FROM snapshot_vector_ids WHERE snapshot_id = ? ORDER BY vector_position ASC
            """,
            (snapshot_id,),
        )
        return [np.uint32(row[0]) for row in self.cursor.fetchall()]

    def __insert_cumulative_summary_offset(
        self, snapshot_id: str, file_offset: int
    ) -> None:
        self.cursor.execute(
            """
            INSERT OR REPLACE INTO cumulative_summary_offsets (snapshot_id, file_offset)
            VALUES (?, ?)
            """,
            (snapshot_id, int(file_offset)),
        )
        self.conn.commit()

    def __select_cumulative_summary_vector_id(self, snapshot_id: str) -> Optional[int]:
        self.cursor.execute(
            """
            SELECT cumulative_summary_vector_id FROM conversation_snapshots WHERE snapshot_id = ?
            """,
            (snapshot_id,),
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def __select_file_offset(self, snapshot_id: str) -> Optional[int]:
        self.cursor.execute(
            """
            SELECT file_offset FROM cumulative_summary_offsets WHERE snapshot_id = ?
            """,
            (snapshot_id,),
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    # --- Public API Methods ---

    def insert_snapshot(
        self, snapshot_node: SnapShotNode, topic_id: str, project_id: str
    ) -> str:
        """
        Inserts a SnapShotNode and its vector IDs into the database.
        Returns the snapshot_id from the SnapShotNode.
        """
        logger.info(f"Inserting snapshot metadata: snapshot_id='{snapshot_node.snapshot_id}', conversation_id='{snapshot_node.conversation_id}'")
        return self.__insert_snapshot_metadata(snapshot_node, topic_id, project_id)

    def load_snap_shot_objects(self, conversation_id: str) -> List[SnapShotNode]:
        """
        Retrieves all SnapShotNode objects for a given conversation.
        Uses a LEFT JOIN query to load all metadata and vector IDs in a single query (resolving N+1 pattern).
        """
        self.cursor.execute(
            """
            SELECT s.snapshot_id, s.project_id, s.topic_id, s.conversation_id, s.timestamp,
                   s.size_of_the_summary, s.len_of_the_summary, s.cumulative_summary_vector_id,
                   v.vector_id
            FROM conversation_snapshots s
            LEFT JOIN snapshot_vector_ids v ON s.snapshot_id = v.snapshot_id
            WHERE s.conversation_id = ?
            ORDER BY s.row_id ASC, v.vector_position ASC
            """,
            (conversation_id,),
        )
        rows = self.cursor.fetchall()

        snapshots_map = {}
        for row in rows:
            (
                snapshot_id,
                project_id,
                topic_id,
                conversation_id,
                timestamp,
                size_of_the_summary,
                len_of_the_summary,
                cumulative_summary_vector_id,
                vector_id,
            ) = row

            if snapshot_id not in snapshots_map:
                snapshots_map[snapshot_id] = {
                    "timestamp": timestamp,
                    "size_of_the_summary": size_of_the_summary,
                    "len_of_the_summary": len_of_the_summary,
                    "conversation_id": conversation_id,
                    "cumulative_summary_vector_id": cumulative_summary_vector_id,
                    "summary_vector_ids": [],
                }
            if vector_id is not None:
                snapshots_map[snapshot_id]["summary_vector_ids"].append(
                    np.uint32(vector_id)
                )

        snapshots: List[SnapShotNode] = []
        for snap_id, data in snapshots_map.items():
            snapshot_node = SnapShotNode(
                snap_id,
                data["timestamp"],
                data["size_of_the_summary"],
                data["len_of_the_summary"],
                data["summary_vector_ids"],
                data["conversation_id"],
                np.uint32(data["cumulative_summary_vector_id"]),
            )
            snapshots.append(snapshot_node)

        return snapshots

    def get_snapshot_metadata(self, conversation_id: str) -> List[tuple]:
        """
        Retrieves raw snapshot metadata records from the database.
        """
        return self.__select_snapshot_metadata(conversation_id)

    def insert_vector_ids(self, snapshot_id: str, vector_ids: List[np.uint32]) -> None:
        """
        Inserts/maps a list of vector IDs to a specific snapshot.
        """
        # Ensure snapshot exists first
        self.cursor.execute(
            "SELECT 1 FROM conversation_snapshots WHERE snapshot_id = ?", (snapshot_id,)
        )
        if not self.cursor.fetchone():
            logger.error(f"Failed to insert vector IDs: snapshot '{snapshot_id}' does not exist.")
            raise ValueError(f"Snapshot with ID '{snapshot_id}' does not exist.")

        logger.debug(f"Inserting {len(vector_ids)} vector IDs for snapshot '{snapshot_id}'")
        self.__insert_vector_ids(snapshot_id, vector_ids)

    def insert_cumulative_summary_offset(
        self, snapshot_id: str, file_offset: int
    ) -> None:
        """
        Inserts or updates the file offset mapped to a specific snapshot ID.
        """
        # Ensure snapshot exists first
        self.cursor.execute(
            "SELECT 1 FROM conversation_snapshots WHERE snapshot_id = ?", (snapshot_id,)
        )
        if not self.cursor.fetchone():
            logger.error(f"Failed to insert cumulative summary offset: snapshot '{snapshot_id}' does not exist.")
            raise ValueError(f"Snapshot with ID '{snapshot_id}' does not exist.")

        logger.debug(f"Inserting cumulative summary offset {file_offset} for snapshot '{snapshot_id}'")
        self.__insert_cumulative_summary_offset(snapshot_id, int(file_offset))

    def get_latest_cumulative_summary_vector_id(
        self, conversation_id: str
    ) -> Optional[int]:
        """
        Gets the cumulative summary vector ID of the latest snapshot in a conversation.
        """
        snapshot_metadata = self.__select_snapshot_metadata(conversation_id)
        if snapshot_metadata:
            return snapshot_metadata[-1][
                7
            ]  # Returns cumulative_summary_vector_id of the latest snapshot
        return None

    def get_cumulative_vector_id(self, snapshot_id: str):
        return self.__select_cumulative_summary_vector_id(snapshot_id)

    def get_file_offset(self, snapshot_id: str) -> Optional[int]:
        """
        Gets the file offset mapped to a specific snapshot ID.
        """
        return self.__select_file_offset(snapshot_id)

    def close(self) -> None:
        """
        Closes the SQLite database connection.
        """
        logger.debug(f"Closing database connection for '{self.db_path}'")
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


ConversationVectorManager = ConversationVectorMetaDataManager

