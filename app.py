import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# 1. アプリ設定 & データ読み込み
# ==========================================
st.set_page_config(page_title="VALO-TYPE 40", page_icon="🎯")
st.title("🎯 VALO-TYPE 40")
st.write("プロ仕様の40問で、あなたのプレイスタイルを精密に分析します。")

@st.cache_data
def load_data():
    # 作成したExcelファイルを読み込む
    return pd.read_excel("valorant_questions_v2.xlsx")

try:
    df = load_data()
except Exception as e:
    st.error("エラー: 'valorant_questions_v2.xlsx' が読み込めません。GitHubにアップロードされているか確認してください。")
    st.stop()

# ==========================================
# 2. 診断フォーム (5段階評価)
# ==========================================
user_scores = []
# 選択肢の定義（1〜5点）
options = {1: "全く違う", 2: "あまりない", 3: "どちらでもない", 4: "まあまあある", 5: "強くそう思う"}

with st.form("diagnosis_form"):
    st.write("以下の質問に、直感で答えてください。")
    for index, row in df.iterrows():
        st.subheader(f"Q{index+1}. {row['question']}")
        # 5段階のスライダーを表示
        choice = st.select_slider(
            "あてはまる度合い:",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: options[x], # 数値を文字に変換して表示
            key=f"q_{index}",
            value=3 # デフォルトは真ん中
        )
        user_scores.append({"category": row['category'], "score": choice})
    
    st.write("---")
    submit_btn = st.form_submit_button("全40問の結果を解析する")

# ==========================================
# 3. 解析ロジック & 結果表示
# ==========================================
if submit_btn:
    # --- 集計 ---
    summary = {"Aggro": 0, "Logic": 0, "Stoic": 0, "Teamwork": 0}
    counts = {"Aggro": 0, "Logic": 0, "Stoic": 0, "Teamwork": 0}
    
    for item in user_scores:
        cat = item["category"]
        if cat in summary:
            summary[cat] += item["score"]
            counts[cat] += 1
            
    # 平均点（1.0〜5.0）を算出
    avg = {k: v / counts[k] if counts[k] > 0 else 0 for k, v in summary.items()}

    # --- タイプ判定 (しきい値 3.2) ---
    threshold = 3.2
    m = ""
    m += "A" if avg["Aggro"] >= threshold else "P"
    m += "L" if avg["Logic"] >= threshold else "I"
    m += "S" if avg["Stoic"] >= threshold else "E"
    m += "T" if avg["Teamwork"] >= threshold else "C"

    # --- 適性ロール判定 (一番高い数値を参照) ---
    # 単純比較で一番高いステータスに適したロールを割り当て
    max_stat = max(avg, key=avg.get)
    if max_stat == "Aggro": best_role = "Duelist"
    elif max_stat == "Teamwork": best_role = "Initiator"
    elif max_stat == "Logic": best_role = "Sentinel"
    else: best_role = "Controller" # Stoicが高い場合など

    # --- 16タイプの結果タイトル定義 ---
    results_data = {
        "ALST": "冷静な戦術指揮官", "ALSC": "孤高の天才軍師", "ALET": "理論武装した情熱家", "ALEC": "計算された破壊屋",
        "AIST": "本能で動くエース", "AISC": "野生の狩人", "AIET": "熱き突撃隊長", "AIEC": "暴走する破壊神",
        "PLST": "完璧主義の守護神", "PLSC": "冷徹な影の支配者", "PLET": "盤面の教育者", "PLEC": "職人気質の仕事人",
        "PIST": "静かなる暗殺者", "PISC": "マイペースな仕事師", "PIET": "心優しいサポーター", "PIEC": "感性豊かなムードメーカー"
    }
    title = results_data.get(m, "変幻自在なエージェント")

    # --- 画面表示 ---
    st.balloons()
    st.header(f"あなたのタイプ: {m}型")
    st.subheader(f"「{title}」")
    st.info(f"適性ロール: **{best_role}**")

    # --- レーダーチャート描画 ---
    # グラフを閉じるために最初のデータを最後に追加
    categories = ['積極性(A)', '論理性(L)', '精神安定(S)', '協力意識(T)']
    values = [avg["Aggro"], avg["Logic"], avg["Stoic"], avg["Teamwork"]]
    values += values[:1] 
    categories += categories[:1]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        line_color='#ff4b4b'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[1, 5])), # 1〜5の範囲で固定
        showlegend=False,
        title="プレイスタイル分析グラフ"
    )
    st.plotly_chart(fig)

    # --- Discord共有用テキスト ---
    st.write("### 💬 Discord共有用テキスト")
    share_text = f"**【VALO-TYPE 40 診断結果】**\n🛡️ タイプ: {title} ({m}型)\n🔫 適性ロール: {best_role}\n📊 A:{avg['Aggro']:.1f} / L:{avg['Logic']:.1f} / S:{avg['Stoic']:.1f} / T:{avg['Teamwork']:.1f}\n#VALOTYPE40"
    st.code(share_text, language=None)
    st.caption("テキストをコピーして貼り付けてね！グラフはスクショでシェア！")