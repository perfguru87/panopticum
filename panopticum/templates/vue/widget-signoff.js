Vue.component('widget-signoff', {
  props: ['status', 'history', 'signoff-status'],
  computed: {
      classObject: function() {
        return {
          'el-icon-success yes': this.status == 'yes',
          'el-icon-error no': this.status == 'no',
          'unknown': this.status == 'n/a',
          'el-icon-question': this.status == 'unknown' || !this.status 
        }
      }
  },
  template: `
    {% verbatim %}<span>
      <el-popover
                  v-if="['yes', 'no', 'n/a'].includes(status) && history"
                  placement="top-end"
                  width="200"
                  trigger="click"
                  popper-class="signoff-popover"
            >
              <div>Updated by {{ history.user.username }} <br/>
              at {{ history.date }}</div>
              <span v-bind:class="classObject" slot="reference" style="cursor: pointer">
                {{ status.toUpperCase() }}
              </span>
      </el-popover>
      <i v-else-if="['yes', 'no'].includes(status) && !history" v-bind:class="classObject" style="font-size: 16px;"></i>
      <i v-else-if="['n/a'].includes(status) && !history" v-bind:class="classObject" style="font-size: 12px;">
      N/A
</i>
      <i v-else class="el-icon-question" style="color: crimson;" style="font-size: 16px;"></i>
    </span>{% endverbatim %}
  `
})
