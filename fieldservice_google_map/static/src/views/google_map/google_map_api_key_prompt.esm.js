import {onMounted, onPatched, onWillStart, useRef} from "@odoo/owl";
import {GoogleMapRenderer} from "@web_view_google_map/views/google_map/google_map_renderer.esm";
import {loadGoogleMaps} from "@web_view_google_map/views/google_map/google_maps_loader.esm";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

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

    openGoogleMapsSettings() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "res.config.settings",
            views: [[false, "form"]],
            target: "current",
            context: {module: "base_google_map"},
        });
    },
});
