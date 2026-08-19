/** @odoo-module **/

/**
 * District Polygon Map Editor (Google Maps)
 *
 * Attaches a Google Maps instance to the #district_polygon_map div inside the
 * district form view. Points are synced to/from the polygon_ids One2many
 * list via the ORM service.
 *
 * Strategy: pure DOM/event approach (no OWL component) so it works
 * regardless of how the form view is rendered. We watch for the map
 * container to appear in DOM, then initialise Google Maps once.
 */

import { loadJS } from "@web/core/assets";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

// ── Google Maps loader ────────────────────────────────────────────────────────────

let _gmapsReady = null;
function loadGoogleMaps() {
    if (_gmapsReady) return _gmapsReady;
    _gmapsReady = (async () => {
        const resp = await rpc("/website/google_maps_api_key", {});
        const data = JSON.parse(resp);
        const key = data.google_maps_api_key || "";
        if (!key) {
            throw new Error("Google Maps API key not configured");
        }
        await loadJS(
            `https://maps.googleapis.com/maps/api/js?v=3.exp&key=${encodeURIComponent(key)}`
        );
        return window.google;
    })();
    return _gmapsReady;
}

// ── Map initialiser ───────────────────────────────────────────────────────────

const RIYADH = { lat: 24.7136, lng: 46.6753 };

async function initPolygonMap(container, existingPoints, onPointsChange) {
    const google = await loadGoogleMaps();

    const map = new google.maps.Map(container, {
        center: RIYADH,
        zoom: 11,
        mapTypeControl: false,
        streetViewControl: false,
    });

    let points = []; // [{lat, lng, marker}]
    let polygon = null;

    function refresh() {
        if (polygon) { polygon.setMap(null); polygon = null; }
        if (points.length > 2) {
            polygon = new google.maps.Polygon({
                paths: points.map(p => ({ lat: p.lat, lng: p.lng })),
                strokeColor: "#2563eb",
                strokeOpacity: 0.8,
                strokeWeight: 2,
                fillColor: "#93c5fd",
                fillOpacity: 0.25,
                map: map,
            });
        }
        onPointsChange(points.map(p => ({ lat: p.lat, lng: p.lng })));
        updateStatus();
    }

    function updateStatus() {
        const el = document.getElementById("polygon_status");
        if (!el) return;
        if (points.length === 0) {
            el.textContent = "Click on the map to add points";
        } else if (points.length < 3) {
            el.textContent = `${points.length} point — need at least 3`;
        } else {
            el.textContent = `${points.length} point — active polygon ✓`;
        }
    }

    function addMarker(lat, lng) {
        const marker = new google.maps.Circle({
            center: { lat, lng },
            radius: 60,
            strokeColor: "#2563eb",
            strokeOpacity: 0.9,
            strokeWeight: 2,
            fillColor: "#2563eb",
            fillOpacity: 0.9,
            map: map,
        });
        points.push({ lat, lng, marker });
        refresh();
    }

    // Load existing points
    if (existingPoints && existingPoints.length) {
        existingPoints.forEach(p => addMarker(p.lat, p.lng));
        const bounds = new google.maps.LatLngBounds();
        existingPoints.forEach(p => bounds.extend({ lat: p.lat, lng: p.lng }));
        map.fitBounds(bounds);
    } else {
        updateStatus();
    }

    // Click to add
    map.addListener("click", e => addMarker(e.latLng.lat(), e.latLng.lng()));

    // Undo button
    const undoBtn = document.getElementById("btn_polygon_undo");
    if (undoBtn) {
        undoBtn.addEventListener("click", () => {
            if (!points.length) return;
            const last = points.pop();
            last.marker.setMap(null);
            refresh();
        });
    }

    // Clear button
    const clearBtn = document.getElementById("btn_polygon_clear");
    if (clearBtn) {
        clearBtn.addEventListener("click", () => {
            if (!points.length) return;
            if (!confirm("Clear all boundary points?")) return;
            points.forEach(p => p.marker.setMap(null));
            points = [];
            refresh();
        });
    }

    return { map, getPoints: () => points.map(p => ({ lat: p.lat, lng: p.lng })) };
}

