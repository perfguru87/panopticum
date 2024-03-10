Vue.component('app-status', {
    props: [
      'status', 
      'light-icon'
    ],
    computed: {
        classObject: function() {
            return {
                'el-icon-circle-check yes': this.status && this.status.id == STATUS_READY,
                'el-icon-remove no': this.status && this.status.id == STATUS_NOT_READY,
                'unknown fa fa-question-circle': this.status && this.status.id == STATUS_UNKNOWN,
                'unknown fa fa-question-circle': !this.status || this.status.id == STATUS_UNKNOWN,
            }
        }
    },
    template: `{% verbatim %}
    <span style='margin: 0px;'>
        <i v-if="status && [3, 2].includes(status.id)" v-bind:class="classObject"></i>
        <i v-else-if="status && [4].includes(status.id)" v-bind:class="classObject" style="font-size: 10px;">
        N/A
        </i>
        <i v-else class="unknown fa fa-question-circle"></i>
    </span>
    {% endverbatim %}`
})
