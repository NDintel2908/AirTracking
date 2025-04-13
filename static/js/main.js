document.addEventListener('DOMContentLoaded', function() {
    // Initialize
    updateLastUpdated();
    fetchCurrentData();
    initializeMainChart();

    // Event listeners
    document.getElementById('refresh-btn').addEventListener('click', function() {
        fetchCurrentData();
        updateMainChart(document.getElementById('chart-param').value);
    });

    document.getElementById('chart-param').addEventListener('change', function() {
        updateMainChart(this.value);
    });

    // Auto refresh data every 30 seconds
    setInterval(function() {
        fetchCurrentData();
        updateMainChart(document.getElementById('chart-param').value);
    }, 30000);

    // Functions
    function updateLastUpdated() {
        const now = new Date();
        document.getElementById('last-updated').textContent = `Last updated: ${now.toLocaleTimeString()}`;
    }

    function fetchCurrentData() {
        fetch('/api/current')
            .then(response => response.json())
            .then(data => {
                renderDataCards(data);
                updateLastUpdated();
            })
            .catch(error => {
                console.error('Error fetching data:', error);
                document.getElementById('data-grid').innerHTML = 
                    '<div class="error">Error loading data. Please try again.</div>';
            });
    }

    function renderDataCards(data) {
        const dataGrid = document.getElementById('data-grid');
        dataGrid.innerHTML = '';

        // Parameter to icon mapping
        const paramIcons = {
            'pm10': 'fa-cloud',
            'pm25': 'fa-smog',
            'temperature': 'fa-thermometer-half',
            'humidity': 'fa-water',
            'noise': 'fa-volume-up',
            'co': 'fa-wind',
            'co2': 'fa-leaf'
        };

        // Parameter to display name mapping
        const paramNames = {
            'pm10': 'PM10',
            'pm25': 'PM2.5',
            'temperature': 'Temperature',
            'humidity': 'Humidity',
            'noise': 'Noise',
            'co': 'CO',
            'co2': 'CO2'
        };

        for (const [param, reading] of Object.entries(data)) {
            const card = document.createElement('div');
            card.className = 'data-card';
            card.innerHTML = `
                <div class="card-title">
                    <i class="fas ${paramIcons[param]}"></i> ${paramNames[param]}
                </div>
                <div class="card-value">${reading.value}</div>
                <div class="card-unit">${reading.unit}</div>
                <div class="card-status ${reading.status}">
                    ${reading.status.toUpperCase()}
                </div>
            `;
            
            // Add click event to navigate to detail page
            card.addEventListener('click', () => {
                window.location.href = `/parameter/${param}`;
            });
            
            dataGrid.appendChild(card);
        }
    }

    function initializeMainChart() {
        // Default to PM2.5 when loading the page
        updateMainChart('pm25');
    }

    function updateMainChart(parameter) {
        fetch('/api/historical')
            .then(response => response.json())
            .then(data => {
                const paramData = data[parameter];
                const labels = paramData.map(point => point.timestamp);
                const values = paramData.map(point => point.value);

                // Get the parameter unit from the current data
                return fetch('/api/current')
                    .then(response => response.json())
                    .then(currentData => {
                        const unit = currentData[parameter].unit;
                        const paramName = parameter.toUpperCase();
                        updateChart(labels, values, paramName, unit);
                    });
            })
            .catch(error => {
                console.error('Error updating chart:', error);
            });
    }

    function updateChart(labels, values, paramName, unit) {
        const ctx = document.getElementById('main-chart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (window.mainChart) {
            window.mainChart.destroy();
        }
        
        window.mainChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: `${paramName} (${unit})`,
                    data: values,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false
                    }
                }
            }
        });
    }
});
