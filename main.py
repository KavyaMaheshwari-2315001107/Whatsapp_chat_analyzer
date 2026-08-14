import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Whatsapp Chat Analyzer", layout="wide")

st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader(
    "Choose a file",
    type=["txt"],
    key="whatsapp_chat_upload"
)

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()

    # Safe decoding
    try:
        data = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            data = bytes_data.decode("utf-16")
        except UnicodeDecodeError:
            data = bytes_data.decode("latin-1")

    # preprocess
    df = preprocessor.preprocess(data)

    if df.empty:
        st.error("No messages could be parsed. Export the WhatsApp chat again using **Without Media**.")
        st.stop()

    # fetch unique users
    user_list = df['user'].unique().tolist()

    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox(
        "Show analysis wrt",
        user_list
    )

    if st.sidebar.button("Show Analysis"):

        # Stats Area
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)

        with col2:
            st.header("Total Words")
            st.title(words)

        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)

        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # Monthly Timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(timeline['time'], timeline['message'], color='green', linewidth=2)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

        # Daily Timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black', linewidth=2)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

        # Activity Map
        st.title("Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user, df)

            fig, ax = plt.subplots(figsize=(5, 4))
            ax.bar(busy_day.index, busy_day.values, color='skyblue')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)

            fig, ax = plt.subplots(figsize=(5, 4))
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

        # Weekly Activity Heatmap
        st.title("Weekly Activity Heatmap")
        user_heatmap = helper.activity_heatmap(selected_user, df)

        fig, ax = plt.subplots(figsize=(10, 4))
        sns.heatmap(user_heatmap, ax=ax, cmap='YlGnBu')
        plt.tight_layout()
        st.pyplot(fig)

        # Most Busy Users
        if selected_user == 'Overall':
            st.title("Most Busy Users")
            x, new_df = helper.most_busy_users(df)

            col1, col2 = st.columns(2)

            with col1:
                fig, ax = plt.subplots(figsize=(5, 4))
                ax.bar(x.index, x.values, color='red')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)

        # WordCloud
        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user, df)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.imshow(df_wc)
        ax.axis("off")
        plt.tight_layout()
        st.pyplot(fig)

        # Most Common Words
        st.title("Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh(most_common_df[0], most_common_df[1], color='purple')
        plt.tight_layout()
        st.pyplot(fig)

        # Emoji Analysis
        st.title("Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)

        with col2:
            if not emoji_df.empty:
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(
                    emoji_df[1].head(),
                    labels=emoji_df[0].head(),
                    autopct="%0.2f"
                )
                st.pyplot(fig)