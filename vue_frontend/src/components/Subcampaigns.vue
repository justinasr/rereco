<template>
  <div style="height: calc(100vh - 118px); overflow: auto;">
    <div style="display: flex;">
      <div style="flex: 1 1 auto;">
        <div>
          <div style="width: calc(100vw - 32px); position: sticky; left: 16px;">
            <h1 class="page-title">Subcampaigns</h1>
            <ColumnSelector :columns="columns"
                            v-on:updateColumns="updateTableColumns"/>
          </div>
        </div>
        <v-data-table :headers="headers"
                      :items="dataItems"
                      :items-per-page="itemsPerPage"
                      :loading="loading"
                      disable-sort
                      hide-default-footer
                      class="elevation-1"
                      dense>
          <template v-slot:item._actions="{ item }">
            <a :href="'subcampaigns/edit?prepid=' + item.prepid" v-if="role('manager')" title="Edit subcampaign">Edit</a>&nbsp;
            <a style="text-decoration: underline;" @click="showDeleteDialog(item)" v-if="role('manager')" title="Delete subcampaign">Delete</a>&nbsp;
            <a v-if="role('manager')" :href="'subcampaigns/edit?clone=' + item.prepid" title="Clone subcampaign">Clone</a>&nbsp;
            <a :href="'requests?subcampaign=' + item.prepid" :title="'Show all requests in '+ item.prepid">Requests</a>&nbsp;
          </template>
          <template v-slot:item.prepid="{ item }">
            <a :href="'subcampaigns?prepid=' + item.prepid" title="Show only this subcampaign">{{item.prepid}}</a>
          </template>
          <template v-slot:item.history="{ item }">
            <HistoryCell :data="item.history"/>
          </template>
          <template v-slot:item.sequences="{ item }">
            <SequencesCell :data="item.sequences"/>
          </template>
          <template v-slot:item.memory="{ item }">
            {{item.memory}} MB
          </template>
          <template v-slot:item.energy="{ item }">
            {{item.energy}} TeV
          </template>
          <template v-slot:item.cmssw_release="{ item }">
            <a :href="'subcampaigns?cmssw_release=' + item.cmssw_release" :title="'Show all subcampaigns with ' + item.cmssw_release">{{item.cmssw_release.replace('_', ' ').replace(/_/g, '.')}}</a>
            <br>
            <small><a :href="'subcampaigns?scram_arch=' + item.scram_arch" :title="'Show all subcampaigns with ' + item.scram_arch">{{item.scram_arch}}</a></small>
          </template>
          <template v-slot:item.notes="{ item }">
            <pre v-if="item.notes.length" class="notes">{{item.notes}}</pre>
          </template>
          <template v-slot:item.campaign="{ item }">
            <a :href="'subcampaigns?prepid=' + getCampaign(item.prepid) + '-*'" title="Show all subcampaigns in the same campaign">{{getCampaign(item.prepid)}}</a>
          </template>
          <template v-slot:item.runs_json_path="{ item }">
            <a target="_blank" :href="'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/' + item.runs_json_path" title="Open JSON file with runs list">{{item.runs_json_path}}</a>
          </template>
        </v-data-table>
      </div>
    </div>

    <v-dialog v-model="dialog.visible"
              max-width="50%">
      <v-card>
        <v-card-title class="headline">
          {{dialog.title}}
        </v-card-title>
        <v-card-text>
          {{dialog.description}}
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn small class="mr-1 mb-1" color="primary" @click="dialog.cancel">
            Cancel
          </v-btn>
          <v-btn small class="mr-1 mb-1" color="error" @click="dialog.ok">
            OK
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="errorDialog.visible"
              max-width="50%">
      <v-card>
        <v-card-title class="headline">
          {{errorDialog.title}}
        </v-card-title>
        <v-card-text>
          <span v-html="errorDialog.description"></span>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn small class="mr-1 mb-1" color="primary" @click="errorDialog.visible = false">
            Dismiss
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <footer>
      <a :href="'subcampaigns/edit'" v-if="role('manager')" title="Create new subcampaign">New subcampaign</a>
      <Paginator :totalRows="totalItems"
                 v-on:update="onPaginatorUpdate"/>
    </footer>
  </div>
