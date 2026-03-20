# Databricks notebook source

# MAGIC %md
# MAGIC # OpenAI API キー セットアップノートブック
# MAGIC
# MAGIC このノートブックを実行すると、OpenAI API キーが Databricks Secret Scope に自動登録されます。
# MAGIC
# MAGIC ## 手順
# MAGIC 1. 下の **`OPENAI_API_KEY`** ウィジェットに OpenAI API キーを入力してください。
# MAGIC 2. 必要に応じて `SECRET_SCOPE_NAME` を変更してください（デフォルト: `openai-secrets`）。
# MAGIC 3. **「Run All」** を実行してください。
# MAGIC
# MAGIC > **注意**: API キーはウィジェットに表示されます。実行後はノートブックを閉じるか、ウィジェットをクリアしてください。

# COMMAND ----------

# ウィジェットの初期化
dbutils.widgets.text("OPENAI_API_KEY", "", "OpenAI API Key (sk-...)")
dbutils.widgets.text("SECRET_SCOPE_NAME", "openai-secrets", "Secret Scope Name")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. 入力値の取得と検証

# COMMAND ----------

import re

openai_api_key  = dbutils.widgets.get("OPENAI_API_KEY").strip()
secret_scope    = dbutils.widgets.get("SECRET_SCOPE_NAME").strip()
secret_key_name = "openai-api-key"

# --- バリデーション ---
assert openai_api_key,          "OpenAI API キーを入力してください。"
assert openai_api_key.startswith("sk-"), \
    f"OpenAI API キーは 'sk-' で始まる必要があります。入力値: {openai_api_key[:6]}..."
assert re.match(r'^[a-zA-Z0-9_\-]+$', secret_scope), \
    "Secret Scope 名に使用できるのは英数字・ハイフン・アンダースコアのみです。"

print(f"Secret Scope : {secret_scope}")
print(f"Secret Key   : {secret_key_name}")
print(f"API Key 先頭 : {openai_api_key[:8]}... (全{len(openai_api_key)}文字)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Databricks REST API でシークレットを登録
# MAGIC
# MAGIC `dbutils.secrets` は読み取り専用のため、登録には Databricks REST API を使用します。

# COMMAND ----------

import requests, json

# ノートブック実行コンテキストからトークンとホストを自動取得
ctx        = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
api_token  = ctx.apiToken().get()
workspace_url = f"https://{spark.conf.get('spark.databricks.workspaceUrl')}"
headers    = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}

print(f"Workspace URL: {workspace_url}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2-1. Secret Scope の作成（既存の場合はスキップ）

# COMMAND ----------

scope_url = f"{workspace_url}/api/2.0/secrets/scopes/create"
scope_payload = {"scope": secret_scope, "initial_manage_principal": "users"}

resp = requests.post(scope_url, headers=headers, json=scope_payload)

if resp.status_code == 200:
    print(f"✓ Secret Scope '{secret_scope}' を作成しました。")
elif resp.status_code == 400 and "already exists" in resp.text:
    print(f"✓ Secret Scope '{secret_scope}' は既に存在します（スキップ）。")
else:
    raise Exception(f"Scope 作成に失敗しました: {resp.status_code} {resp.text}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2-2. OpenAI API キーの登録

# COMMAND ----------

put_url = f"{workspace_url}/api/2.0/secrets/put"
put_payload = {
    "scope":        secret_scope,
    "key":          secret_key_name,
    "string_value": openai_api_key,
}

resp = requests.post(put_url, headers=headers, json=put_payload)

if resp.status_code == 200:
    print(f"✓ シークレット '{secret_key_name}' を Scope '{secret_scope}' に登録しました。")
else:
    raise Exception(f"シークレット登録に失敗しました: {resp.status_code} {resp.text}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. 動作確認

# COMMAND ----------

retrieved_key = dbutils.secrets.get(scope=secret_scope, key=secret_key_name)

# 値が取得できれば成功（セキュリティ上、実際の値は表示されない）
assert retrieved_key, "シークレットの取得に失敗しました。"
print(f"✓ dbutils.secrets.get() でシークレットの取得に成功しました。")
print(f"  → 取得値: {retrieved_key[:3]}... (Databricks により値はマスクされます)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. セットアップ完了
# MAGIC
# MAGIC 以下の設定で OpenAI API キーが登録されました。
# MAGIC
# MAGIC | 項目 | 値 |
# MAGIC |------|----|
# MAGIC | Secret Scope | `openai-secrets` |
# MAGIC | Secret Key   | `openai-api-key` |
# MAGIC
# MAGIC ### チャットボットノートブックへの反映
# MAGIC
# MAGIC `databricks_notebook.py` の設定セルを以下のように変更してください：
# MAGIC
# MAGIC ```python
# MAGIC DATABRICKS_SECRET_SCOPE = "openai-secrets"
# MAGIC DATABRICKS_SECRET_KEY   = "openai-api-key"
# MAGIC ```
# MAGIC
# MAGIC ### セキュリティに関する注意
# MAGIC - このノートブックの実行後、ウィジェットの API キーをクリアすることを推奨します。
# MAGIC - `dbutils.widgets.removeAll()` を実行するか、ノートブックを再起動してください。

# COMMAND ----------

# ウィジェットをクリアして API キーをメモリから削除
dbutils.widgets.remove("OPENAI_API_KEY")
print("✓ ウィジェットをクリアしました。セットアップが完了しました。")
