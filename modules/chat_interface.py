import streamlit as st
from modules import llm_helper, document_generator, legal_logic

def render_chat():
    """Renders the chat interface."""
    
    # Phase Visualization
    phase_map = {"empathy": 33, "structuring": 66, "report": 100}
    current_progress = phase_map.get(st.session_state.current_phase, 33)
    
    st.markdown(f'<div class="info-plate" style="margin-bottom: 16px;">現在のフェーズ: {st.session_state.current_phase}</div>', unsafe_allow_html=True)
    st.progress(current_progress)

    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input (Only if not in report phase)
    if st.session_state.current_phase != "report":
        from streamlit_mic_recorder import speech_to_text
        
        # 音声入力UIを下部に配置
        st.markdown('<div class="mic-container">', unsafe_allow_html=True)
        speech_result = speech_to_text(
            language='ja',
            start_prompt="🎤 マイクで話して相談する",
            stop_prompt="⏹️ 録音を終わって送信する",
            just_once=True,
            key='STT'
        )
        st.markdown('</div>', unsafe_allow_html=True)

        user_input_text = None
        if speech_result:
            user_input_text = speech_result

        chat_prompt = st.chat_input("またはテキストで状況を教えてください...")
        if chat_prompt:
            user_input_text = chat_prompt

        if user_input_text:
            # Add user message to state
            st.session_state.messages.append({"role": "user", "content": user_input_text})
            with st.chat_message("user"):
                st.markdown(user_input_text)

            # Get AI Response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                
                # Call LLM
                api_key = st.session_state.get("api_key")
                with st.spinner("考えています..."):
                    response_text = llm_helper.get_chat_response(
                        [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                        api_key
                    )
                
                message_placeholder.markdown(response_text)
            
            # Add assistant message to state
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            st.rerun()

    # Finish Interview Button & Report Generation
    if st.session_state.messages and st.session_state.current_phase != "report":
        st.divider()
        if st.button("相談を終了してレポートを作成する"):
            st.session_state.current_phase = "report"
            st.rerun()

    # Report Phase View
    if st.session_state.current_phase == "report":
        st.divider()
        st.header("📊 相談レポート & アドバイス")
        
        api_key = st.session_state.get("api_key")
        if not api_key:
            st.error("システム連携キー（APIキー）が設定されていません。プロジェクトのルートディレクトリにある `.env` ファイルに `GOOGLE_API_KEY` を設定してください。")
            return

        # 1. Automatic Fact Extraction (if not yet done)
        if not st.session_state.facts:
            with st.spinner("情報を整理中... (数秒かかります)"):
                facts = llm_helper.extract_facts_from_chat(st.session_state.messages, api_key)
                st.session_state.facts = facts
        
        # Display Extracted Facts
        with st.expander("📝 整理された事実関係 (確認用)", expanded=True):
            facts = st.session_state.facts
            
            st.markdown("### 【ご相談の概要】")
            # Create a simple mapping for Japanese labels
            st.markdown(f"**主なご相談内容:**\n{facts.get('main_issue', '不明')}")
            st.markdown(f"**ご希望の解決の形:**\n{facts.get('user_desire', '不明')}")
            
            st.markdown("### 【関係者と証拠】")
            parties = ", ".join(facts.get('parties', [])) if facts.get('parties') else "不明"
            evidence = ", ".join(facts.get('evidence', [])) if facts.get('evidence') else "特になし"
            st.markdown(f"**関係者:** {parties}")
            st.markdown(f"**証拠となるもの:** {evidence}")

            st.markdown("### 【時系列の出来事】")
            timeline = facts.get('timeline', [])
            if timeline:
                for event in timeline:
                    st.markdown(f"- {event}")
            else:
                st.markdown("不明")
                
            missing_info = facts.get('missing_info', '')
            if missing_info and missing_info != "不明":
                st.markdown("---")
                st.info(f"💡 **アドバイス:** {missing_info} についてもメモしておくと、専門家へ相談する際にスムーズです。")

        # 2. Recommendations
        st.subheader("🔗 推奨される相談窓口")
        # Use simple keyword matching based on the summary or full text
        # Concatenate user messages for search
        user_text = " ".join([m["content"] for m in st.session_state.messages if m["role"] == "user"])
        recommendations = legal_logic.get_recommendations(user_text)
        
        if recommendations:
            for rec in recommendations:
                st.info(f"**{rec['name']}**\n\n{rec['description']}")
        else:
            st.write("条件に一致する特定の窓口が見つかりませんでした。法テラスなどの総合窓口をお勧めします。")

        # 3. PDF Generation
        st.subheader("📄 相談シート")
        
        # Streamlitでは st.button の中に st.download_button を入れるとリロードされてダウンロードできないため、
        # 事前にPDFを作成して直接 download_button を配置するか、セッションステートで管理する。
        # ここでは事実抽出が終わったタイミングで一緒にPDF도準備しておくのがスムーズ。
        
        if "pdf_data" not in st.session_state:
            st.session_state.pdf_data = None
            
        if st.session_state.pdf_data is None:
            with st.spinner("PDFレポートを作成中..."):
                report_path = document_generator.create_pdf_report(st.session_state.messages, st.session_state.facts)
                if report_path:
                    with open(report_path, "rb") as file:
                        st.session_state.pdf_data = file.read()
                else:
                    st.error("レポートの作成に失敗しました。")
                    
        if st.session_state.pdf_data:
            st.download_button(
                label="📥 相談シートを保存する (PDF)",
                data=st.session_state.pdf_data,
                file_name="legal_consultation_sheet.pdf",
                mime="application/pdf"
            )
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("会話に戻る"):
            st.session_state.current_phase = "structuring"
            st.rerun()

