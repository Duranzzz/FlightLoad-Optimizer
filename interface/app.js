/* ===================================================
   FlightLoad Optimizer — Three.js 3D Visualization
   v2: Fuselage, dynamic compartments, rejected cargo
   =================================================== */

(function () {
    'use strict';

    // ─── Color Palette for Loaded Boxes ────────────────
    const BOX_COLORS = [
        { hex: '#6366f1', name: 'Índigo' },
        { hex: '#a855f7', name: 'Púrpura' },
        { hex: '#22d3ee', name: 'Cian' },
        { hex: '#10b981', name: 'Esmeralda' },
        { hex: '#f59e0b', name: 'Ámbar' },
        { hex: '#f43f5e', name: 'Rosa' },
        { hex: '#3b82f6', name: 'Azul' },
        { hex: '#ef4444', name: 'Rojo' },
        { hex: '#14b8a6', name: 'Turquesa' },
        { hex: '#e879f9', name: 'Fucsia' },
    ];

    // Rejected boxes use muted red/orange tones
    const REJECTED_COLOR = '#7f1d1d';
    const REJECTED_EDGE_COLOR = '#f43f5e';

    // ─── DOM References ────────────────────────────────
    const loadingScreen = document.getElementById('loading-screen');
    const errorScreen = document.getElementById('error-screen');
    const app = document.getElementById('app');
    const threeContainer = document.getElementById('three-container');
    const tooltip = document.getElementById('tooltip');
    const tooltipTitle = document.getElementById('tooltip-title');
    const tooltipBody = document.getElementById('tooltip-body');

    // ─── State ─────────────────────────────────────────
    let scene, camera, renderer, controls;
    let raycaster, mouse;
    let boxMeshes = [];           // All interactive meshes (loaded + rejected)
    let hoveredMesh = null;
    let animationFrameId;
    let data = null;

    // Computed fuselage dimensions (set during buildScene)
    let fuselage = { length: 0, radius: 0, centerX: 0, centerZ: 0 };

    // ─── Fetch Data ────────────────────────────────────
    async function loadData() {
        try {
            const response = await fetch('resultado_optimizacion.json');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            data = await response.json();
            showApp();
        } catch (err) {
            console.error('Error al cargar datos:', err);
            showError();
        }
    }

    function showError() {
        loadingScreen.classList.add('hidden');
        errorScreen.classList.remove('hidden');
    }

    function showApp() {
        loadingScreen.classList.add('hidden');
        app.classList.remove('hidden');
        populateSidebar();
        initThree();
        buildScene();
        animate();
        initSidebarToggle();
    }

    // ─── Compute Global Metrics from Data ──────────────
    function computeMetrics() {
        const comps = data.compartimientos || [];

        // Find the maximum extent in Y (longitudinal axis)
        let maxY = 0;
        let maxLX = 0;
        let maxLZ = 0;

        comps.forEach(c => {
            const endY = (c.Ycomp || 0) + c.L_Y;
            if (endY > maxY) maxY = endY;
            if (c.L_X > maxLX) maxLX = c.L_X;
            if (c.L_Z > maxLZ) maxLZ = c.L_Z;
        });

        // Fuselage dimensions (with padding for nose/tail)
        const nosePadding = 3;
        const tailPadding = 4;
        fuselage.length = maxY + nosePadding + tailPadding;
        // Use half-diagonal + margin so fuselage fully encloses compartments
        const halfW = maxLX / 2;
        const halfH = maxLZ / 2;
        fuselage.radius = Math.sqrt(halfW * halfW + halfH * halfH) + 0.8;
        fuselage.centerX = maxLX / 2;   // Compartments centered on X
        fuselage.centerY = maxLZ / 2;   // Vertical center (Three.js Y-up)
        fuselage.centerZ = maxY / 2;    // Center of the longitudinal axis (mapped to Z in Three.js)
        fuselage.maxLX = maxLX;
        fuselage.maxLZ = maxLZ;
        fuselage.maxY = maxY;
        fuselage.nosePadding = nosePadding;
        fuselage.tailPadding = tailPadding;
    }

    // ─── Sidebar Population ────────────────────────────
    function populateSidebar() {
        // Airplane name
        document.getElementById('airplane-name').textContent = data.avion || '—';

        // Optimized value
        const val = data.valor_total_optimizado;
        document.getElementById('opt-value').textContent =
            val != null ? `$${val.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '—';

        // Compartments
        const compList = document.getElementById('compartments-list');
        compList.innerHTML = '';
        (data.compartimientos || []).forEach(c => {
            const el = document.createElement('div');
            el.className = 'comp-item';
            el.innerHTML = `
                <div class="comp-item-header">
                    <span class="comp-item-name">${c.id_comp}</span>
                    <span class="comp-item-badge">Comp</span>
                </div>
                <div class="comp-item-dims">${c.L_X} × ${c.L_Y} × ${c.L_Z} &nbsp;|&nbsp; Y₀ = ${c.Ycomp}</div>
            `;
            compList.appendChild(el);
        });

        // Loaded Boxes
        const boxList = document.getElementById('boxes-list');
        boxList.innerHTML = '';
        const legendItems = document.getElementById('legend-items');
        legendItems.innerHTML = '';

        // Wireframe legend
        const wfLegend = document.createElement('div');
        wfLegend.className = 'legend-item';
        wfLegend.innerHTML = `<span class="legend-color wireframe"></span><span>Compartimiento</span>`;
        legendItems.appendChild(wfLegend);

        (data.cajas_cargadas || []).forEach((b, i) => {
            const color = BOX_COLORS[i % BOX_COLORS.length];
            const el = document.createElement('div');
            el.className = 'box-item';
            el.dataset.boxId = b.id_caja;
            const valorStr = b.valor != null ? `$${Number(b.valor).toLocaleString('es-MX')}` : '';
            el.innerHTML = `
                <div class="box-item-header">
                    <span class="box-item-name">
                        <span class="box-color-dot" style="background:${color.hex}"></span>${b.id_caja}
                    </span>
                    <span class="box-item-weight">${b.peso} kg${valorStr ? ' · ' + valorStr : ''}</span>
                </div>
                <div class="box-item-dims">${b.dx}×${b.dy}×${b.dz} &nbsp;→&nbsp; ${b.compartimiento}</div>
            `;
            el.addEventListener('mouseenter', () => highlightBoxById(b.id_caja, true));
            el.addEventListener('mouseleave', () => highlightBoxById(b.id_caja, false));
            boxList.appendChild(el);

            // Legend
            const li = document.createElement('div');
            li.className = 'legend-item';
            li.innerHTML = `<span class="legend-color" style="background:${color.hex}"></span><span>${b.id_caja} (${b.peso} kg)</span>`;
            legendItems.appendChild(li);
        });

        // Rejected Boxes
        const rejectedList = document.getElementById('rejected-list');
        const rejectedEmpty = document.getElementById('rejected-empty');
        rejectedList.innerHTML = '';

        const rejectedBoxes = data.cajas_no_cargadas || [];
        if (rejectedBoxes.length === 0) {
            rejectedEmpty.classList.remove('hidden');
        } else {
            rejectedEmpty.classList.add('hidden');
            rejectedBoxes.forEach(b => {
                const el = document.createElement('div');
                el.className = 'box-item-rejected';
                el.dataset.boxId = b.id_caja;
                const rValorStr = b.valor != null ? `$${Number(b.valor).toLocaleString('es-MX')}` : '';
                el.innerHTML = `
                    <div class="box-item-header">
                        <span class="box-item-name">
                            <span class="box-color-dot" style="background:${REJECTED_EDGE_COLOR}; opacity:0.6"></span>${b.id_caja}
                        </span>
                        <span class="box-item-weight">${b.peso} kg${rValorStr ? ' · ' + rValorStr : ''}</span>
                    </div>
                    <div class="box-item-dims">${b.dx}×${b.dy}×${b.dz} &nbsp;— Rechazada</div>
                `;
                el.addEventListener('mouseenter', () => highlightBoxById(b.id_caja, true));
                el.addEventListener('mouseleave', () => highlightBoxById(b.id_caja, false));
                rejectedList.appendChild(el);
            });

            // Rejected legend
            const rejLegend = document.createElement('div');
            rejLegend.className = 'legend-item';
            rejLegend.innerHTML = `<span class="legend-color rejected"></span><span>Rechazada</span>`;
            legendItems.appendChild(rejLegend);
        }

        // Stats
        const totalBoxes = (data.cajas_cargadas || []).length;
        const totalWeight = (data.cajas_cargadas || []).reduce((s, b) => s + (b.peso || 0), 0);
        const totalComps = (data.compartimientos || []).length;
        const rejectedCount = rejectedBoxes.length;
        const rejectedWeight = rejectedBoxes.reduce((s, b) => s + (b.peso || 0), 0);

        // Volume utilization
        let totalCompVol = 0;
        (data.compartimientos || []).forEach(c => { totalCompVol += c.L_X * c.L_Y * c.L_Z; });
        let totalBoxVol = 0;
        (data.cajas_cargadas || []).forEach(b => { totalBoxVol += b.dx * b.dy * b.dz; });
        const volPct = totalCompVol > 0 ? ((totalBoxVol / totalCompVol) * 100).toFixed(1) : 0;

        document.getElementById('stat-total-boxes').textContent = totalBoxes;
        document.getElementById('stat-total-weight').textContent = totalWeight;
        document.getElementById('stat-total-comps').textContent = totalComps;
        document.getElementById('stat-volume-pct').textContent = `${volPct}%`;
        document.getElementById('stat-rejected-boxes').textContent = rejectedCount;
        document.getElementById('stat-rejected-weight').textContent = rejectedWeight;
    }

    // ─── Highlight a box from sidebar hover ────────────
    function highlightBoxById(id, on) {
        const mesh = boxMeshes.find(m => m.userData.id_caja === id);
        if (!mesh) return;
        if (on) {
            mesh.material.emissiveIntensity = 0.6;
            mesh.scale.set(1.04, 1.04, 1.04);
        } else {
            mesh.material.emissiveIntensity = mesh.userData._baseEmissive || 0.15;
            mesh.scale.set(1, 1, 1);
        }
    }

    // ─── Three.js Initialization ───────────────────────
    function initThree() {
        const w = threeContainer.clientWidth;
        const h = threeContainer.clientHeight;

        // Scene
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a0e1a);
        scene.fog = new THREE.FogExp2(0x0a0e1a, 0.008);

        // Camera
        camera = new THREE.PerspectiveCamera(50, w / h, 0.1, 500);
        camera.position.set(18, 14, 22);

        // Renderer
        renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(w, h);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.1;
        threeContainer.appendChild(renderer.domElement);

        // Controls
        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.08;
        controls.maxPolarAngle = Math.PI * 0.85;
        controls.minDistance = 5;
        controls.maxDistance = 120;
        controls.target.set(0, 4, 0);

        // Raycaster
        raycaster = new THREE.Raycaster();
        mouse = new THREE.Vector2(-999, -999);

        // Events
        renderer.domElement.addEventListener('mousemove', onMouseMove);
        window.addEventListener('resize', onResize);
    }

    // ─── Build the 3D Scene ────────────────────────────
    function buildScene() {
        computeMetrics();
        addLighting();
        addGroundPlane();
        addFuselage();
        addCompartments();
        addLoadedBoxes();
        addRejectedZone();
        addAxisLabels();
        centerCamera();
    }

    function addLighting() {
        // Ambient
        const ambient = new THREE.AmbientLight(0x8899bb, 0.5);
        scene.add(ambient);

        // Main directional
        const dir = new THREE.DirectionalLight(0xffffff, 0.9);
        dir.position.set(15, 25, 20);
        dir.castShadow = true;
        dir.shadow.mapSize.set(2048, 2048);
        dir.shadow.camera.left = -40;
        dir.shadow.camera.right = 40;
        dir.shadow.camera.top = 40;
        dir.shadow.camera.bottom = -40;
        scene.add(dir);

        // Fill light
        const fill = new THREE.DirectionalLight(0x6366f1, 0.3);
        fill.position.set(-10, 10, -15);
        scene.add(fill);

        // Rim / back light
        const rim = new THREE.DirectionalLight(0xa855f7, 0.2);
        rim.position.set(0, 5, -20);
        scene.add(rim);

        // Point light inside fuselage for interior glow
        const interiorLight = new THREE.PointLight(0x334488, 0.4, 30);
        interiorLight.position.set(fuselage.centerX, fuselage.centerY, fuselage.centerZ);
        scene.add(interiorLight);
    }

    function addGroundPlane() {
        // Grid
        const gridSize = 80;
        const gridHelper = new THREE.GridHelper(gridSize, gridSize, 0x1e293b, 0x1e293b);
        gridHelper.position.y = -0.01;
        scene.add(gridHelper);

        // Ground
        const groundGeo = new THREE.PlaneGeometry(gridSize, gridSize);
        const groundMat = new THREE.MeshStandardMaterial({
            color: 0x0f172a,
            roughness: 0.85,
            metalness: 0.1,
            transparent: true,
            opacity: 0.6,
        });
        const ground = new THREE.Mesh(groundGeo, groundMat);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        scene.add(ground);
    }

    // ─── Fuselage (Aircraft Silhouette) ────────────────
    function addFuselage() {
        const comps = data.compartimientos || [];
        if (comps.length === 0) return;

        // Compute fuselage cross-section from the widest/tallest compartment
        const maxLX = fuselage.maxLX;
        const maxLZ = fuselage.maxLZ;

        // Elliptical cross-section radii: must enclose the full compartment rectangle
        // Compartments span [0, maxLX] in X and [0, maxLZ] in height.
        // Fuselage is centered at (maxLX/2, maxLZ/2), so half-extents are maxLX/2 and maxLZ/2.
        // Add generous margin so nothing touches the hull.
        const margin = 1.0;
        const rxOuter = maxLX / 2 + margin;
        const ryOuter = maxLZ / 2 + margin;
        const cyFuselage = maxLZ / 2;  // vertical center of the ellipse

        // Fuselage total span in Y-axis (Three.js Z-axis)
        const yStart = -fuselage.nosePadding;
        const yEnd = fuselage.maxY + fuselage.tailPadding;
        const fLen = yEnd - yStart;
        const fCenter = (yStart + yEnd) / 2;

        // Center X for the fuselage (center of widest compartment)
        const cx = maxLX / 2;

        // Build fuselage using a LatheGeometry (rotational silhouette)
        // We'll create a tube-like shape with tapered nose and tail using custom geometry
        const segments = 48;
        const rings = 32;
        const points = [];

        // Profile curve: creates a cigar/tube shape
        for (let i = 0; i <= rings; i++) {
            const t = i / rings;    // 0 → 1 along the length
            const z = yStart + t * fLen;  // position along fuselage

            // Taper function: 1 at center, 0 at tips
            let taper;
            const noseEnd = 0;              // where the nose section ends (yStart → 0)
            const tailStart = fuselage.maxY; // where the tail section starts
            const noseRatio = (z - yStart) / (noseEnd - yStart);
            const tailRatio = (z - tailStart) / (yEnd - tailStart);

            if (z < noseEnd) {
                // Nose: smooth taper
                taper = Math.pow(Math.max(0, noseRatio), 0.6);
            } else if (z > tailStart) {
                // Tail: smooth taper (slightly more pointed)
                taper = Math.pow(Math.max(0, 1 - tailRatio), 0.8);
            } else {
                // Body: full width
                taper = 1;
            }

            points.push({ z, taper });
        }

        // Build the tube geometry as a series of elliptical rings
        const vertices = [];
        const indices = [];
        const normals = [];

        for (let r = 0; r <= rings; r++) {
            const { z, taper } = points[r];
            for (let s = 0; s <= segments; s++) {
                const theta = (s / segments) * Math.PI * 2;
                const px = cx + rxOuter * taper * Math.cos(theta);
                const py = cyFuselage + ryOuter * taper * Math.sin(theta);
                const pz = z;

                vertices.push(px, py, pz);

                // Normal (approximate)
                const nx = Math.cos(theta);
                const ny = Math.sin(theta);
                normals.push(nx, ny, 0);
            }
        }

        // Triangulate
        for (let r = 0; r < rings; r++) {
            for (let s = 0; s < segments; s++) {
                const a = r * (segments + 1) + s;
                const b = a + segments + 1;
                indices.push(a, b, a + 1);
                indices.push(b, b + 1, a + 1);
            }
        }

        const fuselageGeo = new THREE.BufferGeometry();
        fuselageGeo.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
        fuselageGeo.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
        fuselageGeo.setIndex(indices);
        fuselageGeo.computeVertexNormals();

        // Material: translucent silver/blue
        const fuselageMat = new THREE.MeshPhysicalMaterial({
            color: 0x8899bb,
            transparent: true,
            opacity: 0.12,
            roughness: 0.4,
            metalness: 0.6,
            side: THREE.DoubleSide,
            depthWrite: false,
            envMapIntensity: 0.5,
        });

        // In Three.js: X = model X, Y = model Z (up), Z = model Y (depth/longitudinal)
        // Our vertices are built as (px, py, pz) where py = vertical, pz = longitudinal
        // We need to swap Y/Z for Three.js coordinate system
        const posAttr = fuselageGeo.getAttribute('position');
        const normalAttr = fuselageGeo.getAttribute('normal');
        for (let i = 0; i < posAttr.count; i++) {
            const x = posAttr.getX(i);
            const y = posAttr.getY(i);  // vertical in model
            const z = posAttr.getZ(i);  // longitudinal in model
            posAttr.setXYZ(i, x, y, z); // X stays, Y = up (vertical), Z = depth (longitudinal)

            const nx = normalAttr.getX(i);
            const ny = normalAttr.getY(i);
            const nz = normalAttr.getZ(i);
            normalAttr.setXYZ(i, nx, ny, nz);
        }
        posAttr.needsUpdate = true;
        normalAttr.needsUpdate = true;
        fuselageGeo.computeVertexNormals();

        const fuselageMesh = new THREE.Mesh(fuselageGeo, fuselageMat);
        scene.add(fuselageMesh);

        // Add a wireframe outline for the fuselage
        const wireframeMat = new THREE.MeshBasicMaterial({
            color: 0x6366f1,
            wireframe: true,
            transparent: true,
            opacity: 0.06,
        });
        const wireframeMesh = new THREE.Mesh(fuselageGeo.clone(), wireframeMat);
        scene.add(wireframeMesh);

        // Fuselage center line (longitudinal axis indicator)
        const lineGeo = new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(cx, cyFuselage, yStart),
            new THREE.Vector3(cx, cyFuselage, yEnd),
        ]);
        const lineMat = new THREE.LineBasicMaterial({
            color: 0x6366f1,
            transparent: true,
            opacity: 0.2,
        });
        scene.add(new THREE.Line(lineGeo, lineMat));

        // Nose & Tail labels
        const labelY = cyFuselage + ryOuter * 0.6;
        addTextSprite('NOSE ✈', cx, labelY, yStart - 1.2, 0.5, '#6366f1');
        addTextSprite('TAIL', cx, labelY, yEnd + 1.2, 0.5, '#94a3b8');
    }

    // ─── Compartments as Wireframe Rooms ───────────────
    function addCompartments() {
        const comps = data.compartimientos || [];
        const maxLX = comps.length > 0 ? Math.max(...comps.map(c => c.L_X)) : 0;

        comps.forEach(comp => {
            const lx = comp.L_X;
            const ly = comp.L_Y;
            const lz = comp.L_Z;
            const yOff = comp.Ycomp || 0;

            // Center compartment on X if no explicit X offset
            const xOffset = comp.Xcomp != null ? comp.Xcomp : (maxLX - lx) / 2;

            // Three.js mapping: model(X,Y,Z) → three(X, Z_up, Y_depth)
            const geo = new THREE.BoxGeometry(lx, lz, ly);

            // Wireframe edges
            const edges = new THREE.EdgesGeometry(geo);
            const lineMat = new THREE.LineBasicMaterial({
                color: 0x94a3b8,
                linewidth: 1,
                transparent: true,
                opacity: 0.6,
            });
            const wireframe = new THREE.LineSegments(edges, lineMat);
            wireframe.position.set(
                xOffset + lx / 2,
                lz / 2,
                yOff + ly / 2
            );
            scene.add(wireframe);

            // Transparent floor for the compartment
            const floorGeo = new THREE.PlaneGeometry(lx, ly);
            const floorMat = new THREE.MeshStandardMaterial({
                color: 0x6366f1,
                transparent: true,
                opacity: 0.06,
                roughness: 0.9,
                side: THREE.DoubleSide,
                depthWrite: false,
            });
            const floor = new THREE.Mesh(floorGeo, floorMat);
            floor.rotation.x = -Math.PI / 2;
            floor.position.set(xOffset + lx / 2, 0.02, yOff + ly / 2);
            scene.add(floor);

            // Transparent walls (subtle fill)
            const fillMat = new THREE.MeshStandardMaterial({
                color: 0x6366f1,
                transparent: true,
                opacity: 0.03,
                roughness: 0.9,
                metalness: 0.0,
                side: THREE.DoubleSide,
                depthWrite: false,
            });
            const fillMesh = new THREE.Mesh(geo, fillMat);
            fillMesh.position.copy(wireframe.position);
            scene.add(fillMesh);

            // Label
            addTextSprite(
                comp.id_comp,
                xOffset + lx / 2,
                lz + 0.8,
                yOff + ly / 2,
                0.6,
                '#e2e8f0'
            );
        });
    }

    // ─── Loaded Boxes (Inside Compartments) ────────────
    function addLoadedBoxes() {
        const comps = data.compartimientos || [];
        const maxLX = comps.length > 0 ? Math.max(...comps.map(c => c.L_X)) : 0;

        // Build a lookup for compartment offsets
        const compOffsets = {};
        comps.forEach(c => {
            compOffsets[c.id_comp] = {
                Ycomp: c.Ycomp || 0,
                Xcomp: c.Xcomp != null ? c.Xcomp : (maxLX - c.L_X) / 2,
            };
        });

        (data.cajas_cargadas || []).forEach((box, i) => {
            const color = BOX_COLORS[i % BOX_COLORS.length];
            const offsets = compOffsets[box.compartimiento] || { Ycomp: 0, Xcomp: 0 };

            const geo = new THREE.BoxGeometry(box.dx, box.dz, box.dy);

            const mat = new THREE.MeshStandardMaterial({
                color: new THREE.Color(color.hex),
                roughness: 0.35,
                metalness: 0.15,
                emissive: new THREE.Color(color.hex),
                emissiveIntensity: 0.15,
                transparent: true,
                opacity: 0.88,
            });

            const mesh = new THREE.Mesh(geo, mat);
            // Position = compartment offset + local box position + half-size for centering
            mesh.position.set(
                offsets.Xcomp + box.x + box.dx / 2,
                box.z + box.dz / 2,
                offsets.Ycomp + box.y + box.dy / 2
            );
            mesh.castShadow = true;
            mesh.receiveShadow = true;

            // Metadata
            mesh.userData = {
                id_caja: box.id_caja,
                peso: box.peso,
                valor: box.valor,
                compartimiento: box.compartimiento,
                dims: `${box.dx} × ${box.dy} × ${box.dz}`,
                pos: `(${box.x}, ${box.y}, ${box.z})`,
                color: color.hex,
                isRejected: false,
                _baseEmissive: 0.15,
            };

            scene.add(mesh);
            boxMeshes.push(mesh);

            // White edges for definition
            const edgesGeo = new THREE.EdgesGeometry(geo);
            const edgesMat = new THREE.LineBasicMaterial({
                color: 0xffffff,
                transparent: true,
                opacity: 0.25,
            });
            const edgeLines = new THREE.LineSegments(edgesGeo, edgesMat);
            edgeLines.position.copy(mesh.position);
            scene.add(edgeLines);
        });
    }

    // ─── Rejected Cargo Zone (Hangar/Warehouse) ────────
    function addRejectedZone() {
        const rejectedBoxes = data.cajas_no_cargadas || [];
        if (rejectedBoxes.length === 0) return;

        const comps = data.compartimientos || [];
        const maxLX = comps.length > 0 ? Math.max(...comps.map(c => c.L_X)) : 5;

        // Place the rejected zone to the LEFT of the airplane (negative X)
        const zoneX = -maxLX * 1.2;  // Offset to the left
        const zoneZ = fuselage.maxY * 0.3;  // Roughly centered along the plane's length

        // Ground marking for the rejected zone
        const zonePadding = 1.5;
        const cols = Math.ceil(Math.sqrt(rejectedBoxes.length));

        // Compute grid layout dimensions
        let maxDx = 0, maxDy = 0;
        rejectedBoxes.forEach(b => {
            if (b.dx > maxDx) maxDx = b.dx;
            if (b.dy > maxDy) maxDy = b.dy;
        });
        const cellW = maxDx + 0.5;
        const cellD = maxDy + 0.5;
        const gridW = cols * cellW + zonePadding * 2;
        const gridD = Math.ceil(rejectedBoxes.length / cols) * cellD + zonePadding * 2;

        // Zone platform
        const platformGeo = new THREE.PlaneGeometry(gridW, gridD);
        const platformMat = new THREE.MeshStandardMaterial({
            color: 0x1c1017,
            roughness: 0.9,
            metalness: 0.0,
            transparent: true,
            opacity: 0.5,
        });
        const platform = new THREE.Mesh(platformGeo, platformMat);
        platform.rotation.x = -Math.PI / 2;
        platform.position.set(
            zoneX - gridW / 2,
            0.02,
            zoneZ + gridD / 2
        );
        platform.receiveShadow = true;
        scene.add(platform);

        // Zone border (wireframe rectangle)
        const borderGeo = new THREE.EdgesGeometry(new THREE.PlaneGeometry(gridW, gridD));
        const borderMat = new THREE.LineBasicMaterial({
            color: 0xf43f5e,
            transparent: true,
            opacity: 0.4,
        });
        const borderLines = new THREE.LineSegments(borderGeo, borderMat);
        borderLines.rotation.x = -Math.PI / 2;
        borderLines.position.copy(platform.position);
        borderLines.position.y = 0.03;
        scene.add(borderLines);

        // "CARGA RECHAZADA" label
        addTextSprite(
            '⛔ CARGA RECHAZADA',
            zoneX - gridW / 2,
            3.5,
            zoneZ - 0.5,
            0.6,
            '#f43f5e'
        );

        // Place rejected boxes in a grid
        rejectedBoxes.forEach((box, i) => {
            const col = i % cols;
            const row = Math.floor(i / cols);

            const bx = zoneX - zonePadding - col * cellW - cellW / 2;
            const bz = zoneZ + zonePadding + row * cellD + cellD / 2;
            const by = box.dz / 2;

            const geo = new THREE.BoxGeometry(box.dx, box.dz, box.dy);

            const mat = new THREE.MeshStandardMaterial({
                color: new THREE.Color(REJECTED_COLOR),
                roughness: 0.6,
                metalness: 0.05,
                emissive: new THREE.Color(REJECTED_EDGE_COLOR),
                emissiveIntensity: 0.08,
                transparent: true,
                opacity: 0.7,
            });

            const mesh = new THREE.Mesh(geo, mat);
            mesh.position.set(bx, by, bz);
            mesh.castShadow = true;
            mesh.receiveShadow = true;

            mesh.userData = {
                id_caja: box.id_caja,
                peso: box.peso,
                valor: box.valor,
                compartimiento: 'N/A — Rechazada',
                dims: `${box.dx} × ${box.dy} × ${box.dz}`,
                pos: 'Almacén',
                color: REJECTED_EDGE_COLOR,
                isRejected: true,
                _baseEmissive: 0.08,
            };

            scene.add(mesh);
            boxMeshes.push(mesh);

            // Red-tinted edges
            const edgesGeo = new THREE.EdgesGeometry(geo);
            const edgesMat = new THREE.LineBasicMaterial({
                color: new THREE.Color(REJECTED_EDGE_COLOR),
                transparent: true,
                opacity: 0.35,
            });
            const edgeLines = new THREE.LineSegments(edgesGeo, edgesMat);
            edgeLines.position.copy(mesh.position);
            scene.add(edgeLines);

            // ✕ marker (red strikethrough lines over the box)
            const crossSize = Math.min(box.dx, box.dy) * 0.4;
            const crossY = box.dz + 0.05;
            const crossGeo = new THREE.BufferGeometry().setFromPoints([
                new THREE.Vector3(bx - crossSize, crossY, bz - crossSize),
                new THREE.Vector3(bx + crossSize, crossY, bz + crossSize),
                new THREE.Vector3(bx + crossSize, crossY, bz - crossSize),
                new THREE.Vector3(bx - crossSize, crossY, bz + crossSize),
            ]);
            crossGeo.setIndex([0, 1, 2, 3]);
            const crossMat = new THREE.LineBasicMaterial({
                color: 0xf43f5e,
                transparent: true,
                opacity: 0.6,
            });
            scene.add(new THREE.LineSegments(crossGeo, crossMat));
        });
    }

    // ─── Sprite-based Text Labels ──────────────────────
    function addTextSprite(text, x, y, z, scale, color) {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = 512;
        canvas.height = 128;

        ctx.font = 'bold 44px Inter, sans-serif';
        ctx.fillStyle = color || '#ffffff';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text, 256, 64);

        const texture = new THREE.CanvasTexture(canvas);
        texture.minFilter = THREE.LinearFilter;

        const spriteMat = new THREE.SpriteMaterial({
            map: texture,
            transparent: true,
            depthWrite: false,
        });
        const sprite = new THREE.Sprite(spriteMat);
        sprite.position.set(x, y, z);
        sprite.scale.set(scale * 5, scale * 1.2, 1);
        scene.add(sprite);
    }

    function addAxisLabels() {
        // X axis
        addTextSprite('X', -1.5, 0.3, 0, 0.35, '#f43f5e');
        // Y axis (mapped to Z in Three.js)
        addTextSprite('Y', 0, 0.3, -1.5, 0.35, '#10b981');
        // Z axis (up)
        addTextSprite('Z', -0.5, 2.5, -0.5, 0.35, '#3b82f6');

        // Small axis lines
        const axLen = 2;
        const axMat = (c) => new THREE.LineBasicMaterial({ color: c, transparent: true, opacity: 0.6 });

        // X line (red)
        const xGeo = new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(0, 0.01, 0),
            new THREE.Vector3(axLen, 0.01, 0)
        ]);
        scene.add(new THREE.Line(xGeo, axMat(0xf43f5e)));

        // Y line (green → Z in threejs)
        const yGeo = new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(0, 0.01, 0),
            new THREE.Vector3(0, 0.01, axLen)
        ]);
        scene.add(new THREE.Line(yGeo, axMat(0x10b981)));

        // Z line (blue → Y in threejs)
        const zGeo = new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(0, 0, 0),
            new THREE.Vector3(0, axLen, 0)
        ]);
        scene.add(new THREE.Line(zGeo, axMat(0x3b82f6)));
    }

    function centerCamera() {
        const comps = data.compartimientos || [];
        let minX = Infinity, minY = Infinity, minZ = Infinity;
        let maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity;

        comps.forEach(c => {
            const y0 = c.Ycomp || 0;
            const xOff = c.Xcomp != null ? c.Xcomp : 0;
            minX = Math.min(minX, xOff);
            maxX = Math.max(maxX, xOff + c.L_X);
            minZ = Math.min(minZ, y0);
            maxZ = Math.max(maxZ, y0 + c.L_Y);
            minY = Math.min(minY, 0);
            maxY = Math.max(maxY, c.L_Z);
        });

        // Include rejected zone in the bounding calculation
        const rejected = data.cajas_no_cargadas || [];
        if (rejected.length > 0) {
            const maxLX = comps.length > 0 ? Math.max(...comps.map(c => c.L_X)) : 5;
            minX = Math.min(minX, -maxLX * 2.5);
        }

        const cx = (minX + maxX) / 2;
        const cy = (minY + maxY) / 2;
        const cz = (minZ + maxZ) / 2;

        controls.target.set(cx, cy, cz);

        const extentX = maxX - minX;
        const extentY = maxY - minY;
        const extentZ = maxZ - minZ;
        const extent = Math.max(extentX, extentY, extentZ);
        const dist = extent * 1.8;

        camera.position.set(cx + dist * 0.6, cy + dist * 0.5, cz + dist * 0.7);
        controls.update();
    }

    // ─── Mouse Interaction ─────────────────────────────
    function onMouseMove(event) {
        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        // Tooltip positioning (screen space)
        tooltip._screenX = event.clientX - rect.left;
        tooltip._screenY = event.clientY - rect.top;
    }

    function updateRaycast() {
        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(boxMeshes);

        if (intersects.length > 0) {
            const mesh = intersects[0].object;
            if (hoveredMesh !== mesh) {
                // Unhover previous
                if (hoveredMesh) {
                    hoveredMesh.material.emissiveIntensity = hoveredMesh.userData._baseEmissive || 0.15;
                    hoveredMesh.material.opacity = hoveredMesh.userData.isRejected ? 0.7 : 0.88;
                    hoveredMesh.scale.set(1, 1, 1);
                }
                // Hover current
                hoveredMesh = mesh;
                mesh.material.emissiveIntensity = 0.5;
                mesh.material.opacity = 1.0;
                mesh.scale.set(1.03, 1.03, 1.03);
            }

            // Update tooltip
            const ud = mesh.userData;
            const icon = ud.isRejected ? '🚫' : '📦';
            const valorLine = ud.valor != null ? `<br>Valor: <strong style="color:#10b981">$${Number(ud.valor).toLocaleString('es-MX')}</strong>` : '';
            tooltipTitle.textContent = `${icon} ${ud.id_caja}`;
            tooltipBody.innerHTML = `
                Peso: <strong>${ud.peso} kg</strong>${valorLine}<br>
                Dims: ${ud.dims}<br>
                ${ud.isRejected ? 'Estado: <strong style="color:#f43f5e">Rechazada</strong>' : `Pos: ${ud.pos}<br>Comp: ${ud.compartimiento}`}
            `;
            tooltip.classList.remove('hidden');
            tooltip.style.left = `${tooltip._screenX}px`;
            tooltip.style.top = `${tooltip._screenY}px`;

            renderer.domElement.style.cursor = 'pointer';
        } else {
            if (hoveredMesh) {
                hoveredMesh.material.emissiveIntensity = hoveredMesh.userData._baseEmissive || 0.15;
                hoveredMesh.material.opacity = hoveredMesh.userData.isRejected ? 0.7 : 0.88;
                hoveredMesh.scale.set(1, 1, 1);
                hoveredMesh = null;
            }
            tooltip.classList.add('hidden');
            renderer.domElement.style.cursor = 'grab';
        }
    }

    // ─── Animation Loop ────────────────────────────────
    function animate() {
        animationFrameId = requestAnimationFrame(animate);
        controls.update();
        updateRaycast();
        renderer.render(scene, camera);
    }

    // ─── Resize Handling ───────────────────────────────
    function onResize() {
        if (!renderer) return;
        const w = threeContainer.clientWidth;
        const h = threeContainer.clientHeight;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
    }

    // ─── Sidebar Toggle ────────────────────────────────
    function initSidebarToggle() {
        const sidebar = document.getElementById('sidebar');
        const toggleBtn = document.getElementById('sidebar-toggle');
        const iconHide = document.getElementById('toggle-icon-hide');
        const iconShow = document.getElementById('toggle-icon-show');

        if (!toggleBtn) return;

        toggleBtn.addEventListener('click', () => {
            const isCollapsed = sidebar.classList.toggle('collapsed');

            // Swap chevron icon
            iconHide.classList.toggle('hidden', isCollapsed);
            iconShow.classList.toggle('hidden', !isCollapsed);

            // After the CSS transition ends, resize the 3D renderer
            // to fill the newly available space
            setTimeout(() => onResize(), 370);
        });
    }

    // ─── Bootstrap ─────────────────────────────────────
    loadData();

})();
