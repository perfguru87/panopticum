
Vue.component('widget-requirements', {
    props: ['requirementsets', 'requirementset__ui_slot', 'component_version'],
    data: function() {
      return {
        requirements: [],
        applicable: true,
        statuses: {},
        table: [],
        title: "",
        na_status: {id: window.REQ_STATUS_NOT_APPLICABLE },
        unknown_status: {id: window.REQ_STATUS_UNKNOWN },
        id: 0,
        doc_link: "",
        description: "",
      }
    },
    computed: {
        apiUrl: function() {
            return `${window.location.origin}/api`
        }
    },
    methods: {
        fetchStatuses: async function () {
            return axios.get(`${this.apiUrl}/requirement_status/?component_version=${this.$props.component_version.id}&requirementset__ui_slot=${this.$props.requirementset__ui_slot}`)
                .then(resp => {
                    for (let i = 0; i < resp.data.results.length; i++) {
                        row = resp.data.results[i];
                        req_id = this.getIDfromHref(row.requirement);
                        if (this.statuses[req_id] == undefined) {
                            this.statuses[req_id] = {
                                ownerStatus: this.unknown_status,
                                ownerNotes: '',
                                signeeStatus: this.unknown_status,
                                signeeNotes: '',
                            };
                        }
                        if (row.type == 'component owner') {
                            this.statuses[req_id].ownerStatus = {id: this.getIDfromHref(row.status) }
                            this.statuses[req_id].ownerNotes = row.notes;
                        }
                        if (row.type == 'requirement reviewer') {
                            this.statuses[req_id].signeeStatus = {id: this.getIDfromHref(row.status) }
                            this.statuses[req_id].signeeNotes = row.notes;
                        }
                    }
                });
        },
        getIDfromHref(href) {
            const idPattern = new RegExp("^.*/(\\d+)/(?:\\?.+)?$");
            return Number(idPattern.exec(href)[1]);
        },
        getId: function (href) {
            return Number(href.split('/').slice(-2)[0])
        },
        updateRequirements: function() {
            for (let i = 0; i < this.$props.requirementsets.length; i++) {
                rs = this.$props.requirementsets[i];
                if (rs.ui_slot == this.$props.requirementset__ui_slot) {
                    this.id = rs.id;
                    this.title = rs.name;
                    this.doc_link = rs.doc_link;
                    this.description = rs.description;
                    this.requirements = rs.requirements;
                    break;
                }
            }
        },
        updateTable: function() {
            this.table = [];
            for (let requirement of this.requirements) {
                if (this.$props.component_version.excluded_requirement_set.includes(this.id)) {
                    this.applicable = false;
                    this.table.push({title: requirement.title, doc_link: requirement.doc_link, ownerStatus: this.na_status, signeeStatus: this.na_status, ownerNotes: "", signeeNotes: ""})
                } else if (this.statuses[requirement.id] == undefined) {
                    this.table.push({title: requirement.title, doc_link: requirement.doc_link, ownerStatus: null, signeeStatus: null, ownerNotes: "", signeeNotes: ""})
                } else {
                    let s = this.statuses[requirement.id];
                    this.table.push({
                        title: requirement.title,
                        description: marked.parse(requirement.description),
                        doc_link: requirement.doc_link,
                        ownerStatus: s.ownerStatus,
                        ownerNotes: s.ownerNotes,
                        signeeStatus: s.signeeStatus,
                        signeeNotes: s.signeeNotes
                    });
                }
            }
        },
    },
    mounted: function() {
        Promise.all([this.fetchStatuses()]).then(() => {
            this.updateRequirements();
            this.updateTable();

            $('.req-title-tooltip').each(function(index, el) {
                 pa_tooltip(el);
            });
        }).catch(err => {
            console.error('Initialization of quadrants or rings failed', err);
        });
    },
    watch: {
        component_version: function() {
            this.updateStatuses().then(_ => this.updateTable())
        }
    },
    template: `
    {% verbatim %}<el-card v-if='title'>
        <div slot="header" class="clearfix">
            <h2>{{title }} <small v-if=doc_link><a v-bind:href="doc_link" target=_blank><i class='fa fa-external-link'></i></a></small></h2>
        </div>

        <table class='status-table' v-bind:class="[ (requirements && applicable) ? '' : 'status-table-na']">
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
                <td><span class='req-title-tooltip' v-cloak data-toggle="tooltip" data-placement="bottom" data-container="body" :title="row.description">{{ row.title }}</span></td>

                <td>
                   <widget-status v-if="applicable" v-bind:status="row.ownerStatus"></widget-status>
                   <widget-status v-else v-bind:status="na_status"></widget-status>
                </td>
                <td>
                   <widget-status v-if="applicable" v-bind:status="row.signeeStatus"></widget-status>
                   <widget-status v-else v-bind:status="na_status"></widget-status>
                </td>
                <td class='notes'>
                   <widget-note v-if="row.ownerNotes && row.signeeNotes" v-bind:short="true">{{ row.ownerNotes }} / {{ row.signeeNotes }}</widget-note>
                   <widget-note v-else v-bind:short="true">{{ row.ownerNotes }}{{ row.signeeNotes }}</widget-note>
                </td>
            </tr>
            </tbody>
        </table>
    </el-card>{% endverbatim %}
    `
})
