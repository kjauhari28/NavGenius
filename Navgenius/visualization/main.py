import inspect
import colorsys
import textwrap
import streamlit as st
import pandas as pd
import pydeck as pdk

# Mumbai-themed colors
colors = [
    [255, 87, 51],    # Gateway of India Orange
    [0, 150, 136],    # Marine Drive Green
    [63, 81, 181],    # Mumbai Blue
    [233, 30, 99],    # Local Train Pink
    [156, 39, 176],   # Taxi Purple
    [255, 193, 7],    # Auto Rickshaw Yellow
    [76, 175, 80],    # BEST Bus Green
    [33, 150, 243],   # Metro Blue
    [244, 67, 54],    # Monsoon Red
    [121, 85, 72]     # Dabbawala Brown
]

ICON_URL = 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Google_Maps_pin.svg/137px-Google_Maps_pin.svg.png'

icon_data = {
    "url": ICON_URL,
    "width": 137,
    "height": 240,
    "anchorY": 240,
    "mask": True
}

@st.cache_data
def getdf():
    df = pd.read_json('srcdf.json')
    df['icon_data'] = None
    for i in df.index:
        df.at[i, 'icon_data'] = icon_data
    return [pd.read_json(x) for x in ['destdf.json','fulldf.json']] + [df]

def srcpath(src):
    @st.cache_data
    def lay(src):
        layers = []
        df = df0.query(f"`src`=={src}")

        for i in range(df.shape[0]):
            layer = pdk.Layer(
                type='PathLayer',
                data=df[i:i+1],
                rounded=True,
                billboard=True,
                pickable=True,
                width_min_pixels=3,
                auto_highlight=True,
                get_color=colors[i],
                get_path='path',
            )
            layers.append(layer)
        
        srclayer = pdk.Layer(
            "ScatterplotLayer",
            data=dfs[src:src+1],
            pickable=True,
            stroked=True,
            filled=True,
            opacity=1,
            get_radius=3999,
            radius_max_pixels=12,
            get_position="coordinates",
            get_fill_color=[0,0,0],
        )
        layers.append(srclayer)
        
        iconlayer = pdk.Layer(
            type='IconLayer',
            data=dfs[src:src+1],
            billboard=True,
            get_icon='icon_data',
            get_size=79,
            get_color=[155,155,155],
            size_scale=1,
            size_min_pixels=10,
            opacity=0.6,
            size_max_pixels=100,
            get_position='coordinates',
            pickable=True
        )
        layers.append(iconlayer)
        return layers

    layers = lay(src)
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": dfs["coordinates"][src][1], 
            "longitude": dfs["coordinates"][src][0], 
            "zoom": 12,  # Increased zoom for Mumbai
            "pitch": 30
        },
        layers=layers,
    ))

def getpath(src, tp, veh):
    df = df0.query(f"`src`=={src}").query(f"`type`=={tp}").query(f"`veh`=={veh}")
    if df.empty:
        st.warning("No route found for selected combination.")
        return

    path = df.iloc[0]["path"]
    source = path[0]
    dests = path[1:-1]

    depot_df = pd.DataFrame([{
        "name": f"Depot {src}",
        "lat": source[1],
        "lon": source[0],
        "icon_data": icon_data
    }])

    dest_df = pd.DataFrame([{
        "name": f"Dest {chr(65+i)}",  # A, B, C...
        "lat": coord[1],
        "lon": coord[0]
    } for i, coord in enumerate(dests)])

    layers = []
    layers.append(pdk.Layer(
        "PathLayer",
        data=pd.DataFrame([{"path": path}]),
        get_path="path",
        get_color=colors[src % len(colors)],
        width_min_pixels=5,
        pickable=True,
        auto_highlight=True,
    ))

    layers.append(pdk.Layer(
        "IconLayer",
        data=depot_df,
        get_icon="icon_data",
        get_size=60,
        size_scale=1,
        size_min_pixels=10,
        opacity=0.8,
        get_position='[lon, lat]',
        pickable=True
    ))

    layers.append(pdk.Layer(
        "ScatterplotLayer",
        data=depot_df,
        get_position='[lon, lat]',
        get_color='[0, 0, 0]',
        get_radius=100,
        pickable=True
    ))

    layers.append(pdk.Layer(
        "ScatterplotLayer",
        data=dest_df,
        get_position='[lon, lat]',
        get_color='[0, 0, 255]',
        get_radius=60,
        pickable=True
    ))

    tooltip = {
        "html": "<b>{name}</b>",
        "style": {"color": "white"}
    }

    mid = path[len(path) // 2]
    view_state = pdk.ViewState(
        latitude=mid[1],
        longitude=mid[0],
        zoom=12,
        pitch=30,
    )

    st.pydeck_chart(pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="mapbox://styles/mapbox/light-v9"
    ))

