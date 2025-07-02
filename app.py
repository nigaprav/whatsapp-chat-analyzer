import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from matplotlib import pyplot as plt
import preprocessor,helper
from wordcloud import wordcloud

st.sidebar.title('WhatsApp Chat Analyzer')
uploaded_file = st.sidebar.file_uploader('Choose a file')
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode('utf-8')
    df = preprocessor.preprocessor(data)
    user_list = helper.select_user(df)
    selected_user = st.sidebar.selectbox('Select User',user_list)

    if 'show_analysis' not in st.session_state:
        st.session_state.show_analysis = False

    if st.sidebar.button('Show Analysis'):
        st.session_state.show_analysis = True

    if st.session_state.show_analysis:


        st.title('Top Statistics')
        total,word_count, total_media, total_no_of_links = helper.fetch_stats(df,selected_user)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header('Total Messages')
            st.title(total)
        with col2:
            st.header('Total Words Used')
            st.title(word_count)
        with col3:
            st.header('Total Media Shared')
            st.title(total_media)
        with col4:
            st.header('Total Links Shared')
            st.title(total_no_of_links)

        if selected_user == 'Overall':

            col1, col2 = st.columns(2)
            with col1:
                st.title('Most Busy Users')
                busy_user_df = helper.busy_users(df)
                st.table(busy_user_df)

            with col2:
                fig = go.Figure(data=[go.Bar(x=busy_user_df['User'],y=busy_user_df['Contribution (%)'])])
                fig.update_layout(
                    xaxis_title='Users',
                    yaxis_title='Contribution (%)',
                    xaxis=dict(
                        tickangle=90
                )
                )
                st.plotly_chart(fig)

        st.title('Activity Map')
        col1, col2 = st.columns(2)
        month_df = helper.busy_month(df,selected_user)
        day_df = helper.busy_week(df,selected_user)

        with col1:
            st.header('Most Busy Months')
            fig = go.Figure(data=[go.Bar(x=month_df['Month'],y=month_df['count'])])
            fig.update_layout(
                    xaxis_title='Month',
                    yaxis_title='Message Count',
                    xaxis=dict(
                        tickangle=45
                )
                )
            st.plotly_chart(fig)

        with col2:
            st.header('Most Busy Days')
            fig = go.Figure(data=[go.Bar(x=day_df['Day Name'],y=day_df['count'],marker_color = 'orange')])
            fig.update_layout(
                    xaxis_title='Days',
                    yaxis_title='Message Count',

                    xaxis=dict(
                        tickangle=45
                )
                )
            st.plotly_chart(fig)

        st.title('Weekly Activity')
        if selected_user == 'Overall':
            fig, ax = plt.subplots(figsize=(15,10))
            ax = sns.heatmap(pd.pivot_table(df, index='Day Name', columns='Period', values='Message', aggfunc='count'),
                    cmap='Blues')
            plt.xticks(rotation=45)
            st.pyplot(fig)
        elif selected_user != 'Overall':
            df = df[df['User']==selected_user]
            fig, ax = plt.subplots(figsize=(15,10))
            ax = sns.heatmap(pd.pivot_table(df, index='Day Name', columns='Period', values='Message', aggfunc='count'),
                    cmap='Blues')
            plt.xticks(rotation=45)
            st.pyplot(fig)


        st.title('Word Cloud')
        wc_df = helper.word_cloud(df,selected_user)
        fig, ax = plt.subplots()
        ax.imshow(wc_df)
        st.pyplot(fig)

        st.title('Most Common Words')
        col1, col2 = st.columns(2)
        with col1:
            most_common_words = helper.most_used_words(df, selected_user)
            st.dataframe(most_common_words)

        with col2:
            fig = go.Figure(data=[go.Bar(x = most_common_words['Word'],y=most_common_words['Count'])])
            fig.update_layout(
                xaxis_title='Words',
                yaxis_title='Count',
                xaxis=dict(
                    tickangle=-45
            )
            )
            st.plotly_chart(fig)

        st.title('Most Common Emojis')
        col1, col2 = st.columns(2)
        with col1:
            most_common_emoji = helper.emoji_count(df, selected_user)
            st.dataframe(most_common_emoji)

        with col2:
            fig = go.Figure(data=[go.Bar(x=most_common_emoji['Emoji'], y=most_common_emoji['Count'])])
            fig.update_layout(
                xaxis_title='Words',
                yaxis_title='Count',
                xaxis=dict(
                    tickangle=0
                )
            )
            st.plotly_chart(fig)

        st.title('Yearly Timeline')
        year_list = helper.select_year(df)
        selected_year = st.selectbox('Select Year', year_list)
        col1, col2 = st.columns(2)
        if selected_year != 'None Selected':
            with col1:
                most_busy_months = helper.yearly_timeline(df, selected_year)
                st.dataframe(most_busy_months)

            with col2:
                fig = go.Figure(data=[go.Line(x=most_busy_months['Month'], y=most_busy_months['Message Count'])])
                fig.update_layout(
                    xaxis_title='Month',
                    yaxis_title='Message Count',
                    xaxis=dict(
                        tickangle=45
                    )
                )
                st.plotly_chart(fig)
        elif selected_year == 'None Selected':
            st.subheader('Please select a Year')

        st.title('Monthly Timeline')
        month_list = helper.select_month(df)
        year_list = helper.select_year(df)

        col1, col2 = st.columns(2)

        with col1:
                selected_month = st.selectbox('Select Month', month_list,key='month')

        with col2:
            selected_year = st.selectbox('Select Year', year_list,key='year')

        if selected_month != 'None Selected' and selected_year != 'None Selected':
            temp_df = helper.daily_timeline(df,selected_year,selected_month)
            col3, col4 = st.columns(2)
            with col3:
                st.dataframe(temp_df)
            with col4:
                fig = go.Figure(data=[go.Line(x=temp_df['Day'], y=temp_df['Message Count'])])
                fig.update_layout(
                    xaxis_title='Days',
                    yaxis_title='Message Count',
                    title = 'Monthly Timeline',
                    xaxis=dict(
                        tickangle=45
                    )
                )
                st.plotly_chart(fig)
        elif selected_month == 'None Selected' and selected_year != 'None Selected':
            st.subheader('Please select a Month')
        elif selected_month != 'None Selected' and selected_year == 'None Selected':
            st.subheader('Please select a Year')



    else:
        st.header('Click Analyze to see the Statistics')

else:
    st.header('Upload a File for Analysis')