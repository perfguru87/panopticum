<template>
    <span>
        <el-popover
                    v-if="['yes', 'no'].includes(status) && signoff"
                    placement="top-end"
                    width="200"
                    trigger="click"
                    popper-class="signoff-popover"
             >
                <div>Updated by {{ signoff.user.username }} <br/>
                at {{ signoff.date }}</div>
                <span v-bind:class="classObject" slot="reference" style="cursor: pointer">
                  {{ status.toUpperCase() }}
                </span>
        </el-popover>
        <span v-else-if="['yes', 'no'].includes(status) && !signoff" v-bind:class="classObject">
                  {{ status.toUpperCase() }}
        </span>
        <i v-else class="unknown fa fa-question-circle" style="font-size: 12px; color: crimson;"></i>
    </span>
</template>

<script>
    module.exports = {
      props: ['status', 'signoff'],
      computed: {
          classObject: function() {
            return {
              yes: this.status == 'yes',
              no: this.status == 'no',
              unknown: this.status == 'unknown' || this.status === null
            }
          }
      },
    }
</script>

