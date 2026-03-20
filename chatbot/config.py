MODEL_NAME = "claude-sonnet-4-6"
MAX_TOKENS = 1024
SYSTEM_PROMPT = "あなたは親切なアシスタントです。簡潔でわかりやすい返答をしてください。"

# Databricks Secrets の設定
# dbutils.secrets.put(scope="YOUR_SCOPE", key="anthropic-api-key", string_value="sk-ant-...")
DATABRICKS_SECRET_SCOPE = "YOUR_SECRET_SCOPE"   # 作成したスコープ名に変更
DATABRICKS_SECRET_KEY = "anthropic-api-key"      # シークレットのキー名
