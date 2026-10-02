/* 
  Tourist Crowd Level Planner - Main Application Logic
*/

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    loadAttractions();
    loadDashboardStats();

    // Default Date to today
    const today = new Date().toISOString().split('T')[0];
    const dateInput = document.getElementById('planner-date');
    if (dateInput) {
        dateInput.value = today;
    }

    // Attach Event Listeners
    const plannerForm = document.getElementById('planner-form');
    if (plannerForm) {
        plannerForm.addEventListener('submit', handlePredictSubmit);
    }

    const histSearch = document.getElementById('hist-search');
    if (histSearch) {
        histSearch.addEventListener('input', debounce(() => loadHistoricalTable(1), 300));
    }

    const histAttr = document.getElementById('hist-filter-attr');
    if (histAttr) histAttr.addEventListener('change', () => loadHistoricalTable(1));

    const histMonth = document.getElementById('hist-filter-month');
    if (histMonth) histMonth.addEventListener('change', () => loadHistoricalTable(1));

    const histCat = document.getElementById('hist-filter-cat');
    if (histCat) histCat.addEventListener('change', () => loadHistoricalTable(1));

    // Trigger initial prediction for default view
    setTimeout(() => {
        executePrediction('Taj Mahal', today, '10:00');
    }, 400);
});

/* Navigation Router */
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const viewSections = document.querySelectorAll('.view-section');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetView = link.getAttribute('data-view');

            navLinks.forEach(nl => nl.classList.remove('active'));
            viewSections.forEach(vs => vs.classList.remove('active'));

            link.classList.add('active');
            const targetEl = document.getElementById(`view-${targetView}`);
            if (targetEl) {
                targetEl.classList.add('active');
            }

            // Load view-specific data if needed
            if (targetView === 'historical') {
                loadHistoricalTable(1);
            } else if (targetView === 'attractions') {
                renderAttractionsGrid();
            }
        });
    });
}

let cachedAttractions = [];

async function loadAttractions() {
    try {
        const response = await fetch('/api/attractions');
        const res = await response.json();
        if (res.success) {
            cachedAttractions = res.attractions;
            populateDropdowns(cachedAttractions);
            renderAttractionsGrid();
        }
    } catch (err) {
        console.error('Error fetching attractions:', err);
    }
}

function populateDropdowns(attractions) {
    const selectEl = document.getElementById('planner-attraction');
    const histAttrSelect = document.getElementById('hist-filter-attr');
    const compAttr1 = document.getElementById('comp-attr-1');
    const compAttr2 = document.getElementById('comp-attr-2');

    if (selectEl) {
        selectEl.innerHTML = attractions.map(a => `<option value="${a.name}">${a.name} (${a.location.split(',')[0]})</option>`).join('');
    }

    if (histAttrSelect) {
        histAttrSelect.innerHTML = `<option value="All">All Attractions</option>` +
            attractions.map(a => `<option value="${a.name}">${a.name}</option>`).join('');
    }

    if (compAttr1 && compAttr2) {
        compAttr1.innerHTML = attractions.map(a => `<option value="${a.name}">${a.name}</option>`).join('');
        compAttr2.innerHTML = attractions.map(a => `<option value="${a.name}" ${a.name === 'Golden Temple' ? 'selected' : ''}>${a.name}</option>`).join('');
    }
}

async function handlePredictSubmit(e) {
    e.preventDefault();
    const attraction = document.getElementById('planner-attraction').value;
    const date = document.getElementById('planner-date').value;
    const time = document.getElementById('planner-time').value;

    await executePrediction(attraction, date, time);
}

