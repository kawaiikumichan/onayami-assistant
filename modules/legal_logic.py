import streamlit as st
import json

RESOURCE_DATA = {
  "resources": [
    {
      "name": "法テラス千葉（日本司法支援センター）",
      "category": "General/Financial Aid",
      "description": "経済的に余裕がない場合の無料法律相談や、弁護士費用の立替え制度があります。",
      "access": "JR千葉駅・京成千葉駅 徒歩など"
    },
    {
      "name": "柏市役所 広聴相談課（無料法律相談）",
      "category": "Initial Consultation",
      "description": "柏市民を対象とした、弁護士による20分間の無料法律相談です（予約制）。",
      "note": "まずは市役所に電話して予約状況を確認してください。"
    },
    {
      "name": "千葉県弁護士会 松戸支部",
      "category": "Lawyer Introduction",
      "description": "柏市を含む東葛飾地域の弁護士が所属しています。有料の法律相談センターがあります。",
      "access": "松戸駅 徒歩10分"
    },
    {
      "name": "柏労働基準監督署",
      "category": "Labor Issues",
      "description": "未払い残業代や不当解雇など、労働基準法違反の疑いがある場合の相談窓口です。",
      "target_issues": ["残業代", "解雇", "労災", "過重労働"]
    },
    {
      "name": "柏警察署（生活安全課）",
      "category": "Safety/Criminal",
      "description": "DV（配偶者暴力）やストーカー被害など、身の危険がある場合の相談。",
      "target_issues": ["DV", "ストーカー", "暴力", "詐欺"]
    }
  ]
}

def render_disclaimer():
    """Renders the disclaimer and consent button."""
    st.markdown("## ⚠️ 利用規約・免責事項")
    st.warning("本サービスは法的助言を行うものではありません。")
    st.markdown("""
    1.  **非弁行為の禁止**: 本AIは弁護士ではありません。法律相談や法的判断は行いません。
    2.  **情報の整理**: 本サービスは、ユーザーの入力情報を整理し、一般的な相談窓口を案内するものです。
    3.  **自己責任**: 本サービスの結果を利用したことによる損害について、運営者は一切の責任を負いません。
    """)
    
    agreed = st.button("同意して開始する")
    if agreed:
        st.session_state.user_agreed = True
        st.rerun()

def get_recommendations(user_input):
    """
    Simple keyword matching to recommend resources.
    In a real app, this would be more sophisticated or LLM-driven.
    """
    recommendations = []
    text = user_input.lower()
    
    for res in RESOURCE_DATA["resources"]:
        keyword_match = False
        # Check target issues if they exist
        if "target_issues" in res:
            for issue in res["target_issues"]:
                if issue in text:
                    keyword_match = True
                    break
        
        # Check description and name
        if not keyword_match:
             if "description" in res and any(phrase in res["description"] for phrase in ["経済的", "お金", "費用"]):
                 if "お金" in text or "費用" in text or "経済的" in text:
                     keyword_match = True
             if "name" in res and "法テラス" in res["name"] and ("お金" in text or "費用" in text):
                 keyword_match = True
        
        if keyword_match:
            recommendations.append(res)
        
    return recommendations
