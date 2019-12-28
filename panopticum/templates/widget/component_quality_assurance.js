function init_qa_radar()
{
    if ($('#qa-radar').length) {

        var options = {
            legend: { display: false },
            scale: {
                ticks: {
                    max: 3,
                    min: 0,
                    stepSize: 1
                }
            }
        }

        var ctx = document.getElementById("qa-radar");
        var data = {
            labels: ["Unit tests", "End-to-end", "Performance", "Long haul", "Security", "API validation", "Anonymisation", "Upgrade"],
            datasets: [
            {
                label: "Tests Scope",
                backgroundColor: "rgba(3, 88, 106, 0.2)",
                borderColor: "rgba(3, 88, 106, 0.80)",
                pointBorderColor: "rgba(3, 88, 106, 0.80)",
                pointBackgroundColor: "rgba(3, 88, 106, 0.80)",
                pointHoverBackgroundColor: "#fff",
                pointHoverBorderColor: "rgba(220,220,220,1)",
                data: [3, 3, 3, 0, 1, 2, 1, 2]
            }]
        };

        var canvasRadar = new Chart(ctx, {
            display: false,
            type: 'radar',
            options: options,
            data: data,
        });
    }
}

init_qa_radar();