async function executePrediction(attraction, date, time) {
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ attraction, date, time })
        });
        const res = await response.json();

        if (res.success) {
            updateDashboardCards(res.data);
            renderHourlyChart(res.data.hourly_curve);

            // Fetch trends data for additional charts
            const trendsResponse = await fetch(`/api/trends?attraction=${encodeURIComponent(attraction)}`);
            const trendsRes = await trendsResponse.json();
            if (trendsRes.success) {
                renderDailyChart(trendsRes.data.daily);
                renderMonthlyChart(trendsRes.data.monthly);
            }

            renderCategoryChart({ Low: 30, Moderate: 40, High: 20, VeryHigh: 10 });
        }
    } catch (err) {
        console.error('Prediction failed:', err);
    }
}

function updateDashboardCards(data) {
    // 1. Selected Attraction Info
    const attrObj = cachedAttractions.find(a => a.name === data.attraction) || {};
    
    document.getElementById('card-attr-name').textContent = data.attraction;
    document.getElementById('card-attr-sub').textContent = `${data.day_of_week}, ${data.date} @ ${data.time_slot}`;
    
    if (attrObj.image_url) {
        const imgEl = document.getElementById('card-attr-img');
        if (imgEl) imgEl.src = attrObj.image_url;
    }

    // 2. Crowd Level Category
    const catBadge = document.getElementById('card-crowd-badge');
    if (catBadge) {
        catBadge.className = `crowd-badge ${data.crowd_category.replace(' ', '-')}`;
        catBadge.innerHTML = `<i class="fas ${data.icon}"></i> ${data.crowd_category}`;
    }

    // 3. Score Radial & Gauge
    const scoreVal = document.getElementById('card-score-val');
    const radialCircle = document.getElementById('card-score-circle');
    
    if (scoreVal) scoreVal.textContent = data.crowd_score;
    if (radialCircle) {
        radialCircle.style.background = `conic-gradient(${data.status_color} ${data.crowd_score * 3.6}deg, rgba(255,255,255,0.08) 0deg)`;
        radialCircle.style.color = data.status_color;
    }

    // 4. Recommendation Golden Hour
    document.getElementById('card-best-time').textContent = data.recommended_time;
    document.getElementById('card-peak-hours').textContent = data.peak_hours_to_avoid;
    document.getElementById('card-wait-time').textContent = data.estimated_wait_time;
    document.getElementById('card-condition-text').textContent = data.condition_description;

    // Detailed Banner text
    document.getElementById('banner-rec-title').textContent = `Recommended Window: ${data.recommended_time}`;
    document.getElementById('banner-rec-desc').textContent = `For ${data.attraction} on ${data.day_of_week}, visiting during early morning hours results in lower crowd density (Avg Score < 35). Avoid ${data.peak_hours_to_avoid} to minimize entry lines.`;
}

