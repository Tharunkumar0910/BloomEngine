function displayDifficulty(difficulty) {
    switch (difficulty) {
        case "Medium":
            return "Moderate";
        case "Hard":
            return "Difficult";
        default:
            return difficulty || "";
    }
}
window.displayDifficulty = displayDifficulty;

document.addEventListener('DOMContentLoaded', () => {
    
    // --- View Navigation Logic ---
    const navLinks = document.querySelectorAll('.sidebar .nav-link');
    const views = document.querySelectorAll('.view-section');
    const sidebar = document.getElementById('sidebar');
    const openSidebarBtn = document.getElementById('openSidebarBtn');
    const closeSidebarBtn = document.getElementById('closeSidebarBtn');

    let bsDrawer = { show: () => { sidebar.classList.remove('-translate-x-full'); sidebar.classList.add('translate-x-0'); document.getElementById('mobileBackdrop').classList.remove('hidden'); }, hide: () => { sidebar.classList.add('-translate-x-full'); sidebar.classList.remove('translate-x-0'); document.getElementById('mobileBackdrop').classList.add('hidden'); } };

    if (openSidebarBtn) {
        openSidebarBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            bsDrawer.show();
        });
    }
    if (closeSidebarBtn) closeSidebarBtn.addEventListener('click', () => bsDrawer.hide());
    document.getElementById('mobileBackdrop').addEventListener('click', () => bsDrawer.hide());

    let systemModelsInterval = null;

    window.switchTab = function(targetId) {


        // Reset window scroll position to top when switching tabs to prevent content cutoff
        window.scrollTo({ top: 0, behavior: 'instant' });

        const titleMap = {
            'view-dashboard': 'Dashboard',
            'view-manual': 'Question Studio',
            'view-batch': 'Bulk Processing',
            'view-analytics': 'Analytics',
            'view-modelinfo': 'System Models'
        };
        const headerTitle = document.getElementById('headerTitle');
        if (headerTitle && titleMap[targetId]) {
            headerTitle.textContent = titleMap[targetId];
        }

        navLinks.forEach(link => {
            if (link.dataset.target === targetId) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });

        views.forEach(view => {
            if (view.id === targetId) {
                view.classList.remove('hidden');
            } else {
                view.classList.add('hidden');
            }
        });

        sidebar.classList.add('-translate-x-full'); sidebar.classList.remove('translate-x-0'); document.getElementById('mobileBackdrop').classList.add('hidden');

        if (targetId === 'view-dashboard') {
            if(dashBChart) dashBChart.resize();
            if(cChart) cChart.resize();
            if(dashDistChart) dashDistChart.resize();
            fetchBatchHistory(); // Refresh history when viewing dashboard
        }
        if (targetId === 'view-analytics') {
            if (dChart) dChart.resize();
            if (cChart) cChart.resize();
        }
        if (targetId === 'view-modelinfo') {
            if (typeof fetchSystemHealth === 'function') {
                fetchSystemHealth();
            }
            if (!systemModelsInterval) {
                systemModelsInterval = setInterval(fetchSystemHealth, 5000);
            }
        } else {
            if (systemModelsInterval) {
                clearInterval(systemModelsInterval);
                systemModelsInterval = null;
            }
        }
    };

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = link.dataset.target;
            if(target) switchTab(target);
        });
    });


    // --- Dark Mode Toggle ---
    const themeToggle = document.getElementById('themeToggle');
    const themeToggleIcon = document.getElementById('themeToggleIcon');

    function syncThemeUI() {
        const isDark = document.documentElement.classList.contains('dark');
        if (themeToggleIcon) {
            themeToggleIcon.textContent = isDark ? 'light_mode' : 'dark_mode';
        }
        if (themeToggle) {
            themeToggle.setAttribute('aria-label', isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode');
        }
    }

    // Initial switch state setup
    syncThemeUI();

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const isDark = document.documentElement.classList.contains('dark');
            if (isDark) {
                document.documentElement.classList.remove('dark');
                document.documentElement.classList.add('light');
                localStorage.setItem('theme', 'light');
            } else {
                document.documentElement.classList.remove('light');
                document.documentElement.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            }
            syncThemeUI();
            updateChartColors();
        });
    }

    // --- Dashboard History ---
    let batchHistoryData = [];
    let manualClassificationsData = [];
    let batchHistoryCurrentPage = 1;
    const batchHistoryItemsPerPage = 5;

    // Unified Activity Feed Variables
    let unifiedActivityCurrentPage = 1;
    const unifiedActivityItemsPerPage = 5;
    let activitySortAsc = false;
    let currentDashboardChartType = 'bloom';
    let dashBChart = null;
    let cChart = null;
    let dashDistChart = null;
    let dashDistType = 'difficulty';

    async function fetchManualClassifications() {
        try {
            const response = await fetch('/manual-classifications');
            if (response.ok) {
                manualClassificationsData = await response.json();
            } else {
                manualClassificationsData = [];
            }
        } catch (e) {
            console.error("Error fetching manual classifications", e);
            manualClassificationsData = [];
        }
    }

    async function fetchBatchHistory() {
        try {
            await fetchManualClassifications();

            const response = await fetch('/batch-history');
            const history = await response.json();
            
            // Sort by uploaded timestamp descending
            history.sort((a, b) => (b.upload_time || '').localeCompare(a.upload_time || ''));
            batchHistoryData = history;
            
            // Update both dashboard stats and unified activity table!
            updateDashboardWorkspaceStats();
            renderUnifiedActivityTable();
        } catch(e) {
            console.error("Error fetching history", e);
        }
    }

    function updateDashboardWorkspaceStats(opts = {}) {
        // lightweight: true → update only KPI number cards, skip chart renders
        const lightweight = opts.lightweight === true;
        // 1. Get manual classifications
        const manualList = manualClassificationsData;
        
        // 2. Aggregate from manual classifications
        let total = manualList.length;
        let easy = 0, medium = 0, hard = 0;
        let bloomCounts = { Remember: 0, Understand: 0, Apply: 0, Analyze: 0, Evaluate: 0, Create: 0 };
        let totalConf = 0;
        let confCount = 0;
        let maxConf = 0;
        let minConf = 100;
        
        // Confidence ranges for the confidence chart
        let highConfRange = 0; // >= 90
        let medConfRange = 0;  // 70-89
        let lowConfRange = 0;  // < 70

        manualList.forEach(m => {
            if (m.difficulty === 'Easy') easy++;
            else if (m.difficulty === 'Medium' || m.difficulty === 'Moderate') medium++;
            else if (m.difficulty === 'Hard' || m.difficulty === 'Difficult') hard++;
            
            if (m.bloom_level in bloomCounts) {
                bloomCounts[m.bloom_level]++;
            }
            
            const conf = parseFloat(m.confidence) || 0;
            totalConf += conf;
            confCount++;
            if (conf > maxConf) maxConf = conf;
            if (conf < minConf) minConf = conf;
            
            if (conf >= 90) highConfRange++;
            else if (conf >= 70) medConfRange++;
            else lowConfRange++;
        });

        // 3. Aggregate from completed batch history sessions (or active ones)
        batchHistoryData.forEach(h => {
            if (h.completed_questions > 0) {
                total += h.completed_questions;
                easy += h.easy_count || 0;
                medium += h.medium_count || 0;
                hard += h.hard_count || 0;
                
                if (h.bloom_counts) {
                    for (let bl in bloomCounts) {
                        bloomCounts[bl] += (h.bloom_counts[bl] || 0);
                    }
                }
                
                const avgConf = parseFloat(h.avg_confidence) || 0;
                totalConf += avgConf * h.completed_questions;
                confCount += h.completed_questions;
                
                if (avgConf > maxConf) maxConf = avgConf;
                if (avgConf > 0 && avgConf < minConf) minConf = avgConf;
                
                if (avgConf >= 90) highConfRange += h.completed_questions;
                else if (avgConf >= 70) medConfRange += h.completed_questions;
                else lowConfRange += h.completed_questions;
            }
        });

        // Update KPI metric cards
        const dashTotal = document.getElementById('dashTotal');
        const dashEasy = document.getElementById('dashEasy');
        const dashMod = document.getElementById('dashMod');
        const dashDiff = document.getElementById('dashDiff');
        if (dashTotal) dashTotal.textContent = total.toLocaleString();
        if (dashEasy) dashEasy.textContent = easy.toLocaleString();
        if (dashMod) dashMod.textContent = medium.toLocaleString();
        if (dashDiff) dashDiff.textContent = hard.toLocaleString();
        // Percentage labels
        const el = (id) => document.getElementById(id);
        if (el('dashEasyPct')) el('dashEasyPct').textContent = total > 0 ? (easy/total*100).toFixed(1) + '% of total' : '—% of total';
        if (el('dashModPct')) el('dashModPct').textContent = total > 0 ? (medium/total*100).toFixed(1) + '% of total' : '—% of total';
        if (el('dashDiffPct')) el('dashDiffPct').textContent = total > 0 ? (hard/total*100).toFixed(1) + '% of total' : '—% of total';
        // Bottom metric counts
        if (el('dashTotalBatch')) el('dashTotalBatch').textContent = batchHistoryData.length;
        const manualListCount = manualClassificationsData.length;
        if (el('dashManualCount')) el('dashManualCount').textContent = manualListCount.toLocaleString();
        // Confidence legend
        if (el('confHighCount')) el('confHighCount').textContent = highConfRange.toLocaleString();
        if (el('confMedCount')) el('confMedCount').textContent = medConfRange.toLocaleString();
        if (el('confLowCount')) el('confLowCount').textContent = lowConfRange.toLocaleString();

        // Most common bloom
        let mostCommonBloom = '—';
        let mostCommonPctVal = '—';
        let maxBloomCount = 0;
        for (let bl in bloomCounts) {
            if (bloomCounts[bl] > maxBloomCount) { maxBloomCount = bloomCounts[bl]; mostCommonBloom = bl; }
        }
        if (total > 0 && maxBloomCount > 0) mostCommonPctVal = ((maxBloomCount / total) * 100).toFixed(1) + '% of all questions';
        if (el('mostCommonBloomLabel')) el('mostCommonBloomLabel').textContent = mostCommonBloom;
        if (el('mostCommonBloomPct')) el('mostCommonBloomPct').textContent = mostCommonPctVal;
        const finalAvgConf = confCount > 0 ? (totalConf / confCount).toFixed(1) + '%' : '0.0%';
        if (el('avgConfLabel')) el('avgConfLabel').textContent = finalAvgConf;
        if (el('maxConfLabel')) el('maxConfLabel').textContent = (maxConf || 0).toFixed(1) + '%';
        if (el('minConfLabel')) el('minConfLabel').textContent = (minConf === 100 ? 0 : minConf).toFixed(1) + '%';

        // Render/update charts — skipped in lightweight mode
        if (!lightweight) {
            renderDashboardInteractiveChart(bloomCounts, { Easy: easy, Medium: medium, Hard: hard });
            renderDashDistributionChart(bloomCounts, { Easy: easy, Medium: medium, Hard: hard });
        }
    }

    // Calculate a human-friendly step size for chart Y-axis
    function calculateNiceStep(maxVal) {
        if (!maxVal || maxVal <= 0) return 1;
        if (maxVal <= 5) return 1;
        
        const niceSteps = [1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000];
        let bestStep = niceSteps[0];
        let bestScore = Infinity;
        
        for (const step of niceSteps) {
            const divisions = maxVal / step;
            if (divisions < 2) continue; // too few divisions
            if (divisions > 10) continue; // too many divisions
            
            // Score: distance from 5 divisions
            let score = Math.abs(divisions - 5);
            
            // Divisibility bonus: lower score by 1.0 if maxVal is a clean multiple
            if (maxVal % step === 0) {
                score -= 1.0;
            }
            
            if (score < bestScore) {
                bestScore = score;
                bestStep = step;
            }
        }
        return bestStep;
    }

    function renderDashboardInteractiveChart(bloomCounts, diffCounts) {
        const canvas = document.getElementById('dashBloomChart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');

        const getStyleVal = (varName) => getComputedStyle(document.documentElement).getPropertyValue(varName).trim();
        const textColor = getStyleVal('--analytics-chart-legend') || '#666';
        const barColor = getStyleVal('--analytics-chart-bar') || '#1E88E5';
        const gridColor = getStyleVal('--analytics-chart-grid') || 'rgba(0,0,0,0.1)';

        const isBloom = currentDashboardChartType === 'bloom';
        const titleText = isBloom ? 'Bloom Level Distribution' : 'Difficulty Distribution';
        const titleEl = document.getElementById('dashChartTitle');
        if (titleEl) titleEl.textContent = titleText;

        const labels = isBloom ? Object.keys(bloomCounts) : Object.keys(diffCounts).map(displayDifficulty);
        const data = isBloom ? Object.values(bloomCounts) : Object.values(diffCounts);
        const maxVal = Math.max(...data, 0);
        const step = calculateNiceStep(maxVal);
        const suggestedMax = step * Math.ceil((maxVal || 1) / step);
        
        const totalCount = data.reduce((a, b) => a + b, 0);
        const noDataMsg = document.getElementById('dashNoDataMsg');
        if (totalCount === 0) {
            if (noDataMsg) noDataMsg.classList.remove('hidden');
            canvas.style.display = 'none';
            return;
        } else {
            if (noDataMsg) noDataMsg.classList.add('hidden');
            canvas.style.display = 'block';
        }

        let bgColors = barColor;
        if (!isBloom) {
            bgColors = [
                getStyleVal('--analytics-chart-pie-easy') || '#28a745',
                getStyleVal('--analytics-chart-pie-medium') || '#ffc107',
                getStyleVal('--analytics-chart-pie-hard') || '#dc3545'
            ];
        }

        if (dashBChart) {
            dashBChart.data.labels = labels;
            dashBChart.data.datasets[0].data = data;
            dashBChart.data.datasets[0].backgroundColor = bgColors;
            dashBChart.data.datasets[0].barThickness = isBloom ? 24 : 36;
            dashBChart.options.scales.y.suggestedMax = suggestedMax;
            dashBChart.options.scales.y.ticks.stepSize = step;
            dashBChart.update();
        } else {
            dashBChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Count',
                        data: data,
                        backgroundColor: bgColors,
                        borderRadius: 6,
                        borderWidth: 0,
                        barThickness: isBloom ? 24 : 36
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: {
                            grid: { color: gridColor },
                            ticks: { color: textColor }
                        },
                        y: {
                            grid: { color: gridColor },
                            suggestedMin: 0,
                            suggestedMax: suggestedMax,
                            ticks: {
                                color: textColor,
                                stepSize: step,
                                precision: 0,
                                callback: (v) => Number.isInteger(v) ? v : ''
                            }
                        }
                    }
                }
            });
        }
    }

    // Distribution Pie Chart (Difficulty/Bloom toggle)
    function renderDashDistributionChart(bloomCounts, diffCounts) {
        const canvas = document.getElementById('dashDistPieChart');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const isDiff = dashDistType === 'difficulty';
        const bloomColors = ['#6366f1','#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6'];
        const diffColors = ['#22c55e','#f59e0b','#ef4444'];
        const labels = isDiff ? ['Easy', displayDifficulty('Medium'), displayDifficulty('Hard')] : Object.keys(bloomCounts);
        const data = isDiff ? Object.values(diffCounts) : Object.values(bloomCounts);
        const colors = isDiff ? diffColors : bloomColors;
        const total = data.reduce((a,b) => a+b, 0);

        // Update Center Total Questions Count Overlay (Constant across views)
        const grandTotal = Object.values(diffCounts).reduce((a,b) => a+b, 0);
        const centerNumEl = document.getElementById('dashDistCenterNumber');
        if (centerNumEl) {
            centerNumEl.textContent = grandTotal > 0 ? grandTotal.toLocaleString() : '90';
        }

        const isDark = document.documentElement.classList.contains('dark');
        const cardBgColor = isDark ? '#0f172a' : '#ffffff';

        if (dashDistChart) {
            dashDistChart.data.labels = labels;
            dashDistChart.data.datasets[0].data = total > 0 ? data : labels.map(() => 1);
            dashDistChart.data.datasets[0].backgroundColor = total > 0 ? colors : (isDark ? ['#334155'] : ['#e2e8f0']);
            dashDistChart.data.datasets[0].borderColor = cardBgColor;
            dashDistChart.update({
                duration: 250,
                easing: 'easeInOutQuart'
            });
        } else {
            dashDistChart = new Chart(ctx, {
                type: 'doughnut',
                data: { 
                    labels, 
                    datasets: [{ 
                        data: total > 0 ? data : labels.map(() => 1), 
                        backgroundColor: total > 0 ? colors : (isDark ? ['#334155'] : ['#e2e8f0']), 
                        borderWidth: 2, 
                        borderColor: cardBgColor,
                        borderRadius: 4,
                        spacing: 2
                    }] 
                },
                options: { 
                    responsive: true, 
                    maintainAspectRatio: false, 
                    cutout: '72%', 
                    animation: {
                        duration: 250,
                        easing: 'easeInOutQuart'
                    },
                    plugins: { 
                        legend: { display: false }, 
                        tooltip: { 
                            enabled: total > 0,
                            padding: 8,
                            boxPadding: 4,
                            callbacks: {
                                label: function(context) {
                                    const val = context.raw || 0;
                                    const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                                    return ` ${context.label}: ${val} (${pct}%)`;
                                }
                            }
                        } 
                    } 
                }
            });
        }

        // Render Legend (Fixed card height compatible, 2-column for Bloom)
        const legend = document.getElementById('dashDistLegend');
        if (legend && total > 0) {
            if (isDiff) {
                // Difficulty Legend: Clean 1-column list (3 items)
                legend.innerHTML = `
                    <div class="space-y-1.5 px-0.5">
                        ${labels.map((l, i) => `
                            <div class="flex items-center justify-between py-1 border-b border-slate-100 dark:border-slate-800/60 last:border-none">
                                <div class="flex items-center gap-2">
                                    <span class="w-2.5 h-2.5 rounded-full shrink-0 shadow-xs" style="background:${colors[i]}"></span>
                                    <span class="font-medium text-slate-700 dark:text-slate-300 text-xs">${l}</span>
                                </div>
                                <span class="font-bold text-slate-900 dark:text-white text-xs">
                                    ${data[i].toLocaleString()} <span class="font-normal text-slate-400 dark:text-slate-500 text-[11px] ml-1">(${(data[i]/total*100).toFixed(1)}%)</span>
                                </span>
                            </div>
                        `).join('')}
                    </div>
                `;
            } else {
                // Bloom Level Legend: Clean 2-column grid (3 x 2, 6 items)
                legend.innerHTML = `
                    <div class="grid grid-cols-2 gap-x-3 gap-y-1 px-0.5">
                        ${labels.map((l, i) => `
                            <div class="flex items-center justify-between py-1 px-1.5 rounded-md hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors">
                                <div class="flex items-center gap-1.5 min-w-0">
                                    <span class="w-2 h-2 rounded-full shrink-0" style="background:${colors[i]}"></span>
                                    <span class="font-medium text-slate-600 dark:text-slate-300 text-[11px] truncate">${l}</span>
                                </div>
                                <span class="font-bold text-slate-800 dark:text-slate-200 text-[11px] shrink-0 ml-1">
                                    ${data[i].toLocaleString()} <span class="font-normal text-slate-400 text-[10px]">(${(data[i]/total*100).toFixed(1)}%)</span>
                                </span>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
        } else if (legend) { 
            legend.innerHTML = '<div class="text-slate-400 text-center py-2 text-xs">No data available</div>'; 
        }
    }

    // Toggle handlers for distribution chart
    setTimeout(() => {
        const btnDiff = document.getElementById('dashDistToggleDiff');
        const btnBloom = document.getElementById('dashDistToggleBloom');
        if (btnDiff) btnDiff.addEventListener('click', () => {
            dashDistType = 'difficulty';
            btnDiff.classList.add('bg-white','dark:bg-slate-900','text-slate-800','dark:text-white','shadow-sm'); 
            btnDiff.classList.remove('text-slate-500','dark:text-slate-400');
            if (btnBloom) { 
                btnBloom.classList.remove('bg-white','dark:bg-slate-900','text-slate-800','dark:text-white','shadow-sm'); 
                btnBloom.classList.add('text-slate-500','dark:text-slate-400'); 
            }
            const manualList = manualClassificationsData;
            let easy=0,medium=0,hard=0; const bc = {Remember:0,Understand:0,Apply:0,Analyze:0,Evaluate:0,Create:0};
            manualList.forEach(m => { 
                if(m.difficulty==='Easy')easy++;
                else if(m.difficulty==='Medium'||m.difficulty==='Moderate')medium++;
                else if(m.difficulty==='Hard'||m.difficulty==='Difficult')hard++; 
                if(m.bloom_level in bc)bc[m.bloom_level]++; 
            });
            batchHistoryData.forEach(h => { 
                if(h.completed_questions>0) {
                    easy+=h.easy_count||0; 
                    medium+=h.medium_count||0; 
                    hard+=h.hard_count||0; 
                    if(h.bloom_counts)for(let k in bc)bc[k]+=(h.bloom_counts[k]||0); 
                }
            });
            renderDashDistributionChart(bc, {Easy:easy,Medium:medium,Hard:hard});
        });
        if (btnBloom) btnBloom.addEventListener('click', () => {
            dashDistType = 'bloom';
            btnBloom.classList.add('bg-white','dark:bg-slate-900','text-slate-800','dark:text-white','shadow-sm'); 
            btnBloom.classList.remove('text-slate-500','dark:text-slate-400');
            if (btnDiff) { 
                btnDiff.classList.remove('bg-white','dark:bg-slate-900','text-slate-800','dark:text-white','shadow-sm'); 
                btnDiff.classList.add('text-slate-500','dark:text-slate-400'); 
            }
            const manualList = manualClassificationsData;
            let easy=0,medium=0,hard=0; const bc = {Remember:0,Understand:0,Apply:0,Analyze:0,Evaluate:0,Create:0};
            manualList.forEach(m => { 
                if(m.difficulty==='Easy')easy++;
                else if(m.difficulty==='Medium'||m.difficulty==='Moderate')medium++;
                else if(m.difficulty==='Hard'||m.difficulty==='Difficult')hard++; 
                if(m.bloom_level in bc)bc[m.bloom_level]++; 
            });
            batchHistoryData.forEach(h => { 
                if(h.completed_questions>0) {
                    easy+=h.easy_count||0; 
                    medium+=h.medium_count||0; 
                    hard+=h.hard_count||0; 
                    if(h.bloom_counts)for(let k in bc)bc[k]+=(h.bloom_counts[k]||0); 
                }
            });
            renderDashDistributionChart(bc, {Easy:easy,Medium:medium,Hard:hard});
        });
    }, 500);

    function getFilteredActivityData() {
        const query = (document.getElementById('searchActivity') ? document.getElementById('searchActivity').value.toLowerCase().trim() : '');
        const typeFilter = (document.getElementById('filterActivityType') ? document.getElementById('filterActivityType').value : '');
        
        let combined = [];
        
        batchHistoryData.forEach(b => {
            combined.push({
                id: b.session_id,
                type: 'batch',
                details: b.filename,
                timestamp: b.upload_time || '',
                total_questions: b.total_questions,
                completed_questions: b.completed_questions,
                status: b.status,
                raw: b
            });
        });
        
        const manualList = manualClassificationsData;
        manualList.forEach(m => {
            combined.push({
                id: m.id,
                type: 'manual',
                details: m.question,
                timestamp: m.upload_time || '',
                total_questions: 1,
                completed_questions: 1,
                status: 'Completed',
                raw: m
            });
        });

        if (query) {
            combined = combined.filter(item => {
                return item.details.toLowerCase().includes(query) || 
                       (item.type === 'manual' && (item.raw.bloom_level.toLowerCase().includes(query) || item.raw.difficulty.toLowerCase().includes(query) || displayDifficulty(item.raw.difficulty).toLowerCase().includes(query))) ||
                       item.status.toLowerCase().includes(query);
            });
        }

        if (typeFilter) {
            combined = combined.filter(item => item.type === typeFilter);
        }

        combined.sort((a, b) => {
            const dateA = new Date(a.timestamp).getTime() || 0;
            const dateB = new Date(b.timestamp).getTime() || 0;
            return activitySortAsc ? (dateA - dateB) : (dateB - dateA);
        });

        return combined;
    }

    function renderUnifiedActivityTable() {
        const tbody = document.getElementById('unifiedActivityTbody');
        if(!tbody) return;
        
        tbody.innerHTML = '';
        const filteredData = getFilteredActivityData();
        
        if (filteredData.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="text-center text-slate-400 py-8">No matching activities found</td></tr>`;
            const infoSpan = document.getElementById('activityPaginationInfo');
            if (infoSpan) infoSpan.textContent = 'Showing 0 of 0';
            const pagUl = document.getElementById('activityPagination');
            if (pagUl) pagUl.innerHTML = '';
            return;
        }
        
        const totalItems = filteredData.length;
        const totalPages = Math.ceil(totalItems / unifiedActivityItemsPerPage);
        
        if (unifiedActivityCurrentPage > totalPages) {
            unifiedActivityCurrentPage = totalPages;
        }
        if (unifiedActivityCurrentPage < 1) {
            unifiedActivityCurrentPage = 1;
        }
        
        const startIndex = (unifiedActivityCurrentPage - 1) * unifiedActivityItemsPerPage;
        const endIndex = Math.min(startIndex + unifiedActivityItemsPerPage, totalItems);
        const pageItems = filteredData.slice(startIndex, endIndex);
        
        // Bloom badge colors
        const bloomBadge = (b) => { const map = {Remember:'bg-purple-100 text-purple-700',Understand:'bg-blue-100 text-blue-700',Apply:'bg-cyan-100 text-cyan-700',Analyze:'bg-amber-100 text-amber-700',Evaluate:'bg-orange-100 text-orange-700',Create:'bg-pink-100 text-pink-700'}; const cls = map[b]||'bg-slate-100 text-slate-600'; return `<span class="inline-flex items-center rounded-md ${cls} px-2 py-0.5 text-[11px] font-semibold">${b||'—'}</span>`; };
        const diffBadge = (d) => { const map = {Easy:'bg-green-100 text-green-700',Medium:'bg-yellow-100 text-yellow-700',Moderate:'bg-yellow-100 text-yellow-700',Hard:'bg-red-100 text-red-700',Difficult:'bg-red-100 text-red-700'}; const cls = map[d]||'bg-slate-100 text-slate-600'; return d ? `<span class="inline-flex items-center rounded-md ${cls} px-2 py-0.5 text-[11px] font-semibold">${displayDifficulty(d)}</span>` : '—'; };
        const relTime = (ts) => { if(!ts) return '—'; const diff = Date.now() - new Date(ts).getTime(); const m=Math.floor(diff/60000); if(m<1)return 'just now'; if(m<60)return m+' min ago'; const h=Math.floor(m/60); if(h<24)return h+(h===1?' hour':' hours')+' ago'; return Math.floor(h/24)+'d ago'; };

        pageItems.forEach((item, idx) => {
            const tr = document.createElement('tr');
            const isLast = idx === pageItems.length - 1;
            tr.className = `hover:bg-slate-50/50 dark:hover:bg-slate-800/20 transition-colors align-top${isLast ? '' : ' border-b border-slate-100 dark:border-slate-800'}`;
            let typeBadge, detailsHtml, bloomHtml, diffHtml;

            if (item.type === 'manual') {
                typeBadge = '<span class="inline-flex items-center rounded-md bg-indigo-50 px-2 py-0.5 text-[11px] font-semibold text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-400">Manual</span>';
                // Full question text — no truncation, natural word wrap
                detailsHtml = `<div class="font-medium text-slate-800 dark:text-slate-200 text-xs leading-relaxed break-words whitespace-normal">${item.details}</div>`;
                bloomHtml = bloomBadge(item.raw.bloom_level);
                diffHtml = diffBadge(item.raw.difficulty);
            } else {
                typeBadge = '<span class="inline-flex items-center rounded-md bg-emerald-50 px-2 py-0.5 text-[11px] font-semibold text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400">Batch</span>';
                // Filename can truncate if excessively long; show question count on second line
                detailsHtml = `<div class="font-medium text-slate-800 dark:text-slate-200 text-xs truncate max-w-xs" title="${item.details}">${item.details}</div><div class="text-[10px] text-slate-400 mt-0.5">${item.completed_questions || 0} Questions</div>`;
                bloomHtml = '<span class="text-slate-400 text-xs">—</span>';
                diffHtml = '<span class="text-slate-400 text-xs">—</span>';
            }

            tr.innerHTML = `
                <td class="px-5 py-4 align-top text-left">${typeBadge}</td>
                <td class="px-5 py-4 align-top text-left">${detailsHtml}</td>
                <td class="px-5 py-4 align-top text-center">${bloomHtml}</td>
                <td class="px-5 py-4 align-top text-center">${diffHtml}</td>
                <td class="px-5 py-4 align-top text-right text-[11px] text-slate-400 whitespace-nowrap">${relTime(item.timestamp)}</td>
            `;
            tbody.appendChild(tr);
        });

        const infoSpan = document.getElementById('activityPaginationInfo');
        if (infoSpan) {
            infoSpan.textContent = `Showing ${startIndex + 1}-${endIndex} of ${totalItems}`;
        }
        
        renderUnifiedActivityPagination(totalPages);
    }

    function renderUnifiedActivityPagination(totalPages) {
        const pagUl = document.getElementById('activityPagination');
        if (!pagUl) return;
        pagUl.innerHTML = '';
        
        // Prev button
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${unifiedActivityCurrentPage === 1 ? 'disabled' : ''}`;
        prevLi.innerHTML = `
            <button class="flex h-7 w-7 items-center justify-center rounded-md border border-slate-200 bg-white text-slate-500 hover:bg-slate-50 disabled:opacity-50 disabled:pointer-events-none dark:border-slate-800 dark:bg-slate-950 dark:text-slate-400 dark:hover:bg-slate-900 cursor-pointer" ${unifiedActivityCurrentPage === 1 ? 'disabled' : ''}>
                <span class="material-symbols-outlined text-[16px]">chevron_left</span>
            </button>
        `;
        if (unifiedActivityCurrentPage > 1) {
            prevLi.querySelector('button').addEventListener('click', () => {
                unifiedActivityCurrentPage--;
                renderUnifiedActivityTable();
            });
        }
        pagUl.appendChild(prevLi);
        
        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            const pageLi = document.createElement('li');
            const isActive = i === unifiedActivityCurrentPage;
            pageLi.innerHTML = `
                <button class="flex h-7 w-7 items-center justify-center rounded-md text-xs font-semibold cursor-pointer ${isActive ? 'bg-primary text-white' : 'border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-400 dark:hover:bg-slate-900'}">
                    ${i}
                </button>
            `;
            pageLi.querySelector('button').addEventListener('click', () => {
                unifiedActivityCurrentPage = i;
                renderUnifiedActivityTable();
            });
            pagUl.appendChild(pageLi);
        }
        
        // Next button
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${unifiedActivityCurrentPage === totalPages ? 'disabled' : ''}`;
        nextLi.innerHTML = `
            <button class="flex h-7 w-7 items-center justify-center rounded-md border border-slate-200 bg-white text-slate-500 hover:bg-slate-50 disabled:opacity-50 disabled:pointer-events-none dark:border-slate-800 dark:bg-slate-950 dark:text-slate-400 dark:hover:bg-slate-900 cursor-pointer" ${unifiedActivityCurrentPage === totalPages ? 'disabled' : ''}>
                <span class="material-symbols-outlined text-[16px]">chevron_right</span>
            </button>
        `;
        if (unifiedActivityCurrentPage < totalPages) {
            nextLi.querySelector('button').addEventListener('click', () => {
                unifiedActivityCurrentPage++;
                renderUnifiedActivityTable();
            });
        }
        pagUl.appendChild(nextLi);
    }

    function initDashboardListeners() {
        const searchActivity = document.getElementById('searchActivity');
        if (searchActivity) {
            searchActivity.addEventListener('input', () => {
                unifiedActivityCurrentPage = 1;
                renderUnifiedActivityTable();
            });
        }

        const filterActivityType = document.getElementById('filterActivityType');
        if (filterActivityType) {
            filterActivityType.addEventListener('change', () => {
                unifiedActivityCurrentPage = 1;
                renderUnifiedActivityTable();
            });
        }

        const thActivityTime = document.getElementById('thActivityTime');
        if (thActivityTime) {
            thActivityTime.addEventListener('click', () => {
                activitySortAsc = !activitySortAsc;
                const icon = document.getElementById('activitySortIcon');
                if (icon) icon.textContent = activitySortAsc ? '▲' : '▼';
                renderUnifiedActivityTable();
            });
        }

        const toggleBloom = document.getElementById('toggleBloomChart');
        const toggleDifficulty = document.getElementById('toggleDifficultyChart');
        if (toggleBloom && toggleDifficulty) {
            toggleBloom.addEventListener('click', () => {
                setDashboardChartType('bloom');
            });
            toggleDifficulty.addEventListener('click', () => {
                setDashboardChartType('difficulty');
            });
        }
    }

    function setDashboardChartType(type) {
        currentDashboardChartType = type;
        const toggleBloom = document.getElementById('toggleBloomChart');
        const toggleDifficulty = document.getElementById('toggleDifficultyChart');
        if (toggleBloom && toggleDifficulty) {
            if (type === 'bloom') {
                toggleBloom.className = "rounded-md px-3 py-1 text-xs font-semibold bg-white dark:bg-slate-900 text-slate-800 dark:text-white shadow-sm transition-all cursor-pointer";
                toggleDifficulty.className = "rounded-md px-3 py-1 text-xs font-semibold text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white transition-all cursor-pointer";
            } else {
                toggleDifficulty.className = "rounded-md px-3 py-1 text-xs font-semibold bg-white dark:bg-slate-900 text-slate-800 dark:text-white shadow-sm transition-all cursor-pointer";
                toggleBloom.className = "rounded-md px-3 py-1 text-xs font-semibold text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white transition-all cursor-pointer";
            }
        }
        updateDashboardWorkspaceStats();
    }


    window.closeManualDetailsModal = function() {
        const modal = document.getElementById('manualDetailsModal');
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }
    };

    window.viewBatchFromDashboard = function(sessionId) {
        switchTab('view-batch');
        currentSessionId = sessionId;
        pollBatchStatus();
    };

    initDashboardListeners();
    fetchBatchHistory(); // initial load

    // --- Manual Classification ---
    const manualForm = document.getElementById('manualForm');
    const manualQuestion = document.getElementById('manualQuestion');
    const btnClassify = document.getElementById('btnClassify');
    const classifySpinner = document.getElementById('classifySpinner');
    const singleResultSection = document.getElementById('singleResultSection');
    const generationControlsWrapper = document.getElementById('generationControlsWrapper');
    const btnClear = document.getElementById('btnClear');

    if(manualForm) {
        manualForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await performClassification();
        });
    }

    if(btnClear) {
        btnClear.addEventListener('click', () => {
            manualQuestion.value = '';
            singleResultSection.classList.add('hidden');
            if (generationControlsWrapper) generationControlsWrapper.classList.add('hidden');
            const stackedContainer = document.getElementById('stackedAlternativesContainer');
            if (stackedContainer) stackedContainer.innerHTML = '';
            const emptyMsg = document.getElementById('emptyVariantsMsg');
            if (emptyMsg) emptyMsg.classList.remove('hidden');
            const wrapper = document.getElementById('stackedVariantsWrapper');
            if (wrapper) wrapper.classList.add('hidden');
            
            const statusDot = document.getElementById('statusDot');
            const processingStatus = document.getElementById('processingStatus');
            if (statusDot) statusDot.className = 'h-2 w-2 rounded-full bg-emerald-500 animate-pulse';
            if (processingStatus) processingStatus.textContent = 'Ready';
        });
    }

    function getBloomBadgeClass(bloom) {
        const mappings = {
            'Remember': 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/30 dark:text-blue-300 dark:border-blue-900/50',
            'Understand': 'bg-cyan-100 text-cyan-800 border-cyan-200 dark:bg-cyan-900/30 dark:text-cyan-300 dark:border-cyan-900/50',
            'Apply': 'bg-emerald-100 text-emerald-800 border-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-300 dark:border-emerald-900/50',
            'Analyze': 'bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-900/30 dark:text-amber-300 dark:border-amber-900/50',
            'Evaluate': 'bg-purple-100 text-purple-800 border-purple-200 dark:bg-purple-900/30 dark:text-purple-300 dark:border-purple-900/50',
            'Create': 'bg-rose-100 text-rose-800 border-rose-200 dark:bg-rose-900/30 dark:text-rose-300 dark:border-rose-900/50'
        };
        return mappings[bloom] || 'bg-slate-100 text-slate-800 border-slate-200 dark:bg-slate-800 dark:text-slate-350 dark:border-slate-700';
    }

    function getDifficultyBadgeClass(difficulty) {
        const mappings = {
            'Easy': 'bg-emerald-100 text-emerald-800 border-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-300 dark:border-emerald-900/50',
            'Medium': 'bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-900/30 dark:text-amber-300 dark:border-amber-900/50',
            'Moderate': 'bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-900/30 dark:text-amber-300 dark:border-amber-900/50',
            'Hard': 'bg-rose-100 text-rose-800 border-rose-200 dark:bg-rose-900/30 dark:text-rose-300 dark:border-rose-900/50',
            'Difficult': 'bg-rose-100 text-rose-800 border-rose-200 dark:bg-rose-900/30 dark:text-rose-300 dark:border-rose-900/50'
        };
        return mappings[difficulty] || 'bg-slate-100 text-slate-800 border-slate-200 dark:bg-slate-800 dark:text-slate-350 dark:border-slate-700';
    }

    function updateTransformationControls(difficulty) {
        const container = document.getElementById('generationControlsContainer');
        if (!container) return;
        container.innerHTML = '';
        
        const categories = [
            {
                name: 'Easy Questions',
                desc: 'Remember, Understand',
                target: 'Easy',
                color: 'border-emerald-200 bg-emerald-50 text-emerald-800 hover:bg-emerald-100 dark:border-emerald-500/20 dark:bg-emerald-500/5 dark:text-emerald-400'
            },
            {
                name: displayDifficulty('Medium') + ' Questions',
                desc: 'Apply, Analyze',
                target: 'Medium',
                color: 'border-amber-200 bg-amber-50 text-amber-800 hover:bg-amber-100 dark:border-amber-500/20 dark:bg-amber-500/5 dark:text-amber-400'
            },
            {
                name: displayDifficulty('Hard') + ' Questions',
                desc: 'Evaluate, Create',
                target: 'Hard',
                color: 'border-rose-200 bg-rose-50 text-rose-800 hover:bg-rose-100 dark:border-rose-500/20 dark:bg-rose-500/5 dark:text-rose-400'
            }
        ];

        let stdDiff = difficulty;
        if (difficulty === 'Moderate') stdDiff = 'Medium';
        if (difficulty === 'Difficult') stdDiff = 'Hard';

        categories.forEach(cat => {
            const isCurrent = (stdDiff === cat.target);
            if (isCurrent) return; // Only show alternate options
            
            const groupCard = document.createElement('div');
            groupCard.className = 'arena-card rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900 flex flex-col justify-between h-full';
            
            groupCard.innerHTML = `
                <div class="mb-5">
                    <h4 class="text-sm font-bold text-slate-800 dark:text-slate-200">${cat.name}</h4>
                    <p class="text-xs text-slate-500 dark:text-slate-400 mt-1.5">${cat.desc}</p>
                </div>
                <button class="btn-generate-alt w-full rounded-lg border px-3 py-2 text-xs font-semibold transition-all duration-200 ${cat.color}" 
                        data-target="${cat.target}">
                    Generate
                </button>
            `;
            
            const btn = groupCard.querySelector('.btn-generate-alt');
            btn.addEventListener('click', () => triggerGeneration(cat.target, btn));
            
            container.appendChild(groupCard);
        });
    }

    async function performClassification() {
        const question = manualQuestion.value.trim();
        if (!question) {
            alert('Please enter a question.');
            return;
        }

        // Clear previous stacked alternatives and show empty message
        const stackedContainer = document.getElementById('stackedAlternativesContainer');
        if (stackedContainer) stackedContainer.innerHTML = '';
        const emptyMsg = document.getElementById('emptyVariantsMsg');
        if (emptyMsg) emptyMsg.classList.remove('hidden');
        const wrapper = document.getElementById('stackedVariantsWrapper');
        if (wrapper) wrapper.classList.add('hidden');

        btnClassify.disabled = true;
        classifySpinner.classList.remove('hidden');
        
        const statusDot = document.getElementById('statusDot');
        const processingStatus = document.getElementById('processingStatus');
        if (statusDot) statusDot.className = 'h-2 w-2 rounded-full bg-amber-500 animate-pulse';
        if (processingStatus) processingStatus.textContent = 'Classifying...';

        try {
            const response = await fetch('/classify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question })
            });
            const data = await response.json();
            
            if (response.ok) {
                // Fetch the updated manual classifications list from backend
                await fetchManualClassifications();
                
                // Update workspace stats and unified table
                updateDashboardWorkspaceStats();
                renderUnifiedActivityTable();

                displaySingleResult(data);
                if (statusDot) statusDot.className = 'h-2 w-2 rounded-full bg-emerald-500 animate-pulse';
                if (processingStatus) processingStatus.textContent = 'Ready';
            } else {
                alert('Error: ' + data.error);
                if (statusDot) statusDot.className = 'h-2 w-2 rounded-full bg-rose-500 animate-pulse';
                if (processingStatus) processingStatus.textContent = 'Error';
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred during classification.');
            if (statusDot) statusDot.className = 'h-2 w-2 rounded-full bg-rose-500 animate-pulse';
            if (processingStatus) processingStatus.textContent = 'Error';
        } finally {
            btnClassify.disabled = false;
            classifySpinner.classList.add('hidden');
        }
    }

    function createSkeletonCard(targetDifficulty) {
        const id = 'skeleton-' + Date.now();
        const card = document.createElement('div');
        card.id = id;
        card.className = 'arena-card rounded-xl border border-dashed border-gray-300 bg-gray-50/30 dark:border-slate-700 dark:bg-slate-900/50 p-6 space-y-4 animate-pulse';
        card.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex gap-2">
                    <div class="h-6 w-20 rounded bg-gray-200 dark:bg-slate-800"></div>
                    <div class="h-6 w-16 rounded bg-gray-200 dark:bg-slate-800"></div>
                </div>
                <div class="h-5 w-24 rounded bg-gray-200 dark:bg-slate-800"></div>
            </div>
            <div class="h-10 w-full rounded bg-gray-200 dark:bg-slate-800"></div>
            <div class="flex flex-col gap-2 pt-2 border-t border-gray-100 dark:border-slate-800">
                <div class="flex items-center gap-2 text-xs text-slate-500 font-medium">
                    <span class="loading-stage-text">Classification Complete</span>
                </div>
            </div>
        `;
        return { element: card, id };
    }

    function startSkeletonLoading(skeletonEl) {
        const stageText = skeletonEl.querySelector('.loading-stage-text');
        const statusText = document.getElementById('processingStatus');
        const statusDot = document.getElementById('statusDot');
        
        if (statusDot) {
            statusDot.className = 'h-2 w-2 rounded-full bg-amber-500 animate-pulse';
        }

        const stages = [
            '✓ Classification Complete',
            'Generating Question...',
            'Validating...',
            'Selecting Best Candidate...'
        ];

        let idx = 0;
        const updateHTML = () => {
            let prefix = idx === 0 ? '' : '<span class="h-2 w-2 rounded-full bg-blue-500 inline-block animate-ping mr-2"></span>';
            if (stageText) {
                stageText.innerHTML = `${prefix}${stages[idx]}`;
            }
            if (statusText) {
                statusText.textContent = stages[idx];
            }
        };
        
        updateHTML();
        
        const timers = [
            setTimeout(() => { idx = 1; updateHTML(); }, 1500),
            setTimeout(() => { idx = 2; updateHTML(); }, 3800),
            setTimeout(() => { idx = 3; updateHTML(); }, 7500)
        ];
        
        return () => {
            timers.forEach(clearTimeout);
            if (statusText) statusText.textContent = 'Ready';
            if (statusDot) statusDot.className = 'h-2 w-2 rounded-full bg-emerald-500 animate-pulse';
        };
    }

    async function triggerGeneration(targetDifficulty, btn) {
        const originalQuestion = document.getElementById('resQuestion').textContent;
        
        // Disable target buttons
        const allBtns = document.querySelectorAll('.btn-generate-alt');
        allBtns.forEach(b => b.disabled = true);
        
        // Hide empty message and show wrapper
        const emptyMsg = document.getElementById('emptyVariantsMsg');
        if (emptyMsg) emptyMsg.classList.add('hidden');
        const wrapper = document.getElementById('stackedVariantsWrapper');
        if (wrapper) wrapper.classList.remove('hidden');

        // Create and append skeleton card
        const stackedContainer = document.getElementById('stackedAlternativesContainer');
        const { element: skeletonEl, id: skeletonId } = createSkeletonCard(targetDifficulty);
        
        // Prepend skeleton card so the newest generation appears at the top
        stackedContainer.insertBefore(skeletonEl, stackedContainer.firstChild);
        skeletonEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        const stopLoading = startSkeletonLoading(skeletonEl);
        const startTime = performance.now();

        try {
            const response = await fetch('/rephrase', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: originalQuestion, target_difficulty: targetDifficulty })
            });
            const data = await response.json();
            const endTime = performance.now();
            const latency = ((endTime - startTime) / 1000).toFixed(2);

            // Remove skeleton
            skeletonEl.remove();

            if (response.ok) {
                // Render the generated card
                appendStackedAlternative(data, targetDifficulty, latency);
            } else {
                alert('Error: ' + data.error);
                if (stackedContainer.children.length === 0) {
                    emptyMsg.classList.remove('hidden');
                    wrapper.classList.add('hidden');
                }
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred during generation.');
            skeletonEl.remove();
            if (stackedContainer.children.length === 0) {
                emptyMsg.classList.remove('hidden');
                wrapper.classList.add('hidden');
            }
        } finally {
            stopLoading();
            // Re-enable target buttons except the current difficulty
            const currentBloom = document.getElementById('resBloom').textContent;
            const currentDifficulty = document.getElementById('resDiff').textContent;
            const currentConf = parseFloat(document.getElementById('resConfText').textContent);
            const currentExplanation = document.getElementById('resExplanation').textContent;
            displaySingleResult({
                question: originalQuestion,
                bloom_level: currentBloom,
                difficulty: currentDifficulty,
                confidence: currentConf,
                explanation: currentExplanation
            });
        }
    }

    function displaySingleResult(data) {
        document.getElementById('resQuestion').textContent = data.question;
        
        const bloomEl = document.getElementById('resBloom');
        bloomEl.textContent = data.bloom_level;
        bloomEl.className = 'px-2.5 py-0.5 rounded-full text-xs font-semibold border ' + getBloomBadgeClass(data.bloom_level);

        const diffEl = document.getElementById('resDiff');
        diffEl.textContent = data.difficulty;
        diffEl.className = 'px-2.5 py-0.5 rounded-full text-xs font-semibold border ' + getDifficultyBadgeClass(data.difficulty);
        
        const resConfText = document.getElementById('resConfText');
        if (resConfText) resConfText.textContent = data.confidence + '%';
        
        const bar = document.getElementById('resConfBar');
        if (bar) {
            bar.style.width = data.confidence + '%';
            bar.className = 'h-full rounded-full bg-blue-500 transition-all duration-500'; // reset
            if (data.confidence >= 90) bar.classList.add('!bg-emerald-500');
            else if (data.confidence >= 70) bar.classList.add('!bg-amber-500');
            else bar.classList.add('!bg-rose-500');
        }
        
        const resExplanation = document.getElementById('resExplanation');
        if (resExplanation) resExplanation.textContent = data.explanation;

        // Dynamic transformation controls based on current difficulty
        updateTransformationControls(data.difficulty);

        singleResultSection.classList.remove('hidden');
        if (generationControlsWrapper) generationControlsWrapper.classList.remove('hidden');
        singleResultSection.scrollIntoView({ behavior: 'smooth' });
    }

    // --- File Upload & Live Batch Classification ---
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');
    const uploadBtn = document.getElementById('uploadBtn');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const uploadSpinner = document.getElementById('uploadSpinner');
    const uploadStatus = document.getElementById('uploadStatus');
    const batchResultsSection = document.getElementById('batchResultsSection');
    const exportSessionId = document.getElementById('exportSessionId');
    
    // Live UI elements
    const liveProgressPanel = document.getElementById('liveProgressPanel');
    const liveStatsRow = document.getElementById('liveStatsRow');
    const progressText = document.getElementById('progressText');
    const progressBar = document.getElementById('progressBar');
    const progressSpeed = document.getElementById('progressSpeed');
    const progressETA = document.getElementById('progressETA');
    const btnStopBatch = document.getElementById('btnStopBatch');

    if(dropZone) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) { e.preventDefault(); e.stopPropagation(); }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
        });

        dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleFiles(files);
        });

        fileInput.addEventListener('change', function() { handleFiles(this.files); });
    }

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            fileNameDisplay.textContent = file.name;
            uploadBtn.disabled = false;
            const dt = new DataTransfer();
            dt.items.add(file);
            fileInput.files = dt.files;
        }
    }

    let globalBatchResults = [];
    let currentSessionId = null;
    let pollInterval = null;

    // --- Batch polling optimisation state ---
    let _lastProcessedCount = -1;  // last seen processed count for milestone detection
    let _lastKpiMilestone = 0;      // last multiple-of-10 that triggered a KPI update
    let _lastRenderedCount = 0;    // number of results already appended to the live table

    let parsedQuestions = [];
    let currentFileName = '';

    if(uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (fileInput.files.length === 0) return;

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            uploadBtn.disabled = true;
            uploadSpinner.classList.remove('hidden');
            uploadStatus.className = 'alert alert-info mt-3 small py-2 mb-0 text-start mx-auto';
            uploadStatus.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Extracting questions...';
            uploadStatus.classList.remove('hidden');
            
            // Clean up old UI
            globalBatchResults = [];
            liveProgressPanel.classList.add('hidden');
            liveStatsRow.classList.add('hidden');
            batchResultsSection.classList.add('hidden');
            document.getElementById('previewSection').classList.add('hidden');
            
            try {
                // Step 1: Parse Only
                const response = await fetch('/parse-upload', { method: 'POST', body: formData });
                const data = await response.json();
                
                if (response.ok) {
                    parsedQuestions = data.questions;
                    currentFileName = data.filename;
                    renderPreviewTable();
                    
                    uploadStatus.classList.add('hidden');
                    document.getElementById('previewSection').classList.remove('hidden');
                } else {
                    uploadStatus.className = 'alert alert-danger mt-3 small py-2 mb-0 text-start mx-auto';
                    uploadStatus.textContent = 'Error: ' + data.error;
                }
            } catch (error) {
                console.error('Error:', error);
                uploadStatus.className = 'alert alert-danger mt-3 small py-2 mb-0 text-start mx-auto';
                uploadStatus.textContent = 'An error occurred during file parsing.';
            } finally {
                uploadBtn.disabled = false;
                uploadSpinner.classList.add('hidden');
            }
        });
    }

    // --- Preview Flow ---
    function renderPreviewTable() {
        const tbody = document.getElementById('previewTbody');
        if (!tbody) return;
        tbody.innerHTML = '';
        
        parsedQuestions.forEach((q, i) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="ps-3"><input class="form-check-input preview-checkbox" type="checkbox" checked data-index="${i}"></td>
                <td class="preview-text py-2 question-wrap" contenteditable="true" style="outline:none; border-bottom: 1px dashed transparent; transition: border-color 0.2s;" onfocus="this.style.borderColor='#1E88E5'" onblur="this.style.borderColor='transparent'">${q}</td>
                <td class="text-end pe-3"><button class="btn btn-sm btn-light text-danger btn-delete-row" data-index="${i}"><i class="bi bi-trash"></i></button></td>
            `;
            tbody.appendChild(tr);
        });
        if (window.lucide) window.lucide.createIcons();
        
        updatePreviewCount();

        // Bind delete row
        document.querySelectorAll('.btn-delete-row').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.currentTarget.closest('tr').remove();
                updatePreviewCount();
            });
        });
        
        // Bind select all
        const selectAll = document.getElementById('selectAllPreview');
        if(selectAll) {
            selectAll.checked = true;
            selectAll.addEventListener('change', (e) => {
                document.querySelectorAll('.preview-checkbox').forEach(cb => {
                    cb.checked = e.target.checked;
                });
                updatePreviewCount();
            });
        }
        
        // Update count when individual checkboxes change
        document.querySelectorAll('.preview-checkbox').forEach(cb => {
            cb.addEventListener('change', updatePreviewCount);
        });
    }

    function updatePreviewCount() {
        const checkedCount = document.querySelectorAll('.preview-checkbox:checked').length;
        document.getElementById('previewCount').textContent = document.querySelectorAll('#previewTbody tr').length;
        document.getElementById('startProcessingCount').textContent = checkedCount;
    }

    if (document.getElementById('btnDeleteSelectedPreview')) {
        document.getElementById('btnDeleteSelectedPreview').addEventListener('click', () => {
            document.querySelectorAll('.preview-checkbox:checked').forEach(cb => {
                cb.closest('tr').remove();
            });
            updatePreviewCount();
            document.getElementById('selectAllPreview').checked = false;
        });
    }

    function resetBatchUI() {
        globalBatchResults = [];
        currentFilteredResults = [];
        currentFilteredIndex = 0;
        _lastRenderedCount = 0;
        _lastKpiMilestone = 0;
        _lastProcessedCount = -1;
        currentPage = 1;

        if (pollInterval) {
            clearInterval(pollInterval);
            pollInterval = null;
        }
        currentSessionId = null;

        const progressBar = document.getElementById('progressBar');
        if (progressBar) {
            progressBar.style.width = '0%';
            progressBar.classList.remove('progress-bar-animated');
        }

        const progressText = document.getElementById('progressText');
        if (progressText) progressText.textContent = 'Processing: 0 / 0';

        const progressSpeed = document.getElementById('progressSpeed');
        if (progressSpeed) progressSpeed.textContent = 'Speed: 0.0 qs/sec';

        const progressETA = document.getElementById('progressETA');
        if (progressETA) progressETA.textContent = 'ETA: Calculating...';

        const uploadBtn = document.getElementById('uploadBtn');
        if (uploadBtn) {
            uploadBtn.disabled = false;
            uploadBtn.classList.remove('hidden');
        }

        const btnStopBatch = document.getElementById('btnStopBatch');
        if (btnStopBatch) {
            btnStopBatch.classList.add('hidden');
            btnStopBatch.disabled = false;
            btnStopBatch.innerHTML = '<i class="bi bi-stop-circle me-1"></i>Stop';
        }

        const staleBody = document.getElementById('resultsTbody');
        const staleHead = document.getElementById('resultsThead');
        if (staleBody) staleBody.innerHTML = '';
        if (staleHead) staleHead.innerHTML = '';

        const pagInfo = document.getElementById('tablePaginationInfo');
        if (pagInfo) pagInfo.textContent = 'Showing 0 to 0 of 0';

        const pagControls = document.getElementById('tablePagination');
        if (pagControls) pagControls.innerHTML = '';

        const carouselQuestion = document.getElementById('carouselQuestion');
        if (carouselQuestion) carouselQuestion.textContent = '-';

        const carouselCounter = document.getElementById('carouselCounter');
        if (carouselCounter) carouselCounter.textContent = '0 / 0';

        const carouselDiff = document.getElementById('carouselDiff');
        if (carouselDiff) carouselDiff.textContent = '-';

        const carouselExp = document.getElementById('carouselExp');
        if (carouselExp) carouselExp.textContent = '-';

        const liveStatTotal = document.getElementById('liveStatTotal');
        if (liveStatTotal) liveStatTotal.textContent = '0';
        const liveStatEasy = document.getElementById('liveStatEasy');
        if (liveStatEasy) liveStatEasy.textContent = '0';
        const liveStatMod = document.getElementById('liveStatMod');
        if (liveStatMod) liveStatMod.textContent = '0';
        const liveStatDiff = document.getElementById('liveStatDiff');
        if (liveStatDiff) liveStatDiff.textContent = '0';
        const liveStatConf = document.getElementById('liveStatConf');
        if (liveStatConf) liveStatConf.textContent = '0%';
    }

    if (document.getElementById('btnStartProcessingPreview')) {
        document.getElementById('btnStartProcessingPreview').addEventListener('click', async () => {
            // Harvest edited questions
            const finalQuestions = [];
            document.querySelectorAll('#previewTbody tr').forEach(tr => {
                const cb = tr.querySelector('.preview-checkbox');
                if (cb && cb.checked) {
                    const textNode = tr.querySelector('.preview-text');
                    if (textNode && textNode.textContent.trim()) {
                        finalQuestions.push(textNode.textContent.trim());
                    }
                }
            });

            if (finalQuestions.length === 0) {
                alert("No valid questions selected for processing.");
                return;
            }

            // Immediately reset Batch UI to 0% clean state before submission
            resetBatchUI();

            document.getElementById('previewSection').classList.add('hidden');
            if (liveProgressPanel) liveProgressPanel.classList.remove('hidden');
            if (liveStatsRow) liveStatsRow.classList.remove('hidden');
            if (batchResultsSection) batchResultsSection.classList.remove('hidden');
            
            const analyticsContent = document.getElementById('analyticsContent');
            if (analyticsContent) analyticsContent.classList.remove('hidden');
            
            const analyticsEmpty = document.getElementById('analyticsEmpty');
            if (analyticsEmpty) analyticsEmpty.classList.add('hidden');
            
            const dashNoDataMsg = document.getElementById('dashNoDataMsg');
            if (dashNoDataMsg) dashNoDataMsg.classList.add('hidden');
            
            if (uploadBtn) uploadBtn.disabled = true;

            if (btnStopBatch) {
                btnStopBatch.classList.remove('hidden');
                btnStopBatch.disabled = false;
                btnStopBatch.innerHTML = '<i class="bi bi-stop-circle me-1"></i>Stop';
            }

            try {
                const response = await fetch('/upload-batch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ questions: finalQuestions, filename: currentFileName })
                });
                const data = await response.json();
                
                if (response.ok) {
                    currentSessionId = data.session_id;
                    exportSessionId.value = currentSessionId;

                    // Reset polling state for new batch
                    _lastProcessedCount = -1;
                    _lastKpiMilestone = 0;
                    _lastRenderedCount = 0;
                    
                    // Start background thread
                    await fetch(`/start-batch/${currentSessionId}`, { method: 'POST' });
                    
                    // Start 1000ms polling
                    pollInterval = setInterval(pollBatchStatus, 1000);
                } else {
                    alert('Error starting batch: ' + data.error);
                }
            } catch (e) {
                console.error(e);
                alert('Error submitting batch data.');
            }
        });
    }

    async function pollBatchStatus() {
        if(!currentSessionId) return;
        const t_start = performance.now();
        
        let t_net = 0, t_parse = 0, t_prog = 0, t_table = 0, t_pag = 0, t_nav = 0, t_stats = 0;
        let rowsRenderedCount = 0;

        try {
            const t_net_s = performance.now();
            const res = await fetch(`/batch-status/${currentSessionId}`);
            t_net = performance.now() - t_net_s;

            const t_parse_s = performance.now();
            const data = await res.json();
            t_parse = performance.now() - t_parse_s;
            
            if(data.error) {
                clearInterval(pollInterval);
                return;
            }
            
            globalBatchResults = (data.results || []).map(r => {
                if (r.difficulty === 'Moderate') r.difficulty = 'Medium';
                if (r.difficulty === 'Difficult') r.difficulty = 'Hard';
                if (r.variants) {
                    r.variants.forEach(v => {
                        if (v.predicted_difficulty === 'Moderate' || v.target_difficulty === 'Moderate') {
                            if (v.predicted_difficulty === 'Moderate') v.predicted_difficulty = 'Medium';
                            if (v.target_difficulty === 'Moderate') v.target_difficulty = 'Medium';
                        }
                        if (v.predicted_difficulty === 'Difficult' || v.target_difficulty === 'Difficult') {
                            if (v.predicted_difficulty === 'Difficult') v.predicted_difficulty = 'Hard';
                            if (v.target_difficulty === 'Difficult') v.target_difficulty = 'Hard';
                        }
                    });
                }
                return r;
            });
            
            // ── Phase 1: Progress + incremental table/navigator update (every poll) ─
            const t_prog_s = performance.now();
            const pct = data.total > 0 ? (data.processed / data.total) * 100 : 0;
            progressBar.style.width = pct + '%';
            progressText.textContent = `Processing: ${data.processed} / ${data.total}`;
            progressSpeed.textContent = `Speed: ${data.speed} qs/sec`;
            progressETA.textContent = `ETA: ${data.eta} sec`;
            t_prog = performance.now() - t_prog_s;

            // Append newly classified results belonging to active page + update live pagination controls
            if (globalBatchResults.length > _lastRenderedCount) {
                const totalItems = globalBatchResults.length;
                const totalPages = Math.ceil(totalItems / itemsPerPage) || 1;

                if (currentPage > totalPages) currentPage = totalPages;

                const start = (currentPage - 1) * itemsPerPage;
                const end = Math.min(start + itemsPerPage, totalItems);

                const t_table_s = performance.now();
                const newResults = globalBatchResults.slice(_lastRenderedCount);
                newResults.forEach((r, idx) => {
                    const globalIndex = _lastRenderedCount + idx;
                    const itemPage = Math.floor(globalIndex / itemsPerPage) + 1;
                    if (itemPage === currentPage) {
                        appendLiveResult(r);
                        rowsRenderedCount++;
                    }
                });
                _lastRenderedCount = globalBatchResults.length;
                t_table = performance.now() - t_table_s;

                // Dynamic live pagination info & button controls update
                const t_pag_s = performance.now();
                const infoEl = document.getElementById('tablePaginationInfo');
                if (infoEl) infoEl.textContent = `Showing ${start + (totalItems > 0 ? 1 : 0)} to ${end} of ${totalItems}`;
                renderPagination(totalItems, totalPages, globalBatchResults);
                t_pag = performance.now() - t_pag_s;

                // Batch-tab live stat row (Total / Easy / Med / Hard / Avg Conf)
                const t_stats_s = performance.now();
                updateLiveStats(globalBatchResults);
                t_stats = performance.now() - t_stats_s;

                // Question Navigator: advance to the latest classified question
                const t_nav_s = performance.now();
                currentFilteredResults = [];
                currentFilteredIndex = globalBatchResults.length - 1;
                updateCarouselUI();
                t_nav = performance.now() - t_nav_s;
            }

            // Sync in-memory local history entry — no DOM updates here
            let localHist = batchHistoryData.find(h => h.session_id === currentSessionId);
            if (!localHist && currentSessionId) {
                const displayEl = document.getElementById('fileNameDisplay');
                localHist = {
                    session_id: currentSessionId,
                    filename: displayEl ? displayEl.textContent.replace('Uploaded File:', '').replace('File:', '').trim() : 'Batch Upload',
                    upload_time: new Date().toISOString(),
                    total_questions: data.total,
                    completed_questions: data.processed,
                    status: data.status,
                    easy_count: 0,
                    medium_count: 0,
                    hard_count: 0,
                    bloom_counts: { Remember: 0, Understand: 0, Apply: 0, Analyze: 0, Evaluate: 0, Create: 0 },
                    avg_confidence: 0
                };
                batchHistoryData.unshift(localHist);
            }
            if (localHist) {
                localHist.completed_questions = data.processed;
                localHist.total_questions = data.total;
                localHist.status = data.status;

                let easy = 0, medium = 0, hard = 0;
                let bloomCounts = { Remember: 0, Understand: 0, Apply: 0, Analyze: 0, Evaluate: 0, Create: 0 };
                let totalConf = 0;
                globalBatchResults.forEach(r => {
                    if (r.difficulty === 'Easy') easy++;
                    else if (r.difficulty === 'Medium' || r.difficulty === 'Moderate') medium++;
                    else if (r.difficulty === 'Hard' || r.difficulty === 'Difficult') hard++;
                    if (r.bloom_level in bloomCounts) bloomCounts[r.bloom_level]++;
                    totalConf += parseFloat(r.confidence) || 0;
                });
                localHist.easy_count = easy;
                localHist.medium_count = medium;
                localHist.hard_count = hard;
                localHist.bloom_counts = bloomCounts;
                localHist.avg_confidence = globalBatchResults.length > 0 ? (totalConf / globalBatchResults.length) : 0;
            }

            _lastProcessedCount = data.processed;

            // ── Phase 2: Full refresh exactly once on batch completion ────────────
            if (data.status === 'COMPLETED' || data.status === 'STOPPED' || data.status === 'FAILED') {
                if (pollInterval) {
                    clearInterval(pollInterval);
                    pollInterval = null;
                }
                if (uploadBtn) {
                    uploadBtn.disabled = false;
                    uploadBtn.classList.remove('hidden');
                }
                if (uploadSpinner) uploadSpinner.classList.add('hidden');

                if (btnStopBatch) {
                    btnStopBatch.disabled = true;
                    btnStopBatch.classList.add('hidden');
                    if (data.status === 'COMPLETED') btnStopBatch.innerHTML = '<i class="bi bi-check-circle me-1"></i>Completed';
                    else if (data.status === 'STOPPED') btnStopBatch.innerHTML = '<i class="bi bi-pause-circle me-1"></i>Stopped';
                }

                if (progressBar) progressBar.classList.remove('progress-bar-animated');

                // Single comprehensive refresh — each expensive call runs exactly once
                renderTable(globalBatchResults);      // results table
                renderCharts(globalBatchResults);     // Bloom, Difficulty & Confidence charts
                updateCarouselBounds();               // question carousel
                updateLiveStats(globalBatchResults, true); // batch-tab stat row + dashboard KPIs
                fetchBatchHistory();                  // full dashboard: history, activity, stats, charts
                updateDashboardWorkspaceStats();     // full KPI cards update after batch completion

                currentSessionId = null;
            }
            
            const pollDuration = performance.now() - t_start;
            console.log(`[PERF-FRONTEND] pollBatchStatus() took ${pollDuration.toFixed(2)} ms`);
            if (pollDuration > 50) {
                console.warn(`[PERF-WARNING] pollBatchStatus() exceeded 50ms threshold: ${pollDuration.toFixed(2)} ms`);
            }
        } catch(e) {
            console.error("Polling error", e);
        }
    }

    if(btnStopBatch) {
        btnStopBatch.addEventListener('click', async () => {
            if(!currentSessionId) return;
            btnStopBatch.disabled = true;
            btnStopBatch.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
            try {
                await fetch(`/stop-batch/${currentSessionId}`, { method: 'POST' });
            } catch(e) {
                console.error("Error stopping batch", e);
            }
        });
    }

    function updateLiveStats(results, updateDash = false) {
        let easy = 0, mod = 0, diff = 0, totalConf = 0;
        
        results.forEach(r => {
            if (r.difficulty === 'Easy') easy++;
            else if (r.difficulty === 'Medium' || r.difficulty === 'Moderate') mod++;
            else if (r.difficulty === 'Hard' || r.difficulty === 'Difficult') diff++;
            totalConf += parseFloat(r.confidence);
        });

        const avgConf = results.length > 0 ? (totalConf / results.length).toFixed(1) + '%' : '0%';

        // Batch Tab Stats
        document.getElementById('liveStatTotal').textContent = results.length;
        document.getElementById('liveStatEasy').textContent = easy;
        document.getElementById('liveStatMod').textContent = mod;
        document.getElementById('liveStatDiff').textContent = diff;
        if (document.getElementById('liveStatConf')) {
            document.getElementById('liveStatConf').textContent = avgConf;
        }

        if (updateDash) {
            // Dashboard Stats Update only when processing finishes
            document.getElementById('dashTotal').textContent = results.length;
            document.getElementById('dashEasy').textContent = easy;
            document.getElementById('dashMod').textContent = mod;
            document.getElementById('dashDiff').textContent = diff;
        }
    }

    // --- Table Rendering ---
    let currentPage = 1;
    let itemsPerPage = 10;
    
    function getFilteredData() {
        const query = (document.getElementById('searchTable') ? document.getElementById('searchTable').value.toLowerCase() : '');
        const statusFilter = (document.getElementById('filterStatus') ? document.getElementById('filterStatus').value : '');
        
        return globalBatchResults.filter(r => {
            const matchQuery = !query || 
                r.question.toLowerCase().includes(query) || 
                r.bloom_level.toLowerCase().includes(query) ||
                r.difficulty.toLowerCase().includes(query) ||
                displayDifficulty(r.difficulty).toLowerCase().includes(query) ||
                (r.tags && r.tags.some(t => t.toLowerCase().includes(query)));
                
            const matchStatus = !statusFilter || r.status === statusFilter;
            
            return matchQuery && matchStatus;
        });
    }

    function updateTableFilters() {
        currentPage = 1;
        renderTable(getFilteredData());
    }

    if(document.getElementById('searchTable')) {
        document.getElementById('searchTable').addEventListener('input', updateTableFilters);
    }
    if(document.getElementById('filterStatus')) {
        document.getElementById('filterStatus').addEventListener('change', updateTableFilters);
    }
    if(document.getElementById('itemsPerPageSelect')) {
        document.getElementById('itemsPerPageSelect').addEventListener('change', (e) => {
            itemsPerPage = parseInt(e.target.value, 10);
            currentPage = 1;
            renderTable(getFilteredData());
        });
    }

    function renderTable(dataToRender) {
        // Keep a reference to the filtered set driving the current table view
        currentFilteredResults = dataToRender;
        const tbody = document.getElementById('resultsTbody');
        const thead = document.getElementById('resultsThead');
        if(!tbody || !thead) return;
        tbody.innerHTML = '';
        
        thead.innerHTML = `
            <tr class="border-b border-gray-100 text-[11px] uppercase tracking-wider text-slate-400 dark:border-slate-800 dark:text-slate-500">
                <th class="pl-4 pr-2 py-3 w-10 align-middle"><input type="checkbox" id="selectAllRows" class="rounded border-gray-300 text-blue-500 focus:ring-blue-500"></th>
                <th class="pl-2 pr-4 py-3 font-semibold align-middle text-left">Question</th>
                <th class="px-4 py-3 font-semibold w-36 align-middle text-left">Status</th>
                <th class="px-4 py-3 font-semibold w-44 align-middle text-left">Current Difficulty</th>
                <th class="pr-4 pl-2 py-3 font-semibold w-28 text-right align-middle">Actions</th>
            </tr>
        `;

        if (dataToRender.length === 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td colspan="5" class="px-6 py-10 text-center text-slate-500 dark:text-slate-400">
                    <div class="flex flex-col items-center justify-center gap-2">
                        <i data-lucide="inbox" class="h-8 w-8 text-slate-400"></i>
                        <span>No results found</span>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
            if (window.lucide) window.lucide.createIcons();
            document.getElementById('tablePaginationInfo').textContent = 'Showing 0 to 0 of 0';
            const pagContainer = document.getElementById('tablePagination');
            if (pagContainer) pagContainer.innerHTML = '';
            return;
        }
        
        // Bind select all
        setTimeout(() => {
            const selectAll = document.getElementById('selectAllRows');
            if (selectAll) {
                selectAll.addEventListener('change', (e) => {
                    document.querySelectorAll('.row-checkbox').forEach(cb => cb.checked = e.target.checked);
                });
            }
        }, 0);
        
        const totalItems = dataToRender.length;
        const totalPages = Math.ceil(totalItems / itemsPerPage) || 1;
        if (currentPage > totalPages) currentPage = totalPages;
        
        const start = (currentPage - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        const paginatedData = dataToRender.slice(start, end);
 
        paginatedData.forEach((r, idx) => {
            // Find global index
            const globalIndex = globalBatchResults.findIndex(gr => gr.id === r.id);
            if (globalIndex === -1) return;
            
            let diffBadge = '';
            if (r.difficulty === 'Easy') {
                diffBadge = `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/20">${displayDifficulty('Easy')}</span>`;
            } else if (r.difficulty === 'Medium' || r.difficulty === 'Moderate') {
                diffBadge = `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-500/10 dark:text-amber-400 dark:border-amber-500/20">${displayDifficulty('Medium')}</span>`;
            } else {
                diffBadge = `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-500/10 dark:text-rose-400 dark:border-rose-500/20">${displayDifficulty('Hard')}</span>`;
            }
            
            let statusBadge = '';
            if (r.status === 'Verified') statusBadge = '<span class="inline-flex rounded-full bg-emerald-100 px-2 py-0.5 text-[11px] font-semibold text-emerald-900 dark:bg-emerald-500/20 dark:text-emerald-400">Verified</span>';
            else if (r.status === 'Approved') statusBadge = '<span class="inline-flex rounded-full bg-blue-100 px-2 py-0.5 text-[11px] font-semibold text-blue-900 dark:bg-blue-500/20 dark:text-blue-400">Approved</span>';
            else if (r.status === 'Rejected') statusBadge = '<span class="inline-flex rounded-full bg-rose-100 px-2 py-0.5 text-[11px] font-semibold text-rose-900 dark:bg-rose-500/20 dark:text-rose-400">Rejected</span>';
            else statusBadge = '<span class="inline-flex rounded-full bg-amber-100 px-2 py-0.5 text-[11px] font-semibold text-amber-900 dark:bg-amber-500/20 dark:text-amber-400">Needs Review</span>';
 
            const tr = document.createElement('tr');
            tr.className = "hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer transition-colors border-b border-gray-100 dark:border-slate-800";
            
            tr.innerHTML = `
                <td class="pl-4 pr-2 py-3 w-10 align-middle" onclick="event.stopPropagation()"><input type="checkbox" class="row-checkbox rounded border-gray-300 text-blue-500 focus:ring-blue-500" value="${r.id}"></td>
                <td class="pl-2 pr-4 py-3 align-middle" onclick="openDrawer(${globalIndex})"><div class="text-[13px] font-semibold leading-relaxed text-slate-850 dark:text-slate-200 question-wrap" title="${r.question.replace(/"/g, '&quot;')}">${r.question.trim()}</div></td>
                <td class="px-4 py-3 w-36 align-middle" onclick="openDrawer(${globalIndex})">${statusBadge}</td>
                <td class="px-4 py-3 w-44 align-middle" onclick="openDrawer(${globalIndex})">${diffBadge}</td>
                <td class="pr-4 pl-2 py-3 w-28 text-right align-middle" onclick="event.stopPropagation()">
                    <div class="flex justify-end items-center gap-2">
                        <button class="w-8 h-8 flex items-center justify-center rounded-md border border-gray-200 bg-white text-slate-500 hover:bg-slate-50 hover:text-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500/20 disabled:opacity-50 disabled:pointer-events-none dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-blue-400 transition" onclick="openDrawer(${globalIndex})" title="View Details">
                            <i data-lucide="eye" class="w-3.5 h-3.5"></i>
                        </button>
                        <button class="w-8 h-8 flex items-center justify-center rounded-md border border-gray-200 bg-white text-slate-500 hover:bg-slate-50 hover:text-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500/20 disabled:opacity-50 disabled:pointer-events-none dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-blue-400 transition" onclick="sendToStudioFromTable(${globalIndex})" title="Open in Studio">
                            <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
        if (window.lucide) window.lucide.createIcons();
 
        document.getElementById('tablePaginationInfo').textContent = `Showing ${start + (totalItems>0?1:0)} to ${Math.min(end, totalItems)} of ${totalItems}`;
        renderPagination(totalItems, totalPages, dataToRender);
    }

    /**
     * appendLiveResult — appends a single newly classified result row to the
     * results table without rebuilding the entire tbody. Used during live polling.
     */
    function appendLiveResult(r) {
        const t0 = performance.now();
        const tbody = document.getElementById('resultsTbody');
        const thead = document.getElementById('resultsThead');
        if (!tbody || !thead) return;

        // Ensure thead is present on first row render
        if (!thead.innerHTML.trim()) {
            thead.innerHTML = `
                <tr class="border-b border-gray-100 text-[11px] uppercase tracking-wider text-slate-400 dark:border-slate-800 dark:text-slate-500">
                    <th class="pl-4 pr-2 py-3 w-10 align-middle"><input type="checkbox" id="selectAllRows" class="rounded border-gray-300 text-blue-500 focus:ring-blue-500"></th>
                    <th class="pl-2 pr-4 py-3 font-semibold align-middle text-left">Question</th>
                    <th class="px-4 py-3 font-semibold w-36 align-middle text-left">Status</th>
                    <th class="px-4 py-3 font-semibold w-44 align-middle text-left">Current Difficulty</th>
                    <th class="pr-4 pl-2 py-3 font-semibold w-28 text-right align-middle">Actions</th>
                </tr>`;
        }

        const globalIndex = globalBatchResults.findIndex(gr => gr.id === r.id);
        if (globalIndex === -1) return;

        let diffBadge;
        if (r.difficulty === 'Easy') {
            diffBadge = `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/20">${displayDifficulty('Easy')}</span>`;
        } else if (r.difficulty === 'Medium' || r.difficulty === 'Moderate') {
            diffBadge = `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-500/10 dark:text-amber-400 dark:border-amber-500/20">${displayDifficulty('Medium')}</span>`;
        } else {
            diffBadge = `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-500/10 dark:text-rose-400 dark:border-rose-500/20">${displayDifficulty('Hard')}</span>`;
        }

        let statusBadge;
        if (r.status === 'Verified')  statusBadge = '<span class="inline-flex rounded-full bg-emerald-100 px-2 py-0.5 text-[11px] font-semibold text-emerald-900 dark:bg-emerald-500/20 dark:text-emerald-400">Verified</span>';
        else if (r.status === 'Approved') statusBadge = '<span class="inline-flex rounded-full bg-blue-100 px-2 py-0.5 text-[11px] font-semibold text-blue-900 dark:bg-blue-500/20 dark:text-blue-400">Approved</span>';
        else if (r.status === 'Rejected') statusBadge = '<span class="inline-flex rounded-full bg-rose-100 px-2 py-0.5 text-[11px] font-semibold text-rose-900 dark:bg-rose-500/20 dark:text-rose-400">Rejected</span>';
        else statusBadge = '<span class="inline-flex rounded-full bg-amber-100 px-2 py-0.5 text-[11px] font-semibold text-amber-900 dark:bg-amber-500/20 dark:text-amber-400">Needs Review</span>';

        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer transition-colors border-b border-gray-100 dark:border-slate-800';
        tr.innerHTML = `
            <td class="pl-4 pr-2 py-3 w-10 align-middle" onclick="event.stopPropagation()"><input type="checkbox" class="row-checkbox rounded border-gray-300 text-blue-500 focus:ring-blue-500" value="${r.id}"></td>
            <td class="pl-2 pr-4 py-3 align-middle" onclick="openDrawer(${globalIndex})"><div class="text-[13px] font-semibold leading-relaxed text-slate-850 dark:text-slate-200 question-wrap" title="${r.question.replace(/"/g, '&quot;')}">${r.question.trim()}</div></td>
            <td class="px-4 py-3 w-36 align-middle" onclick="openDrawer(${globalIndex})">${statusBadge}</td>
            <td class="px-4 py-3 w-44 align-middle" onclick="openDrawer(${globalIndex})">${diffBadge}</td>
            <td class="pr-4 pl-2 py-3 w-28 text-right align-middle" onclick="event.stopPropagation()">
                <div class="flex justify-end items-center gap-2">
                    <button class="w-8 h-8 flex items-center justify-center rounded-md border border-gray-200 bg-white text-slate-500 hover:bg-slate-50 hover:text-blue-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-blue-400 transition" onclick="openDrawer(${globalIndex})" title="View Details"><i data-lucide="eye" class="w-3.5 h-3.5"></i></button>
                    <button class="w-8 h-8 flex items-center justify-center rounded-md border border-gray-200 bg-white text-slate-500 hover:bg-slate-50 hover:text-blue-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-blue-400 transition" onclick="sendToStudioFromTable(${globalIndex})" title="Open in Studio"><i data-lucide="external-link" class="w-3.5 h-3.5"></i></button>
                </div>
            </td>`;
        tbody.appendChild(tr);
        if (window.lucide) window.lucide.createIcons();

        const duration = performance.now() - t0;
        console.log(`[PERF-FRONTEND] appendLiveResult() took ${duration.toFixed(2)} ms for question id ${r.id}`);
        if (duration > 50) {
            console.warn(`[PERF-WARNING] appendLiveResult() exceeded 50ms threshold: ${duration.toFixed(2)} ms`);
        }
    }

    window.editQuestion = async function(id, globalIndex) {
        const r = globalBatchResults[globalIndex];
        const newQ = prompt("Edit Question:", r.question.replace(/\s+/g, ' ').trim());
        if (!newQ || newQ === r.question) return;
        
        const sessionId = document.getElementById('exportSessionId').value;
        try {
            const response = await fetch(`/update-question/${sessionId}/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: newQ })
            });
            const data = await response.json();
            if (data.error) {
                alert(data.error);
                return;
            }
            // Update local array
            globalBatchResults[globalIndex] = data.result;
            
        } catch(e) {
            alert("Error updating question: " + e.message);
        }
    };

    function renderPagination(totalItems, totalPages, currentData) {
        const pagContainer = document.getElementById('tablePagination');
        if(!pagContainer) return;
        pagContainer.innerHTML = '';
        
        // Previous Button
        const prevDisabled = currentPage === 1;
        pagContainer.innerHTML += `
            <li>
                <a class="${prevDisabled ? 'w-9 h-9 rounded-md border border-gray-100 bg-gray-50 text-slate-400 dark:border-slate-800 dark:bg-slate-900/50 dark:text-slate-600 flex items-center justify-center cursor-not-allowed pointer-events-none' : 'w-9 h-9 rounded-md border border-gray-200 bg-white text-slate-600 hover:bg-gray-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 flex items-center justify-center transition-colors cursor-pointer'}" onclick="${prevDisabled ? '' : `changePage(${currentPage - 1})`}">
                    <i data-lucide="chevron-left" class="w-4 h-4"></i>
                </a>
            </li>
        `;
        
        for(let i=1; i<=totalPages; i++){
            if(i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)){
                const isActive = currentPage === i;
                pagContainer.innerHTML += `
                    <li>
                        <a class="${isActive ? 'w-9 h-9 text-xs font-semibold rounded-md border border-blue-600 bg-blue-600 text-white dark:border-blue-500 dark:bg-blue-500 flex items-center justify-center transition-colors cursor-pointer' : 'w-9 h-9 text-xs font-medium rounded-md border border-gray-200 bg-white text-slate-600 hover:bg-gray-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 flex items-center justify-center transition-colors cursor-pointer'}" onclick="changePage(${i})">${i}</a>
                    </li>
                `;
            } else if (i === currentPage - 2 || i === currentPage + 2) {
                pagContainer.innerHTML += `<li><span class="w-9 h-9 text-xs font-medium text-slate-400 dark:text-slate-600 flex items-center justify-center select-none">...</span></li>`;
            }
        }

        // Next Button
        const nextDisabled = currentPage === totalPages;
        pagContainer.innerHTML += `
            <li>
                <a class="${nextDisabled ? 'w-9 h-9 rounded-md border border-gray-100 bg-gray-50 text-slate-400 dark:border-slate-800 dark:bg-slate-900/50 dark:text-slate-600 flex items-center justify-center cursor-not-allowed pointer-events-none' : 'w-9 h-9 rounded-md border border-gray-200 bg-white text-slate-600 hover:bg-gray-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 flex items-center justify-center transition-colors cursor-pointer'}" onclick="${nextDisabled ? '' : `changePage(${currentPage + 1})`}">
                    <i data-lucide="chevron-right" class="w-4 h-4"></i>
                </a>
            </li>
        `;
    }

    window.changePage = function(page) {
        const filtered = getFilteredData();
        const totalItems = filtered.length;
        const totalPages = Math.ceil(totalItems / itemsPerPage) || 1;
        if(page >= 1 && page <= totalPages) {
            currentPage = page;
            renderTable(filtered);
        }
    }

    // --- Carousel Navigator ---
    let carouselIndex = 0;
    
    // --- Drawer Integration V3 ---
    let currentDrawerIndex = -1;

    // Tracks the filtered/visible result set so carousel prev/next stays in sync
    let currentFilteredResults = [];
    let currentFilteredIndex = 0;

    window.closeDrawer = function() {
        const drawerEl = document.getElementById('questionDetailDrawer');
        const drawerOverlay = document.getElementById('drawerOverlay');
        if (drawerEl) {
            drawerEl.classList.remove('translate-x-0');
            drawerEl.classList.add('translate-x-full');
        }
        if (drawerOverlay) {
            drawerOverlay.classList.add('hidden');
        }
        currentDrawerIndex = -1;
    }

    const closeDrawerBtn = document.getElementById('closeDrawerBtn');
    if (closeDrawerBtn) closeDrawerBtn.addEventListener('click', closeDrawer);
    
    const drawerOverlay = document.getElementById('drawerOverlay');
    if (drawerOverlay) drawerOverlay.addEventListener('click', closeDrawer);

    window.openDrawer = function(index) {
        if (index >= 0 && index < globalBatchResults.length) {
            currentDrawerIndex = index;
            const r = globalBatchResults[index];

            // Sync carousel/filtered index: find position of this question in the currently filtered list
            const filteredPos = currentFilteredResults.findIndex(fr => fr.id === r.id);
            currentFilteredIndex = filteredPos >= 0 ? filteredPos : 0;
            
            // Populate ID and Timestamp
            document.getElementById('drawerQuestionId').textContent = r.id;
            document.getElementById('drawerTimestamp').textContent = r.timestamp || '-';
            
            // Populate Details
            document.getElementById('drawerQuestion').textContent = r.question;
            document.getElementById('drawerBloom').textContent = r.bloom_level;
            
            const diffBadge = document.getElementById('drawerDiff');
            if (diffBadge) {
                diffBadge.textContent = displayDifficulty(r.difficulty);
                diffBadge.className = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ';
                if (r.difficulty === 'Easy') {
                    diffBadge.classList.add('bg-emerald-50', 'text-emerald-700', 'border-emerald-200', 'dark:bg-emerald-500/10', 'dark:text-emerald-400', 'dark:border-emerald-500/20');
                } else if (r.difficulty === 'Medium' || r.difficulty === 'Moderate') {
                    diffBadge.classList.add('bg-amber-50', 'text-amber-700', 'border-amber-200', 'dark:bg-amber-500/10', 'dark:text-amber-400', 'dark:border-amber-500/20');
                } else {
                    diffBadge.classList.add('bg-rose-50', 'text-rose-700', 'border-rose-200', 'dark:bg-rose-500/10', 'dark:text-rose-400', 'dark:border-rose-500/20');
                }
            }
            
            const drawerConfText = document.getElementById('drawerConfText');
            if (drawerConfText) drawerConfText.textContent = r.confidence + '%';
            
            const drawerConfBar = document.getElementById('drawerConfBar');
            if (drawerConfBar) drawerConfBar.style.width = r.confidence + '%';
            
            document.getElementById('drawerExplanation').innerHTML = r.explanation;
            
            // Populate Status Badge & Select
            const statusSelect = document.getElementById('drawerStatusSelect');
            const statusBadge = document.getElementById('drawerStatusBadge');
            if (statusSelect) statusSelect.value = r.status || 'Verified';
            if (statusBadge) {
                statusBadge.textContent = r.status || 'Verified';
                statusBadge.className = 'rounded-full px-2.5 py-0.5 text-[11px] font-semibold flex items-center ';
                if (r.status === 'Verified') statusBadge.classList.add('bg-emerald-100', 'text-emerald-900', 'dark:bg-emerald-500/20', 'dark:text-emerald-400');
                else if (r.status === 'Approved') statusBadge.classList.add('bg-blue-100', 'text-blue-900', 'dark:bg-blue-500/20', 'dark:text-blue-400');
                else if (r.status === 'Rejected') statusBadge.classList.add('bg-rose-100', 'text-rose-900', 'dark:bg-rose-500/20', 'dark:text-rose-400');
                else statusBadge.classList.add('bg-amber-100', 'text-amber-900', 'dark:bg-amber-500/20', 'dark:text-amber-400');
                statusBadge.classList.remove('hidden');
            }
 
            // Populate Previous Classification if it exists
            const prevContainer = document.getElementById('drawerPrevClassContainer');
            if (r.previous_classification) {
                document.getElementById('drawerPrevBloom').textContent = r.previous_classification.bloom_level;
                
                const prevDiffBadge = document.getElementById('drawerPrevDiff');
                if (prevDiffBadge) {
                    prevDiffBadge.textContent = displayDifficulty(r.previous_classification.difficulty);
                    prevDiffBadge.className = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ';
                    if (r.previous_classification.difficulty === 'Easy') {
                        prevDiffBadge.classList.add('bg-emerald-50/70', 'text-emerald-700/70', 'border-emerald-200/70', 'dark:bg-emerald-500/5', 'dark:text-emerald-400/70', 'dark:border-emerald-500/10');
                    } else if (r.previous_classification.difficulty === 'Medium' || r.previous_classification.difficulty === 'Moderate') {
                        prevDiffBadge.classList.add('bg-amber-50/70', 'text-amber-700/70', 'border-amber-200/70', 'dark:bg-amber-500/5', 'dark:text-amber-400/70', 'dark:border-amber-500/10');
                    } else {
                        prevDiffBadge.classList.add('bg-rose-50/70', 'text-rose-700/70', 'border-rose-200/70', 'dark:bg-rose-500/5', 'dark:text-rose-400/70', 'dark:border-rose-500/10');
                    }
                }
                
                const prevConfText = document.getElementById('drawerPrevConfText');
                if (prevConfText) prevConfText.textContent = r.previous_classification.confidence + '%';
                if (prevContainer) prevContainer.classList.remove('hidden');
            } else {
                if (prevContainer) prevContainer.classList.add('hidden');
            }
 
            // Populate Notes & Tags
            document.getElementById('drawerNotes').value = r.notes || '';
            renderTags(r.tags || []);
 
            // Populate Variants
            renderDrawerVariants(r.variants || []);

            // Populate Dynamic Generation buttons in Drawer Variant Workspace
            const drawerBtnContainer = document.getElementById('drawerGenerationControlsContainer');
            if (drawerBtnContainer) {
                drawerBtnContainer.innerHTML = '';
                let options = [];
                if (r.difficulty === 'Easy') {
                    options = [
                        { label: displayDifficulty('Medium'), target: 'Medium', colorClass: 'border-amber-200 bg-amber-50 text-amber-700 hover:bg-amber-100 dark:border-amber-900/30 dark:bg-amber-500/10 dark:text-amber-400 dark:hover:bg-amber-500/20' },
                        { label: displayDifficulty('Hard'), target: 'Hard', colorClass: 'border-rose-200 bg-rose-50 text-rose-700 hover:bg-rose-100 dark:border-rose-900/30 dark:bg-rose-500/10 dark:text-rose-400 dark:hover:bg-rose-500/20' }
                    ];
                } else if (r.difficulty === 'Medium') {
                    options = [
                        { label: displayDifficulty('Easy'), target: 'Easy', colorClass: 'border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 dark:border-emerald-900/30 dark:bg-emerald-500/10 dark:text-emerald-400 dark:hover:bg-emerald-500/20' },
                        { label: displayDifficulty('Hard'), target: 'Hard', colorClass: 'border-rose-200 bg-rose-50 text-rose-700 hover:bg-rose-100 dark:border-rose-900/30 dark:bg-rose-500/10 dark:text-rose-400 dark:hover:bg-rose-500/20' }
                    ];
                } else if (r.difficulty === 'Hard') {
                    options = [
                        { label: displayDifficulty('Easy'), target: 'Easy', colorClass: 'border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 dark:border-emerald-900/30 dark:bg-emerald-500/10 dark:text-emerald-400 dark:hover:bg-emerald-500/20' },
                        { label: displayDifficulty('Medium'), target: 'Medium', colorClass: 'border-amber-200 bg-amber-50 text-amber-700 hover:bg-amber-100 dark:border-amber-900/30 dark:bg-amber-500/10 dark:text-amber-400 dark:hover:bg-amber-500/20' }
                    ];
                }
                
                options.forEach(opt => {
                    const btn = document.createElement('button');
                    btn.className = `btn-generate-variant h-9 px-3.5 inline-flex items-center justify-center gap-1.5 rounded-md text-xs font-semibold border transition focus:outline-none focus:ring-2 focus:ring-blue-500/20 disabled:opacity-50 ${opt.colorClass}`;
                    btn.dataset.target = opt.target;
                    btn.innerHTML = opt.label;
                    
                    // Bind event listener directly to this new button
                    btn.addEventListener('click', async (e) => {
                        if (currentDrawerIndex === -1) return;
                        const targetDifficulty = e.currentTarget.dataset.target;
                        const originalQuestion = globalBatchResults[currentDrawerIndex].question;
                        
                        const originalHtml = e.currentTarget.innerHTML;
                        e.currentTarget.innerHTML = '<span class="spinner-border spinner-border-sm w-3 h-3 border-2"></span>';
                        e.currentTarget.disabled = true;
 
                        try {
                            const response = await fetch('/rephrase', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ question: originalQuestion, target_difficulty: targetDifficulty })
                            });
                            const data = await response.json();
                            
                            if (response.ok && data.variants && data.variants.length > 0) {
                                if (!globalBatchResults[currentDrawerIndex].variants) globalBatchResults[currentDrawerIndex].variants = [];
                                data.variants.forEach(newVar => {
                                    newVar.target_difficulty = targetDifficulty;
                                    globalBatchResults[currentDrawerIndex].variants.push(newVar);
                                });
                                renderDrawerVariants(globalBatchResults[currentDrawerIndex].variants);
                            } else {
                                alert('Error: ' + data.error);
                            }
                        } catch (err) {
                            console.error(err);
                            alert("Error generating variant.");
                        } finally {
                            e.currentTarget.innerHTML = originalHtml;
                            e.currentTarget.disabled = false;
                            if (window.lucide) window.lucide.createIcons();
                        }
                    });
                    
                    drawerBtnContainer.appendChild(btn);
                });
            }
            
            // Re-bind carousel index just in case
            carouselIndex = index;
            updateCarouselUI();
            
            // Show Drawer
            const drawerEl = document.getElementById('questionDetailDrawer');
            if (drawerEl) {
                drawerEl.classList.remove('translate-x-full');
                drawerEl.classList.add('translate-x-0');
            }
            if (drawerOverlay) {
                drawerOverlay.classList.remove('hidden');
            }
            if (window.lucide) window.lucide.createIcons();
        }
    }

    // --- Drawer Event Listeners ---
    
    // Status Change
    if(document.getElementById('drawerStatusSelect')) {
        document.getElementById('drawerStatusSelect').addEventListener('change', (e) => {
            if (currentDrawerIndex > -1) {
                globalBatchResults[currentDrawerIndex].status = e.target.value;
                // Re-open to refresh badge internally, or just re-render table
                openDrawer(currentDrawerIndex);
                updateTableFilters(); // update main table
            }
        });
    }

    // Notes auto-save
    if(document.getElementById('drawerNotes')) {
        document.getElementById('drawerNotes').addEventListener('input', (e) => {
            if (currentDrawerIndex > -1) {
                globalBatchResults[currentDrawerIndex].notes = e.target.value;
            }
        });
    }

    // Tags rendering and addition
    function renderTags(tags) {
        const container = document.getElementById('drawerTagsContainer');
        if (!container) return;
        container.innerHTML = '';
        if (tags.length === 0) {
            container.innerHTML = '<span class="text-xs text-slate-400 italic">No tags added</span>';
            return;
        }
        tags.forEach((tag, idx) => {
            const span = document.createElement('span');
            span.className = 'inline-flex items-center gap-1 rounded-lg bg-indigo-50/40 px-2 py-1 text-[10px] font-bold text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-400 border border-indigo-100/50 dark:border-indigo-950/30';
            span.innerHTML = `${tag} <button class="hover:text-indigo-900 dark:hover:text-indigo-300" onclick="removeTag(${idx})"><span class="material-symbols-outlined text-[12px] leading-none">close</span></button>`;
            container.appendChild(span);
        });
        if (window.lucide) window.lucide.createIcons();
    }

    window.removeTag = function(tagIndex) {
        if (currentDrawerIndex > -1) {
            const tags = globalBatchResults[currentDrawerIndex].tags || [];
            tags.splice(tagIndex, 1);
            globalBatchResults[currentDrawerIndex].tags = tags;
            renderTags(tags);
            updateTableFilters();
        }
    };

    function addTag(tag) {
        if (!tag || currentDrawerIndex === -1) return;
        if (!globalBatchResults[currentDrawerIndex].tags) globalBatchResults[currentDrawerIndex].tags = [];
        if (!globalBatchResults[currentDrawerIndex].tags.includes(tag)) {
            globalBatchResults[currentDrawerIndex].tags.push(tag);
            renderTags(globalBatchResults[currentDrawerIndex].tags);
            updateTableFilters();
        }
        document.getElementById('drawerTagInput').value = '';
    }

    if(document.getElementById('btnDrawerAddTag')) {
        document.getElementById('btnDrawerAddTag').addEventListener('click', () => {
            addTag(document.getElementById('drawerTagInput').value.trim());
        });
        document.getElementById('drawerTagInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') addTag(e.target.value.trim());
        });
    }

    document.querySelectorAll('.btn-suggest-tag').forEach(btn => {
        btn.addEventListener('click', (e) => {
            addTag(e.currentTarget.dataset.tag);
        });
    });

    // Variants rendering
    function renderDrawerVariants(variants) {
        const container = document.getElementById('drawerVariantsContainer');
        const emptyMsg = document.getElementById('drawerNoVariantsMsg');
        if (!container || !emptyMsg) return;
        
        container.innerHTML = '';
        if (variants.length === 0) {
            emptyMsg.classList.remove('hidden');
            return;
        }
        emptyMsg.classList.add('hidden');

        variants.forEach((v, vIdx) => {
            let borderClass = 'border-blue-500';
            let textClass = 'text-blue-600 dark:text-blue-400';
            let targetDifficulty = v.target_difficulty || v.predicted_difficulty || 'Unknown';
            if (targetDifficulty === 'Moderate') targetDifficulty = 'Medium';
            if (targetDifficulty === 'Difficult') targetDifficulty = 'Hard';
            let difficultyLabel = displayDifficulty(targetDifficulty);
            
            if (targetDifficulty === 'Easy') { borderClass = 'border-emerald-500'; textClass = 'text-emerald-600 dark:text-emerald-400'; }
            else if (targetDifficulty === 'Medium') { borderClass = 'border-amber-500'; textClass = 'text-amber-600 dark:text-amber-400'; }
            else if (targetDifficulty === 'Hard') { borderClass = 'border-rose-500'; textClass = 'text-rose-600 dark:text-rose-400'; }

            const card = document.createElement('div');
            card.className = `rounded-xl border border-slate-200 bg-white p-4 shadow-sm border-l-4 ${borderClass} dark:border-slate-800 dark:bg-slate-900`;
            
            const encodedQ = v.question.replace(/"/g, '&quot;');
            
            card.innerHTML = `
                <div class="flex justify-between items-start mb-3">
                    <h5 class="text-xs font-bold flex items-center gap-1.5 ${textClass}"><span class="material-symbols-outlined text-[15px]">auto_awesome</span> ${difficultyLabel} Question</h5>
                    <div class="flex gap-1 items-center">
                        <button class="rounded-lg border border-slate-200 bg-white px-2 py-1 text-[10px] font-bold text-slate-500 hover:bg-slate-50 hover:text-slate-800 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 btn-copy-variant" title="Copy Variant" data-question="${encodedQ}">Copy</button>
                        <button class="rounded-lg border border-slate-200 bg-white p-1 text-slate-400 hover:bg-slate-50 hover:text-blue-500 dark:border-slate-800 dark:bg-slate-900 dark:hover:bg-slate-850" title="Open In Studio" onclick="sendVariantToStudio(${vIdx})"><span class="material-symbols-outlined text-[15px]">open_in_new</span></button>
                        <button class="rounded-lg border border-slate-200 bg-white p-1 text-slate-400 hover:bg-slate-50 hover:text-rose-500 dark:border-slate-800 dark:bg-slate-900 dark:hover:bg-slate-850" title="Delete Variant" onclick="deleteVariant(${vIdx})"><span class="material-symbols-outlined text-[15px]">delete</span></button>
                    </div>
                </div>
                <p class="text-[13px] font-semibold text-slate-800 dark:text-slate-200 mb-4 whitespace-pre-line break-words">${v.question}</p>
                
                <div class="mt-3 rounded-lg bg-blue-50/20 p-3 dark:bg-blue-950/10 border border-blue-100/30 dark:border-blue-900/10">
                    <div class="mb-1 flex items-center gap-1.5 text-[10px] font-bold text-blue-500 uppercase tracking-widest">
                        <span class="material-symbols-outlined text-[14px]">info</span> AI Explanation
                    </div>
                    <p class="text-xs leading-relaxed text-slate-650 dark:text-slate-300 whitespace-pre-line break-words">${v.explanation || ''}</p>
                </div>
            `;
            container.appendChild(card);
        });
        
        document.querySelectorAll('.btn-copy-variant').forEach(btn => {
            btn.addEventListener('click', (e) => {
                copyText(e.currentTarget.getAttribute('data-question'));
            });
        });
        
        if (window.lucide) window.lucide.createIcons();
    }

    window.deleteVariant = function(vIdx) {
        if (currentDrawerIndex > -1) {
            const variants = globalBatchResults[currentDrawerIndex].variants || [];
            variants.splice(vIdx, 1);
            globalBatchResults[currentDrawerIndex].variants = variants;
            renderDrawerVariants(variants);
        }
    }

    window.sendVariantToStudio = function(vIdx) {
        if (currentDrawerIndex === -1) return;
        const r = globalBatchResults[currentDrawerIndex];
        const v = r.variants[vIdx];
        
        closeDrawer();
        switchTab('view-manual');
        
        document.getElementById('manualQuestion').value = v.question.replace(/\s+/g, ' ').trim();
        
        const resQuestion = document.getElementById('resQuestion');
        if (resQuestion) resQuestion.textContent = v.question.replace(/\s+/g, ' ').trim();
        
        const resBloom = document.getElementById('resBloom');
        if (resBloom) {
            resBloom.textContent = v.predicted_bloom;
            resBloom.className = 'px-2.5 py-0.5 rounded-full text-xs font-semibold border ' + getBloomBadgeClass(v.predicted_bloom);
        }
        
        const resDiff = document.getElementById('resDiff');
        if (resDiff) {
            resDiff.textContent = displayDifficulty(v.predicted_difficulty);
            resDiff.className = 'px-2.5 py-0.5 rounded-full text-xs font-semibold border ' + getDifficultyBadgeClass(v.predicted_difficulty);
        }
        
        const resConfText = document.getElementById('resConfText');
        if (resConfText) resConfText.textContent = v.confidence + '%';
        
        const resConfBar = document.getElementById('resConfBar');
        if (resConfBar) {
            resConfBar.style.width = v.confidence + '%';
            resConfBar.className = 'h-full rounded-full transition-all duration-500';
            if (v.confidence >= 90) resConfBar.classList.add('bg-emerald-500');
            else if (v.confidence >= 70) resConfBar.classList.add('bg-amber-500');
            else resConfBar.classList.add('bg-rose-500');
        }
        
        const resExplanation = document.getElementById('resExplanation');
        if (resExplanation) resExplanation.textContent = v.explanation || '';

        updateTransformationControls(v.predicted_difficulty);
        
        const singleResultSection = document.getElementById('singleResultSection');
        if (singleResultSection) singleResultSection.classList.remove('hidden');
        
        const genControlsWrapper = document.getElementById('generationControlsWrapper');
        if (genControlsWrapper) genControlsWrapper.classList.remove('hidden');
        
        const stackedContainer = document.getElementById('stackedAlternativesContainer');
        if (stackedContainer) stackedContainer.innerHTML = '';
        
        const emptyMsg = document.getElementById('emptyVariantsMsg');
        if(emptyMsg) emptyMsg.classList.remove('hidden');
        
        const wrapper = document.getElementById('stackedVariantsWrapper');
        if(wrapper) wrapper.classList.add('hidden');
    }

    // Generate Variant within Drawer
    document.querySelectorAll('.btn-generate-variant').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            if (currentDrawerIndex === -1) return;
            const targetDifficulty = e.currentTarget.dataset.target;
            const originalQuestion = globalBatchResults[currentDrawerIndex].question;
            
            const originalHtml = e.currentTarget.innerHTML;
            e.currentTarget.innerHTML = '<span class="spinner-border spinner-border-sm w-3 h-3 border-2"></span>';
            e.currentTarget.disabled = true;

            try {
                const response = await fetch('/rephrase', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: originalQuestion, target_difficulty: targetDifficulty })
                });
                const data = await response.json();
                
                if (response.ok && data.variants && data.variants.length > 0) {
                    if (!globalBatchResults[currentDrawerIndex].variants) globalBatchResults[currentDrawerIndex].variants = [];
                    // Add newly generated variants
                    data.variants.forEach(newVar => {
                        newVar.target_difficulty = targetDifficulty;
                        globalBatchResults[currentDrawerIndex].variants.push(newVar);
                    });
                    renderDrawerVariants(globalBatchResults[currentDrawerIndex].variants);
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (err) {
                console.error(err);
                alert("Error generating variant.");
            } finally {
                e.currentTarget.innerHTML = originalHtml;
                e.currentTarget.disabled = false;
                if (window.lucide) window.lucide.createIcons();
            }
        });
    });

    // Reclassify
    if(document.getElementById('btnDrawerReclassify')) {
        document.getElementById('btnDrawerReclassify').addEventListener('click', async (e) => {
            if (currentDrawerIndex === -1) return;
            const r = globalBatchResults[currentDrawerIndex];
            
            const originalHtml = e.currentTarget.innerHTML;
            e.currentTarget.innerHTML = '<span class="spinner-border spinner-border-sm w-3 h-3 border-2"></span>';
            e.currentTarget.disabled = true;

            try {
                const response = await fetch('/classify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: r.question })
                });
                const data = await response.json();
                
                if (response.ok) {
                    // Save previous
                    r.previous_classification = {
                        bloom_level: r.bloom_level,
                        difficulty: r.difficulty,
                        confidence: r.confidence
                    };
                    
                    // Update current
                    r.bloom_level = data.bloom_level;
                    r.difficulty = data.difficulty;
                    r.confidence = data.confidence;
                    r.explanation = data.explanation;
                    
                    // Trigger table update and drawer re-render
                    updateTableFilters();
                    openDrawer(currentDrawerIndex);
                    showToast("Reclassification completed");
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (err) {
                console.error(err);
                alert("Error reclassifying.");
            } finally {
                e.currentTarget.innerHTML = originalHtml;
                e.currentTarget.disabled = false;
                if (window.lucide) window.lucide.createIcons();
            }
        });
    }

    // Copy / Toast
    window.copyText = function(text) {
        navigator.clipboard.writeText(text);
        showToast("Copied to clipboard");
    }

    window.showToast = function(message) {
        const container = document.getElementById('toastContainer');
        if (!container) return;
        const toast = document.createElement('div');
        toast.className = 'flex items-center gap-2 rounded-lg bg-slate-800 px-4 py-2.5 text-sm font-medium text-white shadow-lg animate-fade-in-up mb-2 transition-all duration-300';
        toast.innerHTML = `<i data-lucide="check-circle" class="h-4 w-4 text-emerald-400"></i> ${message}`;
        container.appendChild(toast);
        if (window.lucide) window.lucide.createIcons();
        
        setTimeout(() => {
            toast.classList.add('opacity-0');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    if(document.getElementById('btnDrawerCopy')) {
        document.getElementById('btnDrawerCopy').addEventListener('click', () => {
            if (currentDrawerIndex === -1) return;
            const r = globalBatchResults[currentDrawerIndex];
            const details = `ID: ${r.id}\nQuestion: ${r.question}\nBloom: ${r.bloom_level}\nDifficulty: ${displayDifficulty(r.difficulty)}\nConfidence: ${r.confidence}%\nExplanation: ${r.explanation}`;
            copyText(details);
        });
    }

    // Analytics Deep Link
    if(document.getElementById('btnDrawerAnalytics')) {
        document.getElementById('btnDrawerAnalytics').addEventListener('click', () => {
            if (currentDrawerIndex === -1) return;
            const r = globalBatchResults[currentDrawerIndex];
            
            closeDrawer();
            switchTab('view-batch'); // Analytics are embedded within batch view
            
            // Populate Contextual Card
            const alID = document.getElementById('alID');
            if (alID) alID.textContent = r.id;
            
            const alQuestion = document.getElementById('alQuestion');
            if (alQuestion) alQuestion.textContent = r.question;
            
            const alStatus = document.getElementById('alStatus');
            if (alStatus) alStatus.textContent = r.status || 'Verified';
            
            const alBloom = document.getElementById('alBloom');
            if (alBloom) alBloom.textContent = r.bloom_level;
            
            const alDiff = document.getElementById('alDiff');
            if (alDiff) alDiff.textContent = displayDifficulty(r.difficulty);
            
            const alConf = document.getElementById('alConf');
            if (alConf) alConf.textContent = r.confidence + '%';
            
            const alVarCount = document.getElementById('alVarCount');
            if (alVarCount) alVarCount.textContent = (r.variants && r.variants.length) || 0;
            
            const card = document.getElementById('analyticsDeepLinkCard');
            if (card) {
                card.classList.remove('hidden');
                card.classList.add('animate-fade-in-up');
            }
        });
    }

    if(document.getElementById('btnClearAnalyticsFilter')) {
        document.getElementById('btnClearAnalyticsFilter').addEventListener('click', () => {
            document.getElementById('analyticsDeepLinkCard').classList.add('hidden');
        });
    }

    // Studio Deep Link (Enhanced Phase 11)
    window.sendToStudioFromTable = function(index) {
        if (index >= 0 && index < globalBatchResults.length) {
            currentDrawerIndex = index; // set so btnDrawerStudio can use it
            document.getElementById('btnDrawerStudio').click();
        }
    }

    if(document.getElementById('btnDrawerStudio')) {
        document.getElementById('btnDrawerStudio').addEventListener('click', () => {
            if (currentDrawerIndex === -1) return;
            const r = globalBatchResults[currentDrawerIndex];
            
            closeDrawer();
            switchTab('view-manual');
            
            document.getElementById('manualQuestion').value = r.question.replace(/\s+/g, ' ').trim();
            
            // Simulate classification result
            document.getElementById('resQuestion').textContent = r.question.replace(/\s+/g, ' ').trim();
            
            const resBloom = document.getElementById('resBloom');
            if (resBloom) {
                resBloom.textContent = r.bloom_level;
                resBloom.className = 'px-2.5 py-0.5 rounded-full text-xs font-semibold border ' + getBloomBadgeClass(r.bloom_level);
            }
            
            const resDiff = document.getElementById('resDiff');
            if (resDiff) {
                resDiff.textContent = displayDifficulty(r.difficulty);
                resDiff.className = 'px-2.5 py-0.5 rounded-full text-xs font-semibold border ' + getDifficultyBadgeClass(r.difficulty);
            }
            
            document.getElementById('resConfText').textContent = r.confidence + '%';
            document.getElementById('resConfBar').style.width = r.confidence + '%';
            document.getElementById('resExplanation').innerHTML = r.explanation;
            
            const bar = document.getElementById('resConfBar');
            bar.className = 'h-full rounded-full transition-all duration-500';
            if (r.confidence >= 90) bar.classList.add('bg-emerald-500');
            else if (r.confidence >= 70) bar.classList.add('bg-amber-500');
            else bar.classList.add('bg-rose-500');

            updateTransformationControls(r.difficulty);

            document.getElementById('singleResultSection').classList.remove('hidden');
            if (document.getElementById('generationControlsWrapper')) document.getElementById('generationControlsWrapper').classList.remove('hidden');
            
            // Restore Variants in Studio
            const stackedContainer = document.getElementById('stackedAlternativesContainer');
            if (stackedContainer) stackedContainer.innerHTML = '';
            const emptyMsg = document.getElementById('emptyVariantsMsg');
            const wrapper = document.getElementById('stackedVariantsWrapper');
            
            if (r.variants && r.variants.length > 0) {
                if(emptyMsg) emptyMsg.classList.add('hidden');
                if(wrapper) wrapper.classList.remove('hidden');
                
                // Construct fake data object to reuse appendStackedAlternative (which expects data.variants = [...])
                r.variants.forEach(v => {
                    const fakeData = { variants: [v] };
                    appendStackedAlternative(fakeData, v.predicted_difficulty || 'Medium');
                });
            } else {
                if(emptyMsg) emptyMsg.classList.remove('hidden');
                if(wrapper) wrapper.classList.add('hidden');
            }
        });
    }

    // Export Logic
    function downloadData(data, filename, type) {
        const blob = new Blob([data], { type: type });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function getSelectedOrAll(selectedOnly) {
        if (!selectedOnly) return globalBatchResults;
        const checked = document.querySelectorAll('.row-checkbox:checked');
        const ids = Array.from(checked).map(cb => parseInt(cb.value));
        return globalBatchResults.filter(r => ids.includes(r.id));
    }

    function exportToCSV(results) {
        if (results.length === 0) return;
        const headers = ["ID", "Question", "Bloom Level", "Difficulty", "Confidence", "Status", "Tags", "Notes"];
        const rows = results.map(r => {
            return [
                r.id,
                `"${r.question.replace(/"/g, '""')}"`,
                r.bloom_level,
                r.difficulty,
                r.confidence,
                r.status || 'Verified',
                `"${(r.tags || []).join(', ')}"`,
                `"${(r.notes || '').replace(/"/g, '""')}"`
            ].join(',');
        });
        const csv = headers.join(',') + '\n' + rows.join('\n');
        downloadData(csv, `bloomai_export_${Date.now()}.csv`, 'text/csv');
    }

    function exportToJSON(results) {
        if (results.length === 0) return;
        const json = JSON.stringify(results, null, 2);
        downloadData(json, `bloomai_export_${Date.now()}.json`, 'application/json');
    }

    if(document.getElementById('btnExportSelected')) {
        document.getElementById('btnExportSelected').addEventListener('click', () => {
            const results = getSelectedOrAll(true);
            if (results.length === 0) {
                alert("No rows selected.");
                return;
            }
            exportToCSV(results); // default to CSV for selected
            showToast("Exported Selected as CSV");
        });
    }

    if(document.getElementById('btnExportAllCSV')) {
        document.getElementById('btnExportAllCSV').addEventListener('click', () => {
            exportToCSV(globalBatchResults);
            showToast("Exported All as CSV");
        });
    }

    if(document.getElementById('btnExportAllJSON')) {
        document.getElementById('btnExportAllJSON').addEventListener('click', () => {
            exportToJSON(globalBatchResults);
            showToast("Exported All as JSON");
        });
    }
    
    if(document.getElementById('btnDrawerExport')) {
        document.getElementById('btnDrawerExport').addEventListener('click', () => {
            if (currentDrawerIndex === -1) return;
            const r = globalBatchResults[currentDrawerIndex];
            exportToJSON([r]);
            showToast("Exported Question Report");
        });
    }

    function updateCarouselBounds() {
        const displayList = currentFilteredResults.length > 0 ? currentFilteredResults : globalBatchResults;
        if (displayList.length === 0) return;
        if (currentFilteredIndex >= displayList.length) {
            currentFilteredIndex = displayList.length - 1;
        }
        if (currentFilteredIndex < 0) currentFilteredIndex = 0;
        // Also update global carouselIndex for consistency
        carouselIndex = globalBatchResults.findIndex(gr => gr.id === displayList[currentFilteredIndex]?.id);
        if (carouselIndex < 0) carouselIndex = 0;
        updateCarouselUI();
    }

    function updateCarouselUI() {
        // Use the filtered list when available, fall back to global
        const displayList = currentFilteredResults.length > 0 ? currentFilteredResults : globalBatchResults;
        if (displayList.length === 0) return;
        
        // clamp index
        if (currentFilteredIndex >= displayList.length) currentFilteredIndex = displayList.length - 1;
        if (currentFilteredIndex < 0) currentFilteredIndex = 0;

        const r = displayList[currentFilteredIndex];
        // Keep carouselIndex (global) in sync so openDrawer works correctly
        carouselIndex = globalBatchResults.findIndex(gr => gr.id === r.id);

        document.getElementById('carouselCounter').textContent = `${currentFilteredIndex + 1} / ${displayList.length}`;
        document.getElementById('carouselQuestion').textContent = r.question;
        document.getElementById('carouselBloom').textContent = r.bloom_level;
        document.getElementById('carouselDiff').textContent = displayDifficulty(r.difficulty);
        document.getElementById('carouselConf').textContent = r.confidence + '%';
        document.getElementById('carouselExp').innerHTML = r.explanation;
        
        document.getElementById('btnPrevQuestion').disabled = (currentFilteredIndex === 0);
        document.getElementById('btnNextQuestion').disabled = (currentFilteredIndex === displayList.length - 1);
    }

    if(document.getElementById('btnPrevQuestion')) {
        document.getElementById('btnPrevQuestion').addEventListener('click', () => {
            const displayList = currentFilteredResults.length > 0 ? currentFilteredResults : globalBatchResults;
            if (currentFilteredIndex > 0) {
                currentFilteredIndex--;
                updateCarouselUI();
            }
        });
        document.getElementById('btnNextQuestion').addEventListener('click', () => {
            const displayList = currentFilteredResults.length > 0 ? currentFilteredResults : globalBatchResults;
            if (currentFilteredIndex < displayList.length - 1) {
                currentFilteredIndex++;
                updateCarouselUI();
            }
        });
    }

    // --- Charts ---
    let dChart;
    
    function renderCharts(results) {
        if(results.length === 0) return;
        
        const bloomCounts = { Remember:0, Understand:0, Apply:0, Analyze:0, Evaluate:0, Create:0 };
        let easy=0, mod=0, diff=0;
        let highConf=0, medConf=0, lowConf=0;
        let totalConf = 0;
        let maxConf = -1;
        let minConf = 101;

        results.forEach(r => {
            bloomCounts[r.bloom_level] = (bloomCounts[r.bloom_level] || 0) + 1;
            
            if (r.difficulty === 'Easy') easy++;
            else if (r.difficulty === 'Medium' || r.difficulty === 'Moderate') mod++;
            else if (r.difficulty === 'Hard' || r.difficulty === 'Difficult') diff++;

            let confVal = parseFloat(r.confidence);
            if (confVal >= 90) highConf++;
            else if (confVal >= 70) medConf++;
            else lowConf++;

            totalConf += confVal;
            if (confVal > maxConf) maxConf = confVal;
            if (confVal < minConf) minConf = confVal;
        });

        let mostCommon = '-';
        let mostCommonPct = '0%';
        let maxCount = 0;
        for (const [bloom, count] of Object.entries(bloomCounts)) {
            if (count > maxCount) {
                maxCount = count;
                mostCommon = bloom;
            }
        }
        if (results.length > 0) {
            mostCommonPct = ((maxCount / results.length) * 100).toFixed(1) + '%';
        }
        
        const mcbLabel = document.getElementById('mostCommonBloomLabel');
        const mcbPct = document.getElementById('mostCommonBloomPct');
        if (mcbLabel) mcbLabel.textContent = mostCommon;
        if (mcbPct) mcbPct.textContent = mostCommonPct;

        const avgLabel = document.getElementById('avgConfLabel');
        const maxLabel = document.getElementById('maxConfLabel');
        const minLabel = document.getElementById('minConfLabel');
        if (avgLabel) avgLabel.textContent = (totalConf / results.length).toFixed(1) + '%';
        if (maxLabel) maxLabel.textContent = maxConf.toFixed(1) + '%';
        if (minLabel) minLabel.textContent = minConf === 101 ? '-' : minConf.toFixed(1) + '%';

        const canvasDashBloom = document.getElementById('dashBloomChart');
        const canvasDiff = document.getElementById('diffChart');
        const canvasConf = document.getElementById('confChart');

        const ctxDashBloom = canvasDashBloom ? canvasDashBloom.getContext('2d') : null;
        const ctxDiff = canvasDiff ? canvasDiff.getContext('2d') : null;
        const ctxConf = canvasConf ? canvasConf.getContext('2d') : null;

        if (ctxDashBloom && dashBChart) {
            dashBChart.destroy();
            dashBChart = null;
        }
        if (ctxDiff && dChart) {
            dChart.destroy();
            dChart = null;
        }
        if (ctxConf && cChart) {
            cChart.destroy();
            cChart = null;
        }

        // Helper to query design system tokens dynamically
        const getStyleVal = (varName) => getComputedStyle(document.documentElement).getPropertyValue(varName).trim();
        const textColor = getStyleVal('--analytics-chart-legend') || '#666';
        const barColor = getStyleVal('--analytics-chart-bar') || '#1E88E5';
        const gridColor = getStyleVal('--analytics-chart-grid') || 'rgba(0,0,0,0.1)';

        const pieColors = [
            getStyleVal('--analytics-chart-pie-easy') || '#28a745',
            getStyleVal('--analytics-chart-pie-medium') || '#ffc107',
            getStyleVal('--analytics-chart-pie-hard') || '#dc3545'
        ];

        const donutColors = [
            getStyleVal('--analytics-chart-donut-high') || '#1E88E5',
            getStyleVal('--analytics-chart-donut-medium') || '#17a2b8',
            getStyleVal('--analytics-chart-donut-low') || '#6c757d'
        ];

        // Dashboard Bloom Chart
        if (ctxDashBloom) {
            dashBChart = new Chart(ctxDashBloom, {
                type: 'bar',
                data: {
                    labels: Object.keys(bloomCounts),
                    datasets: [{
                        label: 'Count',
                        data: Object.values(bloomCounts),
                        backgroundColor: barColor,
                        borderRadius: 4
                    }]
                },
                options: {
                    animation: false,
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { 
                        legend: { display: false },
                        tooltip: { enabled: true, mode: 'index', intersect: false }
                    },
                    scales: { 
                        y: { 
                            beginAtZero: true, 
                            title: { display: true, text: 'Question Count', color: textColor },
                            ticks: { color: textColor, precision: 0 },
                            grid: { color: gridColor }
                        },
                        x: { 
                            ticks: { color: textColor },
                            grid: { color: gridColor }
                        }
                    }
                }
            });
        }

        // Analytics Diff Chart
        if (ctxDiff) {
            dChart = new Chart(ctxDiff, {
                type: 'pie',
                data: {
                    labels: ['Easy', displayDifficulty('Medium'), displayDifficulty('Hard')],
                    datasets: [{
                        data: [easy, mod, diff],
                        backgroundColor: pieColors
                    }]
                },
                options: {
                    animation: false,
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { 
                        legend: { position: 'bottom', labels: { color: textColor } },
                        tooltip: { enabled: true, callbacks: { label: function(context) { return ' ' + context.label + ': ' + context.raw + ' Questions'; } } }
                    }
                }
            });
        }

        // Analytics Conf Chart
        if (ctxConf) {
            cChart = new Chart(ctxConf, {
                type: 'doughnut',
                data: {
                    labels: ['High (>90%)', 'Medium (70-90%)', 'Low (<70%)'],
                    datasets: [{
                        data: [highConf, medConf, lowConf],
                        backgroundColor: donutColors
                    }]
                },
                options: {
                    animation: false,
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '70%',
                    plugins: { 
                        legend: { position: 'bottom', labels: { color: textColor } },
                        tooltip: { enabled: true, callbacks: { label: function(context) { return ' ' + context.label + ': ' + context.raw + ' Questions'; } } }
                    }
                }
            });
        }
    }

    function updateChartColors() {
        const getStyleVal = (varName) => getComputedStyle(document.documentElement).getPropertyValue(varName).trim();
        const textColor = getStyleVal('--analytics-chart-legend') || '#666';
        const barColor = getStyleVal('--analytics-chart-bar') || '#1E88E5';
        const gridColor = getStyleVal('--analytics-chart-grid') || 'rgba(0,0,0,0.1)';

        const pieColors = [
            getStyleVal('--analytics-chart-pie-easy') || '#28a745',
            getStyleVal('--analytics-chart-pie-medium') || '#ffc107',
            getStyleVal('--analytics-chart-pie-hard') || '#dc3545'
        ];

        const donutColors = [
            getStyleVal('--analytics-chart-donut-high') || '#1E88E5',
            getStyleVal('--analytics-chart-donut-medium') || '#17a2b8',
            getStyleVal('--analytics-chart-donut-low') || '#6c757d'
        ];
        
        if(dashBChart) {
            dashBChart.options.scales.x.ticks.color = textColor;
            dashBChart.options.scales.y.ticks.color = textColor;
            if(dashBChart.options.scales.y.title) {
                dashBChart.options.scales.y.title.color = textColor;
            }
            if(dashBChart.options.scales.y.grid) {
                dashBChart.options.scales.y.grid.color = gridColor;
            }
            if(dashBChart.options.scales.x.grid) {
                dashBChart.options.scales.x.grid.color = gridColor;
            }
            
            const isBloom = currentDashboardChartType === 'bloom';
            dashBChart.data.datasets[0].backgroundColor = isBloom ? barColor : pieColors;
            dashBChart.update();
        }

        if(dChart) {
            dChart.options.plugins.legend.labels.color = textColor;
            dChart.data.datasets[0].backgroundColor = pieColors;
            dChart.update();
        }

        if(cChart) {
            if (cChart.options.plugins.legend && cChart.options.plugins.legend.labels) {
                cChart.options.plugins.legend.labels.color = textColor;
            }
            cChart.data.datasets[0].backgroundColor = donutColors;
            if (cChart.data.datasets[0].borderColor) {
                cChart.data.datasets[0].borderColor = getComputedStyle(document.documentElement).getPropertyValue('--color-bg-card') || '#fff';
            }
            cChart.update();
        }

        if(dashDistChart) {
            const isDiff = dashDistType === 'difficulty';
            const bloomColors = ['#6366f1','#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6'];
            const diffColors = ['#22c55e','#f59e0b','#ef4444'];
            dashDistChart.data.datasets[0].backgroundColor = isDiff ? diffColors : bloomColors;
            if (dashDistChart.data.datasets[0].borderColor) {
                dashDistChart.data.datasets[0].borderColor = getComputedStyle(document.documentElement).getPropertyValue('--color-bg-card') || '#fff';
            }
            dashDistChart.update();
        }
    }

    // --- Manual Rephrase Stacked Logic ---
    const stackedContainer = document.getElementById('stackedAlternativesContainer');
    const btnGenerateAlts = document.querySelectorAll('.btn-generate-alt');

    btnGenerateAlts.forEach(btn => {
        btn.addEventListener('click', async () => {
            const originalQuestion = document.getElementById('resQuestion').textContent;
            const targetDifficulty = btn.dataset.target;

            // Optional: prevent double clicks or show a small spinner inside the button
            const originalHTML = btn.innerHTML;
            btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>Generating...`;
            btn.disabled = true;

            try {
                const response = await fetch('/rephrase', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: originalQuestion, target_difficulty: targetDifficulty })
                });
                const data = await response.json();

                if (response.ok) {
                    appendStackedAlternative(data, targetDifficulty);
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred during generation.');
            } finally {
                btn.innerHTML = originalHTML;
                btn.disabled = false;
            }
        });
    });

    function appendStackedAlternative(data, targetDifficulty, latency = 'N/A') {
        if (!stackedContainer) return;

        // Hide empty message and show wrapper
        const emptyMsg = document.getElementById('emptyVariantsMsg');
        if (emptyMsg) emptyMsg.classList.add('hidden');
        const wrapper = document.getElementById('stackedVariantsWrapper');
        if (wrapper) wrapper.classList.remove('hidden');

        data.variants.forEach(variant => {
            const card = document.createElement('div');
            // Border colors matching target difficulty
            let borderClass = 'border-slate-200 dark:border-slate-800';
            if (targetDifficulty === 'Easy') borderClass = 'border-emerald-500/30';
            else if (targetDifficulty === 'Medium' || targetDifficulty === 'Moderate') borderClass = 'border-amber-500/30';
            else if (targetDifficulty === 'Hard' || targetDifficulty === 'Difficult') borderClass = 'border-rose-500/30';

            card.className = `arena-card rounded-2xl border bg-white p-6 shadow-sm dark:bg-slate-900 w-full animate-fade-in-up transition-all duration-300 ring-0 ring-blue-500/0 flex flex-col gap-4 ${borderClass}`;
            
            const bloomBadgeClass = getBloomBadgeClass(variant.target_bloom || variant.predicted_bloom);
            const diffBadgeClass = getDifficultyBadgeClass(variant.target_difficulty || targetDifficulty);
            
            const attempts = variant.attempts || (variant.attempts_list ? variant.attempts_list.length : 1);

            let statusLabel = '✓ Generated Successfully';
            let statusColorClass = 'text-emerald-600 dark:text-emerald-400';
            if (variant.validation_status === 'Best Candidate') {
                statusLabel = '⚠ Best Available Candidate';
                statusColorClass = 'text-amber-600 dark:text-amber-400';
            } else if (variant.validation_status === 'Fail' || variant.validation_status === 'Rejected') {
                statusLabel = '✗ Generation Failed';
                statusColorClass = 'text-rose-600 dark:text-rose-400';
            } else if (variant.validation_status === 'Pass' && attempts > 1) {
                statusLabel = '✓ Passed after Retry';
                statusColorClass = 'text-emerald-600 dark:text-emerald-400';
            }

            const targetBloomLevel = variant.target_bloom || variant.predicted_bloom || 'Understand';
            const targetDiffLevel = displayDifficulty(variant.target_difficulty || targetDifficulty || 'Medium');

            let explanationText = variant.explanation || variant.reasoning || variant.rationale || variant.ai_explanation;

            if (!explanationText && variant.question) {
                explanationText = `This question is transformed to the ${targetBloomLevel} level because it asks the learner to address ${variant.question.replace(/\.$/, '')}. The difficulty is ${targetDiffLevel} to match the depth of reasoning expected in the solution.`;
            }

            if (!explanationText) {
                explanationText = 'Explanation is not available for this generated variant.';
            }

            card.innerHTML = `
                <!-- Top Row: Bloom Badge & Difficulty Badge -->
                <div class="flex items-center gap-2">
                    <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold border ${bloomBadgeClass}">
                        ${variant.target_bloom || variant.predicted_bloom}
                    </span>
                    <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold border ${diffBadgeClass}">
                        ${displayDifficulty(variant.target_difficulty || targetDifficulty)}
                    </span>
                </div>

                <!-- Question -->
                <div class="flex-1">
                    <p class="text-[15px] font-medium leading-relaxed text-slate-850 dark:text-slate-200 select-all">
                        ${variant.question}
                    </p>
                </div>

                <!-- Explanation Block (styled like Classification Result explanation card) -->
                <div class="bg-purple-50/60 p-4 dark:bg-purple-950/40 rounded-xl border border-purple-100 dark:border-purple-900/40 flex flex-col gap-2">
                    <div class="flex items-center gap-2 text-xs font-bold text-[#6D4AFF]">
                        <span class="material-symbols-outlined text-[18px]">info</span> Explanation
                    </div>
                    <p class="text-xs sm:text-sm leading-relaxed text-slate-700 dark:text-slate-300">
                        ${explanationText}
                    </p>
                </div>

                <!-- Action Row -->
                <div class="border-t border-gray-100 dark:border-slate-800/60 pt-3.5">
                    <div class="flex flex-col sm:flex-row gap-2.5 items-start sm:items-center justify-start">
                        <button class="btn-copy-variant inline-flex h-9 items-center justify-center gap-1.5 rounded-lg border border-gray-200 bg-white px-3.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 active:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800 transition" title="Copy question">
                            <span>Copy Question</span>
                        </button>
                        <button class="btn-generate-again inline-flex h-9 items-center justify-center gap-1.5 rounded-lg bg-blue-500 px-3.5 text-xs font-semibold text-white hover:bg-blue-600 active:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-550 transition" title="Generate again">
                            <span>Generate Again</span>
                        </button>
                    </div>
                </div>

                <!-- Bottom Row -->
                <div class="flex items-center justify-between text-xs text-slate-500 border-t border-gray-50 dark:border-slate-800/40 pt-2.5">
                    <div class="flex items-center gap-4">
                        <span><strong>Attempts:</strong> <span class="font-semibold text-slate-750 dark:text-slate-300">${attempts}</span></span>
                        <span><strong>Latency:</strong> <span class="font-semibold text-slate-750 dark:text-slate-300">${latency}s</span></span>
                    </div>
                    <div class="flex items-center gap-1.5">
                        <span class="${statusColorClass} font-semibold">${statusLabel}</span>
                    </div>
                </div>
            `;

            // Setup actions
            card.querySelector('.btn-copy-variant').addEventListener('click', (e) => {
                navigator.clipboard.writeText(variant.question);
                const btnSpan = e.currentTarget.querySelector('span');
                const origText = btnSpan.textContent;
                btnSpan.textContent = '✓ Copied!';
                setTimeout(() => { btnSpan.textContent = origText; }, 2000);
            });

            card.querySelector('.btn-generate-again').addEventListener('click', () => {
                triggerGeneration(targetDifficulty, null);
            });

            // Prepend new cards to the container
            if (stackedContainer.firstChild) {
                stackedContainer.insertBefore(card, stackedContainer.firstChild);
            } else {
                stackedContainer.appendChild(card);
            }
            
            // Highlight effect
            setTimeout(() => {
                card.classList.add('ring-4', 'ring-blue-500/20');
                setTimeout(() => card.classList.remove('ring-4', 'ring-blue-500/20'), 1500);
            }, 100);

            card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        });
    }

    // --- Dynamic System Models Polling & UI Updater ---
    window.fetchSystemHealth = async function() {
        try {
            const response = await fetch('/health');
            if (!response.ok) {
                throw new Error('Failed to fetch system health');
            }
            const data = await response.json();
            updateSystemModelsUI(data);
        } catch (err) {
            console.error('Error fetching system health:', err);
            const sysStatus = document.getElementById('sys-status');
            if (sysStatus) {
                sysStatus.textContent = 'Error';
                sysStatus.className = 'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-bold bg-rose-105 text-rose-800 dark:bg-rose-900/30 dark:text-rose-450';
            }
        }
    };

    function formatUptime(seconds) {
        if (!seconds || isNaN(seconds)) return '00d 00h 00m 00s';
        const d = Math.floor(seconds / (3600 * 24));
        const h = Math.floor((seconds % (3600 * 24)) / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = Math.floor(seconds % 60);
        
        const pad = (num) => String(num).padStart(2, '0');
        return `${pad(d)}d ${pad(h)}h ${pad(m)}m ${pad(s)}s`;
    }

    function updateSystemModelsUI(data) {
        // Card 1: System Status
        const sysStatus = document.getElementById('sys-status');
        if (sysStatus) {
            const isHealthy = data.status === 'healthy';
            sysStatus.textContent = isHealthy ? 'Healthy' : 'Initializing';
            sysStatus.className = isHealthy 
                ? 'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400'
                : 'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-bold bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400';
        }
        
        const sysUptime = document.getElementById('sys-uptime');
        if (sysUptime) {
            sysUptime.textContent = formatUptime(data.uptime_seconds);
        }
        
        const sysMemory = document.getElementById('sys-memory');
        if (sysMemory) {
            sysMemory.textContent = (data.memory_usage_mb || 0.0).toFixed(1) + ' MB';
        }

        const sysPythonVer = document.getElementById('sys-python-ver');
        if (sysPythonVer) {
            sysPythonVer.textContent = data.python_version || '-';
        }

        // Card 2: DeBERTa
        const debertaInfo = data.models ? data.models.deberta : null;
        if (debertaInfo) {
            const loadedEl = document.getElementById('deberta-loaded');
            if (loadedEl) loadedEl.textContent = debertaInfo.loaded ? 'Yes' : 'No';
            
            const deviceEl = document.getElementById('deberta-device');
            if (deviceEl) deviceEl.textContent = debertaInfo.device || '-';
            
            const warmupEl = document.getElementById('deberta-warmup');
            if (warmupEl) warmupEl.textContent = debertaInfo.warmup ? 'Yes' : 'No';
            
            const statusEl = document.getElementById('deberta-status');
            if (statusEl) {
                statusEl.textContent = debertaInfo.loaded ? 'Online' : 'Offline';
                statusEl.className = debertaInfo.loaded
                    ? 'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400'
                    : 'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-bold bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-350';
            }
        }

        // Card 3: FLAN-T5
        const flanInfo = data.models ? data.models.flan_t5 : null;
        if (flanInfo) {
            const loadedEl = document.getElementById('flan-loaded');
            if (loadedEl) loadedEl.textContent = flanInfo.loaded ? 'Yes' : 'No';
            
            const deviceEl = document.getElementById('flan-device');
            if (deviceEl) deviceEl.textContent = flanInfo.device || '-';
            
            const readyEl = document.getElementById('flan-ready');
            if (readyEl) readyEl.textContent = flanInfo.warmup ? 'Yes' : 'No';
            
            const statusEl = document.getElementById('flan-status');
            if (statusEl) {
                statusEl.textContent = flanInfo.loaded ? 'Online' : 'Offline';
                statusEl.className = flanInfo.loaded
                    ? 'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400'
                    : 'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-bold bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-350';
            }
        }

        // Card 4: Sentence Transformers
        const stInfo = data.models ? data.models.sentence_transformer : null;
        if (stInfo) {
            const loadedEl = document.getElementById('st-loaded');
            if (loadedEl) loadedEl.textContent = stInfo.loaded ? 'Yes' : 'No';
            
            const deviceEl = document.getElementById('st-device');
            if (deviceEl) deviceEl.textContent = stInfo.device || '-';
            
            const cacheEl = document.getElementById('st-cache-status');
            if (cacheEl) cacheEl.textContent = stInfo.loaded ? 'Yes' : 'No';
        }

        // Card 6: Embedding Cache
        const cacheInfo = data.embedding_cache;
        if (cacheInfo) {
            const hitsEl = document.getElementById('cache-hits');
            if (hitsEl) hitsEl.textContent = cacheInfo.hits.toLocaleString();
            
            const missesEl = document.getElementById('cache-misses');
            if (missesEl) missesEl.textContent = cacheInfo.misses.toLocaleString();
            
            const total = cacheInfo.hits + cacheInfo.misses;
            const totalEl = document.getElementById('cache-total-requests');
            if (totalEl) totalEl.textContent = total.toLocaleString();
            
            const hitRateEl = document.getElementById('cache-hit-rate');
            if (hitRateEl) {
                const rate = total > 0 ? (cacheInfo.hits / total * 100).toFixed(1) : '0.0';
                hitRateEl.textContent = rate + '%';
            }
        }
    }
});


// Auto-initialize Lucide icons
if (window.lucide) window.lucide.createIcons();
