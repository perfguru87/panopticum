Vue.component('widget-techradar-ring', {
    props: [
        'attrib',
    ],
    data: function() {
        return {
            quadrants: [],
            rings: [],
        }
    },
    created: async function() {
        try {
            await Promise.all([this.initQuadrants(), this.initRings()]);
            this.initEntries();
        } catch (err) {
            console.error('Initialization of quadrants or rings failed', err);
        }
    },
    computed: {
    },
    methods: {
        initQuadrants: async function() {
            try {
                const response = await fetch('/api/techradar_quadrants/');
                const data = await response.json();
                this.quadrants = data['results'];
            } catch (err) {
                console.log('Error loading techradar quadrants', err);
            }
        },
        initRings: async function() {
            try {
                const response = await fetch('/api/techradar_rings/');
                const data = await response.json();
                this.rings = data['results'];
            } catch (err) {
                console.log('Error loading techradar rings', err);
            }
        },
        initEntries: async function() {
            try {
                const response = await fetch('/api/techradar_entries/');
                const data = await response.json();
                radar_visualization({
                    svg_id: "radar",
                    width: 1250,
                    height: 800,
                    colors: {
                        background: "#fff",
                        grid: '#dddde0',
                        inactive: "#ddd"
                    },
                    quadrants: this.quadrants,
                    rings: this.rings,
                    print_layout: true,
                    links_in_new_tabs: true,
                    // zoomed_quadrant: 0,
                    entries: data.results
                });
            } catch (err) {
                console.log('Error loading techradar entries', err);
            }
        }
    },
    template: `
    {% verbatim %}
        <svg id="radar" viewBox="0 0 1250 800" preserveAspectRatio="xMidYMid meet" style="width: 100%; height: auto; left: -20px; position: relative;"></svg>
    {% endverbatim %}
    `
});