function renderAttractionsGrid() {
    const grid = document.getElementById('attractions-grid');
    if (!grid) return;

    if (!cachedAttractions.length) {
        grid.innerHTML = `<p class="text-muted">Loading attractions...</p>`;
        return;
    }

    grid.innerHTML = cachedAttractions.map(attr => `
        <div class="attraction-card">
            <div class="attraction-img-wrapper">
                <img src="${attr.image_url}" alt="${attr.name}" class="attraction-img" loading="lazy">
                <span class="attraction-category-tag">${attr.category}</span>
            </div>
            <div class="attraction-body">
                <h3 class="attraction-name">${attr.name}</h3>
                <div class="attraction-location"><i class="fas fa-map-marker-alt"></i> ${attr.location}</div>
                
                <ul class="attraction-details-list">
                    <li><i class="fas fa-sun"></i> <strong>Best Time:</strong> ${attr.best_time}</li>
                    <li><i class="fas fa-user-clock"></i> <strong>Peak Hours:</strong> ${attr.peak_hours}</li>
                    <li><i class="fas fa-ticket-alt"></i> <strong>Ticket:</strong> ${attr.ticket_price}</li>
                    <li><i class="fas fa-door-open"></i> <strong>Hours:</strong> ${attr.opening_hours}</li>
                </ul>

                <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem;">${attr.description}</p>

                <div class="attraction-footer">
                    <span class="crowd-badge Moderate"><i class="fas fa-chart-line"></i> Base Score ${attr.base_score}</span>
                    <button class="btn-primary" style="padding: 0.5rem 1rem; font-size: 0.85rem;" onclick="selectAndPlanAttraction('${attr.name}')">
                        Plan Visit <i class="fas fa-arrow-right"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function selectAndPlanAttraction(name) {
    const navLink = document.querySelector('.nav-link[data-view="home"]');
    if (navLink) navLink.click();

    const selectEl = document.getElementById('planner-attraction');
    if (selectEl) selectEl.value = name;

    const today = new Date().toISOString().split('T')[0];
    executePrediction(name, today, '10:00');
}

/* Historical Data Table Logic */
let currentPage = 1;

async function loadHistoricalTable(page = 1) {
    currentPage = page;
    const attraction = document.getElementById('hist-filter-attr')?.value || 'All';
    const month = document.getElementById('hist-filter-month')?.value || 'All';
    const category = document.getElementById('hist-filter-cat')?.value || 'All';
    const search = document.getElementById('hist-search')?.value || '';

    const query = `/api/historical?page=${page}&attraction=${encodeURIComponent(attraction)}&month=${encodeURIComponent(month)}&category=${encodeURIComponent(category)}&search=${encodeURIComponent(search)}`;

    try {
        const response = await fetch(query);
        const res = await response.json();

        if (res.success) {
            renderTableRows(res.records);
            renderPagination(res.page, res.total_pages, res.total);
        }
    } catch (err) {
        console.error('Failed to load historical data:', err);
    }
}

function renderTableRows(records) {
    const tbody = document.getElementById('hist-table-body');
    if (!tbody) return;

    if (!records.length) {
        tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding: 2rem; color: var(--text-muted);">No records found matching filters.</td></tr>`;
        return;
    }

    tbody.innerHTML = records.map(r => `
        <tr>
            <td><strong>#${r.id}</strong></td>
            <td><strong>${r.attraction_name}</strong></td>
            <td>${r.date_str}</td>
            <td>${r.month}</td>
            <td>${r.day_of_week} ${r.is_weekend ? '<span style="color:#f59e0b; font-size:0.75rem;">(Weekend)</span>' : ''}</td>
            <td><i class="far fa-clock"></i> ${r.time_slot}</td>
            <td><strong>${r.visitor_count.toLocaleString()}</strong></td>
            <td><span style="font-weight:700; color:${r.crowd_score > 70 ? '#ef4444' : r.crowd_score > 40 ? '#f59e0b' : '#10b981'}">${r.crowd_score}/100</span></td>
            <td><span class="crowd-badge ${r.crowd_category.replace(' ', '-')}">${r.crowd_category}</span></td>
        </tr>
    `).join('');
}

function renderPagination(page, totalPages, totalRecords) {
    const pInfo = document.getElementById('page-info');
    const pPrev = document.getElementById('btn-prev');
    const pNext = document.getElementById('btn-next');

    if (pInfo) pInfo.textContent = `Showing Page ${page} of ${totalPages} (${totalRecords} total records)`;
    if (pPrev) {
        pPrev.disabled = page <= 1;
        pPrev.onclick = () => loadHistoricalTable(page - 1);
    }
    if (pNext) {
        pNext.disabled = page >= totalPages;
        pNext.onclick = () => loadHistoricalTable(page + 1);
    }
}

async function loadDashboardStats() {
    try {
        const response = await fetch('/api/stats');
        const res = await response.json();
        if (res.success) {
            const elTotal = document.getElementById('stat-total-records');
            const elAvg = document.getElementById('stat-avg-score');
            const elBusiest = document.getElementById('stat-busiest');
            const elQuietest = document.getElementById('stat-quietest');

            if (elTotal) elTotal.textContent = res.total_records;
            if (elAvg) elAvg.textContent = `${res.avg_crowd_score}/100`;
            if (elBusiest) elBusiest.textContent = `${res.busiest_attraction} (${res.busiest_score})`;
            if (elQuietest) elQuietest.textContent = `${res.quietest_attraction} (${res.quietest_score})`;
        }
    } catch (err) {
        console.error('Failed to load stats:', err);
    }
}

