import streamlit as st
import requests
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium

API_URL = "http://localhost:8000/create_map"
st.set_page_config(layout="wide")

def main():
    #st.title("Events Along Route Finder")
    data = st.session_state.get("route_data")

    col1, col2, col3 = st.columns([1,2,2])

    with col1:
        st.subheader("Insert data")

        origin_address = st.text_input("Origin Address", value="Padova")
        destination_address = st.text_input("Destination Address", value="Verona")
        buffer_distance = st.number_input("Buffer Distance (km)", min_value=0, value=5)

        query_text = st.text_input("Search Query Text", value="Sport")
        numevents = st.number_input("Number of Events to Retrieve", min_value=1, value=10)

        profile_choice = st.selectbox(
            "Transport Profile",
            options=["driving-car", "cycling-regular", "cycling-road", "foot-walking"],
            index=0,
            help="Select the transport profile for routing"
        )

        # Compact start datetime inputs side by side
        #st.write("Start Date and Time")
        start_col1, start_col2 = st.columns(2)
        with start_col1:
            start_date = st.date_input("Start Date", value=datetime.today())
        with start_col2:
            if 'start_time' not in st.session_state:
                st.session_state.start_time = datetime.now().time()
            start_time = st.time_input("Start Time", key='start_time')

        # Compact end datetime inputs side by side
        #st.write("End Date and Time")
        end_col1, end_col2 = st.columns(2)
        with end_col1:
            end_date = st.date_input("End Date", value=datetime.today() + timedelta(days=4))
        with end_col2:
            if 'end_time' not in st.session_state:
                st.session_state.end_time = datetime.now().time()
            end_time = st.time_input("End Time", key='end_time')

        error_msgs = []
        if end_date < start_date:
            error_msgs.append("End Date cannot be earlier than Start Date.")
        if end_date == start_date and end_time < start_time:
            error_msgs.append("If Start Date and End Date are the same, End Time cannot be earlier than Start Time.")

        if error_msgs:
            for msg in error_msgs:
                st.error(msg)
        else:
            startinputdate = datetime.combine(start_date, start_time).isoformat()
            endinputdate = datetime.combine(end_date, end_time).isoformat()

        search_disabled = len(error_msgs) > 0

        if st.button("Search Events", disabled=search_disabled):
            payload = {
                "origin_address": origin_address,
                "destination_address": destination_address,
                "buffer_distance": buffer_distance,
                "startinputdate": startinputdate,
                "endinputdate": endinputdate,
                "query_text": query_text,
                "numevents": numevents,
                "profile_choice": profile_choice,
            }
            with st.spinner("Querying events..."):
                response = requests.post(API_URL, json=payload)

            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    st.warning(data["message"])
                    return
                if not all(k in data for k in ("origin", "destination", "route_coords")):
                    st.error("Incomplete route data received from backend.")
                    return
                st.session_state["route_data"] = data
            else:
                st.error(f"API call failed with status {response.status_code}: {response.text}")
                return

    with col2:
        if data:
            st.subheader("Route Map")
            center_lat = (data['origin']['lat'] + data['destination']['lat']) / 2
            center_lon = (data['origin']['lon'] + data['destination']['lon']) / 2
            m = folium.Map(location=[center_lat, center_lon], zoom_start=9, disable_3d=True)
            #m = folium.Map(location=[center_lat, center_lon], zoom_start=9, attributionControl=False, disable_3d=True)

            # m = folium.Map(
            #     location=[center_lat, center_lon],
            #     zoom_start=9,
            #     tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
            #     attr='&copy; OpenStreetMap contributors &copy; CARTO',
            #     disable_3d=True
            # )


            try:
                route_latlon = [(coord[1], coord[0]) for coord in data['route_coords']]
                folium.PolyLine(
                    locations=route_latlon,
                    color='blue',
                    weight=5,
                    opacity=0.8,
                    tooltip="Route"
                ).add_to(m)
            except Exception as e:
                st.warning(f"Could not add route polyline: {e}")

            if data.get('buffer_polygon'):
                try:
                    buffer_coords = [data['buffer_polygon']]
                    geojson = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": buffer_coords
                        }
                    }
                    folium.GeoJson(
                        geojson,
                        style_function=lambda x: {'color': 'red', 'fillOpacity': 0.1}
                    ).add_to(m)
                except Exception as e:
                    st.warning(f"Could not render buffer polygon: {e}")
                    st.json(data['buffer_polygon'])

            try:
                folium.Marker(
                    location=[data['origin']['lat'], data['origin']['lon']],
                    popup=folium.Popup(f"Start from: {origin_address}", max_width=300, min_width=150),
                    icon=folium.Icon(color="orange", icon="play")
                ).add_to(m)
                folium.Marker(
                    location=[data['destination']['lat'], data['destination']['lon']],
                    popup=folium.Popup(f"Arrive to: {destination_address}", max_width=300, min_width=150),
                    icon=folium.Icon(color="purple", icon="stop")
                ).add_to(m)
            except Exception as e:
                st.warning(f"Error adding origin/destination markers: {e}")

            events = data.get('events', [])
            for event in events:
                lat = event.get('lat') or event.get('latitude')
                lon = event.get('lon') or event.get('longitude')
                if lat is None or lon is None:
                    st.warning(f"Event missing coordinates: {event.get('title', 'No Title')}")
                    continue
                popup_content = (
                    f"<b>{event.get('title', 'No Title')}</b><br>"
                    f"<b>{event.get('address', 'No Address')}</b><br>"
                    f"{event.get('description', '')}<br>"
                    f"<i>Start: {event.get('start_date', 'N/A')}</i><br>"
                    f"<i>End: {event.get('end_date', 'N/A')}</i>"
                )
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_content, max_width=300, min_width=150),
                    icon=folium.Icon(icon="star")
                ).add_to(m)

            st_folium(m, width=None, height=700, use_container_width=True, key="route_map")
        else:
            st.info("Enter details and click 'Search Events' to find events along the route.")

    with col3:
        if data:
            st.subheader("Events Along Route")
            events = data.get('events', [])
            if events:
                container = st.container()
                with container:
                    for event in events:
                        with st.expander(event.get('title', 'No Title')):
                            st.write(event.get('address', ''))
                            st.write(event.get('description', ''))
                            st.write(f"Start: {event.get('start_date', 'N/A')}  |  End: {event.get('end_date', 'N/A')}")
            else:
                st.info("No events found for this route in the specified date range.")

if __name__ == "__main__":
    main()
