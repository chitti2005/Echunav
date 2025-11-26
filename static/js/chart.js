// static/js/chart.js
document.addEventListener("DOMContentLoaded", () => {
    const chartScript = document.getElementById("chart-data");
    if (!chartScript) return;

    const chartData = JSON.parse(chartScript.textContent);

    const ctx = document.getElementById("voteChart").getContext("2d");

    new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    data: chartData.votes,
                    backgroundColor: [
                        "#007bff", "#28a745", "#ffc107",
                        "#17a2b8", "#e83e8c", "#6610f2", "#fd7e14"
                    ],
                    hoverOffset: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,   // ⛔ Prevents chart from growing infinitely
            animation: false,
            layout: { padding: 10 },
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        font: { size: 13 }
                    }
                },
                title: {
                    display: true,
                    text: "Live Vote Distribution",
                    font: { size: 18, weight: "bold" }
                }
            }
        }
    });
});
