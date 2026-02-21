# Legal Prep (法律相談事前整理AI)

## 概要
法的トラブルを抱えるユーザーが、弁護士相談の前に事実関係を整理し、適切な相談窓口を見つけるためのAIアシスタントツールです。

## セットアップ

### 必要要件
- Python 3.8以上
- OpenAI API Key

### インストール
以下のコマンドで依存ライブラリをインストールしてください。

```bash
python -m pip install -r requirements.txt
```

## 実行方法

以下のコマンドでアプリケーションを起動します。

```bash
python -m streamlit run app.py
```

ブラウザが自動的に開き、アプリが表示されます。
初回起動時に、サイドバーにてOpenAI API Keyを入力してください。

## ファイル構成
- `app.py`: メインアプリケーション
- `modules/`: アプリケーションロジック
- `requirements.txt`: 依存ライブラリ一覧