</template>

<script>

import axios from 'axios'
import ColumnSelector from './ColumnSelector'
import Paginator from './Paginator'
import HistoryCell from './HistoryCell'
import SequencesCell from './SequencesCell'
import { roleMixin } from '../mixins/UserRoleMixin.js'
import { utilsMixin } from '../mixins/UtilsMixin.js'

export default {
  components: {
    ColumnSelector,
    Paginator,
    HistoryCell,
    SequencesCell
  },
  mixins: [roleMixin, utilsMixin],
  data () {
    return {
      databaseName: undefined,
      columns: [
        {'dbName': 'prepid', 'displayName': 'PrepID', 'visible': 1},
        {'dbName': '_actions', 'displayName': 'Actions', 'visible': 1},
        {'dbName': 'campaign', 'displayName': 'Campaign', 'visible': 1},
        {'dbName': 'cmssw_release', 'displayName': 'CMSSW Release', 'visible': 1},
        {'dbName': 'energy', 'displayName': 'Energy', 'visible': 1},
        {'dbName': 'memory', 'displayName': 'Memory', 'visible': 1},
        {'dbName': 'notes', 'displayName': 'Notes', 'visible': 1},
        {'dbName': 'history', 'displayName': 'History', 'visible': 0},
        {'dbName': 'runs_json_path', 'displayName': 'Runs JSON', 'visible': 0},
        {'dbName': 'sequences', 'displayName': 'Sequences', 'visible': 0},
      ],
      headers: [],
      dataItems: [],
      loading: false,
      itemsPerPage: 1,  // If initial value is 0, table does not appear after update
      totalItems: 0,
      dialog: {
        visible: false,
        title: '',
        description: '',
        cancel: undefined,
        ok: undefined,
      },
      errorDialog: {
        visible: false,
        title: '',
        description: ''
      }
    }
  },
  computed: {
    visibleColumns: function () {
      return this.columns.filter(col => col.visible)
    }
  },
  created () {
    this.clearDialog();
  },
  methods: {
    fetchObjects () {
      let component = this;
      this.loading = true;
      let query = this.$route.query;
      let queryParams = '';
      Object.keys(query).forEach(k => {
        if (k != 'shown') {
          queryParams += '&' + k + '=' + query[k];
        }
      });
      axios.get('api/search?db_name=subcampaigns' + queryParams).then(response => {
        component.dataItems = response.data.response.results.map(function (x) { x._actions = undefined; return x});
        component.totalItems = response.data.response.total_rows;
        component.loading = false;
      });
    },
    updateTableColumns: function(columns, headers) {
      this.columns = columns;
      this.headers = headers;
    },
    onPaginatorUpdate: function(page, itemsPerPage) {
      this.itemsPerPage = itemsPerPage;
      this.fetchObjects();
    },
    clearDialog: function() {
      this.dialog.visible = false;
      this.dialog.title = '';
      this.dialog.description = '';
      this.dialog.ok = function() {};
      this.dialog.cancel = function() {};
    },
    clearErrorDialog: function() {
      this.errorDialog.visible = false;
      this.errorDialog.title = '';
      this.errorDialog.description = '';
    },
    showError: function(title, description) {
      this.clearErrorDialog();
      this.errorDialog.title = title;
      this.errorDialog.description = description;
      this.errorDialog.visible = true;
    },
    showDeleteDialog: function(subcampaign) {
      let component = this;
      this.dialog.title = "Delete " + subcampaign.prepid + "?";
      this.dialog.description = "Are you sure you want to delete " + subcampaign.prepid + " subcampaign?";
      this.dialog.ok = function() {
        component.loading = true;
        axios.delete('api/subcampaigns/delete', {data: {'prepid': subcampaign.prepid}}).then(() => {
          component.clearDialog();
          component.fetchObjects();
        }).catch(error => {
          component.loading = false;
          component.clearDialog();
          component.showError("Error deleting subcampaign", component.getError(error));
        });
      }
      this.dialog.cancel = function() {
        component.clearDialog();
      }
      this.dialog.visible = true;
    },
    getCampaign: function(prepid) {
      return prepid.split('-').filter(Boolean)[0];
    }
  }
}
</script>
