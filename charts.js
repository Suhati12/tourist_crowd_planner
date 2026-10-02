/* 
  Chart.js visualizers for Tourist Crowd Level Planner
*/

let hourlyChartInstance = null;
let dailyChartInstance = null;
let monthlyChartInstance = null;
let categoryChartInstance = null;

function renderHourlyChart(hourlyData) {
    const ctx = document.getElementById('hourlyChart');
    if (!ctx) return;

    if (hourlyChartInstance) {
        hourlyChartInstance.destroy();
    }

    const labels = hourlyData.map(item => item.time_label);
    const scores = hourlyData.map(item => item.score);
    
    // Dynamic bar/point colors based on category
    const pointColors = hourlyData.map(item => {
        if (item.score <= 30) return '#10b981';
        if (item.score <= 60) return '#f59e0b';
        if (item.score <= 80) return '#ef4444';
        return '#9333ea';
    });

    const canvasCtx = ctx.getContext('2d');
    const gradient = canvasCtx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(99, 102, 241, 0.4)');
    gradient.addColorStop(1, 'rgba(99, 102, 241, 0.0)');

    hourlyChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Crowd Score (0-100)',
                data: scores,
                borderColor: '#6366f1',
                borderWidth: 3,
                backgroundColor: gradient,
                fill: true,
                tension: 0.35,
                pointBackgroundColor: pointColors,
                pointBorderColor: '#fff',
                pointRadius: 5,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#0f172a',
                    titleColor: '#fff',
                    bodyColor: '#cbd5e1',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            const val = context.parsed.y;
                            let cat = "Low";
                            if (val > 80) cat = "Very High";
                            else if (val > 60) cat = "High";
                            else if (val > 30) cat = "Moderate";
                            return `Crowd Score: ${val}/100 (${cat})`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.06)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.06)' },
                    ticks: { color: '#94a3b8' }
                }
            }
        }
    });
}

function renderDailyChart(dailyData) {
    const ctx = document.getElementById('dailyChart');
    if (!ctx) return;

    if (dailyChartInstance) {
        dailyChartInstance.destroy();
    }

    const barColors = dailyData.scores.map(s => {
        if (s > 70) return '#ef4444';
        if (s > 55) return '#f59e0b';
        return '#10b981';
    });

    dailyChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dailyData.labels,
            datasets: [{
                label: 'Avg Crowd Level',
                data: dailyData.scores,
                backgroundColor: barColors,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { backgroundColor: '#0f172a' }
            },
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.06)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8' }
                }
            }
        }
    });
}

function renderMonthlyChart(monthlyData) {
    const ctx = document.getElementById('monthlyChart');
    if (!ctx) return;

    if (monthlyChartInstance) {
        monthlyChartInstance.destroy();
    }

    monthlyChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: monthlyData.labels,
            datasets: [{
                label: 'Visitor Density Index',
                data: monthlyData.scores,
                borderColor: '#06b6d4',
                borderWidth: 2,
                backgroundColor: 'rgba(6, 182, 212, 0.1)',
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { backgroundColor: '#0f172a' }
            },
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.06)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.06)' },
                    ticks: { color: '#94a3b8' }
                }
            }
        }
    });
}

function renderCategoryChart(categoryCounts) {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;

    if (categoryChartInstance) {
        categoryChartInstance.destroy();
    }

    categoryChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Low (0-30)', 'Moderate (31-60)', 'High (61-80)', 'Very High (81-100)'],
            datasets: [{
                data: [
                    categoryCounts.Low || 25,
                    categoryCounts.Moderate || 40,
                    categoryCounts.High || 25,
                    categoryCounts.VeryHigh || 10
                ],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444', '#9333ea'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#cbd5e1', font: { size: 11 } }
                }
            },
            cutout: '70%'
        }
    });
}
