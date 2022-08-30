import requests
import datetime
import pandas as pd


def get_last_available_day() -> int:
    '''Retrun last available day for data fetching'''
    responce = requests.get('https://api.rated.network/v0/eth/validators/1/effectiveness?size=10')
    return responce.json()['data'][0]['day']



def get_validators_info(address_list, date_from, date_to) -> list:
    '''Return list of dicts of with all validators data passed based on
    list of indices, pubkeys or deposit addresses,'''
    validators_data_index_pubkeys = []
    validators_data_deposit = []
    dates = convert_dates_to_int(date_from, date_to)
    if not isinstance(address_list, pd.DataFrame):
        address_list = pd.DataFrame(address_list, columns=['address'])
    print(len(address_list))

    for validator_number in range(len(address_list)):
        validator_info = address_list.iloc[validator_number][0]
        validator_type = get_type(validator_info)

        if validator_type == 'pubkey':
            pubkey_data = get_validator_by_pubkey(address_list.iloc[validator_number][0], size=dates['size'],
                                                  from_day=dates['from'])
            validators_data_index_pubkeys += pubkey_data
            print(f'{validator_number + 1} out of {len(address_list)} done')

        if validator_type == 'index':
            index_data = get_validator_by_index(address_list.iloc[validator_number][0], size=dates['size'],
                                                from_day=dates['from'])
            validators_data_index_pubkeys += index_data
            print(f'{validator_number + 1} out of {len(address_list)} done')

        if validator_type == 'deposit':
            deposit_data = get_validator_by_deposit_address(address_list.iloc[validator_number][0], size=dates['size'],
                                                            from_day=dates['from'])
            validators_data_deposit += deposit_data
            print(f'{validator_number + 1} out of {len(address_list)} done')

    return validators_data_index_pubkeys, validators_data_deposit


def create_date_df():
    '''Create list of dates with indexes starting from genesis up to current date '''
    try:
        daterange = pd.date_range('2020-12-01', datetime.date.today() - datetime.timedelta(days=1))
        index_list = list(range(0, get_last_available_day() + 1))
        return daterange.to_series(index=index_list).reset_index(level=0).rename(columns={'index': 'day', 0: 'date'})
    except ValueError:
        daterange = pd.date_range('2020-12-01', datetime.date.today() - datetime.timedelta(days=2))
        index_list = list(range(0, get_last_available_day() + 1))
        return daterange.to_series(index=index_list).reset_index(level=0).rename(columns={'index': 'day', 0: 'date'})


def create_df_with_dates(validators_info: list):
    '''Convert validators info into dataframe and add dates to it'''
    validators_info_df = pd.DataFrame(validators_info)
    dates_df = create_date_df()
    validators_info_df = validators_info_df.merge(dates_df, how='inner', on='day')
    validators_info_df
    return validators_info_df


def get_validators_info_dataframe(address_list, date_from, date_to, csv: str = ''):
    '''Take address list and their type as parametr and return DataFrame with all validators info with dates
      if optional parametr csv is passed also save it in csv file'''

    address_df = pd.read_csv(address_list)
    validator_info = get_validators_info(address_df, date_from, date_to)
    for type in range(len(validator_info)):
        try:
            validator_info_df = create_df_with_dates(validator_info[type])
            if csv and type == 0:
                name = csv + "_index_pubkeys.csv"
                validator_info_df.to_csv(name, sep=',', encoding='utf-8', index=False)
            elif csv and type == 1:
                name = csv + "_deposits.csv"
                validator_info_df.to_csv(name, sep=',', encoding='utf-8', index=False)
        except KeyError:
            continue


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