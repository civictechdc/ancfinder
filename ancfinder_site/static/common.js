function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const createMap = (containerName) => {
    return new mapboxgl.Map({
        container: containerName,
        style: 'mapbox://styles/opendatadc/cjtf0zr475ffb1fojc048myrl',
        center: [-77.003632, 38.893443],
        zoom: 10.0,
        interactive: false
    });
}

const ancLayerId= 'ancLayerId';

const addAncHighlightToMap = (ancGeojson, map) => () => {
    if(map.getLayer(ancLayerId)) {
        map.removeLayer(ancLayerId);
        map.removeSource(ancLayerId);
    }
    map.addLayer({
        id: ancLayerId,
        type: 'line',
        source: {
            type: 'geojson',
            data: {
                ...ancGeojson
            }
        },
        layout: {},
        paint: {
            'line-color': '#DA253B',
            'line-width': 3
        }
    });
}

const fetchAncGeojson = () => {
    return fetch('/api/anc-geojson', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(rsp => rsp.json())
    .then(rawData => {
        return rawData.features;
    })
    .catch(err => {
        console.error(err);
    });
}