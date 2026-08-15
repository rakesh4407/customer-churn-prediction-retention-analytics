/**
 * ChurnGuard — Main JavaScript
 * Handles dashboard charts, mobile navigation, and form interaction.
 */

// ============================================
// Color Palette for Charts
// ============================================
const CHART_COLORS = {
    primary: '#0ea5e9',
    primaryLight: '#7dd3fc',
    danger: '#ef4444',
    dangerLight: '#fca5a5',
    success: '#10b981',
    successLight: '#6ee7b7',
    purple: '#8b5cf6',
    warning: '#f59e0b',
    gray: '#94a3b8',
    teal: '#14b8a6',
};

const CHART_PALETTE = [
    '#0ea5e9', '#8b5cf6', '#ef4444', '#10b981',
    '#f59e0b', '#14b8a6', '#ec4899', '#6366f1',
];

// ============================================
// Chart.js Default Config
// ============================================
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = '#64748b';
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.padding = 16;

// ============================================
// Dashboard Charts
// ============================================
function loadDashboardCharts() {
    loadContractChart();
    loadDistributionChart();
    loadInternetChart();
    loadTenureChart();
}

async function fetchChartData(type) {
    const response = await fetch(`/api/chart-data/${type}`);
    if (!response.ok) throw new Error(`Failed to fetch ${type}`);
    return response.json();
}

function loadContractChart() {
    fetchChartData('churn-by-contract').then(data => {
        const ctx = document.getElementById('chartContract');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Churn Rate (%)',
                    data: data.values,
                    backgroundColor: [CHART_COLORS.danger, CHART_COLORS.warning, CHART_COLORS.success],
                    borderRadius: 6,
                    maxBarThickness: 60,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx => `${ctx.parsed.y}% churn rate`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { callback: v => v + '%' },
                        grid: { color: '#f1f5f9' },
                    },
                    x: {
                        grid: { display: false },
                    }
                }
            }
        });
    });
}

function loadDistributionChart() {
    fetchChartData('churn-distribution').then(data => {
        const ctx = document.getElementById('chartDistribution');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: [CHART_COLORS.success, CHART_COLORS.danger],
                    borderWidth: 0,
                    hoverOffset: 6,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    tooltip: {
                        callbacks: {
                            label: ctx => {
                                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                                const pct = (ctx.parsed / total * 100).toFixed(1);
                                return `${ctx.label}: ${ctx.parsed.toLocaleString()} (${pct}%)`;
                            }
                        }
                    }
                }
            }
        });
    });
}

function loadInternetChart() {
    fetchChartData('churn-by-internet').then(data => {
        const ctx = document.getElementById('chartInternet');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Churn Rate (%)',
                    data: data.values,
                    backgroundColor: [CHART_COLORS.primary, CHART_COLORS.purple, CHART_COLORS.gray],
                    borderRadius: 6,
                    maxBarThickness: 60,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx => `${ctx.parsed.y}% churn rate`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { callback: v => v + '%' },
                        grid: { color: '#f1f5f9' },
                    },
                    x: {
                        grid: { display: false },
                    }
                }
            }
        });
    });
}

function loadTenureChart() {
    fetchChartData('churn-by-tenure').then(data => {
        const ctx = document.getElementById('chartTenure');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Churn Rate (%)',
                    data: data.values,
                    backgroundColor: CHART_COLORS.primary,
                    borderRadius: 6,
                    maxBarThickness: 50,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx => `${ctx.parsed.y}% churn rate`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { callback: v => v + '%' },
                        grid: { color: '#f1f5f9' },
                    },
                    x: {
                        grid: { display: false },
                    }
                }
            }
        });
    });
}

// ============================================
// Mobile Sidebar Toggle
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    if (menuToggle && sidebar && overlay) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            overlay.classList.toggle('active');
        });

        overlay.addEventListener('click', () => {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
        });
    }
});
