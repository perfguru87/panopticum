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
      return this.status && (this.status.notes || this.history) && this.status.status != 'unknown';
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
      'user': null,
      loading: true
    }
  },
  mounted: function() {
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
            axios.get(this.history.history_user).then(resp => {
              this.user = resp.data;
              this.loading = false
            });
          }
        })
    },
    formatDate: function(date) {
      return moment(date).fromNow();
  }
  },
  template: `{% verbatim %}
  <el-popover
              placement="bottom-end"
              width="250"
              trigger="click"
              popper-class="signoff-popover"
              v-bind:disabled = "!popupEnabled"
              :offset="10"
              @show="updateLastChange(status)"
  >
    <div v-if="history && user" :v-loading="loading">
      <div class="text item">Updated by <span style="font-weight: bold">{{ username }}</span></div>
      <div class="text item">{{ formatDate(history.history_date) }}</div>
      <div class="text item" v-if="status && status.notes && status.type=='requirement reviewer'">{{ status.notes }}</div>
    </div>
    <span slot="reference">
      <widget-status :status="status ? status.status : null " :class="classObject"></widget-status>
    </span>
  </el-popover>{% endverbatim %}
  `
})
