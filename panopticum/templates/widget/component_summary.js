<script>
function init_activity_chart() {
    if ($('#activity-chart').length) {

        var ctx = document.getElementById("activity-chart");
        var chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"],
                datasets: [{
                    label: 'Bugs in JIRA',
                    backgroundColor: "#26B99A",
                    data: [51, 30, 40, 28, 92, 50, 45]
                }, {
                    label: 'Commits in Git',
                    backgroundColor: "#03586A",
                    data: [41, 56, 25, 48, 72, 34, 12]
                }]
            },

            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                }
            }
        });

    }
}
$(document).ready(function() {
    init_activity_chart();
});
</script>
