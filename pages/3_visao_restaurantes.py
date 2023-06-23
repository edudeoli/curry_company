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
import numpy as np

st.set_page_config(page_title='Visão Restaurantes', page_icon='', layout='wide')

#_______________________________________________________________________
# Funçoes
#_______________________________________________________________________

def avg_std_time_on_traffic(df1):
        df_aux = ( df1.loc[:, ['City','Time_taken(min)', 'Road_traffic_density']]
                        .groupby(['City', 'Road_traffic_density'])
                        .agg({'Time_taken(min)': ['mean','std']}))
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()
        fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                            color='std_time', color_continuous_scale='RdBu',
                            color_continuous_midpoint=np.average(df_aux['std_time']))
        return fig

def avg_time(df1):
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['distance'] = ( df1.loc[:, ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']].apply(lambda x: 
                                            haversine((x['Restaurant_latitude'], 
                                                        x['Restaurant_longitude']), (
                                                        x['Delivery_location_latitude'], 
                                                        x['Delivery_location_longitude'])), axis=1))
    avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
    fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])     
    return fig

def avg_time_std_time_graph(df1):
    df_aux = df1.loc[:, ['City','Time_taken(min)']].groupby('City').agg({'Time_taken(min)': ['mean','std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')
    return fig

def avg_std_time_delivery(df1, op, festival):
        """ 
                    Esta funcao calcula o tempo édio e o desvio padrao do tempo de entrega.
                    Parâmetros:
                        input:
                            -df: Daframe com os dados necessarios para o calculo
                            -op: Tipo de operacao que precisa ser calculado
                                'avg_time': Calcula o tempo médio
                                'std_time': Calcula o desvio padrao de tempo.
                        Output:
                            -df: Dataframe com 2 colunas e 1 linhas:
        """              
        cols = ['Time_taken(min)', 'Festival']
        df_aux = df1.loc[:, cols].groupby(['Festival']).agg({'Time_taken(min)': ['mean','std']})
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()
        linhas_selecionadas = df_aux['Festival'] == festival
        #df_aux = np.round(df_aux.loc[linhas_selecionadas, op], 2)
        df_aux['rounded_' + op] = np.round(df_aux.loc[linhas_selecionadas, op], 2)
        return df_aux

def distance(df1):
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        # criar a coluna 'distance'
        df1['distance'] = df1.loc[:, cols].apply(lambda x:
                                    haversine( 
                                    (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis = 1)
        avg_distance = np.round(df1['distance'].mean(), 2)
        return avg_distance

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

st.header('Marketplace - Visão Restaurantes')


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
tab1, tab2, tab3 = st.tabs(['Overall', 'Tempo', 'Distância'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Cad. Entregadores Únicos', delivery_unique)
                                  
        with col2:
            avg_distance = distance(df1)
            col2.metric('Distância média das entregas', avg_distance)
            
        with col3:
            df_aux = avg_std_time_delivery( df1, 'avg_time', 'Yes')
            col3.metric('AVG entregas com Festival', df_aux)
            
        
        st.markdown("""---""")
        col4, col5, col6 = st.columns(3)
        with col4:
            df_aux = avg_std_time_delivery( df1, 'std_time', 'Yes' )
            col4.metric('STD entregas com Festival', df_aux)
            
            
        with col5:
            df_aux = avg_std_time_delivery( df1, 'avg_time', 'No' )
            col5.metric('AVG entregas sem Festival', df_aux)
            
            
        with col6:
            df_aux = avg_std_time_delivery( df1, 'std_time', 'No' )
            col6.metric('STD entregas sem Festival', df_aux)
        
with tab2:
    with st.container():
            st.markdown('#### Tempo Médio de Entrega por Cidade')
            fig = avg_time_std_time_graph(df1)
            st.plotly_chart(fig)
            
            
    with st.container():
            st.markdown("""___""")
            st.markdown('#### Distribuição do Tempo')
            fig = avg_time(df1)
            st.plotly_chart(fig)
               
    with st.container():
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig)
        

with tab3:
    with st.container():
        st.markdown("""___""")
        st.title('Distância')
        st.markdown('##### Ditribuição da Distância')
        df_aux = df1.loc[:, ['City','Time_taken(min)', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean','std']})
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()
        st.dataframe(df_aux)
