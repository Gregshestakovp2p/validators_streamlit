import requests
import datetime
import pandas as pd


def get_last_available_day() -> int:
    '''Retrun last available day for data fetching'''
    responce = requests.get('https://api.rated.network/v0/eth/validators/1/effectiveness?size=10')
    return responce.json()['data'][0]['day']



def create_date_df():
    '''Create list of dates with indexes starting from genesis up to current date '''
    daterange = pd.date_range('2020-12-01', datetime.date.today() - datetime.timedelta(days=1))
    index_list = list(range(0, len(daterange)))
    return daterange.to_series(index=index_list).reset_index(level=0).rename(columns={'index': 'day', 0: 'date'})


def create_df_with_dates(validators_info: list):
    '''Convert validators info into dataframe and add dates to it'''
    validators_info_df = pd.DataFrame(validators_info)
    dates_df = create_date_df()
    validators_info_df = validators_info_df.merge(dates_df, how='inner', on='day')
    validators_info_df
    return validators_info_df


def get_operator_performance(operator, date_from, date_to):
    dates = convert_dates_to_int(date_from, date_to)
    operator_data = get_operator_by_name(operator, size=dates['size'], from_day=dates['from'])
    operator_df = create_df_with_dates(operator_data)

    return operator_df


def get_operator_by_name(operator: str, size: int, from_day: int) -> list:
    '''Return list of dicts with operator info in certain date range'''
    link = f'https://api.rated.network/v0/eth/operators/{operator}/effectiveness?from={from_day}&size={size}'
    responce = requests.get(link)
    return responce.json()['data']


def convert_dates_to_int(date_from, date_to):
    date_df = create_date_df()
    print(date_df)
    from_to_dict = {}

    from_to_dict['from'] = date_df[date_df['date'] == date_to].iloc[0, 0]
    from_to_dict['size'] = (date_df[date_df['date'] == date_to].iloc[0, 0] - date_df[date_df['date'] == date_from].iloc[
        0, 0]) + 1
    return from_to_dict

def get_rewards(result_df):
  return result_df['sumEstimatedRewards'].sum()*10**(-9)

def get_penaltlies(result_df):
  return result_df['sumEstimatedPenalties'].sum()*10**(-9)*(-1)

def df_for_chart(result_df):
  visulize_df=result_df[['date','sumEstimatedRewards', 'sumEstimatedPenalties']]
  visulize_df['sumEstimatedRewards']=visulize_df['sumEstimatedRewards']*10**(-9)
  visulize_df['sumEstimatedPenalties']=visulize_df['sumEstimatedPenalties']*10**(-9)*(-1)
  return visulize_df