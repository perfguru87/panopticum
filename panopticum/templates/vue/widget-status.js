Vue.component('widget-status', {
    props: [
      'status',
      'light-icon',
    ],
    data: function() {
      return {
        REQ_STATUS_NOT_READY: window.REQ_STATUS_NOT_READY,
        REQ_STATUS_READY: window.REQ_STATUS_READY,
        REQ_STATUS_NOT_APPLICABLE: window.REQ_STATUS_NOT_APPLICABLE,
        REQ_STATUS_WAITING_FOR_APPROVAL: window.REQ_STATUS_WAITING_FOR_APPROVAL,
        REQ_STATUS_WAITING_FOR_NA_APPROVAL: window.REQ_STATUS_WAITING_FOR_NA_APPROVAL,
      };
    },
    computed: {
        classObject: function() {
            return {
                'el-icon-circle-check yes': this.status && this.status.id == window.REQ_STATUS_READY,
                'el-icon-remove no': this.status && this.status.id == window.REQ_STATUS_NOT_READY,
                'fa fa-clock-o': this.status && this.status.id == window.REQ_STATUS_WAITING_FOR_APPROVAL,
                'fa fa-clock-o': this.status && this.status.id == window.REQ_STATUS_WAITING_FOR_NA_APPROVAL,
                'unknown fa fa-question-circle': this.status && this.status.id == window.REQ_STATUS_UNKNOWN,
                'unknown fa fa-question-circle': !this.status || this.status.id == window.REQ_STATUS_UNKNOWN,
            }
        }
    },
    template: `{% verbatim %}
    <span style='margin: 0px;'>
        <i v-if="status && [REQ_STATUS_NOT_READY, REQ_STATUS_READY, REQ_STATUS_WAITING_FOR_APPROVAL, REQ_STATUS_WAITING_FOR_NA_APPROVAL].includes(status.id)" v-bind:class="classObject"></i>
        <span v-else-if="status && [REQ_STATUS_NOT_APPLICABLE].includes(status.id)" v-bind:class="classObject" style="font-size: 12px; color: gray;">
        n/a
        </span>
        <i v-else class="unknown fa fa-question-circle"></i>
    </span>
    {% endverbatim %}`
})
