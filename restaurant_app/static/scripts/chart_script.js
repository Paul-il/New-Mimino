var myChart;

window.addEventListener('DOMContentLoaded', initializeChart);

function initializeChart() {
    var ctx = document.getElementById('expenseChart').getContext('2d');
    myChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: [], // Пустой массив, будет заполнен позже
            datasets: [{
                data: [], // Пустой массив, будет заполнен позже
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',    // Красный
                    'rgba(54, 162, 235, 0.2)',   // Синий
                    'rgba(255, 206, 86, 0.2)',   // Желтый
                    'rgba(75, 192, 192, 0.2)',   // Зеленый (циан)
                    'rgba(153, 102, 255, 0.2)',  // Фиолетовый
                    'rgba(255, 159, 64, 0.2)',   // Оранжевый
                    'rgba(205, 92, 92, 0.2)',    // IndianRed
                    'rgba(138, 43, 226, 0.2)',   // BlueViolet
                    'rgba(60, 179, 113, 0.2)',   // MediumSeaGreen
                    'rgba(199, 21, 133, 0.2)',   // MediumVioletRed
                    'rgba(32, 178, 170, 0.2)',   // LightSeaGreen
                    'rgba(100, 149, 237, 0.2)',  // CornflowerBlue
                    'rgba(123, 104, 238, 0.2)',  // MediumSlateBlue
                    'rgba(72, 61, 139, 0.2)',    // DarkSlateBlue
                    'rgba(50, 205, 50, 0.2)'     // LimeGreen
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',
                    'rgba(205, 92, 92, 1)',
                    'rgba(138, 43, 226, 1)',
                    'rgba(60, 179, 113, 1)',
                    'rgba(199, 21, 133, 1)',
                    'rgba(32, 178, 170, 1)',
                    'rgba(100, 149, 237, 1)',
                    'rgba(123, 104, 238, 1)',
                    'rgba(72, 61, 139, 1)',
                    'rgba(50, 205, 50, 1)'
                ],
                borderWidth: 1
                
            }]
        },
        options: {
            responsive: false,
            legend: {
                position: 'bottom',
                labels: {
                    padding: 10  // Это значение задает отступ между легендой и диаграммой.
                }
            }
        }
    });
}

// Функция для заполнения данными
function populateChartData(labels, data) {
    myChart.data.labels = labels;
    myChart.data.datasets[0].data = data;
    myChart.update();
}
