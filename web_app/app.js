document.addEventListener('DOMContentLoaded', () => {
    const compoundList = document.getElementById('compoundList');
    const searchInput = document.getElementById('searchInput');
    const compoundTitle = document.getElementById('compoundTitle');
    const compoundBadges = document.getElementById('compoundBadges');
    const smilesCanvas = document.getElementById('smilesCanvas');
    const smilesText = document.getElementById('smilesText');
    const detailsBody = document.getElementById('detailsBody');
    const viewerLoading = document.getElementById('viewerLoading');
    
    let compounds = [];
    let currentViewer = null;
    let smilesDrawer = new SmilesDrawer.Drawer({
        width: 500,
        height: 400,
        theme: 'dark'
    });

    // Initialize 3D Viewer
    let viewerConfig = { backgroundColor: '#1e293b' };
    currentViewer = $3Dmol.createViewer("viewer3d", viewerConfig);

    // Fetch compounds from API
    fetch('/api/compounds')
        .then(response => response.json())
        .then(data => {
            compounds = data;
            renderList(compounds);
        })
        .catch(err => console.error('Failed to fetch compounds:', err));

    // Search functionality
    searchInput.addEventListener('input', (e) => {
        const term = e.target.value.toLowerCase();
        const filtered = compounds.filter(c => 
            c.marker_compound.toLowerCase().includes(term) || 
            c.compound_type.toLowerCase().includes(term)
        );
        renderList(filtered);
    });

    function renderList(items) {
        compoundList.innerHTML = '';
        items.forEach(c => {
            const li = document.createElement('li');
            li.className = 'compound-item';
            li.innerHTML = `
                <div class="compound-name">${c.marker_compound}</div>
                <div class="compound-formula">${c.formula_verified} • ${c.compound_type}</div>
            `;
            li.addEventListener('click', () => {
                document.querySelectorAll('.compound-item').forEach(el => el.classList.remove('active'));
                li.classList.add('active');
                selectCompound(c);
            });
            compoundList.appendChild(li);
        });
    }

    function selectCompound(c) {
        compoundTitle.textContent = c.marker_compound;
        
        // Render badges
        compoundBadges.innerHTML = '';
        if(c.temperament && c.temperament !== 'Unknown' && c.temperament !== '') {
            const parts = c.temperament.split('-');
            parts.forEach(p => {
                if(p !== 'NS' && p !== 'Unknown') {
                    const badge = document.createElement('span');
                    badge.className = `badge ${p.toLowerCase()}`;
                    badge.textContent = p;
                    compoundBadges.appendChild(badge);
                }
            });
        }
        
        // Render 2D
        if(c.smiles) {
            smilesText.textContent = c.smiles;
            SmilesDrawer.parse(c.smiles, function(tree) {
                smilesDrawer.draw(tree, 'smilesCanvas', 'dark', false);
            }, function(err) {
                console.error(err);
                const ctx = smilesCanvas.getContext('2d');
                ctx.clearRect(0,0,500,400);
                ctx.fillStyle = '#94a3b8';
                ctx.font = '14px Inter';
                ctx.fillText('Could not parse SMILES for 2D', 150, 200);
            });
        }

        // Render details
        detailsBody.innerHTML = `
            <div class="details-grid">
                <div class="detail-item">
                    <div class="detail-label">Formula</div>
                    <div class="detail-value">${c.formula_verified || 'N/A'}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Class</div>
                    <div class="detail-value">${c.compound_type || 'Unknown'}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Verification</div>
                    <div class="detail-value" style="font-size:0.9rem">${c.verification_strength || 'Unknown'}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Data Sources</div>
                    <div class="detail-value" style="font-size:0.9rem">${(c.source_files || '').replace(/;/g, ', ')}</div>
                </div>
            </div>
        `;

        // Render 3D
        load3DModel(c.marker_compound, c.smiles);
    }

    function load3DModel(name, smiles) {
        currentViewer.clear();
        viewerLoading.style.display = 'block';
        
        // Try fetching SDF by name from PubChem
        const encodedName = encodeURIComponent(name);
        const url = `https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/${encodedName}/SDF?record_type=3d`;
        
        fetch(url)
            .then(response => {
                if(!response.ok) throw new Error('Network response was not ok');
                return response.text();
            })
            .then(sdfData => {
                viewerLoading.style.display = 'none';
                currentViewer.addModel(sdfData, "sdf");
                currentViewer.setStyle({}, {stick: {radius: 0.15}, sphere: {scale: 0.3}});
                currentViewer.zoomTo();
                currentViewer.render();
            })
            .catch(err => {
                // Fallback to 2D SDF if 3D fails or try SMILES
                const fallbackUrl = `https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/${encodeURIComponent(smiles)}/SDF`;
                fetch(fallbackUrl)
                    .then(res => res.ok ? res.text() : Promise.reject('Fallback failed'))
                    .then(sdfData => {
                        viewerLoading.style.display = 'none';
                        currentViewer.addModel(sdfData, "sdf");
                        currentViewer.setStyle({}, {stick: {radius: 0.15}, sphere: {scale: 0.3}});
                        currentViewer.zoomTo();
                        currentViewer.render();
                    })
                    .catch(e => {
                        console.warn("Could not load 3D model for", name);
                        viewerLoading.style.display = 'none';
                        viewerLoading.textContent = '3D not available';
                        viewerLoading.style.display = 'block';
                    });
            });
    }
});
