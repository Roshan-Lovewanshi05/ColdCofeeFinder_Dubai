import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from helper.utils import calculate_distance,is_open_spot
st.set_page_config(layout="wide")
df = pd.read_csv("datasets/dubai_cold_coffee_spots_clean.csv")
df_areas = pd.read_csv("./datasets/dubai_areas_with_label.csv")

st.title("☕ Dubai Cold Coffee Finder")

st.write("Find the nearest cold coffee spots around you in Dubai.")
st.write("Explore cafes, carts, and trucks based on distance, rating, and availability.")

st.header("📍 Select Your Area")
area_labels = list(df_areas["area_label"])

selected_area = st.selectbox("Choose your area",area_labels)

with st.sidebar:
    st.subheader("🔍 Search & Filters")
    spot_name = st.text_input("Search by name",placeholder="Arctic Brew")
    if spot_name:
        df = df[df["name"]==spot_name]
    st.divider()
    st.subheader("⚙️ Filters")
    unique_type = list(df["type"].unique())
    unique_type.insert(0,"All")
    select_type = st.selectbox("Spot type",unique_type)
    max_dis = st.slider("Max Distance (km)",min_value=1,max_value=20,value=5)
    min_rating = st.slider("Min Rating",min_value=1.0,max_value=5.0,value=2.5,step=.1)

    is_open = st.checkbox("only open spots",value=False)

    sort_by = st.radio("Sort by",["Distance","Rating"])

values = df_areas[df_areas["area_label"]==selected_area][["lat","lng"]].iloc[0]
user_location = tuple(values)

if select_type != "All":
    df = df[df["type"] == select_type]

def get_distance(row):
    lat = row['lat']
    lng = row['lng']
    spot_location = (lat,lng)
    return calculate_distance(user_location,spot_location)

df['distance'] = df.apply(get_distance,axis=1)
df['is_open_spot'] = df.apply(is_open_spot,axis=1)

original_df = df.copy()


df = df[df['distance'] <= max_dis]
df = df[df['rating'] >= min_rating ]
if is_open:
   df = df[df['is_open_spot'] == 'Open']

if sort_by == "Distance":
   
   df = df.sort_values(by="distance")
else:
    
    df = df.sort_values(by="rating",ascending=False)


tab1,tab2,tab3=st.tabs(["🗺️ Nearby Spots","📊 Analytics","🏆 Leaderboard"])



with tab1:
    number = len(df)
    st.subheader(f"{number} spot(s) found")
    dubai_map = folium.Map(location=user_location,zoom_start=12)

    icon = folium.Icon(color="orange",icon="user",prefix='fa')
    marker = folium.Marker(user_location,icon=icon,tooltip=f"selected area:{selected_area}")
    marker.add_to(dubai_map)

    for da in df.iterrows():
      
      row = da[1]
      
      lat = row['lat']
      lng = row['lng']
      spot_type = row['type']
      name = row["name"]
      if_open = row["is_open_spot"]
      spot_location = (lat,lng)


      icon = folium.Icon(color="green",icon="coffee",prefix='fa') if if_open == "Open" else folium.Icon(color="red",icon="coffee",prefix='fa') 
      marker = folium.Marker(spot_location,icon=icon,tooltip=f"{selected_area}")
      marker.add_to(dubai_map)



    st_folium(dubai_map,height=350,use_container_width=True)
    for i in range(0,len(df),2):
         rows = df.iloc[i:i+2]
         cols = st.columns(2)
         for j in range(len(rows)):
              row = rows.iloc[j]
              name = row["name"]
              type = row["type"]
              status = row["is_open_spot"]
              dis = row["distance"]
              open_time = row["opening_time"]
              close_time = row["closing_time"]
              rating = row["rating"]
              col = cols[j]
              with col:
                   with st.container():
                        if type=="cafe":
                             st.subheader(f"🏠 {name}")
                        elif type=="cart":
                             st.subheader(f"🛒  {name}")
                        else:
                              st.subheader(f"🚚  {name}")
                             
                        
                        c1,c2 = st.columns(2)
                        c1.markdown(f"**Type:** {type}")
                        if status == "Open":
                             icon = "🟢"
                        else:
                             icon = "🔴"
                                                    
                                                
                        
                        c2.markdown(f"**Status:** {icon} {status}")
                             
                        c1.markdown(f"**Distance:** {dis}km")
                        c2.markdown(f"**Rating:**{"⭐" * int(rating)} {rating}")
                        st.caption(f"🕐 {open_time}:{close_time}")
                        

                        

                        

    


with tab2:
    st.header("📈 Summary Stats")
    c1,c2,c3,c4 = st.columns(4)
    with c1:
          st.metric("Total spots",len(original_df))
    with c2:
             avg_rating = original_df['rating'].mean().round(2)
             st.metric("Average Rating",avg_rating)
    
    with c3:
             total_open_spots = len(original_df[original_df['is_open_spot'] == 'Open'])
             st.metric("Open Spots",f"{total_open_spots}/{len(original_df)}")
    
    with c4:
             st.metric("Nearest Spot",f"{original_df['distance'].min()} km")
    st.subheader("Spot Count By Type")
    data = original_df['type'].value_counts()
    st.bar_chart(data,color='#ffaa00')
    
    st.subheader("Average Rating by Type")
    data = original_df.groupby('type')['rating'].mean().round(2)
    st.bar_chart(data,color="#1716149a")


with tab3:
       st.subheader("Top 10 rated spots")
    
       top_10_rated_spots = original_df.sort_values(by='rating',ascending=False,ignore_index=True).head(10)
       top_10_rated_spots.index = top_10_rated_spots.index + 1
       st.dataframe(top_10_rated_spots[["name","type","rating","is_open_spot","distance"]])
    
       st.subheader("Nereast 10 spots")
    
       nearst_10_rated_spots = original_df.sort_values(by='rating').head(10)
       st.dataframe(nearst_10_rated_spots[["name","type","rating","is_open_spot","distance"]],hide_index=True)
       
    


