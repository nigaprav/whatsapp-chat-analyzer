import re
import pandas as pd


def preprocessor(data):
    import re

    # Regex to capture 3 groups: datetime, user, message
    pattern = r'(\d{1,2}/\d{1,2}/\d{2}, \d{1,2}:\d{2}\s?[ap]m) - ([^:]+): (.+)'

    matches = re.findall(pattern, data)

    datetime = []
    user = []
    message = []

    for dt, usr, msg in matches:
        datetime.append(dt)
        user.append(usr)
        message.append(msg)

    df = pd.DataFrame({'Datetime': datetime, 'User': user, 'Message': message})
    df['Datetime'] = df['Datetime'].str.replace('\u202f', ' ', regex=False)
    df['Datetime'] = pd.to_datetime(df['Datetime'], format='%d/%m/%y, %I:%M %p')
    df['Year'] = df['Datetime'].dt.year
    df['Month'] = df['Datetime'].dt.month_name()
    df['Day'] = df['Datetime'].dt.day
    df['Hour'] = df['Datetime'].dt.hour
    df['Minute'] = df['Datetime'].dt.minute
    df['Day Name'] = df['Datetime'].dt.day_name()
    period = []
    for i in df['Hour']:
        if i == 23:
            period.append(str(i) + '-' + str(00))
        elif i == 0:
            period.append(str(i) + '-' + str(i + 1))
        else:
            period.append(str(i) + '-' + str(i + 1))
    df['Period'] = period

    return df

