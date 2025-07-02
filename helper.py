import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from matplotlib import pyplot as plt
from wordcloud import WordCloud
from urlextract import URLExtract
import os
import emoji
from collections import Counter

extractor = URLExtract()

def select_user(df):
    user_list = df['User'].unique().tolist()
    user_list.insert(0,'Overall')
    return user_list

def select_year(df):
    year_list = df['Year'].unique().tolist()
    year_list.insert(0,'None Selected')
    return year_list

def select_month(df):
    month_list = df['Month'].unique().tolist()
    month_list.insert(0,'None Selected')
    return month_list

def fetch_stats(df, selected_user):
    word_count =[]
    temp_df = df[df['User'] == selected_user]
    if selected_user == 'Overall':
        total = df.shape[0]
        for i in df['Message']:
            word_count.extend(i.split())
        total_media = df[df['Message']=='<Media omitted>'].shape[0]
        total_links_shared = []
        for i in df['Message']:
            urls = extractor.find_urls(i)
            total_links_shared.extend(urls)
        total_no_of_links = len(total_links_shared)

    else:
        total = temp_df.shape[0]
        word_count = []
        for i in temp_df['Message']:
            word_count.extend(i.split())
        total_media = temp_df[temp_df['Message'] == '<Media omitted>'].shape[0]
        total_links_shared = []
        for i in temp_df['Message']:
            urls = extractor.find_urls(i)
            total_links_shared.extend(urls)
        total_no_of_links = len(total_links_shared)


    return total, len(word_count), total_media, total_no_of_links

def busy_users(df):
    temp_df = df['User'].value_counts() / df.shape[0] * 100
    temp_df = temp_df.reset_index()
    temp_df.rename(columns={'count': 'Contribution (%)'}, inplace=True)
    return temp_df

def busy_month(df,selected_user):
    df_copy = df.copy()
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    if selected_user == 'Overall':
        final_df = df_copy['Month'].value_counts().reset_index()
    elif selected_user != 'Overall' :
        df_copy = df_copy[df_copy['User']== selected_user]
    final_df = df_copy['Month'].value_counts().reset_index()
    final_df.columns = ['Month', 'count']
    final_df['Month'] = pd.Categorical(final_df['Month'], month_order,ordered=True)
    final_df.sort_values(by='Month', ascending=True, inplace=True)
    return final_df

def busy_week(df,selected_user):
    df_copy = df.copy()
    df_copy['Day Name'] = df_copy['Datetime'].dt.day_name()
    day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    if selected_user == 'Overall':
        final_df = df_copy['Day Name'].value_counts().reset_index()
    elif selected_user != 'Overall' :
        df_copy = df_copy[df_copy['User']==selected_user]
    final_df = df_copy['Day Name'].value_counts().reset_index()
    final_df.columns = ['Day Name', 'count']
    final_df['Day Name'] = pd.Categorical(final_df['Day Name'], day_order,ordered=True)
    final_df.sort_values(by='Day Name', ascending=True, inplace=True)
    return final_df

import re
from collections import Counter
def most_used_words(df, selected_user):
    from collections import Counter
    most_commonly_used_words =[]
    stopwords_path = os.path.join(os.path.dirname(__file__), 'stop_hinglish.txt')
    temp_df = df[df['User'] != 'group notification']
    temp_df = temp_df[temp_df['Message'] != '<Media omitted>']
    temp_df = temp_df[~temp_df['Message'].str.contains(r'https?://', na=False)]
    with open(stopwords_path, 'r', encoding='utf-8') as f:
        stop_words = f.read()
    if selected_user != 'Overall':
        temp_df = temp_df[temp_df['User'] == selected_user]
        popular_words = []
        for message in temp_df['Message']:
            words = re.findall(r'\b[a-zA-Z]+\b', message.lower())
            for word in words:
                if word not in stop_words:
                    popular_words.append(word)

        most_commonly_used_words = Counter(popular_words).most_common(20)
    elif selected_user == 'Overall':
        popular_words = []
        for message in temp_df['Message']:
            words = re.findall(r'\b[a-zA-Z]+\b', message.lower())
            for word in words:
                if word not in stop_words:
                    popular_words.append(word)
        from collections import Counter
        most_commonly_used_words = Counter(popular_words).most_common(20)
    final_df = pd.DataFrame(most_commonly_used_words, columns=['Word', 'Count']).sort_values('Count', ascending=False).head(20)
    final_df['Rank'] = range(1,len(final_df)+1)
    final_df.set_index('Rank', inplace=True)

    return final_df

def word_cloud(df, selected_user):
    temp_df = most_used_words(df, selected_user)
    w_cloud = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    wc_df = w_cloud.generate(temp_df['Word'].str.cat(sep=' '))

    return wc_df

def emoji_count(df,selected_user):
    emoji_list = []
    for i in df['Message']:
        for c in i:
            if c in emoji.EMOJI_DATA:
                emoji_list.extend(c)
    count = Counter(emoji_list).most_common()
    emoji_df = pd.DataFrame(count, columns=['Emoji', 'Count']).head(20)
    emoji_df['Rank'] = range(1,len(emoji_df)+1)
    emoji_df.set_index('Rank', inplace=True)

    return emoji_df

def yearly_timeline(df,selected_year):
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']

    temp_df = df[df['Year']==selected_year]
    temp_df = temp_df['Month'].value_counts().reset_index()
    temp_df.rename({'count':'Message Count'}, axis=1, inplace=True)
    temp_df['Month'] = pd.Categorical(temp_df['Month'], categories=month_order, ordered=True)
    temp_df.sort_values('Month', inplace=True)
    return temp_df

def daily_timeline(df,selected_year,selected_month):
    temp_df = df[df['Year']==selected_year]
    temp_df = temp_df[temp_df['Month'] == selected_month]
    monthly_df = temp_df['Day'].value_counts().reset_index()
    monthly_df.rename({'count': 'Message Count'}, axis=1, inplace=True)
    monthly_df.sort_values(by='Day', ascending=True, inplace=True)
    monthly_df.reset_index(drop=True, inplace=True)

    return monthly_df