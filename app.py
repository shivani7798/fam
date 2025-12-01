import streamlit as st
import gspread
from datetime import datetime
from PIL import Image
import base64
from io import BytesIO

# -------------------------------
# PAGE CONFIG + STYLE
# -------------------------------
st.set_page_config(page_title="Family Diary",
                   layout="wide",
                   page_icon="📖")

# Fun CSS theme
st.markdown("""
    <style>
        body {
            background-color: #FFFAED;
        }
        .title {
            font-size: 42px; 
            font-weight: 800; 
            color: #d35400;
            text-align: center;
        }
        .incident-title {
            font-size: 28px; 
            font-weight: 800; 
            color: #8e44ad;
        }
        .box {
            background: #FFF5D6;
            padding: 20px;
            border-radius: 12px;
            margin-top: 15px;
            border: 2px solid #F2C94C;
        }
        .sidebar .sidebar-content {
            background-color: #FFF2CC;
        }
        .comment-box {
            background: #ffffff;
            padding: 15px;
            border-radius: 10px;
            margin-top: 10px;
            border: 1px solid #ccc;
        }
    </style>
""", unsafe_allow_html=True)


# -------------------------------
# CONNECT TO GOOGLE SHEETS
# -------------------------------
gc = gspread.service_account(filename="creds.json")

# Main incidents sheet
sheet = gc.open("FamilyDiary").sheet1

# Comments sheet (create manually in Google Sheets)
comments_sheet = gc.open("FamilyDiary").worksheet("Comments")


# -------------------------------
# FUNCTIONS
# -------------------------------
def image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()


def base64_to_image(b64):
    if not b64:
        return None
    return Image.open(BytesIO(base64.b64decode(b64)))


# -------------------------------
# MAIN UI
# -------------------------------

st.markdown("<div class='title'>📖 Family Memories Diary</div>", unsafe_allow_html=True)
st.write("A place to save funny, silly, unforgettable family moments 😊")

records = sheet.get_all_records()


# -------------------------------
# SIDEBAR — LIST OF INCIDENTS
# -------------------------------
st.sidebar.header("📚 All Incidents")

if records:
    titles = [r["Title"] for r in records]
    selected_title = st.sidebar.selectbox("Choose an incident", titles)
else:
    selected_title = None
    st.sidebar.write("No incidents yet!")


# -------------------------------
# SHOW SELECTED INCIDENT
# -------------------------------
if selected_title:
    data = next(r for r in records if r["Title"] == selected_title)

    st.markdown(f"<div class='incident-title'>{data['Title']}</div>", 
                unsafe_allow_html=True)

    st.markdown(f"<div class='box'>{data['Content']}</div>", 
                unsafe_allow_html=True)

    st.caption(f"🗓 Added on: {data['Date']}")

    # Display image
    img = base64_to_image(data.get("Image"))
    if img:
        st.image(img, caption="Family moment ❤️", use_container_width=True)

    # -----------------------------------
    # SHOW COMMENTS
    # -----------------------------------
    st.subheader("💬 Comments")

    all_comments = comments_sheet.get_all_records()

    incident_comments = [
        c for c in all_comments if c["IncidentTitle"] == selected_title
    ]

    if incident_comments:
        for c in incident_comments:
            st.markdown(
                f"""
                <div class='comment-box'>
                    <b>{c['Name']}:</b> {c['Comment']}  
                    <br><span style='font-size:12px; color:gray;'>🗓 {c['Date']}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("No comments yet — be the first!")


    # -----------------------------------
    # ADD NEW COMMENT (GUEST)
    # -----------------------------------
    st.subheader("➕ Add a Comment")

    guest_name = st.text_input("Your Name (anything, guest allowed)")
    guest_comment = st.text_area("Your Comment")

    if st.button("Post Comment"):
        if not guest_name.strip() or not guest_comment.strip():
            st.error("Please enter both a name and a comment!")
        else:
            comments_sheet.append_row([
                selected_title,
                guest_name,
                guest_comment,
                str(datetime.now())
            ])
            st.success("Comment added!")
            st.experimental_rerun()


# -------------------------------
# ADD NEW INCIDENT
# -------------------------------
st.subheader("➕ Add a New Family Incident")

title = st.text_input("Incident Title")
content = st.text_area("Write the story")

uploaded_img = st.file_uploader("Upload an image (optional)", type=["jpg", "jpeg", "png"])

if uploaded_img:
    img = Image.open(uploaded_img)
    st.image(img, caption="Preview", use_container_width=True)
    img_base64 = image_to_base64(img)
else:
    img_base64 = ""

if st.button("Save Incident"):
    if not title or not content:
        st.error("Please enter a title and story!")
    else:
        sheet.append_row([title, content, str(datetime.now()), img_base64])
        st.success("🎉 Incident added successfully!")
        st.experimental_rerun()
