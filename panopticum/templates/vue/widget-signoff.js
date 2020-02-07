Vue.component('widget-signoff', {
  props: ['status', 'signoff-status'],
  computed: {
    classObject: function() {
      return {
        'el-icon-success yes': this.status && this.status.status == 'yes',
        'el-icon-error no': this.status && this.status.status == 'no',
        'unknown': this.status && this.status.status == 'n/a',
        'el-icon-question': !this.status || this.status.status == 'unknown',
        'pointer': this.popupEnabled
      }
    },
    apiUrl: function() {
      return `${window.location.origin}/api`
    },
    popupEnabled: function() {
      return this.status && (this.status.notes || this.history)
    }
  },
  data: function() {
    return {
      'history': null,
    }
  },
  watch: {
    history: function() {
      console.log(this.history.user);
    }
  },
  mounted: function() {
    if (this.status) this.updateLastChange(this.status);
  },
  methods: {
    updateLastChange: function(status) {
      return axios.get(`${status.url}history/?limit=1`)
      .then(resp => {
        if (resp.data.count > 0) {
          this.history = resp.data.results[0];
          axios.get(this.history.history_user).then(resp => this.history.user = resp.data)
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
  >
    <div v-if="history && history.user">Updated by {{ history.user }} <br/>
    at {{ formatDate(history.history_date) }}</div>
    <span slot="reference" >
      <i v-if="status && ['yes', 'no'].includes(status.status)" v-bind:class="classObject" style="font-size: 16px;"></i>
      <i v-else-if="status && ['n/a'].includes(status.status)" v-bind:class="classObject" style="font-size: 12px;">
      N/A
      </i>
      <i v-else class="el-icon-question" style="color: grey;font-size: 16px;"></i>
    </span>
  </el-popover>{% endverbatim %}
  `
})
