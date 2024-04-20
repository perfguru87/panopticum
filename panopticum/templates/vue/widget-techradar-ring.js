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
        Promise.all([this.initQuadrants(), this.initRings()]).then(() => {
            this.initEntries();
        }).catch(err => {
            console.error('Initialization of quadrants or rings failed', err);
        });
    },
    computed: {
    },
    methods: {
        initQuadrants: async function() {
           fetch('/api/techradar_quadrants/').then(function(response) {
             return response.json();
           }).then(function(data) {;
             this.quadrants = data['results'];
           }).catch(function(err) {
             console.log('Error loading techradar quadrants', err);
           });
        },
        initRings: async function() {
           fetch('/api/techradar_rings/').then(function(response) {
             return response.json();
           }).then(function(data) {;
             this.rings = data['results'];
           }).catch(function(err) {
             console.log('Error loading techradar rings', err);
           });
        },
        initEntries() {
           fetch('/api/techradar_entries/').then(function(response) {
             return response.json();
           }).then(function(data) {
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
           }).catch(function(err) {
             console.log('Error loading techradar entries', err);
           });
        }
    },
    template: `
    {% verbatim %}
        <svg id="radar" viewBox="0 0 1250 800" preserveAspectRatio="xMidYMid meet" style="width: 100%; height: auto; left: -20px; position: relative;"></svg>
    {% endverbatim %}
    `
})
