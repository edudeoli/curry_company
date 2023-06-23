# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import datetime

# Bibliotecas necessárias
import pandas as pd
import streamlit as st
import folium
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadores', page_icon='', layout='wide')

#_______________________________________________________________________
# Funçoes
#_______________________________________________________________________

def top_delivers(df1, top_asc):
    df2 = ( df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                .groupby(['City', 'Delivery_person_ID'])
                .max().sort_values(['City', 'Time_taken(min)'], ascending = top_asc) ).reset_index()

    df_aux1 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux2 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux3 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat( [df_aux1, df_aux2, df_aux3] ).reset_index( drop = True)
    return df3


def clean_code(df1):
    """ Está função tem a responsabilidade de limpar o dataframe
        
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaçoes das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica)
        
        Input: Dataframe
        Output: Dataframe
    """
    # 1. convertendo a coluna Age de string para numero inteiro (int)
    linhas_selecionadas = df1['Delivery_person_Age'] != "NaN "
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    linhas_selecionadas = df1['Road_traffic_density'] != "NaN "
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['City'] != "NaN "
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['Festival'] != "NaN "
    df1 = df1.loc[linhas_selecionadas, :].copy()

    # 2. convertendo a coluna Ratings de string para decimal (float)
    df1["Delivery_person_Ratings"] = df1['Delivery_person_Ratings'].astype(float)

    # 3. convertendo a coluna Order_date de string para data 
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format = '%d-%m-%Y')

    # 4. Convertendo multiple_deliveries de texto para INT
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1["multiple_deliveries"] = df1["multiple_deliveries"].astype(int)

    # 5 - Remove as linhas da coluna multiple_deliveries que tenham o conteudo 'NaN '
    # linhas_vazias = df['multiple_deliveries'] != 'NaN '
    # df = df.loc[linhas_vazias, :]
    # df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)

    # 5. Removendo espaços dentro das strings/object/texto
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    # 6. Limpando a coluna de Time_taken(min)
    df1.loc[:,'Time_taken(min)'] = df1.loc[:,'Time_taken(min)'].apply( lambda x: x.split( '(min)')[1])
    df1.loc[:,'Time_taken(min)'] = df1.loc[:,'Time_taken(min)'].astype(int)

    return df1

#___________________________________Início da Estrutura Lógica do Código_____________________________________
#__________________________________
# Import Dataset
#__________________________________

df = pd.read_csv( 'dataset/train.csv' )

#_________________________________
# Limpando dados
#_________________________________

df1 = clean_code(df)


#==================================================================
# BARRA LATERAL
#==================================================================

st.header('Marketplace - Visão Entregadores')

# image_path = 'C:\\Users\\Edu_D\\OneDrive\\Documentos\\edu\\Data Formation\\Repos\\ftc_analisando_dados_com_pyhton\\ciclo_6\\logo.png'
image = Image.open( 'logo.png' )
st.sidebar.image( image, width=120 )

st.sidebar.markdown( '# Curry Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )


st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value = datetime.datetime( 2022, 4, 6 ),
    min_value = datetime.datetime( 2022, 2, 11 ),
    max_value = datetime.datetime( 2022, 4, 6 ),
    format = 'DD-MM-YYYY' )

st.sidebar.markdown( """___""" )
    
traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'] )   

st.sidebar.markdown( """___""" )
st.sidebar.markdown( '### Powered by Comunidade DS' )


# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]


#==================================================================
# LAYOUT NO STREAMLIT 
#==================================================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Avaliações', 'Velocidade'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns( 4, gap = 'large')
        with col1:
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)
            
        with col2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
            
        with col3:
            melhor_condicao = df1.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor_condicao)
        
        with col4:
            pior_condicao = df1.loc[:,'Vehicle_condition'].min()
            col4.metric('Pior condição', pior_condicao)
            
with tab2:
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação média por Entregador')
            df_avg_ratings_per_deliver = ( df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                                              .groupby('Delivery_person_ID')
                                              .mean()
                                              .reset_index() )
            st.dataframe( df_avg_ratings_per_deliver )
                 
        with col2:
            st.markdown('##### Avaliação média por Trânsito')
            df_avg_std_rating_by_traffic = ( df1.loc[:, ['Road_traffic_density', 'Delivery_person_Ratings']]
                                                .groupby('Road_traffic_density')
                                                .agg( {'Delivery_person_Ratings': ['mean', 'std']}) )

            df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
            st.dataframe(df_avg_std_rating_by_traffic)
                
                
                
            st.markdown('##### Avaliação média por Clima')
            df_avg_std_rating_by_weather = ( df1.loc[:, ['Weatherconditions', 'Delivery_person_Ratings']]
                            .groupby('Weatherconditions')
                            .agg( {'Delivery_person_Ratings': ['mean', 'std']}) )


            df_avg_std_rating_by_weather.columns = ['delivery_mean', 'delivery_std']
            df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()
            st.dataframe(df_avg_std_rating_by_weather)
                    
with tab3:
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')
        
        col1, col2 = st.columns(2)
        with col1:    
            st.markdown('##### Top Entregadores Mais Rápidos')
            df3 = top_delivers(df1, top_asc = True)
            st.dataframe(df3)
            
        with col2:
            st.markdown('##### Top Entregadores Mais Lentos')
            df3 = top_delivers(df1, top_asc = False)
            st.dataframe(df3)
            

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
