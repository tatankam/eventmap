import streamlit as st
import streamlit.components.v1 as components
import requests
from datetime import datetime, timedelta
import json

API_URL = "http://localhost:8000/create_map"
st.set_page_config(layout="wide")

def main():
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
        start_col1, start_col2 = st.columns(2)
        with start_col1:
            start_date = st.date_input("Start Date", value=datetime.today())
        with start_col2:
            if 'start_time' not in st.session_state:
                st.session_state.start_time = datetime.now().time()
            start_time = st.time_input("Start Time", key='start_time')

        # Compact end datetime inputs side by side
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
                if not all(k in data for k in ("origin", "destination", "route_coords", "buffer_polygon")):
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

            # Prepare GeoJSON for route polyline
            route_coords = [[lon, lat] for lat, lon in [(c[1], c[0]) for c in data['route_coords']]]
            route_geojson = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": route_coords
                }
            }

            # Prepare markers from events
            markers = []
            for event in data.get('events', []):
                lat = event.get('lat') or event.get('latitude')
                lon = event.get('lon') or event.get('longitude')
                if lat is None or lon is None:
                    continue
                markers.append({
                    "title": event.get("title", "No Title"),
                    "address": event.get("address", ""),
                    "description": event.get("description", ""),
                    "start_date": event.get("start_date", "N/A"),
                    "end_date": event.get("end_date", "N/A"),
                    "coordinates": [lon, lat]
                })

            # Origin and destination markers
            origin_marker = [data['origin']['lon'], data['origin']['lat']]
            destination_marker = [data['destination']['lon'], data['destination']['lat']]

            # Buffer polygon coordinates (list of [lon, lat])
            buffer_polygon_coords = data['buffer_polygon']

            # Create OpenLayers map HTML with buffer polygon and markers
            openlayers_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="utf-8" />
                <title>OpenLayers in Streamlit</title>
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ol@7.3.0/ol.css" type="text/css">
                <style>
                    #map {{
                        width: 100%;
                        height: 700px;
                    }}
                    .ol-popup {{
                        position: absolute;
                        background-color: white;
                        box-shadow: 0 1px 4px rgba(0,0,0,0.2);
                        padding: 15px;
                        border-radius: 10px;
                        border: 1px solid #cccccc;
                        bottom: 12px;
                        left: -50px;
                        min-width: 280px;
                    }}
                    .ol-popup:after, .ol-popup:before {{
                        top: 100%;
                        border: solid transparent;
                        content: " ";
                        height: 0;
                        width: 0;
                        position: absolute;
                        pointer-events: none;
                    }}
                    .ol-popup:after {{
                        border-top-color: white;
                        border-width: 10px;
                        left: 48px;
                        margin-left: -10px;
                    }}
                    .ol-popup:before {{
                        border-top-color: #cccccc;
                        border-width: 11px;
                        left: 48px;
                        margin-left: -11px;
                    }}
                </style>
                <script src="https://cdn.jsdelivr.net/npm/ol@7.3.0/dist/ol.js"></script>
            </head>
            <body>
                <div id="map"></div>
                <script type="text/javascript">
                    const routeGeoJSON = {json.dumps(route_geojson)};
                    const markers = {json.dumps(markers)};
                    const origin = {json.dumps(origin_marker)};
                    const destination = {json.dumps(destination_marker)};
                    const bufferCoords = {json.dumps([buffer_polygon_coords])};

                    // Route polyline
                    const routeFeature = new ol.format.GeoJSON().readFeature(routeGeoJSON, {{
                        featureProjection: "EPSG:3857"
                    }});

                    // Buffer polygon feature
                    const bufferFeature = new ol.Feature({{
                        geometry: new ol.geom.Polygon(bufferCoords).transform('EPSG:4326', 'EPSG:3857')
                    }});

                    const bufferLayer = new ol.layer.Vector({{
                        source: new ol.source.Vector({{
                            features: [bufferFeature]
                        }}),
                        style: new ol.style.Style({{
                            stroke: new ol.style.Stroke({{
                                color: 'red',
                                width: 2
                            }}),
                            fill: new ol.style.Fill({{
                                color: 'rgba(255, 0, 0, 0.1)'
                            }})
                        }})
                    }});

                    // Route layer
                    const routeLayer = new ol.layer.Vector({{
                        source: new ol.source.Vector({{
                            features: [routeFeature]
                        }}),
                        style: new ol.style.Style({{
                            stroke: new ol.style.Stroke({{
                                color: 'blue',
                                width: 4
                            }})
                        }})
                    }});

                    // Marker styles
                    const iconStyleOrigin = new ol.style.Style({{
                        image: new ol.style.Icon({{
                            anchor: [0.5, 1],
                            src: 'https://openlayers.org/en/latest/examples/data/icon.png',
                            color: 'green'
                        }})
                    }});
                    const iconStyleDestination = new ol.style.Style({{
                        image: new ol.style.Icon({{
                            anchor: [0.5, 1],
                            src: 'https://openlayers.org/en/latest/examples/data/icon.png',
                            color: 'red'
                        }})
                    }});
                    const iconStyleEvent = new ol.style.Style({{
                        image: new ol.style.Icon({{
                            anchor: [0.5, 1],
                            src: './icons/event.png',
                            scale: 1.8
                        }})
                    }});

                    // Origin feature
                    const originFeature = new ol.Feature({{
                        geometry: new ol.geom.Point(ol.proj.fromLonLat(origin))
                    }});
                    originFeature.setStyle(iconStyleOrigin);

                    // Destination feature
                    const destinationFeature = new ol.Feature({{
                        geometry: new ol.geom.Point(ol.proj.fromLonLat(destination))
                    }});
                    destinationFeature.setStyle(iconStyleDestination);

                    // Event features
                    const eventFeatures = markers.map(marker => {{
                        const feat = new ol.Feature({{
                            geometry: new ol.geom.Point(ol.proj.fromLonLat(marker.coordinates)),
                            name: marker.title,
                            description: marker.description,
                            address: marker.address,
                            start_date: marker.start_date,
                            end_date: marker.end_date
                        }});
                        feat.setStyle(iconStyleEvent);
                        return feat;
                    }});

                    const markersLayer = new ol.layer.Vector({{
                        source: new ol.source.Vector({{
                            features: [originFeature, destinationFeature, ...eventFeatures]
                        }})
                    }});

                    // Create map
                    const map = new ol.Map({{
                        target: 'map',
                        layers: [
                            new ol.layer.Tile({{
                                source: new ol.source.OSM()
                            }}),
                            bufferLayer,
                            routeLayer,
                            markersLayer
                        ],
                        view: new ol.View({{
                            center: ol.proj.fromLonLat([0, 0]),
                            zoom: 2
                        }})
                    }});

                    // Fit view to route after map and layers loaded
                    const extent = routeFeature.getGeometry().getExtent();
                    map.getView().fit(extent, {{ padding: [50, 50, 50, 50], maxZoom: 15 }});


                    // Popup overlay
                    const container = document.createElement('div');
                    container.className = 'ol-popup';
                    container.style.display = 'none';
                    document.body.appendChild(container);

                    const popup = new ol.Overlay({{
                        element: container,
                        positioning: 'bottom-center',
                        stopEvent: false,
                        offset: [0, -50],
                    }});
                    map.addOverlay(popup);

                    // Show popup on click
                    map.on('click', function(evt) {{
                        const feature = map.forEachFeatureAtPixel(evt.pixel, function(f) {{ return f; }});
                        if (feature && feature.get('name')) {{
                            const coordinates = feature.getGeometry().getCoordinates();
                            const props = feature.getProperties();
                            popup.setPosition(coordinates);
                            container.style.display = 'block';
                            container.innerHTML = `<b>${{props.name}}</b><br>
                                                    <i>${{props.address}}</i><br>
                                                    ${{props.description}}<br>
                                                    <small>Start: ${{props.start_date}} | End: ${{props.end_date}}</small>`;
                        }} else {{
                            container.style.display = 'none';
                        }}
                    }});
                </script>
            </body>
            </html>
            """

            components.html(openlayers_html, height=720, scrolling=True)

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
