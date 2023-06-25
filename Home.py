import streamlit as st
from PIL import Image

st.set_page_config(
    page_title = "Home",
    page_icon = "",
    layout = "wide"
)
    
# image_path = r'C:\Users\Edu_D\OneDrive\Documentos\edu\Data Formation\Repos\ftc_analisando_dados_com_pyhton\ciclo_6'
image = Image.open('logo1.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown( '# Curry Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.write( '#Curry Company Growth Dashboard' )

"""
    Growth Dashoboard foi constrído para acompanhar as metas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard:
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregadores:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
        - edu.deoli@gmail.com
"""
