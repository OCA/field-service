import {onMounted, onPatched, onWillStart, useRef} from "@odoo/owl";
import {GoogleMapRenderer} from "@web_view_google_map/views/google_map/google_map_renderer.esm";
import {browser} from "@web/core/browser/browser";
import {loadGoogleMaps} from "@web_view_google_map/views/google_map/google_maps_loader.esm";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

const GOOGLE_MAPS_API_KEY_FIELD = "google_maps_view_api_key";

function revealGoogleMapsSetting() {
    const started = Date.now();
    const tick = () => {
        const field = document.querySelector(`[name="${GOOGLE_MAPS_API_KEY_FIELD}"]`);
        const setting = field?.closest(".o_setting_box");
        if (setting) {
            setting.scrollIntoView({block: "center"});
            setting.classList.add("o_setting_highlight");
            browser.setTimeout(() => {
                setting.classList.remove("o_setting_highlight");
            }, 5000);
            return;
        }
        if (Date.now() - started < 4000) {
            browser.setTimeout(tick, 50);
        }
    };
    tick();
}

const UNUSABLE_API_KEYS = new Set(["", "YOUR_GOOGLE_MAPS_API_KEY"]);

function isUsableGoogleMapsApiKey(apiKey) {
    return !UNUSABLE_API_KEYS.has(String(apiKey || "").trim());
}

function normalizeArch(arch) {
    if (arch && typeof arch !== "string") {
        return arch;
    }
    const xml = String(arch || "");
    const doc = new DOMParser().parseFromString(xml, "text/xml");
    return doc.documentElement;
}

function parseMarkerColors(colorsAttr) {
    if (!colorsAttr) {
        return [];
    }
    return colorsAttr
        .split(";")
        .map((pair) => pair.trim())
        .filter(Boolean)
        .map((pair) => {
            const idx = pair.indexOf(":");
            if (idx === -1) {
                return null;
            }
            return [pair.slice(0, idx).trim(), pair.slice(idx + 1).trim()];
        })
        .filter(Boolean);
}

GoogleMapRenderer.template = "fieldservice_google_map.GoogleMapApiKeyPrompt";

/**
 * Ask for a Google Maps API key instead of loading Maps JS with an invalid key
 * (which shows Google's "Oops! Something went wrong" page).
 */
