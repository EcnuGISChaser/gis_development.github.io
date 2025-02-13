# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 11:25:48 2023

@author: jpwu
"""

import geopandas as gpd
import folium
from folium import Marker,CircleMarker,Circle
from folium.features import GeoJson
from folium import FeatureGroup
from folium.plugins import MiniMap
import streamlit as st
from streamlit_folium import st_folium
import time
st.title("天目山POI点查询")

@st.cache_data  
def load_data(url):
    gdf = gpd.read_file(url, driver='GeoJSON')
    return gdf

url = "https://EcnuGISChaser.github.io/gis_development/data/tms_POIs.geojson"
#url = r"C:\data\tms\tms_POIs.geojson"
gdf = load_data(url)


#获取所有POI点的名称，用于在下拉列表框中显示
#streamlit界面
with st.form("my_form"):
    selected_POI_name = st.selectbox('选择一个POI',gdf["NAME"])
    submit = st.form_submit_button('查询')

minx = min(gdf.bounds["minx"])
miny = min(gdf.bounds["miny"])
maxx = max(gdf.bounds["maxx"])
maxy = max(gdf.bounds["maxy"]) 

if 'POI_name' not in st.session_state:
    st.session_state['POI_name'] = gdf["NAME"][0]

if submit:
    st.session_state['POI_name'] = selected_POI_name

session_POI_name = st.session_state['POI_name']
#st.text(session_POI_name)  

m = folium.Map(tiles=None)
m.fit_bounds([(miny,minx),(maxy,maxx)])

folium.TileLayer(tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
                name="Carto地图",
                attr="Carto地图",
                control_scale=True).add_to(m)

folium.TileLayer(tiles="http://webrd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}",
                name="高德地图",
                attr="高德地图",
                control_scale=True).add_to(m)

folium.TileLayer(tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.png",
                name="Esri全球影像",
                attr="Esri全球影像",
                control_scale=True).add_to(m)

icon = folium.Icon(color="red",prefix="fa",icon="store",icon_color="white")

POI_layer = FeatureGroup(name='POI')
for i in range(len(gdf)):
    POI = gdf.iloc[i]
    POI_name = POI["NAME"]
    x = POI.geometry.x
    y = POI.geometry.y
    text = POI["text"]
    img_src = POI["photo_url"]
    html = f"""<h4>{POI_name}</h4>
               <h6>{text}</h6>
               <img src={img_src}>
            """
    folium.Marker(location=[y,x],
                popup=html).add_to(POI_layer)


POI_layer.add_to(m)
folium.LayerControl().add_to(m)

fg = folium.FeatureGroup(name="Markers")
point = gdf[gdf["NAME"]==session_POI_name].iloc[0]["geometry"]
text = gdf[gdf["NAME"]==session_POI_name].iloc[0]["text"]
img_src = gdf[gdf["NAME"]==session_POI_name].iloc[0]["photo_url"]
html = f"""<h4>{selected_POI_name}</h4>
           <h6>{text}</h6>
           <img src={img_src}>
        """
folium.Marker(location=[point.y,point.x],icon=icon,popup=html).add_to(fg)
st_folium(m,center=[point.y, point.x],feature_group_to_add=fg,
    width=700, height=500)