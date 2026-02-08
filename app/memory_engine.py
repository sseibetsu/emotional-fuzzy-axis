import chromadb
from chromadb.utils import embedding_functions
import uuid
from datetime import datetime


class LongTermMemory:
    def __init__(self):
        print("Инициализация Vector DB...")
        self.client = chromadb.PersistentClient(path="./chroma_db")

        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        self.collection = self.client.get_or_create_collection(
            name="chat_history",
            embedding_function=self.embedding_fn
        )
        print("Память инициализирована.")

    def save_memory(self, session_id: str, text: str, speaker: str, emotion: str = "neutral"):
        """Сохраняет сообщение с привязкой к сессии."""
        mem_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        self.collection.add(
            documents=[text],
            metadatas=[{
                "session_id": session_id,
                "speaker": speaker,
                "emotion": emotion,
                "timestamp": timestamp
            }],
            ids=[mem_id]
        )

    def get_relevant_context(self, session_id: str, query: str, n_results: int = 3) -> str:
        """Ищет похожие сообщения в рамках текущей сессии."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where={"session_id": session_id}
            )

            context_str = ""
            if results['documents']:
                for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                    speaker = meta.get('speaker', 'Unknown')
                    emo = meta.get('emotion', 'neutral')
                    context_str += f"- {speaker} ({emo}): {doc}\n"

            return context_str
        except Exception as e:
            print(f"Memory Error: {e}")
            return ""

    def get_session_history(self, session_id: str, limit: int = 50):
        """Возвращает историю для фронтенда."""
        try:
            results = self.collection.get(
                where={"session_id": session_id},
                limit=limit
            )

            history = []
            if results['ids']:
                for doc, meta in zip(results['documents'], results['metadatas']):
                    history.append({
                        "content": doc,
                        "isUser": meta['speaker'] == "User",
                        "timestamp": meta['timestamp'],
                        "emotion": meta.get('emotion', 'neutral')
                    })

                history.sort(key=lambda x: x['timestamp'])

            return history
        except Exception:
            return []
