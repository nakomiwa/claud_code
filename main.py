"""
LangGraph チャットボット - CLI エントリーポイント

使い方:
    python main.py

コマンド:
    quit / exit  : 終了
    history      : 会話履歴を表示
"""

import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from chatbot.graph import build_graph


def main() -> None:
    load_dotenv()  # .env ファイルを読み込んで環境変数に設定

    if not os.getenv("ANTHROPIC_API_KEY"):
        raise EnvironmentError(
            "ANTHROPIC_API_KEY が設定されていません。\n"
            ".env.example を .env にコピーして API キーを設定してください。"
        )

    print("LangGraph チャットボット (claude-sonnet-4-6)")
    print("'quit' で終了、'history' で会話履歴を表示\n")

    graph = build_graph()

    # 会話履歴をここで管理する
    # 毎回グラフに渡すことで LLM が文脈を把握できる
    conversation: list = []

    while True:
        try:
            user_input = input("あなた: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nさようなら！")
            break

        if not user_input:
            continue

        if user_input.lower() in {"quit", "exit"}:
            print("さようなら！")
            break

        if user_input.lower() == "history":
            if not conversation:
                print("  (まだメッセージはありません)")
            for msg in conversation:
                role = "あなた" if msg.type == "human" else "Claude"
                print(f"  [{role}] {msg.content}")
            continue

        # 新しいユーザーメッセージを履歴に追加
        conversation.append(HumanMessage(content=user_input))

        # 全会話履歴をグラフに渡して実行
        result = graph.invoke({"messages": conversation})

        # result["messages"] には全メッセージが含まれる
        # 最後のメッセージが Claude の返答
        ai_message = result["messages"][-1]
        print(f"Claude: {ai_message.content}\n")

        # ローカルの履歴をグラフの出力で更新
        conversation = result["messages"]


if __name__ == "__main__":
    main()
