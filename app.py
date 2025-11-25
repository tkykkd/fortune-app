import streamlit as st
import google.generativeai as genai
import datetime

# --- ページ設定 ---
st.set_page_config(page_title="AI統合運勢鑑定", page_icon="🌌", layout="wide")

# --- ロジック群 ---
# 五格の計算ロジックはそのまま残しますが、UIではAIに計算させるため使用しません。
def calculate_gokaku(sei_strokes, mei_strokes):
    """姓名判断の五格を計算する (UIからは使用停止)"""
    ten = sum(sei_strokes)
    chi = sum(mei_strokes)
    jin = sei_strokes[-1] + mei_strokes[0]
    gai = sei_strokes[0] + mei_strokes[-1]
    sou = ten + chi
    return {"天格": ten, "人格": jin, "地格": chi, "外格": gai, "総格": sou}

def get_constellation(month, day):
    """生年月日から星座を計算する"""
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
    """生年月日から数秘術のライフパスナンバーを計算する"""
    date_str = dob.strftime("%Y%m%d")
    def recursive_sum(n_str):
        total = sum(int(d) for d in n_str)
        if total in [11, 22, 33]: return total
        if total < 10: return total
        return recursive_sum(str(total))
    return recursive_sum(date_str)

# --- AIアドバイザー ---
def get_gemini_advice(profile, category):
    """AIに鑑定アドバイスを生成させる"""
    # 【修正: モデル名を安定版 gemini-2.5-flash に固定】
    model = genai.GenerativeModel('gemini-2.5-flash') 

    today = datetime.date.today()
    current_period = f"{today.year}年{today.month}月"

    # プロンプト (AIに画数計算をさせるように修正)
    prompt = f"""
    あなたは、相談者の人生戦略を共に考える「専属の運命コンサルタント」です。
    以下のデータを元に、深く、信頼感のある分析とアドバイスを行ってください。

    【基本スタンス】
    - 文調: 丁寧で落ち着いた敬語。
    - 姿勢: 軽い占いではなく、人生の指針となる「戦略」を提示する。
    - 根拠: なぜそのアドバイスなのか、必ずロジック（画数、数秘、星）と紐付ける。

    【相談者データ】
    - 名前: {profile['name_kanji']} (読み: {profile['name_yomi']})
    - 星座: {profile['constellation']}
    - 数秘: {profile['li
