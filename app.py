import streamlit as st
from docxtpl import DocxTemplate
import json
from datetime import date
from io import BytesIO

# ----------------------------
# 自動補完（作成日・空欄対応＋リスト補完）
# ----------------------------
def fill_data(data):
    data["作成日"] = date.today().strftime("%Y年{}月{}日".format(date.today().month, date.today().day))
    data["活かせる経験"] = data.get("活かせる経験・スキル", data.get("活かせる経験", "（活かせる経験を入力してください）"))
    data["職歴要約"] = data.get("職歴要約", "（職歴要約を入力してください）")
    data["資格特技"] = data.get("資格特技", data.get("資格履歴書用", "（資格・特技を入力してください）"))

    def pad_list(lst, target_len, default_obj):
        lst = lst if isinstance(lst, list) else []
        while len(lst) < target_len:
            lst.append(default_obj.copy())
        return lst

    data["学歴"] = pad_list(data.get("学歴", []), 6, {"年": "", "月": "", "内容": ""})
    data["職歴"] = pad_list(data.get("職歴", []), 8, {"年": "", "月": "", "内容": ""})
    if isinstance(data.get("資格"), list) and all(isinstance(q, str) for q in data["資格"]):
        data["資格"] = [{"年": "", "月": "", "内容": q} for q in data["資格"]]
    data["資格"] = pad_list(data.get("資格", []), 5, {"年": "", "月": "", "内容": ""})

    return data

# ----------------------------
# Word出力処理（テンプレ＋データ）
# ----------------------------
def generate_docx(template_path, data):
    tpl = DocxTemplate(template_path)
    tpl.render(data)
    buffer = BytesIO()
    tpl.save(buffer)
    buffer.seek(0)
    return buffer

# ----------------------------
# Streamlit UI本体
# ----------------------------
st.title("📄 履歴書・職務経歴書 自動作成アプリ")

uploaded_file = st.file_uploader("📂 JSONファイルをアップロードしてください", type="json")
resume_flag = st.checkbox("✅ 履歴書を作成", value=True)
career_flag = st.checkbox("✅ 職務経歴書を作成", value=True)

if uploaded_file:
    try:
        raw = json.load(uploaded_file)
        data = fill_data(raw)
        name = data.get("氏名", "noname").replace(" ", "").replace("　", "")

        if resume_flag:
            try:
                st.write("📂 テンプレートパス確認：履歴書_原本.gpt用.docx を読み込みます")
                resume_docx = generate_docx("履歴書_原本.gpt用.docx", data)
                st.download_button("📥 履歴書をダウンロード", resume_docx, file_name=f"履歴書_{name}.docx")
            except Exception as e:
                st.error(f"❌ 履歴書テンプレート読み込み時のエラー: {e}")

        if career_flag:
            try:
                career_docx = generate_docx("template.docx", data)
                st.download_button("📥 職務経歴書をダウンロード", career_docx, file_name=f"職務経歴書_{name}.docx")
            except Exception as e:
                st.error(f"❌ 職務経歴書テンプレート読み込み時のエラー: {e}")

    except Exception as e:
        st.error(f"❌ JSON読み込みでエラーが発生しました：{e}")
