import os
import glob
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions

RAW_DATA_DIR = './data/format'
CHROMA_DB_PATH = './db'

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                model_name="text-embedding-3-small",
            )

client = chromadb.PersistentClient(CHROMA_DB_PATH)
collection = client.get_or_create_collection(
    name="my_collection",
    embedding_function=openai_ef
)

csv_files = glob.glob(os.path.join(RAW_DATA_DIR, '*.csv'))

for file_path in csv_files:
    try:
        df = pd.read_csv(file_path)
        documents = df.astype(str).agg(' '.join, axis=1).tolist()
        ids = [f"{os.path.basename(file_path)}_{i}" for i in range(len(df))]
        metadatas = [{"source": os.path.basename(file_path)} for _ in range(len(df))]
        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )

        print(f"'{os.path.basename(file_path)}' 파일의 데이터 {len(df)}개를 DB에 추가했습니다.")
    except Exception as e:
        print(f"'{file_path}' 처리 중 오류 발생: {e}")
print("\n모든 CSV 파일의 데이터 처리가 완료되었습니다.")
print(f"현재 컬렉션 '{collection.name}'에는 총 {collection.count()}개의 데이터가 저장되어 있습니다.")