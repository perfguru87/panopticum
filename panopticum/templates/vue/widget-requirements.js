
Vue.component('widget-requirements', {
    props: ['component_version', 'setid'],
    data: function() {
        return {
            requirements: [],
            statuses: [],
            table: [],
            title: "",
            description: "",
            statusDefinitions: []
        }
    },
    computed: {
        apiUrl: function() {
            return `${window.location.origin}/api`
        }
    },
    methods: {
        getRequirementSet: function () {
            return axios.get(`${this.apiUrl}/requirement_set/${this.setid}/`)
                .then(resp => resp.data)
        },
        fetchStatusesDefinition() {
            return axios.get('/api/status/?format=json&allow_for=1&allow_for=2').then(resp => {
                this.statusDefinitions = resp.data.results;
            })
        },
        getIDfromHref(href) {
            const idPattern = new RegExp("^.*/(\\d+)/(?:\\?.+)?$");
            return Number(idPattern.exec(href)[1]);
        },
        getStatuses: function () {
            return axios.get(`${this.apiUrl}/requirement_status/?component_version=${this.component_version.id}&requirement__requrementset_set=${this.setid}`)
                .then(resp => {
                    return resp.data.results.map(status => { 
                        status.status = this.statusDefinitions.find(s=> this.getIDfromHref(status.status) == s.id)
                        return status;
                    })
                })
        },
        getId: function (href) {
            return Number(href.split('/').slice(-2)[0])
        },
        updateRequirements: function() {
            return this.getRequirementSet().then(reqSet => {
                this.title = reqSet.name;
                this.description = reqSet.description;
                this.requirements = reqSet.requirements;
            })
        },
        updateTable: function() {
            this.table = [];
            for (let requirement of this.requirements) {
                let ownerStatus = this.statuses.find(el => requirement.id == this.getId(el.requirement) && el.type == "component owner")
                if (ownerStatus == undefined) {
                    this.table.push({title: requirement.title, status: null, signoffStatus: null, notes: ''})
                } else {
                    let signeeStatus = this.statuses.find(el => requirement.id == this.getId(el.requirement) && el.type == "requirement reviewer");
                    this.table.push({
                        title: requirement.title,
                        status: ownerStatus, 
                        notes: ownerStatus.notes,
                        signoffStatus: signeeStatus,
                        signoffNotes: signeeStatus ? signeeStatus.notes : ""
                    })
                }
            }
        },
        updateStatuses: function() {
            if (!this.component_version.id) return;
            return this.getStatuses().then(statuses => {this.statuses = statuses;}) 
        }
    },
    mounted: function() {
        this.fetchStatusesDefinition();
        this.updateRequirements();
    },
    watch: {
        component_version: function() {
            this.updateStatuses().then(_ => this.updateTable())
        }
    },
    template: `
    {% verbatim %}<el-card>
        <div slot="header" class="clearfix">
                <h2>{{title }}</h2>
                <span class='pa-component-rating' v-if='component_version.op_applicable'>
                        {{ component_version.meta_op_rating }}%
                </span>
                <span class='pa-component-stars' v-if='component_version.op_applicable'>
                        {{ component_version.meta_op_rating }}
                </span>
            </h4>
        </div>

        <table class='status-table' v-bind:class="[ requirements ? '' : 'status-table-na']">
            <thead>
            <tr>
                <th>Requirement</th>
                <th>Status</th>
                <th>Signee</th>
                <th>Notes</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="row of table">
                <td>{{ row.title }}</td>

                <td><widget-signoff v-bind:status="row.status" v-bind:signoff-status="row.signoffStatus"></widget-signoff></td>
                <td><widget-signoff v-bind:status="row.signoffStatus"></widget-signoff></td>
                <td class='pa-replace-urls'><widget-note :short="true">{{ row.notes }}</widget-note></td>
            </tr>
            </tbody>
        </table>
    </el-card>{% endverbatim %}
    `
})
