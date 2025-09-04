from dotenv import load_dotenv
import os

load_dotenv()  # .env를 현재 디렉터리부터 상위로 탐색하며 로드
api_key = os.getenv("OPENAI_API_KEY")