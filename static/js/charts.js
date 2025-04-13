// This file contains chart-related utility functions
// that can be shared between the main page and parameter detail page

/**
 * Get a color based on the parameter value and its thresholds
 * @param {string} param - The parameter name
 * @param {number} value - The parameter value
 * @returns {string} - HEX or RGBA color string
 */
function getColorForValue(param, value) {
    // Default thresholds if not found from API
    const defaultThresholds = {
        'pm10': { warning: 50, danger: 100 },
        'pm25': { warning: 25, danger: 50 },
        'temperature': { warning: 30, danger: 33 },
        'humidity': { warning: 70, danger: 85 },
        'noise': { warning: 70, danger: 85 },
        'co': { warning: 25, danger: 40 },
        'co2': { warning: 1000, danger: 1500 }
    };

    const thresholds = defaultThresholds[param] || { warning: 50, danger: 75 };
    
    if (value >= thresholds.danger) {
        return '#e74c3c'; // Danger color
    } else if (value >= thresholds.warning) {
        return '#f39c12'; // Warning color
    } else {
        return '#2ecc71'; // Normal color
    }
}

/**
 * Creates a gradient background for chart
 * @param {CanvasRenderingContext2D} ctx - The canvas context
 * @param {string} startColor - Start gradient color
 * @param {string} endColor - End gradient color
 * @returns {CanvasGradient}
 */
function createGradientBackground(ctx, startColor, endColor) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, startColor);
    gradient.addColorStop(1, endColor);
    return gradient;
}

/**
 * Format time for chart display
 * @param {string} timestamp - Timestamp string
 * @returns {string} - Formatted time string
 */
function formatTimeForDisplay(timestamp) {
    return timestamp;
}

/**
 * Generate chart options with standard settings
 * @param {string} title - Chart title
 * @param {boolean} includeTime - Whether to include time in tooltips
 * @returns {object} - Chart.js options object
 */
function getStandardChartOptions(title, includeTime = true) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            title: {
                display: !!title,
                text: title
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += context.parsed.y;
                        }
                        if (includeTime && context.label) {
                            label += ` at ${context.label}`;
                        }
                        return label;
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: false,
                ticks: {
                    callback: function(value) {
                        return value;
                    }
                }
            },
            x: {
                ticks: {
                    maxRotation: 45,
                    minRotation: 45
                }
            }
        }
    };
}