// ── Fetch existing polygon points from the One2many list rows ─────────────────

function readPointsFromDOM() {
    const rows = document.querySelectorAll(
        ".o_field_one2many[name='polygon_ids'] .o_data_row"
    );
    const pts = [];
    rows.forEach(row => {
        const cells = row.querySelectorAll(".o_data_cell");
        if (cells.length >= 3) {
            const lat = parseFloat((cells[1].textContent || "").trim().replace(",", "."));
            const lng = parseFloat((cells[2].textContent || "").trim().replace(",", "."));
            if (!isNaN(lat) && !isNaN(lng) && lat !== 0 && lng !== 0) {
                pts.push({ lat, lng });
            }
        }
    });
    return pts;
}

// ── Write points back via RPC ─────────────────────────────────────────────────

async function savePointsViaRPC(districtId, points) {
    if (!districtId) return;
    const res = await fetch("/web/dataset/call_kw", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            jsonrpc: "2.0", method: "call", id: Date.now(),
            params: {
                model: "res.district",
                method: "write",
                args: [[districtId], {
                    polygon_ids: [
                        [5, 0, 0],
                        ...points.map((p, i) => [0, 0, {
                            sequence: (i + 1) * 10,
                            lat: p.lat,
                            lng: p.lng,
                        }])
                    ]
                }],
                kwargs: {},
            }
        }),
        credentials: "same-origin",
    });
    return res.ok;
}

// ── Inject save button ─────────────────────────────────────────────────────────

function addSaveButton(districtId, getPoints) {
    const existing = document.getElementById("btn_polygon_save");
    if (existing) return;
    const clearBtn = document.getElementById("btn_polygon_clear");
    if (!clearBtn) return;

    const btn = document.createElement("button");
    btn.type = "button";
    btn.id = "btn_polygon_save";
    btn.className = "btn btn-sm btn-success";
    btn.textContent = "Save Boundaries";
    btn.addEventListener("click", async () => {
        const pts = getPoints();
        if (pts.length < 3) {
            alert("You must add at least 3 points to form a polygon.");
            return;
        }
        btn.disabled = true;
        btn.textContent = "Saving...";
        const ok = await savePointsViaRPC(districtId, pts);
        btn.disabled = false;
        if (ok) {
            btn.textContent = "✓ Saved";
            btn.className = "btn btn-sm btn-outline-success";
            setTimeout(() => {
                btn.textContent = "Save Boundaries";
                btn.className = "btn btn-sm btn-success";
            }, 2500);
            setTimeout(() => window.location.reload(), 1000);
        } else {
            btn.textContent = "Save Error";
            btn.className = "btn btn-sm btn-danger";
            setTimeout(() => {
                btn.textContent = "Save Boundaries";
                btn.className = "btn btn-sm btn-success";
            }, 3000);
        }
    });

    clearBtn.insertAdjacentElement("afterend", btn);
}

// ── Observe DOM for the map container ────────────────────────────────────────────

let _mapInitialised = false;

function tryInitMap() {
    const container = document.getElementById("district_polygon_map");
    if (!container || _mapInitialised) return;

    const url = window.location.pathname;
    const match = url.match(/\/(\d+)(?:\/|$)/);
    const districtId = match ? parseInt(match[1]) : null;

    _mapInitialised = true;
    container.style.background = "#f0f0f0";

    const existing = readPointsFromDOM();

    initPolygonMap(container, existing, (pts) => {
        // update status only — save is manual via button
    }).then(({ map, getPoints }) => {
        setTimeout(() => google.maps.event.trigger(map, "resize"), 100);
        if (districtId) {
            addSaveButton(districtId, getPoints);
        }
    }).catch((err) => {
        container.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#6c757d;">Google Maps API key not configured</div>';
        console.error("Google Maps load failed:", err);
    });
}

// Watch for map container to appear
const observer = new MutationObserver(() => {
    if (!_mapInitialised && document.getElementById("district_polygon_map")) {
        tryInitMap();
    }
});

function start() {
    observer.observe(document.body, { childList: true, subtree: true });
    tryInitMap();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
} else {
    start();
}
