import streamlit as st
import google.generativeai as genai
import datetime

# --- ページ設定 ---
st.set_page_config(page_title="AI統合運勢鑑定", page_icon="🌌", layout="wide")

# --- ロジック群 ---
def calculate_gokaku(sei_strokes, mei_strokes):
    ten = sum(sei_strokes)
    chi = sum(mei_strokes)
    jin = sei_strokes[-1] + mei_strokes[0]
    gai = sei_strokes[0] + mei_strokes[-1]
    sou = ten + chi
    return {"天格": ten, "人格": jin, "地格": chi, "外格": gai, "総格": sou}

def get_constellation(month, day):
    zodiac_days = [
        (1, 20, "山羊座"), (2, 19, "水瓶座"), (3, 20, "魚座"), (4, 20, "牡羊座"),
        (5, 21, "牡牛座"), (6, 21, "双子座"), (7, 22, "蟹座"), (8, 23, "獅子座"),
        (9, 23, "乙女座"), (10, 23, "天秤座"), (11, 22, "蠍座"), (12, 22, "射手座"),
        (12, 31, "山羊座")
    ]
    for z_month, z_day, z_name in zodiac_days:
        if month == z_month:
            if day <= z_day: return z_name
            else:
                idx = zodiac_days.index((z_month, z_day, z_name))
                if idx + 1 < len(zodiac_days): return zodiac_days[idx+1][2]
                return "山羊座"
    return "不明"

def calculate_lifepath(dob):
    date_str = dob.strftime("%Y%m%d")
    def recursive_sum(n_str):
        total = sum(int(d) for d in n_str)
        if total in [11, 22, 33]: return total
        if total < 10: return total
        return recursive_sum(str(total))
    return recursive_sum(date_str)

# --- AIアドバイザー ---
def get_valid_model_name(api_key):
    genai.configure(api_key=api_key)
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini-1.5-flash' in m.name: return m.name
                if 'gemini-pro' in m.name: return m.name
        return 'gemini-pro'
    except:
        return 'gemini-pro'

def get_gemini_advice(profile, gokaku, category, api_key):
    model_name = get_valid_model_name(api_key)
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    today = datetime.date.today()
    current_period = f"{today.year}年{today.month}月"

    prompt = f\"\"\"
    あなたは、相談者の人生戦略を共に考える「専属の運命コンサルタント」です。
    以下のデータを元に、深く、信頼感のある分析とアドバイスを行ってください。

    【基本スタンス】
    - 文調: 丁寧で落ち着いた敬語。
    - 姿勢: 軽い占いではなく、人生の指針となる「戦略」を提示する。
    - 根拠: なぜそのアドバイスなのか、必ずロジック（画数、数秘、星）と紐付ける。

    【相談者データ】
    - 名前: {profile['name_kanji']} (読み: {profile['name_yomi']})
    - 画数データ: {gokaku}
    - 星座: {profile['constellation']}
    - 数秘: {profile['lifepath']}
    - 性別: {profile['gender']}
    - 悩みカテゴリ: {category}
    - **現在の時期: {current_period}**

    ## 鑑定書構成 (Markdown形式)

    ### 1. 姓名判断と本質プロファイリング
    まずは、あなたの画数が示す「社会的な運勢・才能」を詳しく紐解きます。
    - **総格（晩年・全体）**: ...
    - **人格（性格・才能）**: ...
    - **地格（若年・行動）**: ...
    - **外格（対人・評価）**: ...
    - **天格（宿命）**: ...
    
    続いて、「言霊（響き）」と「星座・数秘」を掛け合わせ、あなたが本来持っているポテンシャルや、内面の葛藤・魅力を分析します。

    ### 2. 未来を切り拓く戦略的アドバイス：{category}
    テーマ「{category}」について、あなたの強みを最大限に活かすための戦略を提案します。

    ### 3. 直近の運勢サイクルと今月の指針 ({current_period})
    数秘術における「パーソナル・マンス（個人月運）」の観点から、
    今月および直近の期間が、どのような「流れ」の中にあり、何を意識すべき時期なのかを解説してください。
    その上で、今月意識すべき「キーワード」を一つ提示してください。

    ### 4. コンサルタントからのメッセージ
    最後に、未来への希望となる、重みのある温かいエールを。
    \"\"\"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"エラー: {str(e)}"

# --- UI構築 ---
st.title("🌌 AI統合運勢鑑定")
st.markdown("姓名判断(詳細) × 言霊 × 占星術 × 月運戦略")

# APIキーはサイドバーで入力させる（セキュリティ対策）
with st.sidebar:
    api_key = st.text_input("Google Gemini APIキー", type="password")
    st.markdown("[キーの取得はこちら(無料)](https://aistudio.google.com/app/apikey)")
    st.info("※キーは保存されません。安心してお使いください。")

with st.form("input_form"):
    col_name1, col_name2 = st.columns(2)
    with col_name1:
        sei = st.text_input("苗字 (漢字)")
        sei_yomi = st.text_input("苗字 (よみ)")
        sei_kaku = st.text_input("苗字画数 (カンマ区切り)", "10,12")
    with col_name2:
        mei = st.text_input("名前 (漢字)")
        mei_yomi = st.text_input("名前 (よみ)")
        mei_kaku = st.text_input("名前画数 (カンマ区切り)", "12,11")
    
    col_attr1, col_attr2 = st.columns(2)
    with col_attr1:
        dob = st.date_input("生年月日", datetime.date(1990, 1, 1))
    with col_attr2:
        gender = st.radio("性別", ["男性", "女性"], horizontal=True)

    category = st.selectbox("今回のテーマ（知りたいこと）", 
                            ["仕事・キャリア・成功", "金運・財運", "人間関係・対人", "恋愛・結婚・パートナー", "自分の才能・強み"])
    
    submitted = st.form_submit_button("詳細鑑定スタート ✨")

if submitted:
    if not api_key:
        st.error("左側のサイドバーにAPIキーを入力してください！")
    else:
        try:
            # 計算処理
            s_list = [int(x) for x in sei_kaku.split(",")]
            m_list = [int(x) for x in mei_kaku.split(",")]
            gokaku = calculate_gokaku(s_list, m_list)
            constellation = get_constellation(dob.month, dob.day)
            lifepath = calculate_lifepath(dob)
            
            profile = {
                "name_kanji": f"{sei} {mei}",
                "name_yomi": f"{sei_yomi} {mei_yomi}",
                "gender": gender,
                "constellation": constellation,
                "lifepath": lifepath
            }
            
            st.success("詳細分析を実行中...")
            
            # スペック表示
            c1, c2, c3 = st.columns(3)
            c1.metric("星座", constellation)
            c2.metric("数秘", str(lifepath))
            c3.metric("総格", f"{gokaku['総格']}画")
            
            # AI鑑定
            with st.spinner("今月の運命サイクルと戦略を構築しています..."):
                advice = get_gemini_advice(profile, gokaku, category, api_key)
            
            st.markdown("---")
            st.subheader(f"📜 {sei} {mei} 様の運勢鑑定書")
            st.markdown(advice)
            st.balloons()
            
        except Exception as e:
            st.error(f"エラー: {e}")
