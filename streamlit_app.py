import streamlit as st

st.set_page_config(page_title="منصة تاور", page_icon="🌾")

st.title("🌾 منصة تاور العلمية")
st.write("الاختصاصي م. عبد القادر إسماعيل تاور")

code = st.text_input("🔑 كود الدخول", type="password")

if code == "202687":
    st.success("👑 مرحباً مالك المنصة")
elif code == "2020":
    st.success("👨‍🔬 مرحباً مختص")
elif code == "2026":
    st.success("🌾 مرحباً مربي")
elif code:
    st.error("❌ كود غير صحيح")

st.caption("© 2026 - جميع الحقوق محفوظة")