def fullpath():
    @st.cache_data
    def lay():
        layers = []
        for i in range(df0['src'].nunique()):
            df = df0.query(f"`src`=={i}")
            layer = pdk.Layer(
                type='PathLayer',
                data=df,
                rounded=True,
                billboard=True,
                pickable=True,
                width_min_pixels=5,
                auto_highlight=True,
                get_color=colors[i],
                get_path='path',
            )
            layers.append(layer)
        return layers

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": 19.0760,
            "longitude": 72.8777,
            "zoom": 11,
            "pitch": 30
        },
        layers=lay(),
    ))

def overview():
    @st.cache_data
    def lay():
        layers = []
        for i in range(dfd['labels'].nunique()):
            df = dfd.query(f"`labels`=={i}")
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=df,
                pickable=True,
                stroked=True,
                filled=True,
                opacity=0.2,
                get_radius=3999,
                radius_max_pixels=19,
                get_position="coordinates",
                get_fill_color=colors[i],
            )
            layers.append(layer)

        srclayer = pdk.Layer(
            "ScatterplotLayer",
            data=dfs,
            pickable=True,
            stroked=True,
            filled=True,
            opacity=1,
            get_radius=3999,
            radius_max_pixels=7,
            get_position="coordinates",
            get_fill_color=[0,0,0],
        )
        layers.append(srclayer)
        
        iconlayer = pdk.Layer(
            type='IconLayer',
            data=dfs,
            billboard=True,
            get_icon='icon_data',
            get_size=89,
            size_scale=1,
            size_min_pixels=10,
            opacity=0.6,
            size_max_pixels=100,
            get_position='coordinates',
            pickable=True
        )
        layers.append(iconlayer)
        return layers

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": 19.0760,
            "longitude": 72.8777,
            "zoom": 10,
            "pitch": 30
        },
        layers=lay(),
    ))

# Main App
st.set_page_config(layout="wide")
st.image('https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Mumbai_Skyline_at_Night.jpg/800px-Mumbai_Skyline_at_Night.jpg', 
         use_column_width=True, caption='Mumbai Route Optimization')

dfd, df0, dfs = getdf()

st.markdown("""
## AI-based route optimization for Mumbai's logistics network

This tool optimizes delivery routes across Mumbai's complex urban landscape, accounting for:
- High-density traffic patterns
- Multiple depot locations
- Diverse vehicle types (trucks, bikes, vans)
- Real-world constraints like time windows and capacity
""")

overview()
st.caption("_(hover and scroll to zoom)_")

st.markdown("""
### Key Features:
1. **Multi-Depot Optimization**: Routes originate from 5 key locations across Mumbai
2. **Smart Clustering**: AI groups destinations efficiently for each vehicle
3. **Real-World Data**: Uses actual Mumbai coordinates and road networks
4. **Visual Analytics**: Interactive maps show optimal routes
""")

dtype = st.radio("", ('Single vehicle demo', 'Full network view'), index=0, horizontal=True)
if dtype == 'Single vehicle demo':
    col1, col2 = st.columns(2)
    with col1:
        src = st.selectbox(
            'Choose depot location',
            options=[
                "South Mumbai (Gateway)",
                "Dadar (Central)",
                "Bandra (West)",
                "Andheri (North West)",
                "Thane (East)"
            ],
            index=0)
        src_id = ["South Mumbai (Gateway)", "Dadar (Central)", "Bandra (West)", 
                 "Andheri (North West)", "Thane (East)"].index(src)
    with col2:
        tp = st.selectbox(
            'Choose vehicle type',
            options=['Two-wheeler', 'Small van', 'Large truck'],
            index=1)
        tp_id = {'Two-wheeler': 0, 'Small van': 0, 'Large truck': 1}[tp]
    
    if tp == 'Large truck':
        getpath(src_id, tp_id, 0)
    else:
        srcpath(src_id)
else:
    st.info('Visualizing entire Mumbai logistics network...')
    fullpath()

st.caption("_(hover and scroll to zoom)_")

st.markdown("""
### About This Project
This system was developed to address Mumbai's unique logistics challenges:
- Extreme traffic congestion
- Limited delivery windows
- High population density
- Diverse neighborhood characteristics

**Team Members:**
- Your Name
- Your Team Member

**Data Sources:**
- OpenStreetMap Mumbai data
- Synthetic data calibrated to Mumbai conditions
""")
