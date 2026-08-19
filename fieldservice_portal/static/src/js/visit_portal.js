/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";

let _gmapsReady = null;
let _visitBookingInitialized = false;

(function () {
    if (!document.getElementById("vbf")) {
        return;
    }

    // ── Google Maps loader ────────────────────────────────────────────
    function loadGoogleMaps() {
        if (_gmapsReady) return _gmapsReady;
        _gmapsReady = rpc('/website/google_maps_api_key', {}).then(function(resp){
            var data = JSON.parse(resp || '{}');
            var key = data.google_maps_api_key || '';
            window._gmapApiKey = key;
            if (!key) {
                var message = document.createElement('div');
                message.className = 'd-flex align-items-center justify-content-center h-100 text-muted';
                message.textContent = document.getElementById('visitMapKeyMissing').textContent.trim();
                document.getElementById('visitLocationMap').replaceChildren(message);
                throw new Error('Google Maps API key not configured');
            }
            return new Promise(function(resolve, reject){
                window._gmapsCallback = function(){ resolve(); };
                var s = document.createElement('script');
                var mapLanguage = document.getElementById('vbf').dataset.mapLanguage || 'en';
                s.src = 'https://maps.googleapis.com/maps/api/js?v=3.exp&libraries=places,geometry&language=' + encodeURIComponent(mapLanguage) + '&callback=_gmapsCallback&key=' + encodeURIComponent(key);
                s.onerror = function(){ reject(new Error('Google Maps failed to load')); };
                document.head.appendChild(s);
            });
        });
        return _gmapsReady;
    }

    function initVisitBooking() {
        if (_visitBookingInitialized) return;
        if (!document.getElementById('visitDistrictPrefix')) {
            setTimeout(initVisitBooking, 10);
            return;
        }
        _visitBookingInitialized = true;
        try {
        var map, marker;
        var selectedLat = null, selectedLng = null, selectedRouteId = null;
        var selectedDistrictId = null;
        var geocodedAddress = '';
        var googleDistrictName = null;
        var allRoutes = [];
        var locationPinned = false;
        var manualLocation = false;
        var portalDefaults = document.getElementById('vbf').dataset;
        var selectedCountry = portalDefaults.countryCode || 'EG';
        function translatedText(id) {
            return document.getElementById(id).textContent.trim();
        }
        var dayNames = ['visitSunday','visitMonday','visitTuesday','visitWednesday','visitThursday','visitFriday','visitSaturday'].map(translatedText);
        var monthNames = ['visitJanuary','visitFebruary','visitMarch','visitApril','visitMay','visitJune','visitJuly','visitAugust','visitSeptember','visitOctober','visitNovember','visitDecember'].map(translatedText);

        // ===== STEPPER =====
        function goToStep(step) {
            document.querySelectorAll('.vbf-section').forEach(function(s){ s.classList.remove('active'); });
            document.getElementById('vstep1').className = 'vbf-step';
            document.getElementById('vstep2').className = 'vbf-step';
            document.getElementById('vstep3').className = 'vbf-step';
            document.getElementById('vstepLine1').className = 'vbf-step-line';
            document.getElementById('vstepLine2').className = 'vbf-step-line';

            if (step === 1) {
                document.getElementById('vSection1').classList.add('active');
                document.getElementById('vstep1').className = 'vbf-step active';
                if (map) setTimeout(function(){ google.maps.event.trigger(map, 'resize'); }, 200);
            } else if (step === 2) {
                document.getElementById('vSection2').classList.add('active');
                document.getElementById('vstep1').className = 'vbf-step done';
                document.getElementById('vstepLine1').className = 'vbf-step-line done';
                document.getElementById('vstep2').className = 'vbf-step active';
                populateAddressFields();
                checkUnitInput();
            } else {
                document.getElementById('vSection3').classList.add('active');
                document.getElementById('vstep1').className = 'vbf-step done';
                document.getElementById('vstep2').className = 'vbf-step done';
                document.getElementById('vstep3').className = 'vbf-step active';
                document.getElementById('vstepLine1').className = 'vbf-step-line done';
                document.getElementById('vstepLine2').className = 'vbf-step-line done';
                loadRoutes();
            }
            if (manualLocation) applyManualStepper();
        }

        function applyManualStepper() {
            document.getElementById('vstep1').classList.add('d-none');
            document.getElementById('vstepLine1').classList.add('d-none');
            document.querySelector('#vstep2 .vbf-step-circle').textContent = '1';
            document.querySelector('#vstep2 .vbf-step-label').textContent = translatedText('visitManualStepAddress');
            document.querySelector('#vstep3 .vbf-step-circle').textContent = '2';
            document.querySelector('#vstep3 .vbf-step-label').textContent = translatedText('visitManualStepAppointment');
            document.getElementById('backToStep1Btn').classList.add('d-none');
        }

        function enableManualLocationMode() {
            manualLocation = true;
            document.querySelectorAll('.manual-location-only').forEach(function(element){
                element.classList.remove('d-none');
            });
            document.querySelectorAll('.map-address-only').forEach(function(element){
                element.classList.add('d-none');
            });
            updateRegionOptions();
            goToStep(2);
        }

        document.getElementById('toStep2Btn').addEventListener('click', function(){ goToStep(2); });
        document.getElementById('backToStep1Btn').addEventListener('click', function(){ goToStep(1); });
        document.getElementById('toStep3Btn').addEventListener('click', function(){ goToStep(3); });
        document.getElementById('backToStep2Btn').addEventListener('click', function(){ goToStep(2); });

        // ===== ADDRESS FIELDS (Step 2) =====
        function populateAddressFields() {
            if (selectedLat && selectedLng) {
                document.getElementById('coordsDisplay').textContent =
                    selectedLat.toFixed(5) + ', ' + selectedLng.toFixed(5);
            }
            var streetEl = document.getElementById('street_input');
            var cityEl   = document.getElementById('city_input');
            var zipEl    = document.getElementById('zip_input');
            var distEl   = document.getElementById('district_display');

            if (!streetEl._userEdited) streetEl.value = document.getElementById('street_field').value;
            if (!cityEl._userEdited)   cityEl.value   = document.getElementById('city_field').value;
            if (!zipEl._userEdited)     zipEl.value   = document.getElementById('zip_field').value;

            if (selectedDistrictId) {
                var d = allDistricts.find(function(x){ return x.id === selectedDistrictId; });
                distEl.value = d ? d.name : '';
            } else {
                distEl.value = '';
            }
        }

        ['street_input','city_input','zip_input'].forEach(function(id){
            document.getElementById(id).addEventListener('input', function(){
                this._userEdited = true;
            });
        });

        function checkUnitInput() {
            var street = document.getElementById('street_input').value.trim();
            var unit   = document.getElementById('unit_input').value.trim();
            var state = document.getElementById('state_select').value;
            var regionSelect = document.getElementById('region_select');
            var regionInput = document.getElementById('region_input');
            var districtSelect = document.getElementById('district_select');
            var region = regionSelect.classList.contains('d-none')
                ? regionInput.value.trim()
                : regionSelect.value;
            var city = manualLocation ? document.getElementById('manual_city_input').value.trim() : true;
            var district = manualLocation ? document.getElementById('district_select').value : true;
            var btn    = document.getElementById('toStep3Btn');
            if (street && unit && city && district && (!manualLocation || (state && region))) { btn.removeAttribute('disabled'); }
            else { btn.setAttribute('disabled','disabled'); }
        }
        document.getElementById('street_input').addEventListener('input', checkUnitInput);
        document.getElementById('unit_input').addEventListener('input', checkUnitInput);
        document.getElementById('manual_city_input').addEventListener('input', checkUnitInput);
        document.getElementById('district_select').addEventListener('change', checkUnitInput);

        function updateRegionOptions() {
            var stateId = document.getElementById('state_select').value;
            var regionSelect = document.getElementById('region_select');
            var regionInput = document.getElementById('region_input');
            var districtSelect = document.getElementById('district_select');
            var matchingRegions = 0;
            Array.from(regionSelect.options).forEach(function(option, index){
                if (!index) return;
                var matches = Boolean(stateId) && option.dataset.stateId === stateId;
                option.hidden = !matches;
                option.disabled = !matches;
                if (matches) matchingRegions += 1;
            });
            regionSelect.value = '';
            regionInput.value = '';
            Array.from(districtSelect.options).forEach(function(option, index){
                if (!index) return;
                var matches = Boolean(stateId) && option.dataset.regionId === regionSelect.value;
                option.hidden = !matches;
                option.disabled = !matches;
            });
            regionSelect.classList.toggle('d-none', matchingRegions === 0);
            regionInput.classList.toggle('d-none', matchingRegions > 0);
            checkUnitInput();
        }
        document.getElementById('state_select').addEventListener('change', updateRegionOptions);
        document.getElementById('region_select').addEventListener('change', function(){
            var regionId = this.value;
            Array.from(document.getElementById('district_select').options).forEach(function(option, index){
                if (!index) return;
                var matches = Boolean(regionId) && option.dataset.regionId === regionId;
                option.hidden = !matches;
                option.disabled = !matches;
            });
            document.getElementById('district_select').value = '';
            checkUnitInput();
        });
        document.getElementById('region_input').addEventListener('input', checkUnitInput);

        // ===== DISTRICT POLYGONS =====
        var districtPolygons = [];
        var gmapPolygons = [];
        var allDistricts = [];

        function loadDistrictPolygons() {
            rpc('/my/visit/districts', {}).then(function(data){
                if (data.districts && data.districts.length) {
                    allDistricts = data.districts;
                    districtPolygons = data.districts.filter(function(d){ return d.polygon && d.polygon.length >= 3; });
                    drawDistrictPolygons();
                    if (selectedLat && locationPinned) checkDistrictCoverage(selectedLat, selectedLng, geocodedAddress);
                }
            }).catch(function(){});
        }

        function drawDistrictPolygons() {
            if (!map) return;
            gmapPolygons.forEach(function(p){ p.setMap(null); });
            gmapPolygons = [];
            districtPolygons.forEach(function(d){
                if (!d.polygon || d.polygon.length < 3) return;
                var paths = d.polygon.map(function(p){ return {lat: p.lat, lng: p.lng}; });
                var poly = new google.maps.Polygon({
                    paths: paths,
                    strokeColor: '#198754',
                    strokeOpacity: 0.8,
                    strokeWeight: 1.5,
                    strokeDashArray: '6,4',
                    fillColor: '#d1e7dd',
                    fillOpacity: 0.15,
                    map: map,
                    clickable: false,
                });
                // Tooltip on hover
                var infoWin = new google.maps.InfoWindow();
                poly.addListener('mouseover', function(e){
                    var districtLabel = document.createElement('span');
                    districtLabel.textContent = d.name;
                    infoWin.setContent(districtLabel);
                    infoWin.setPosition(e.latLng);
                    infoWin.open(map);
                });
                poly.addListener('mouseout', function(){
                    infoWin.close();
                });
                gmapPolygons.push(poly);
            });
        }

        function checkDistrictCoverage(lat, lng, address) {
            var nextBtn = document.getElementById('toStep2Btn');

            if (!locationPinned) {
                nextBtn.setAttribute('disabled','disabled');
                return;
            }
            if (!allDistricts.length) {
                nextBtn.removeAttribute('disabled');
                return;
            }

            function nameMatch(name, list) {
                for (var x = 0; x < list.length; x++) {
                    if (name === list[x].name) return list[x];
                }
                return null;
            }

            var matched = null;

            // PRIORITY 1: Google sublocality/neighborhood text match
            if (!matched && googleDistrictName) {
                matched = nameMatch(googleDistrictName, allDistricts)
                    || nameMatch(translatedText('visitDistrictPrefix') + ' ' + googleDistrictName, allDistricts);
            }

            // PRIORITY 2: Address string contains a district name
            if (!matched && address) {
                for (var m = 0; m < allDistricts.length; m++) {
                    if (address.indexOf(allDistricts[m].name) !== -1) {
                        matched = allDistricts[m]; break;
                    }
                }
            }

            // PRIORITY 3: Polygon containment (geometry fallback)
            if (!matched) {
                var point = new google.maps.LatLng(lat, lng);
                var polygonMatches = [];
                for (var i = 0; i < gmapPolygons.length; i++) {
                    if (google.maps.geometry.poly.containsLocation(point, gmapPolygons[i])) {
                        polygonMatches.push(districtPolygons[i]);
                    }
                }
                if (polygonMatches.length === 1) {
                    matched = polygonMatches[0];
                } else if (polygonMatches.length > 1) {
                    matched = polygonMatches[0];
                }
            }

            selectedDistrictId = matched ? matched.id : null;
            var warningEl = document.getElementById('districtWarning');

            if (matched) {
                warningEl.classList.add('d-none');
            } else {
                warningEl.classList.remove('d-none');
            }

            if (locationPinned) {
                nextBtn.removeAttribute('disabled');
            } else {
                nextBtn.setAttribute('disabled','disabled');
            }
        }

        // ===== MAP =====
        function initMap() {
            if (map) { setTimeout(function(){ google.maps.event.trigger(map, 'resize'); }, 200); return; }
            var defaultLat = parseFloat(portalDefaults.defaultLatitude) || 30.0444;
            var defaultLng = parseFloat(portalDefaults.defaultLongitude) || 31.2357;
            map = new google.maps.Map(document.getElementById('visitLocationMap'), {
                center: {lat: defaultLat, lng: defaultLng},
                zoom: 13,
                mapTypeControl: false,
                streetViewControl: false,
                fullscreenControl: true,
            });
            marker = new google.maps.Marker({
                position: {lat: defaultLat, lng: defaultLng},
                draggable: true,
                map: map,
            });
            marker.addListener('dragend', function(){
                var pos = marker.getPosition();
                locationPinned = true;
                setLocation(pos.lat(), pos.lng());
            });
            map.addListener('click', function(e){
                placeMarker(e.latLng.lat(), e.latLng.lng());
            });
        }

        function placeMarker(lat, lng) {
            marker.setPosition({lat: lat, lng: lng});
            if (!marker.getMap()) marker.setMap(map);
            locationPinned = true;
            setLocation(lat, lng);
            ['street_input','city_input','zip_input'].forEach(function(id){
                document.getElementById(id)._userEdited = false;
            });
        }

        function setLocation(lat, lng) {
            selectedLat = lat; selectedLng = lng;
            document.getElementById('coordsDisplay').textContent =
                lat.toFixed(5) + ', ' + lng.toFixed(5);
            googleDistrictName = null;
            checkDistrictCoverage(lat, lng, geocodedAddress);
            reverseGeocode(lat, lng);
        }

        function reverseGeocode(lat, lng) {
            var geocoder = new google.maps.Geocoder();
            geocoder.geocode({location: {lat: lat, lng: lng}, language: 'ar'}, function(results, status){
                if (status !== 'OK' || !results || !results.length) return;
                var result = results[0];
                geocodedAddress = result.formatted_address || '';
                document.getElementById('locationLabel').textContent = geocodedAddress;

                // Extract standard Google address components.
                var street = '', city = '', cityFallback = '', zip = '';
                googleDistrictName = null;
                var ac = result.address_components || [];
                for (var i = 0; i < ac.length; i++) {
                    var types = ac[i].types;
                    if (types.indexOf('street_number') !== -1) {
                        street = ac[i].long_name + (street ? ' ' : '') + street;
                    }
                    if (types.indexOf('route') !== -1) {
                        street += (street ? ' ' : '') + ac[i].long_name;
                    }
                    if (types.indexOf('locality') !== -1) {
                        city = ac[i].long_name;
                    } else if (types.indexOf('administrative_area_level_2') !== -1) {
                        cityFallback = ac[i].long_name;
                    }
                    if (types.indexOf('postal_code') !== -1) {
                        zip = ac[i].long_name;
                    }
                    if (types.indexOf('country') !== -1) {
                        selectedCountry = ac[i].short_name;
                    }
                    if (types.indexOf('sublocality_level_1') !== -1 || types.indexOf('neighborhood') !== -1) {
                        googleDistrictName = ac[i].long_name;
                    }
                }
                if (!city) city = cityFallback;

                document.getElementById('street_field').value = street;
                document.getElementById('city_field').value = city;
                document.getElementById('zip_field').value = zip;

                var streetEl = document.getElementById('street_input');
                var cityEl   = document.getElementById('city_input');
                var zipEl    = document.getElementById('zip_input');
                if (!streetEl._userEdited) streetEl.value = street;
                if (!cityEl._userEdited)   cityEl.value   = city;
                if (!zipEl._userEdited)     zipEl.value   = zip;

                checkDistrictCoverage(selectedLat, selectedLng, geocodedAddress);
            });
        }

        document.getElementById('locateMeBtn').addEventListener('click', function(){
            if (!navigator.geolocation) return;
            var btn = this;
            setLocateButton(btn, true);
            navigator.geolocation.getCurrentPosition(function(pos){
                setLocateButton(btn, false);
                map.setCenter({lat: pos.coords.latitude, lng: pos.coords.longitude});
                map.setZoom(16);
                placeMarker(pos.coords.latitude, pos.coords.longitude);
            }, function(){
                setLocateButton(btn, false);
            });
        });

        function setLocateButton(button, loading) {
            var icon = document.createElement('i');
            icon.className = loading ? 'fa fa-spinner fa-spin me-1' : 'fa fa-crosshairs me-1';
            button.replaceChildren(icon, document.createTextNode(loading ? translatedText('visitLocating') : translatedText('visitMyLocation')));
        }

        // Load Google Maps then init
        loadGoogleMaps().then(function(){
            initMap();
            loadDistrictPolygons();
        }).catch(function(){
            selectedLat = null;
            selectedLng = null;
            enableManualLocationMode();
        });

        // ===== ROUTES =====
        async function loadRoutes() {
            if (allRoutes.length) { renderWeek(); return; }
            document.getElementById('routeLoading').classList.remove('d-none');
            document.getElementById('routesContainer').classList.add('d-none');
            document.getElementById('routeEmpty').classList.add('d-none');

            try {
                var data = await rpc('/my/visit/routes', {});
                document.getElementById('routeLoading').classList.add('d-none');
                if (data.success && data.routes) {
                    allRoutes = data.routes;
                }
                renderWeek();
                if (allRoutes.length) {
                    document.getElementById('routesContainer').classList.remove('d-none');
                }
            } catch {
                document.getElementById('routeLoading').classList.add('d-none');
                var empty = document.getElementById('routeEmpty');
                empty.querySelector('p').textContent = translatedText('visitRouteLoadError');
                empty.classList.remove('d-none');
            }
        }

        function dateStr(d) {
            return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0');
        }

        function renderWeek() {
            if (!allRoutes.length) {
                document.getElementById('routesContainer').classList.add('d-none');
                document.getElementById('routeEmpty').classList.remove('d-none');
                return;
            }
            var today = new Date(); today.setHours(0,0,0,0);
            var byDate = {};
            allRoutes.forEach(function(r){ if (!byDate[r.date]) byDate[r.date] = []; byDate[r.date].push(r); });

            // Find the last date that has available slots
            var lastSlotDate = null;
            allRoutes.forEach(function(r){
                if (!lastSlotDate || r.date > lastSlotDate) lastSlotDate = r.date;
            });

            // Match the backend's four-week availability window.
            var maxDays = 28;
            var days = [];
            for (var i = 1; i <= maxDays; i++) {
                var d = new Date(today); d.setDate(today.getDate() + i);
                var ds = dateStr(d);
                if (lastSlotDate && ds > lastSlotDate) break;
                days.push(d);
            }
            if (!days.length) {
                document.getElementById('routesContainer').classList.add('d-none');
                document.getElementById('routeEmpty').classList.remove('d-none');
                return;
            }

            var wrapper = document.getElementById('visitBookingDays');
            wrapper.replaceChildren();

            days.forEach(function(d) {
                var ds = dateStr(d);
                var slots = byDate[ds] || [];
                var slide = document.createElement('div');
                slide.className = 'booking-day';
                var card = document.createElement('div');
                card.className = 'day-card' + (slots.length ? ' has-routes' : '');
                card.setAttribute('data-date', ds);
                var dayName = document.createElement('div');
                dayName.className = 'day-name';
                dayName.textContent = dayNames[d.getDay()];
                var dayNumber = document.createElement('div');
                dayNumber.className = 'day-num';
                dayNumber.textContent = String(d.getDate());
                card.append(dayName, dayNumber);
                if (slots.length) {
                    slots.forEach(function(slot){
                        var tag = document.createElement('button');
                        var routeName = slot.route_name || translatedText('visitAppointment');
                        tag.type = 'button';
                        tag.className = 'route-tag';
                        tag.dataset.routeId = String(slot.id);
                        tag.dataset.routeName = dayNames[d.getDay()] + ' ' + d.getDate() + ' ' + monthNames[d.getMonth()] + ' - ' + routeName;
                        var label = document.createElement('small');
                        label.textContent = routeName;
                        tag.appendChild(label);
                        tag.addEventListener('click', function(){
                            document.querySelectorAll('#vbf .route-tag').forEach(function(item){ item.classList.remove('selected'); });
                            tag.classList.add('selected');
                            selectedRouteId = tag.dataset.routeId;
                            document.getElementById('selectedSlotInfo').textContent = tag.dataset.routeName;
                            document.getElementById('selectedSlotDisplay').classList.remove('d-none');
                            document.getElementById('submitVisitBtn').removeAttribute('disabled');
                        });
                        card.appendChild(tag);
                    });
                } else {
                    var noRoutes = document.createElement('div');
                    noRoutes.className = 'day-no-routes mt-2';
                    noRoutes.textContent = translatedText('visitNone');
                    card.appendChild(noRoutes);
                }
                slide.appendChild(card);
                wrapper.appendChild(slide);
            });
        }

        // ===== SUBMIT =====
        function setSubmitButton(button, loading) {
            var icon = document.createElement('i');
            icon.className = loading ? 'fa fa-spinner fa-spin me-2' : 'fa fa-check me-2';
            button.replaceChildren(icon, document.createTextNode(loading ? translatedText('visitBooking') : translatedText('visitConfirm')));
        }

        function showSubmitError(message) {
            var errorPanel = document.getElementById('visitInlineError');
            document.getElementById('visitInlineErrorMessage').textContent = message;
            errorPanel.classList.remove('d-none');
            errorPanel.focus();
        }

        function clearSubmitError() {
            document.getElementById('visitInlineError').classList.add('d-none');
        }

        document.getElementById('submitVisitBtn').addEventListener('click', async function(){
            var btn = this;
            clearSubmitError();
            btn.setAttribute('disabled','disabled');
            setSubmitButton(btn, true);
            try {
                var data = await rpc('/my/visit/submit', {
                    latitude:  selectedLat,
                    longitude: selectedLng,
                    street: document.getElementById('street_input').value,
                    unit:   document.getElementById('unit_input').value,
                    city:   manualLocation ? document.getElementById('manual_city_input').value : document.getElementById('city_input').value,
                    zip:    document.getElementById('zip_input').value,
                    state_id: document.getElementById('state_select').value,
                    region_id: document.getElementById('region_select').classList.contains('d-none') ? null : document.getElementById('region_select').value,
                    manual_region: document.getElementById('region_input').classList.contains('d-none') ? '' : document.getElementById('region_input').value,
                    manual_location: manualLocation,
                    route_id:    selectedRouteId,
                    district_id: manualLocation ? document.getElementById('district_select').value : selectedDistrictId,
                    country_code: selectedCountry,
                });
                if (data.success) {
                    window.location.href = data.redirect;
                } else {
                    showSubmitError(data.error || translatedText('visitSubmitError'));
                    btn.removeAttribute('disabled');
                    setSubmitButton(btn, false);
                }
            } catch {
                showSubmitError(translatedText('visitSubmitError'));
                btn.removeAttribute('disabled');
                setSubmitButton(btn, false);
            }
        });
        } catch (error) {
            _visitBookingInitialized = false;
            setTimeout(initVisitBooking, 50);
        }
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initVisitBooking);
    } else {
        initVisitBooking();
    }
    setTimeout(initVisitBooking, 0);
})();
