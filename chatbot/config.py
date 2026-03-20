MODEL_NAME = "gpt-5-mini"
MAX_TOKENS = 1024
SYSTEM_PROMPT = "あなたは親切なアシスタントです。簡潔でわかりやすい返答をしてください。"

# Databricks Secrets の設定
# databricks secrets create-scope --scope YOUR_SECRET_SCOPE
# databricks secrets put --scope YOUR_SECRET_SCOPE --key openai-api-key
DATABRICKS_SECRET_SCOPE = "YOUR_SECRET_SCOPE"   # 作成したスコープ名に変更
DATABRICKS_SECRET_KEY = "openai-api-key"