/* Modal for Adding Historical Data */
function openAddRecordModal() {
    const modal = document.getElementById('add-modal');
    if (modal) {
        modal.style.display = 'flex';
        // Populate modal select
        const modalSelect = document.getElementById('modal-attraction');
        if (modalSelect && cachedAttractions.length) {
            modalSelect.innerHTML = cachedAttractions.map(a => `<option value="${a.name}">${a.name}</option>`).join('');
        }
        document.getElementById('modal-date').value = new Date().toISOString().split('T')[0];
    }
}

function closeAddRecordModal() {
    const modal = document.getElementById('add-modal');
    if (modal) modal.style.display = 'none';
}

async function handleAddRecordSubmit(e) {
    e.preventDefault();
    const attraction = document.getElementById('modal-attraction').value;
    const date = document.getElementById('modal-date').value;
    const time_slot = document.getElementById('modal-time').value;
    const visitor_count = document.getElementById('modal-visitors').value;

    try {
        const response = await fetch('/api/historical/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ attraction, date, time_slot, visitor_count })
        });
        const res = await response.json();
        if (res.success) {
            alert(`Record added! Calculated Crowd Score: ${res.calculated_score} (${res.category})`);
            closeAddRecordModal();
            loadHistoricalTable(1);
            loadDashboardStats();
        }
    } catch (err) {
        alert('Failed to add record');
    }
}

/* Comparison Tool in Crowd Planner Tab */
async function compareAttractions() {
    const attr1 = document.getElementById('comp-attr-1').value;
    const attr2 = document.getElementById('comp-attr-2').value;
    const date = document.getElementById('planner-date')?.value || new Date().toISOString().split('T')[0];

    try {
        const [res1, res2] = await Promise.all([
            fetch('/api/predict', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ attraction: attr1, date, time: '12:00' }) }).then(r => r.json()),
            fetch('/api/predict', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ attraction: attr2, date, time: '12:00' }) }).then(r => r.json())
        ]);

        if (res1.success && res2.success) {
            const compContainer = document.getElementById('comparison-results');
            if (compContainer) {
                compContainer.innerHTML = `
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: 1.5rem;">
                        <div class="summary-card" style="border-top: 4px solid ${res1.data.status_color}">
                            <h3>${res1.data.attraction}</h3>
                            <p class="card-subtext">${date}</p>
                            <div style="margin: 1rem 0;">
                                <span class="crowd-badge ${res1.data.crowd_category.replace(' ', '-')}">${res1.data.crowd_category} (${res1.data.crowd_score}/100)</span>
                            </div>
                            <p><strong>Best Visiting Window:</strong> ${res1.data.recommended_time}</p>
                            <p><strong>Peak Hours to Avoid:</strong> ${res1.data.peak_hours_to_avoid}</p>
                            <p><strong>Est. Wait Time:</strong> ${res1.data.estimated_wait_time}</p>
                        </div>
                        <div class="summary-card" style="border-top: 4px solid ${res2.data.status_color}">
                            <h3>${res2.data.attraction}</h3>
                            <p class="card-subtext">${date}</p>
                            <div style="margin: 1rem 0;">
                                <span class="crowd-badge ${res2.data.crowd_category.replace(' ', '-')}">${res2.data.crowd_category} (${res2.data.crowd_score}/100)</span>
                            </div>
                            <p><strong>Best Visiting Window:</strong> ${res2.data.recommended_time}</p>
                            <p><strong>Peak Hours to Avoid:</strong> ${res2.data.peak_hours_to_avoid}</p>
                            <p><strong>Est. Wait Time:</strong> ${res2.data.estimated_wait_time}</p>
                        </div>
                    </div>
                `;
            }
        }
    } catch (err) {
        console.error('Comparison failed:', err);
    }
}

// Utility debounce
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}
