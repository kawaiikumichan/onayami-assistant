import streamlit as st
import os
from dotenv import load_dotenv
from modules import chat_interface, legal_logic, document_generator

# Load environment variables
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="お悩み整理アシスタント",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_custom_css():
    st.markdown("""
        <style>
        /* フォント設定 (Noto Sans JP) */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Noto Sans JP', sans-serif !important;
            font-size: 16px !important;
            color: #333333;
        }

        /* 背景：放射状グラデーション（中心から外側へ）で紙のしなりを表現 */
        .stApp {
            background: radial-gradient(circle at center, #FFFFFF 0%, #F5F5F0 100%) !important;
        }

        /* 和紙テクスチャの擬似要素オーバーレイ（不透明度0.08で非常に薄く重ねる） */
        .stApp::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            background-image: url('https://www.transparenttextures.com/patterns/rice-paper-2.png');
            opacity: 0.08;
            pointer-events: none;
        }

        /* デフォルトのメニューやフッターを非表示にする */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* タイトル・見出し：シルクのような光沢のあるロイヤルブルー */
        h1, h2, h3 {
            background: linear-gradient(135deg, #002366 0%, #4169E1 30%, #8FA9FF 50%, #4169E1 70%, #002366 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700 !important;
            letter-spacing: 0.05em;
            margin-bottom: 24px !important;
            /* シルク感を際立たせるための微細なドロップシャドウ（テキスト用） */
            text-shadow: 0px 2px 4px rgba(0, 35, 102, 0.1);
            
            border-bottom: 2px solid #D4AF37 !important; /* シャンパンゴールド */
            padding-bottom: 8px;
            display: inline-block;
        }
        
        /* ボタン: 丸みを帯びたロイヤルブルーのグラデーション ＋ 金色のアクセント */
        .stButton>button {
            background: linear-gradient(135deg, #4169E1 0%, #002366 100%) !important;
            color: white !important;
            border: 1px solid rgba(212, 175, 55, 0.8) !important; /* シャンパンゴールドの細い枠線 */
            border-radius: 30px !important; /* より丸く */
            font-size: 16px !important;
            font-weight: 500 !important;
            padding: 12px 32px !important;
            box-shadow: 0 8px 20px rgba(0, 35, 102, 0.15) !important;
            transition: all 0.3s ease !important;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 24px rgba(212, 175, 55, 0.25) !important; /* 金色の影 */
            background: linear-gradient(135deg, #4b75f2 0%, #002e86 100%) !important;
        }
        
        /* チャットメッセージのグラスモーフィズムデザイン（和紙の上に柔らかく浮かせる） */
        .stChatMessage {
            background: rgba(255, 255, 255, 0.9) !important; /* 半透明の白で背景を透かせる */
            backdrop-filter: blur(12px) !important; 
            -webkit-backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(212, 175, 55, 0.2) !important; /* 繊細なシャンパンゴールドの枠 */
            border-radius: 20px !important;
            padding: 24px !important;
            margin-bottom: 24px !important;
            /* 広く、淡いシャドウで浮遊感を演出 */
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.03), 0 4px 12px rgba(0, 0, 0, 0.02) !important;
            line-height: 1.8 !important; /* ゆったりとした行間 */
        }
        
        /* AI側のメッセージ */
        [data-testid="stChatMessage"]:nth-child(even) {
            background: rgba(250, 251, 252, 0.9) !important; /* わずかに異なるトーン */
            border-left: 4px solid #D4AF37 !important; /* シャンパンゴールドのアクセントライン */
        }

        /* チャット入力欄のグラスモーフィズム */
        .stChatInputContainer {
            background: rgba(255, 255, 255, 0.9) !important;
            backdrop-filter: blur(12px) !important;
            border-radius: 24px !important;
            border: 1px solid rgba(212, 175, 55, 0.3) !important;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.04) !important;
            padding: 8px !important;
        }
        
        .stChatInputContainer textarea {
            font-size: 16px !important;
            color: #333333 !important;
        }
        
        /* エクスパンダー（事実関係）の高級感 */
        .streamlit-expanderHeader {
            background-color: rgba(255, 255, 255, 0.9) !important;
            border-radius: 12px !important;
            font-weight: 500 !important;
            color: #002366 !important;
            border: 1px solid rgba(212, 175, 55, 0.3) !important;
        }
        
        /* サイドバー */
        [data-testid="stSidebar"] {
            background-color: rgba(255, 255, 255, 0.92) !important;
            border-right: 1px solid rgba(212, 175, 55, 0.2) !important;
            box-shadow: 4px 0 24px rgba(0, 0, 0, 0.02) !important;
        }
        
        /* 区切り線を金色のグラデーションに */
        hr {
            border: 0;
            height: 1px;
            background: linear-gradient(to right, rgba(0,0,0,0), rgba(212, 175, 55, 0.4), rgba(0,0,0,0)) !important;
            margin: 32px 0 !important;
        }

        /* 案内テキスト用背景プレート（上品なすりガラス感） */
        .info-plate {
            background-color: rgba(255, 255, 255, 0.88) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(212, 175, 55, 0.2) !important; /* シャンパンゴールドの淡い枠線 */
            border-radius: 16px !important;
            padding: 24px 32px !important; /* ゆったりとした余白 */
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.03) !important; /* 和紙の上にそっと置かれたような影 */
            color: #002366 !important; /* ハイコントラストなロイヤルブルー */
            font-weight: 500 !important;
            font-size: 18px !important; /* 少し大きくして可読性アップ */
            letter-spacing: 0.05em;
            line-height: 1.6;
        }

        /* マイク入力コンテナのスタイリング */
        .mic-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 16px;
            padding: 10px;
            background: rgba(255, 255, 255, 0.6) !important;
            backdrop-filter: blur(8px) !important;
            border-radius: 24px !important;
            border: 1px solid rgba(212, 175, 55, 0.2) !important;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.02) !important;
        }
        </style>
    """, unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_agreed" not in st.session_state:
        st.session_state.user_agreed = False
    if "api_key" not in st.session_state:
        st.session_state.api_key = os.getenv("GOOGLE_API_KEY", "")
    if "facts" not in st.session_state:
        st.session_state.facts = {} # To store extracted 5W1H data
    if "current_phase" not in st.session_state:
        st.session_state.current_phase = "empathy" # empathy, structuring, report

def sidebar_settings():
    """Sidebar for API key and navigation (debug)."""
    with st.sidebar:
        if st.button("🔄 最初からやり直す"):
            st.session_state.messages = []
            st.session_state.facts = {}
            st.session_state.current_phase = "empathy"
            st.session_state.pdf_data = None
            st.rerun()

def main():
    inject_custom_css()
    init_session_state()
    sidebar_settings()

    st.title("🌱 お悩み整理アシスタント")
    st.markdown('<div class="info-plate">日常生活の困りごとを整理し、解決への第一歩をサポートします。</div>', unsafe_allow_html=True)

    # Phase 0: Disclaimer / Consent
    if not st.session_state.user_agreed:
        legal_logic.render_disclaimer()
        return

    # Phase 1 & 2: Chat Interface (Empathy & Structuring)
    chat_interface.render_chat()

if __name__ == "__main__":
    main()
