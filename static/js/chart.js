// chart.js — Dynamic Vote Distribution Chart
document.addEventListener('DOMContentLoaded', () => {
  const chartScript = document.getElementById('chart-data');
  if (!chartScript) return;

  const chartData = JSON.parse(chartScript.textContent);
  const ctx = document.getElementById('voteChart');
  const colors = ['#007bff', '#28a745', '#ffc107', '#17a2b8', '#e83e8c', '#6610f2'];

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: chartData.labels,
      datasets: [{
        data: chartData.votes,
        backgroundColor: colors.slice(0, chartData.labels.length),
        hoverOffset: 8
      }]
    },
    options: {
      plugins: {
        legend: { position: 'bottom' },
        title: {
          display: true,
          text: 'Live Vote Distribution',
          font: { size: 18, weight: 'bold' }
        }
      },
      responsive: true
    }
  });
});
