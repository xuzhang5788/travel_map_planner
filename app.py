import streamlit as st
import googlemaps
import folium
from streamlit_folium import st_folium

# 1. 初始化 Google Maps 客户端
# 建议在部署时将 API Key 存入 Streamlit 的 Secrets 中
API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"] if "GOOGLE_MAPS_API_KEY" in st.secrets else "你的API_KEY"
gmaps = googlemaps.Client(key=API_KEY)

st.title("🗺️ 智能景点规划助手")

# 2. 输入景点
addresses_input = st.text_area("请输入景点地址（每行一个）", height=150, 
                             placeholder="例如：\nEiffel Tower\nLouvre Museum\nArc de Triomphe")

if st.button("开始规划路径"):
    addresses = [a.strip() for a in addresses_input.split('\n') if a.strip()]
    
    if len(addresses) < 2:
        st.error("请至少输入两个地址（起点和终点）")
    else:
        # 3. 路径规划与优化
        # optimize_waypoints=True 会自动寻找最优访问顺序
        directions_result = gmaps.directions(
            origin=addresses[0],
            destination=addresses[-1],
            waypoints=addresses[1:-1],
            optimize_waypoints=True,
            mode="driving"
        )

        if directions_result:
            route = directions_result[0]
            # 获取优化后的顺序
            order = route['waypoint_order']
            st.success("路径优化完成！")

            # 4. 地图显示
            # 创建 Folium 地图，初始点设为起点坐标
            start_coord = route['legs'][0]['start_location']
            m = folium.Map(location=[start_coord['lat'], start_coord['lng']], zoom_start=13)

            # 遍历路径段并在地图上打星标
            for i, leg in enumerate(route['legs']):
                loc = leg['start_location']
                # 标记景点（使用星号图标）
                folium.Marker(
                    location=[loc['lat'], loc['lng']],
                    popup=f"第 {i+1} 站: {leg['start_address']}",
                    icon=folium.Icon(color="orange", icon="star", prefix="fa")
                ).add_to(m)

            # 最后一站
            end_loc = route['legs'][-1]['end_location']
            folium.Marker(
                location=[end_loc['lat'], end_loc['lng']],
                popup=f"终点: {route['legs'][-1]['end_address']}",
                icon=folium.Icon(color="red", icon="star", prefix="fa")
            ).add_to(m)

            # 渲染地图
            st_folium(m, width=700, height=500)
        else:
            st.warning("无法找到路径，请检查地址是否准确。")
