import sqlite3


class Manager:
    def __init__(self, db_path: str, is_chunker_type_hierarchical: bool) -> None:
        self.is_chunker_type_hierarchical = is_chunker_type_hierarchical
        self.connection = sqlite3.connect(db_path)
        self.connection.execute("PRAGMA foreign_keys = ON;")
        self.cursor = self.connection.cursor()
        self._create_table()

    def __create_document_htable(self):
        documentTableQuery = """
            CREATE TABLE IF NOT EXISTS Documents (
                documentId TEXT PRIMARY KEY,
                documentName TEXT
            )
        """
        self.cursor.execute(documentTableQuery)

    def __create_section_htable(self):
        sectionTableQuery = """
            CREATE TABLE IF NOT EXISTS Section(
                sectionId TEXT PRIMARY KEY, 
                documentId TEXT, 
                content TEXT NOT NULL,
                content_length INTEGER NOT NULL,
                startoffset int not null,
                endoffset int not null,
                FOREIGN KEY (documentId) REFERENCES Documents(documentId)
            )
        """
        self.cursor.execute(sectionTableQuery)

    def __create_context_htable(self):
        contextTableQuery = """
            CREATE TABLE IF NOT EXISTS Context(
                contextId TEXT PRIMARY KEY,
                sectionId TEXT , 
                content TEXT not null,
                content_length int not null,
                startoffset int not null,
                endoffset int not null,
                FOREIGN KEY (sectionId) REFERENCES Section(sectionId)
            )
        """
        self.cursor.execute(contextTableQuery)

    def __create_chunk_htable(self):
        chunkTableQuery = """
            CREATE TABLE IF NOT EXISTS Chunk(
                chunkId TEXT PRIMARY KEY,
                contextId TEXT,
                chunks TEXT not null,
                startoffset int not null,
                endoffset int not null,
                FOREIGN KEY (contextId) REFERENCES Context(contextId)
            )
        """
        self.cursor.execute(chunkTableQuery)

    def _create_table(self):
        try:
            if self.is_chunker_type_hierarchical:
                self.__create_document_htable()
                self.__create_section_htable()
                self.__create_context_htable()
                self.__create_chunk_htable()
        except sqlite3.Error as e:
            raise Exception(f"Database setup failed: {e}") from e
