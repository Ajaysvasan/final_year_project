# Conversation Vector Metadata Management (`conversationVectorMetaManager.py`)

## Overview & Purpose
The `conversationVectorMetaManager.py` module defines `ConversationVectorMetaDataManager` (aliased globally as `ConversationVectorManager`). It manages transactional persistence and querying of conversational turn metadata, vector ID lists (`snapshot_vector_ids`), summary vectors, and cumulative file offsets (`cumulative_summary_offsets`) inside SQLite (`conversation_snapshot.db`). The legacy file `conversatoinVectorManager.py` provides memory-mapped binary vector reads (`_read_vectors`) and appends (`add_summary_vectors`).

---

## Classes & Public APIs

### `class ConversationVectorMetaDataManager`
Persistent SQLite metadata and vector ID mapping engine for conversational topic turns and snapshots.

#### Constructor: `__init__(self, db_path: Optional[str] = None) -> None`
Initializes the SQLite database connection (`sqlite3.connect`), enables foreign key enforcement, and ensures required tables exist (`conversation_snapshots`, `snapshot_vector_ids`, `cumulative_summary_offsets`).

##### Parameters
| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `db_path` | `Optional[str]` | `Config.CONVERSATION_SNAPSHOT_DB` | Path to the SQLite snapshot metadata database file. |

---

#### Relational Schema
- **`conversation_snapshots`**: `(row_id INTEGER PK AUTOINCREMENT, snapshot_id TEXT UNIQUE, project_id TEXT, topic_id TEXT, conversation_id TEXT, timestamp TEXT, size_of_the_summary INTEGER, len_of_the_summary INTEGER, cumulative_summary_vector_id INTEGER)`
- **`snapshot_vector_ids`**: `(snapshot_id TEXT FK, vector_id INTEGER, vector_position INTEGER, PRIMARY KEY (snapshot_id, vector_position))`
- **`cumulative_summary_offsets`**: `(snapshot_id TEXT PRIMARY KEY FK, file_offset INTEGER NOT NULL)`

---

#### Public Methods

##### `insert_snapshot(self, snapshot_node: SnapShotNode, topic_id: str, project_id: str) -> str`
Inserts a `SnapShotNode` and any associated `summary_vector_ids` into the SQLite database.

###### Parameters
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `snapshot_node` | `SnapShotNode` | Domain object containing `snapshot_id`, `conversation_id`, summaries, and IDs. |
| `topic_id` | `str` | Topic group identifier. |
| `project_id` | `str` | Project workspace identifier. |

###### Return Value
- **Type:** `str`
- **Description:** Returns the `snapshot_id` of the inserted record.

---

##### `load_snap_shot_objects(self, conversation_id: str) -> List[SnapShotNode]`
Queries all `SnapShotNode` objects for a given conversation using a single `LEFT JOIN` query across `conversation_snapshots` and `snapshot_vector_ids`.

###### Parameters
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `conversation_id` | `str` | Target conversation identifier. |

###### Return Value
- **Type:** `List[SnapShotNode]`
- **Description:** Chronologically ordered list (`ORDER BY s.row_id ASC, v.vector_position ASC`) of reconstructed snapshot domain objects.

---

##### `get_snapshot_metadata(self, conversation_id: str) -> List[tuple]`
Retrieves raw tuple rows directly from `conversation_snapshots` for a given conversation ID (`ORDER BY row_id ASC`).

---

##### `insert_vector_ids(self, snapshot_id: str, vector_ids: List[np.uint32]) -> None`
Maps a list of vector IDs to an existing snapshot. Deletes prior mappings for that snapshot and inserts new rows preserving `vector_position`.

###### Parameters
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `snapshot_id` | `str` | Target snapshot identifier. |
| `vector_ids` | `List[np.uint32]` | Ordered list of unsigned 32-bit integer vector tags. |

---

##### `insert_cumulative_summary_offset(self, snapshot_id: str, file_offset: int) -> None`
Inserts or updates the file byte offset mapped to a specific snapshot ID inside `cumulative_summary_offsets`.

###### Parameters
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `snapshot_id` | `str` | Target snapshot ID. |
| `file_offset` | `int` | Byte offset where the cumulative summary vector is stored in binary disk files. |

---

##### `get_latest_cumulative_summary_vector_id(self, conversation_id: str) -> Optional[int]`
Retrieves the `cumulative_summary_vector_id` of the most recent snapshot in a conversation (`snapshot_metadata[-1][7]`).

---

##### `get_cumulative_vector_id(self, snapshot_id: str) -> Optional[int]`
Queries `cumulative_summary_vector_id` directly from `conversation_snapshots` for a specific snapshot ID.

---

##### `get_file_offset(self, snapshot_id: str) -> Optional[int]`
Queries `file_offset` from `cumulative_summary_offsets` where `snapshot_id = ?`.

---

##### `close(self) -> None`
Closes the underlying SQLite database connection (`self.conn.close()`). Supports context management (`__enter__` and `__exit__`).

---

### `class ConversationVectorManager` (`conversatoinVectorManager.py`)
Legacy memory-mapped binary vector storage manager for appending and slicing vector arrays from raw `.bin` disk files.

#### Methods
- `add_summary_vectors(project_id: str, vectors: np.ndarray) -> Tuple[int, int]`: Appends 2D `np.float32` vector arrays directly to `<cummulative_vector_path>/<project_id>.bin` using `open(file_path, "ab")` and returns logical `(start_idx, end_idx)`.
- `get_cummulative_summary_vector(start_idx: int, end_idx: int, project_id: str) -> np.ndarray`: Memory-maps (`np.memmap`) and slices vectors from `self.summary_path`.
- `get_summary_vector(start_idx: int, end_idx: int, project_id: str) -> np.ndarray`: Memory-maps and slices vectors from `self.cummulative_vector_path`.
