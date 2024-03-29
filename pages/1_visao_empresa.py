
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

st.set_page_config(page_title='Visão Empresa', page_icon='', layout='wide')

#_______________________________________________________________________
# Funçoes
#_______________________________________________________________________

def order_metric(df1):
    # Order Metric
    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
    # Desenhar o gráico
    fig = px.bar(df_aux, x = 'Order_Date', y = 'ID')
    return fig

def traffic_order_share(df1):
    df_aux = (df1.loc[:, ['ID', 'Road_traffic_density']]
                 .groupby('Road_traffic_density')
                 .count()
                 .reset_index())
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN", :]
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    fig = px.pie(df_aux, values = 'entregas_perc', names = 'Road_traffic_density')
    return fig

def traffic_order_density(df1):
    columns = ['ID', 'City', 'Road_traffic_density']
    df_aux = (df.loc[:, columns]
                .groupby( ['City', 'Road_traffic_density'] )
                .count()
                .reset_index())
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
     # gráfico
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig

def order_by_week(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( "%U" )
    df_aux = (df1.loc[:, ['ID', 'week_of_year']]
                .groupby( 'week_of_year' )
                .count()
                .reset_index())
    fig = px.line( df_aux, x='week_of_year', y='ID' )
    return fig

def order_share_by_week(df1):
    df_aux1 = (df1.loc[:, ['ID', 'week_of_year']]
                  .groupby( 'week_of_year' )
                  .count()
                  .reset_index())
    df_aux2 = (df1.loc[:, ['Delivery_person_ID', 'week_of_year']]
                  .groupby( 'week_of_year')
                  .nunique()
                  .reset_index())
    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )
    return fig

def country_maps(df1):
    cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df_aux = (df.loc[:, cols]
                .groupby(['City', 'Road_traffic_density'])
                .median()
                .reset_index())
    
    map = folium.Map(zoom_start=11)
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'], 
                        location_info['Delivery_location_longitude']], 
                         popup=location_info[['City','Road_traffic_density']]).add_to(map)

    folium_static( map, width=1024, height=600 )
        
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

st.header('Marketplace - Visão Empresa')


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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        fig = order_metric(df1)
        st.markdown('# Orders by Day')
        st.plotly_chart( fig, use_container_width = True)
        

    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            fig = traffic_order_share(df1)
            st.markdown('# Traffic Order Share')
            st.plotly_chart(fig, use_container_width = True)
              
            
        with col2:
            fig = traffic_order_density(df1)
            st.markdown('# Traffic Order Density')
            st.plotly_chart(fig, use_container_width = True)
            

with tab2:
    with st.container():
        fig = order_by_week(df1)
        st.markdown('# Order by Week')
        st.plotly_chart(fig, use_container_width = True)
        

        
        
    with st.container():
        fig = order_share_by_week(df1)
        st.markdown('# Order Share by Week')
        st.plotly_chart(fig, use_container_width = True)
        

        

with tab3:
    st.markdown('# Country Maps')
    country_maps(df1)
    
 
