<template>
  <table class="history">
    <tr>
      <th>Time</th>
      <th>User</th>
      <th>Action</th>
      <th>Value</th>
    </tr>
    <tr v-for="(entry, index) in data" :key="index + ':' + entry.time">
      <td>{{niceDate(entry.time)}}</td>
      <td>{{entry.user}}</td>
      <td>{{entry.action}}</td>
      <td v-html='historyValue(entry.value)'></td>
    </tr>
  </table>
</template>

<script>

  import dateFormat from 'dateformat'

  export default {
    props:{
      data: {
        type: Array
      }
    },
    data () {
      return {
      }
    },
    created () {
    },
    watch:{
    },
    methods: {
      niceDate: function (time) {
        return dateFormat(new Date(time * 1000), 'yyyy-mm-dd HH:MM:ss')
      },
      historyValue: function(value) {
        if (typeof value === 'string' || value instanceof String) {
          return value;
        }
        return '<pre>' + JSON.stringify(value, null, 2) + '</pre>';
      }
    },
    computed: {
      
    }
  }
</script>

<style scoped>

.history, .history td, .history th {
  border: 1px solid rgba(0, 0, 0, 0.87) !important;
  border-collapse: collapse;
  padding: 4px !important;
}

.history {
  margin-top: 4px;
  margin-bottom: 4px;
  font-size: 0.9em;
}

tr, td, th {
  height: 14px !important;
}

</style>