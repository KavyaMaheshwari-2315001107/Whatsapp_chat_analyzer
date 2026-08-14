import re
import pandas as pd

def preprocess(data):
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?:\s?[APap][Mm])?\s-\s)'

    split_data = re.split(pattern, data)

    messages = []
    dates = []

    for i in range(1, len(split_data), 2):
        dates.append(split_data[i])
        messages.append(split_data[i + 1])

    df = pd.DataFrame({
        'message_date': dates,
        'user_message': messages
    })

    # Remove trailing " - "
    df['message_date'] = df['message_date'].str.replace(r'\s-\s$', '', regex=True)

    # Convert to datetime
    df['message_date'] = pd.to_datetime(
        df['message_date'],
        dayfirst=True,
        errors='coerce'
    )

    # Remove invalid rows
    df = df.dropna(subset=['message_date'])

    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    final_messages = []

    for message in df['user_message']:
        entry = re.split(r'([^:]+):\s', message, maxsplit=1)

        if len(entry) >= 3:
            users.append(entry[1].strip())
            final_messages.append(entry[2].strip())
        else:
            users.append('group_notification')
            final_messages.append(entry[0].strip())

    df['user'] = users
    df['message'] = final_messages

    df.drop(columns=['user_message'], inplace=True)

    # Date features
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []

    for hour in df['hour']:
        if hour == 23:
            period.append(f'{hour}-00')
        elif hour == 0:
            period.append('00-1')
        else:
            period.append(f'{hour}-{hour+1}')

    df['period'] = period

    return df