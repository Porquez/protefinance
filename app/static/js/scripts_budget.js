// scripts_budget.js
document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('budgetChart').getContext('2d');
    
    const data = {
        labels: {{ data_pairs | map(attribute='0') | list | tojson }},
        datasets: [{
            label: 'Dépenses',
            data: {{ data_pairs | map(attribute='1') | list | tojson }},
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)'
            ],
            borderWidth: 1
        }]
    };

    const budgetChart = new Chart(ctx, {
        type: 'pie', // type de graphique
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false, // Assurez-vous que le graphique ne prend pas toute la place
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Répartition des Dépenses'
                }
            }
        }
    });
});
