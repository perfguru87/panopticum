
Vue.component('widget-requirements', {
    props: ['component_version', 'type'],
    data: function() {
        return {
            apiUrl: '{{API_URL}}',
            requirements: [],
            statuses: [],
            table: []
        }
    },
    methods: {
        getRequirements: function () {
            return axios.get(`${this.apiUrl}/requirement/?type__name=${this.type}`)
                .then(resp => resp.data.results)
        },
        getStatuses: function () {
            return axios.get(`${this.apiUrl}/requirement_status/?component_version=${this.component_version.id}&requirement__type__name=${this.type}`)
                .then(resp => resp.data.results)
        },
        getId: function (href) {
            return Number(href.split('/').slice(-2)[0])
        },
        fetchData: function() {
            if (!this.component_version.id) return;
            let promises = [
                this.getRequirements().then(reqs => this.requirements = reqs),
                this.getStatuses().then(statuses => this.statuses = statuses),
            ]
            Promise.all(promises).then(values => {
                let requirements = values[0];
                let statuses = values[1];
                for (let requirement of requirements) {
                    let ownerStatus = statuses.find(el => requirement.id == this.getId(el.requirement))
                    if (ownerStatus == undefined) {
                        this.table.push({title: requirement.title, status: 'unknown', notes: ''})
                    } else {
                    this.table.push({title: requirement.title, status: ownerStatus.status , notes: ownerStatus.notes})
                    }
                }
            })
        }
    },
    mounted: function() {
        this.fetchData()
    },
    watch: {
        component_version: 'fetchData'
    },
    template: `
    {% verbatim %}<div>
        <h3 v-cloak>Cloud Requirements
            <span class='pa-component-rating' v-cloak v-if='component_version.op_applicable'>
                    {{ component_version.meta_op_rating }}%
            </span>
            <span class='pa-component-stars' v-cloak v-if='component_version.op_applicable'>
                    {{ component_version.meta_op_rating }}
            </span>
        </h3>

        <table class='status-table' v-bind:class="[ component_version.op_applicable ? '' : 'status-table-na']" v-cloak>
            <thead>
            <tr>
                <th>Requirement</th>
                <th>Status</th>
                <th>Notes</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="row of table">
                <td>{{ row.title }}</td>

                <td><widget-signoff v-bind:status="row.status"></widget-signoff></td>
                <td class='pa-replace-urls'>{{ row.notes }}</td>
            </tr>
            </tbody>
        </table>
    </div>{% endverbatim %}
    `
})
