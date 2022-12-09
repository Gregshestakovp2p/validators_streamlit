import streamlit as st
import rewards_penalties_exctractor
import datetime
import plotly.express as px


header=st.container()
operator=st.container()
dates=st.container()
download_result=st.container()



st.title('Validators performance exctractor')


operator_select=st.selectbox(
        "Please select operator",
        ["Blockscape","P2P.ORG - P2P Validator","DSRV","Stakefish - Lido","Staking Facilities","Allnodes","RockX","SkillZ","ChainLayer","BridgeTower","Chorus One","Figment","Simply Staking","InfStones","Everstake","Stakin","Stakely","HashQuark","Blockdaemon","Anyblock Analytics","ConsenSys Codefi","Certus One","CryptoManufaktur - Lido","Kukis Global","RockLogic GmbH","Nethermind - Lido","Sigma Prime - Lido","ChainSafe - Lido"]
    )


start_date=st.date_input(
     "Choose start date",
     datetime.date(2022, 8, 25))

end_date = st.date_input(
        "Choose end date",
        datetime.date(2022, 8, 29))


if st.button('Get info'):


    operator_data = rewards_penalties_exctractor.get_operator_performance(operator=operator_select, date_from=str(start_date), date_to=str(end_date))
    operator_csv=operator_data.to_csv(index=False).encode('utf-8')
    rewards=rewards_penalties_exctractor.get_rewards(operator_data)
    penalties=rewards_penalties_exctractor.get_penaltlies(operator_data)
    st.write(f'For period {operator_select} acquired {rewards:.2f} ETH in rewards ')
    st.write(f'For period {operator_select} acquired {penalties:.2f} ETH in penalties ')
    rewards_for_visulization=rewards_penalties_exctractor.df_for_chart(operator_data)
    fig = px.bar(rewards_for_visulization, x="date", y=["sumEstimatedRewards", "sumEstimatedPenalties"],
                 title="Rewards&Penalties daily")
    st.plotly_chart(fig, use_container_width=True)

    st.download_button(label='Download info',
                       data=operator_csv,
                       file_name=f'{operator_select} from {start_date} to {end_date}.csv',
                       mime='text/csv')






