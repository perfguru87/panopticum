Vue.component('widget-status-popover', {
    props: [
      'owner-status', 'signee-status', 'overall-status'
    ],
    data: function() {
        return {
            _ownerStatus: null,
            _signeeStatus: null,
            _overeallStatus: null,
            history: null,
            user: null,
            loading: true
        }
    },
    computed: {
        classObject: function() {
            return {
              'pointer': this.popupEnabled
            }
        },
        statuses: function() {
            return [ this._signeeStatus, this._ownerStatus, this._overallStatus];
        },
        apiUrl: function() {
            return `${window.location.origin}/api`
        },
        popupEnabled: function() {
            const statuses = this.statuses;
            return statuses.filter(status => {
                return (status && status.status.id != window.REQ_STATUS_UNKNOWN)
            }).some(s => s);
        }
    },
    created: function() {
        this._ownerStatus = this.ownerStatus;
        this._signeeStatus = this.signeeStatus;
        this._overallStatus = this.overallStatus;
    },
    methods: {
        getUsername(user) {
            if (!user) return null;
            if (user.first_name && user.last_name) {
                return `${user.first_name} ${user.last_name}`
            } else {
                return user.username;
            }
        },
        getIDfromHref(href) {
            const idPattern = new RegExp("^.*/(\\d+)/(?:\\?.+)?$");
            return Number(idPattern.exec(href)[1]);
        },
        updateLastChange() {
            let url = document.createElement('a');
            const statuses = this.statuses;
            const requests = statuses.map(status => {
                if (status == undefined)
                    return;
                url.href = status.url;

                return axios.get(`${url.pathname}history/?format=json&limit=1`)
                .then(resp => {
                    if (resp.data.count > 0) {
                        status.history = resp.data.results[0];
                        return axios.get(status.history.history_user).then(resp => {
                               status.user = resp.data;
                        });
                    }
                })
            })
            Promise.all(requests).then((ownerStatus, signeeStatus, overallStatus) => {
                this._ownerStatus = ownerStatus;
                this._signeeStatus = signeeStatus;
                this._overallStatus = overallStatus;
                this.loading = false;
            })

        },
        formatDate: function(date) {
            return moment(date).fromNow();
        }
    },
    template: `{% verbatim %}
    <el-popover
    placement="bottom-end"
    width="300"
    trigger="click"
    popper-class="signoff-popover"
    v-bind:disabled = "!popupEnabled"
    :offset = "10"
    @show="updateLastChange()">

        <el-card v-for="status in statuses.filter(s=>s)" class="clearfix" :v-loading="loading" :key="status.id" >
            <div slot="header" class="clearfix" style="font-weight: bold;">
                {{ status.type }}
            </div>
            <div v-if="status.history && status.user">
                <div class="text item">Status: {{ status.status.name }}
                </div>
                <div class="text item">updated by: <span style="font-weight: bold">{{ getUsername(status.user) }}</span></div>
                <div class="text item">updated time: {{ formatDate(status.history.history_date) }}</div>
                <div class="text item" v-if="status && status.notes">notes: <widget-note>{{ status.notes }}</widget-note></div>
            </div>
        </el-card>
        <span slot="reference">
        <slot></slot>
    </span>
  </el-popover>
    {% endverbatim %}`
})
