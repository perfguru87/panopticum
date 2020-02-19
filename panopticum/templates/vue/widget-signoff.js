Vue.component('widget-signoff', {
  props: [
    'status', 
  ],
  computed: {
    classObject: function() {
      return {
        'pointer': this.popupEnabled
      }
    },
    apiUrl: function() {
      return `${window.location.origin}/api`
    },
    popupEnabled: function() {
      return this.status && (this.status.notes || this.history) && this.status.status != 'unknown'
    },
    username: function() {
      if (!this.user) return null;
      if (this.user.first_name && this.user.last_name) {
        return `${this.user.first_name} ${this.user.last_name}`
      } else { 
        return this.user.username;
      }
    }
  },
  data: function() {
    return {
      'history': null,
      'user': null 
    }
  },
  mounted: function() {
    if (this.status) this.updateLastChange(this.status);
  },
  methods: {
    getIDfromHref(href) {
      const idPattern = new RegExp("^.*/(\\d+)/(?:\\?.+)?$");
      return Number(idPattern.exec(href)[1]);
    },
    updateLastChange: function(status) {
      let url = document.createElement('a');
      url.href = status.url;

      return axios.get(`${url.pathname}history/?format=json&limit=1`)
        .then(resp => {
          if (resp.data.count > 0) {
            this.history = resp.data.results[0];
            axios.get(this.history.history_user).then(resp => this.user = resp.data)
          }
        })
    },
    formatDate: function(date) {
      return new Date(Date.parse(date)).toLocaleString('en-US', 
                                                       {month: 'long', 
                                                       year: 'numeric', 
                                                       day: 'numeric', 
                                                       hour: 'numeric', 
                                                       minute: 'numeric', 
                                                       second: 'numeric'})
    }
  },
  template: `{% verbatim %}
  <el-popover
              placement="top-end"
              width="250"
              trigger="click"
              popper-class="signoff-popover"
              v-bind:disabled = "!popupEnabled"
              offset = -10
  >
    <div v-if="history && user">
      <div class="text item">Updated by <span style="font-weight: bold">{{ username }}</span></div>
      <div class="text item">at {{ formatDate(history.history_date) }}</div>
      <div class="text item" v-if="status && status.notes && status.type=='requirement reviewer'">by reason: {{ status.notes }}</div>
    </div>
    <span slot="reference">
      <app-status :status="status ? status.status : null " ></app-status>
    </span>
  </el-popover>{% endverbatim %}
  `
})
