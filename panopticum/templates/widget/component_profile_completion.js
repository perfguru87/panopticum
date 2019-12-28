function init_profile_gauge() {
    if (typeof(Gauge) === 'undefined') {
        return;
    }

    var chart_gauge_settings = {
        lines: 12,
        angle: 0,
        lineWidth: 0.3,
        pointer: {
            length: 0.75,
            strokeWidth: 0.042,
            color: '#1D212A'
        },
        limitMax: 'false',
        colorStart: '#1ABC9C',
        colorStop: '#1ABC9C',
        strokeColor: '#e0e0e0',
        generateGradient: true
    };

    if ($('#profile-gauge').length) {
        var profile_gauge_elem = document.getElementById('profile-gauge');
        var profile_gauge = new Gauge(profile_gauge_elem).setOptions(chart_gauge_settings);
    }

    if ($('#profile-gauge-text').length) {
        profile_gauge.maxValue = 100;
        profile_gauge.animationSpeed = 10;
        profile_gauge.set(64);
        profile_gauge.setTextField(document.getElementById("profile-gauge-text"));
    }
}
init_profile_gauge();
