import pandas as pd
import io

def get_excel_download_data(df: pd.DataFrame):
    """DataFrame을 엑셀 바이너리 데이터로 변환합니다."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

def render_download_button(df: pd.DataFrame, filename: str, label: str = "📊 엑셀 다운로드"):
    """Streamlit 다운로드 버튼을 렌더링합니다."""
    import streamlit as st
    excel_data = get_excel_download_data(df)
    st.download_button(
        label=label,
        data=excel_data,
        file_name=f"{filename}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"dl_{filename}"
    )
