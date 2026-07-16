import os
import sys
import unittest

import numpy as np

# Add the parent directory to sys.path to resolve imports correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from memory.topic_pool.project_pool.conversation_pool.conversation_data_management.conversationVectorMetaManager import (
    ConversationVectorMetaDataManager,
)
from memory.topic_pool.project_pool.conversation_pool.snapShotNodes import SnapShotNode


class TestConversationVectorManager(unittest.TestCase):
    def setUp(self):
        # Use a temporary database for testing
        self.db_path = "test_conversation_snapshot.db"
        self.manager = ConversationVectorMetaDataManager(db_path=self.db_path)

    def tearDown(self):
        self.manager.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_insert_and_load_snapshots(self):
        # Create a sample SnapShotNode
        node = SnapShotNode(
            snapshot_id="snap-111",
            time_of_snap_shot="2026-07-12 12:00:00",
            size_of_the_summary=150,
            len_of_the_summary=25,
            summary_vector_ids=[np.uint32(10), np.uint32(20), np.uint32(30)],
            conversation_id="conv-123",
            cumulative_summary_vector_id=np.uint32(999),
        )

        # Insert snapshot
        snapshot_id = self.manager.insert_snapshot(
            node, topic_id="topic-abc", project_id="proj-xyz"
        )
        self.assertEqual(snapshot_id, "snap-111")

        # Retrieve snapshots by conversation ID
        snapshots = self.manager.load_snap_shot_objects("conv-123")
        self.assertEqual(len(snapshots), 1)

        retrieved_node = snapshots[0]
        self.assertEqual(retrieved_node.snapshot_id, "snap-111")
        self.assertEqual(retrieved_node.time_of_snap_shot, "2026-07-12 12:00:00")
        self.assertEqual(retrieved_node.size_of_the_summary, 150)
        self.assertEqual(retrieved_node.len_of_the_summary, 25)
        # Verify vector ID order is explicitly preserved
        self.assertEqual(retrieved_node.summary_vector_ids, [10, 20, 30])
        self.assertEqual(retrieved_node.conversation_id, "conv-123")
        self.assertEqual(retrieved_node.cumulative_summary_vector_id, 999)

        # Test insert cumulative summary offset
        self.manager.insert_cumulative_summary_offset(snapshot_id, file_offset=42)
        offset = self.manager.get_file_offset(snapshot_id)
        self.assertEqual(offset, 42)

        # Test get_cumulative_vector_id
        cum_vec_id = self.manager.get_cumulative_vector_id(snapshot_id)
        self.assertEqual(cum_vec_id, 999)

    def test_insert_vector_ids_separately(self):
        # Insert snapshot first
        node = SnapShotNode(
            snapshot_id="snap-222",
            time_of_snap_shot="2026-07-12 13:00:00",
            size_of_the_summary=200,
            len_of_the_summary=30,
            summary_vector_ids=[],  # starts empty
            conversation_id="conv-456",
            cumulative_summary_vector_id=np.uint32(888),
        )
        snapshot_id = self.manager.insert_snapshot(
            node, topic_id="topic-abc", project_id="proj-xyz"
        )

        # Insert vector IDs separately
        vector_ids = [np.uint32(100), np.uint32(200)]
        self.manager.insert_vector_ids(snapshot_id, vector_ids)

        # Load snapshots and verify vector IDs were updated and ordering is preserved
        snapshots = self.manager.load_snap_shot_objects("conv-456")
        self.assertEqual(len(snapshots), 1)
        self.assertEqual(snapshots[0].summary_vector_ids, [100, 200])

    def test_missing_snapshot_errors(self):
        # Attempting to insert vector IDs for non-existing snapshot must fail
        with self.assertRaises(ValueError):
            self.manager.insert_vector_ids("non-existent-snap", [np.uint32(1)])

        # Attempting to insert cumulative offset for non-existing snapshot must fail
        with self.assertRaises(ValueError):
            self.manager.insert_cumulative_summary_offset(
                "non-existent-snap", file_offset=50
            )

    def test_plain_insert_uniqueness_conflict(self):
        # Insert a snapshot
        node = SnapShotNode(
            snapshot_id="snap-333",
            time_of_snap_shot="2026-07-12 14:00:00",
            size_of_the_summary=100,
            len_of_the_summary=10,
            summary_vector_ids=[np.uint32(1)],
            conversation_id="conv-789",
            cumulative_summary_vector_id=np.uint32(777),
        )
        self.manager.insert_snapshot(node, topic_id="topic-abc", project_id="proj-xyz")

        # Inserting a duplicate snapshot_id must raise sqlite3.IntegrityError (plain INSERT)
        import sqlite3

        with self.assertRaises(sqlite3.IntegrityError):
            self.manager.insert_snapshot(
                node, topic_id="topic-abc", project_id="proj-xyz"
            )


if __name__ == "__main__":
    unittest.main()