patch(GoogleMapRenderer.prototype, {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.mapRef = useRef("mapContainer");
        this.gmap = null;
        this.markerCluster = null;
        this.markers = [];
        this.infoWindow = null;
        this.records = [];
        this.theme = "default";
        this.missingApiKey = false;

        const archEl = normalizeArch(this.props.archInfo?.arch || this.props.arch);
        const attrs = archEl.attributes || {};
        this.fieldLat = attrs.getNamedItem("lat")?.value || "partner_latitude";
        this.fieldLng = attrs.getNamedItem("lng")?.value || "partner_longitude";
        this.markerColor = attrs.getNamedItem("color")?.value || null;
        this.markerColors = parseMarkerColors(attrs.getNamedItem("colors")?.value);
        this.markerKindAttr = attrs.getNamedItem("marker")?.value || "";
        this.defaultMarkerColor = "red";
        this.iconUrl = "/web_view_google_map/static/src/img/markers/";
        this.resModel = this.props.resModel;
        this.archFields = [...archEl.querySelectorAll(":scope > field")].map((node) =>
            node.getAttribute("name")
        );

        onWillStart(async () => {
            const apiKey = await this.orm.call("ir.config_parameter", "get_param", [
                "google.api_key_geocode",
                "",
            ]);
            if (!isUsableGoogleMapsApiKey(apiKey)) {
                this.missingApiKey = true;
                return;
            }
            const maps = await loadGoogleMaps(this.orm);
            if (!maps) {
                this.missingApiKey = true;
                return;
            }
            await this.loadTheme();
            await this.loadRecords();
        });

        onMounted(() => {
            if (this.missingApiKey) {
                return;
            }
            this.initMap();
            this.renderMarkers();
        });

        onPatched(() => {
            if (this.gmap) {
                this.renderMarkers();
            }
        });
    },

    /**
     * Location pins keep the stage color. Workers use a person badge so the
     * two stay distinct on the Google roadmap and the OpenStreetMap base map.
     */
    markerKind() {
        if (this.markerKindAttr === "worker" || this.markerKindAttr === "location") {
            return this.markerKindAttr;
        }
        return this.resModel === "fsm.person" ? "worker" : "location";
    },

    async loadRecords() {
        if (this.resModel === "fsm.order") {
            for (const name of ["person_latitude", "person_longitude", "person_id"]) {
                if (!this.archFields.includes(name)) {
                    this.archFields.push(name);
                }
            }
        }
        return super.loadRecords();
    },

    initMap() {
        super.initMap();
        this.addOpenStreetMapType();
        this.addMarkerLegend();
    },

    addOpenStreetMapType() {
        if (!this.gmap || !window.google?.maps || this.gmap.mapTypes.get("osm")) {
            return;
        }
        const osm = new window.google.maps.ImageMapType({
            getTileUrl(coord, zoom) {
                const tiles = 1 << zoom;
                if (coord.y < 0 || coord.y >= tiles) {
                    return "";
                }
                const x = ((coord.x % tiles) + tiles) % tiles;
                return `https://tile.openstreetmap.org/${zoom}/${x}/${coord.y}.png`;
            },
            tileSize: new window.google.maps.Size(256, 256),
            maxZoom: 19,
            minZoom: 0,
            name: "OpenStreetMap",
            alt: "OpenStreetMap",
        });
        this.gmap.mapTypes.set("osm", osm);
        this.gmap.setOptions({
            mapTypeControl: true,
            mapTypeControlOptions: {
                mapTypeIds: [
                    window.google.maps.MapTypeId.ROADMAP,
                    window.google.maps.MapTypeId.SATELLITE,
                    "osm",
                ],
                style: window.google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
            },
        });
        const attribution = document.createElement("div");
        attribution.className = "o_fsm_osm_attribution";
        attribution.style.display = "none";
        attribution.innerHTML =
            '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">OpenStreetMap</a> contributors';
        this.gmap.controls[window.google.maps.ControlPosition.BOTTOM_RIGHT].push(
            attribution
        );
        this.gmap.addListener("maptypeid_changed", () => {
            attribution.style.display =
                this.gmap.getMapTypeId() === "osm" ? "block" : "none";
        });
    },

    addMarkerLegend() {
        if (!this.gmap || this.resModel !== "fsm.order" || this._markerLegend) {
            return;
        }
        const legend = document.createElement("div");
        legend.className = "o_fsm_map_legend";
        const location = document.createElement("div");
        const locationImg = document.createElement("img");
        locationImg.src = `${this.iconUrl}blue.png`;
        locationImg.alt = "";
        location.append(locationImg, document.createTextNode("Location"));
        const worker = document.createElement("div");
        const workerImg = document.createElement("img");
        workerImg.src = this.workerIconUrl();
        workerImg.alt = "";
        worker.append(workerImg, document.createTextNode("Worker"));
        legend.append(location, worker);
        this.gmap.controls[window.google.maps.ControlPosition.LEFT_TOP].push(legend);
        this._markerLegend = legend;
    },

    workerIconUrl() {
        const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 36 36">
            <circle cx="18" cy="18" r="16" fill="#1a56db" stroke="#ffffff" stroke-width="2"/>
            <circle cx="18" cy="13" r="4.5" fill="#ffffff"/>
            <path d="M9 28.5c1.4-5.4 4.6-7.8 9-7.8s7.6 2.4 9 7.8" fill="#ffffff"/>
        </svg>`;
        return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
    },

    workerIcon() {
        return {
            url: this.workerIconUrl(),
            scaledSize: new window.google.maps.Size(36, 36),
            anchor: new window.google.maps.Point(18, 18),
        };
    },

    personLabel(record) {
        const person = record.person_id;
        if (Array.isArray(person) && person.length > 1) {
            return person[1] || "";
        }
        return record.display_name || "";
    },

    spreadPoint(lat, lng, used) {
        let placedLat = lat;
        let placedLng = lng;
        let key = `${placedLat.toFixed(4)},${placedLng.toFixed(4)}`;
        let step = 0;
        while (used.has(key) && step < 8) {
            step += 1;
            const angle = step * (Math.PI / 4);
            placedLat = lat + Math.sin(angle) * 0.004;
            placedLng = lng + Math.cos(angle) * 0.004;
            key = `${placedLat.toFixed(4)},${placedLng.toFixed(4)}`;
        }
        used.add(key);
        return {lat: placedLat, lng: placedLng};
    },

    mapPoints(record) {
        const points = [];
        const kind = this.markerKind();
        const lat = Number(record[this.fieldLat]);
        const lng = Number(record[this.fieldLng]);
        if (lat && lng) {
            points.push({
                lat,
                lng,
                kind,
                label: record.display_name || "",
            });
        }
        if (kind === "location" && this.resModel === "fsm.order") {
            const workerLat = Number(record.person_latitude);
            const workerLng = Number(record.person_longitude);
            if (workerLat && workerLng) {
                points.push({
                    lat: workerLat,
                    lng: workerLng,
                    kind: "worker",
                    label: this.personLabel(record),
                });
            }
        }
        return points;
    },

    renderMarkers() {
        if (!this.gmap) {
            return;
        }
        this.clearMarkers();
        const bounds = new window.google.maps.LatLngBounds();
        const used = new Set();
        let hasPoint = false;
        for (const record of this.records) {
            for (const point of this.mapPoints(record)) {
                const placed = this.spreadPoint(point.lat, point.lng, used);
                const latLng = new window.google.maps.LatLng(placed.lat, placed.lng);
                const marker = new window.google.maps.Marker({
                    position: latLng,
                    map: this.markerCluster ? null : this.gmap,
                    animation: window.google.maps.Animation.DROP,
                    icon:
                        point.kind === "worker"
                            ? this.workerIcon()
                            : this.getIconColorPath(this.getIconColor(record)),
                    title: point.label,
                });
                marker.fsmLabel = point.label;
                marker.addListener("click", () => this.onMarkerClick(marker, record));
                this.markers.push(marker);
                if (this.markerCluster) {
                    this.markerCluster.addMarker(marker);
                }
                bounds.extend(latLng);
                hasPoint = true;
            }
        }
        if (hasPoint) {
            const signature = [...used].sort().join("|");
            if (this.boundsSignature !== signature) {
                this.boundsSignature = signature;
                this.gmap.fitBounds(bounds);
            }
        }
    },

    onMarkerClick(marker, record) {
        if (!marker.fsmLabel || marker.fsmLabel === record.display_name) {
            return super.onMarkerClick(marker, record);
        }
        const previous = record.display_name;
        record.display_name = marker.fsmLabel;
        try {
            return super.onMarkerClick(marker, record);
        } finally {
            record.display_name = previous;
        }
    },

    openGoogleMapsSettings() {
        // Google Maps settings live in the General Settings app
        // (block "Google Maps View"), not in an app named base_google_map.
        // A module key that matches no app hides every settings block.
        this.action
            .doAction("base_setup.action_general_configuration")
            .then(() => revealGoogleMapsSetting());
    },
});
