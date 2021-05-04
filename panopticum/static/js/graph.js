  document.addEventListener("DOMContentLoaded", function(){
    /* initialise & populate component dropdown list*/
    let componentDropdown = document.getElementById('component-dropdown');
    componentDropdown.length = 0;
    
    let defaultOption = document.createElement('option');
    defaultOption.text = 'Select Component';
    defaultOption.value = 0;
    
    componentDropdown.add(defaultOption);
    componentDropdown.selectedIndex = 0; // item numbering in panopticum starts from 1. 0 is treated as invalid id.
    
    const url = '/api/component/';
    
    const request = new XMLHttpRequest();
    request.open('GET', url, true);
    
    request.onload = function() {
      if (request.status === 200) {
        const data = JSON.parse(request.responseText);
        let option;
        for (let i = 0; i < data.results.length; i++) {
          option = document.createElement('option');
          option.text = data.results[i].name;
          option.value = data.results[i].id;
          componentDropdown.add(option);
        }
       } else {
        // server error
      }   
    }

    request.onerror = function() {
      console.error('An error occurred fetching the JSON from ' + url);
    };
    
    request.send();

    /* initialise component version dropdown*/
    let versionDropdown = document.getElementById('component-version-dropdown');
    versionDropdown.length = 0;
    let defaultVersionOption = document.createElement('option');
    defaultVersionOption.text = 'Select Component Version';
    defaultVersionOption.value = 0;
    versionDropdown.add(defaultVersionOption);
    versionDropdown.selectedIndex = 0;
  
    /* helper functions */
    let $$ = selector => Array.from( document.querySelectorAll( selector ) );
    let $ = selector => document.querySelector( selector );
    let tryPromise = fn => Promise.resolve().then( fn );
    let toJson = obj => obj.json();
    let toText = obj => obj.text();
  
    /* initialize cytoscape*/
    let cy;
    let layout =  { 
      'name': 'klay',
      'klay' : {
        'direction': 'RIGHT',
        'nodePlacement': 'LINEAR_SEGMENTS',
        'layoutHierarchy': true,
        'mergeHierarchyCrossingEdges': true,
        'edgeSpacingFactor': 0.4,
        'inLayerSpacingFactor': 1,
        'spacing': 25
      }
    }
    let transformApiResponse = apiData => {
      var newNodes = {
        'nodes': []
      };
      var newEdges = {
        'edges': []
      }

      apiData['components'].forEach(component => {
        if (cy.getElementById(component.id).empty()) {
          newNodes.nodes.push(component);
        }
      })

      cy.zoom(0.001);
      cy.pan({ x: -9999999, y: -9999999 });

      cy.add( newNodes );

      
    }

    /* populate cytoscape graph */
    let getDataset = ([id, version_id]) => {
      if (id != 0){
        // get specific component version if selected in dropdown
        if (version_id != 0){
          return fetch(`api/graph/component/${id}/?depth=2&component_version=${version_id}`).then( toJson );
        }
        else {
          return fetch(`api/graph/component/${id}/?depth=2`).then( toJson );
        }
      }
      else {
        // return dummy node
        return {"components": [
          {
            "id": "display", 
            "name": "Select a component to view", 
            "dependsOn": [], 
            "dependedUpon": [],
            "type": "", "ha": "", "sec": [],
            "info": {
              "version": "",
              "desc": "",
              "privacy": "",
            }
          }], 
        "categories": []};
      }
    }

    let makeComponentNode = component => {
      // helper to construct component node from API response
      var node = {
        "data": {
          "id": component.id,
          "label": component.name,
          "parent": 'cat_' + component.category,
          "edgesTo": component.dependsOn,
          "edgesFrom": component.dependedUpon,
          "info": component.info
        },
        "classes": ""
      }

      // determine the shape of the node
      var nodeStyleType = "typeService"
      if (component.type === "Database") {
        nodeStyleType = "typeDatabase"
      }
      if (component.ha == "ready") {
        nodeStyleType += "HA"
      }
      node.classes = nodeStyleType;

      // add class style for node expansion
      if (node.data.edgesTo.length != 0 || node.data.edgesFrom.length != 0) {
        // node.data.expandable = true;
        node.classes += " expandableNode"
      }

      // add class style for security
      if (component.sec.length > 0) {
        node.classes += " securityAlert";
        node.data.sec = component.sec;
      }

      return node;
    }
    let makeCategoryNode = category => {
      // helper to construct compound node from API response
      return {
        "data": {
          "id": 'cat_' + category.id,
          "label": category.name
        },
        "classes": "compound"
      }
    }
    let makeEdge = (source, target, label) => {
      // helper to construct edge
      return {
        "data": {
          "source": source,
          "target": target,
          "id": source + "_" + target,
          "label": label
        }
      }
    }

    let clearElements = dataset => {
      // promise to clear elements from graph. passes dataset through.
      cy.elements().remove();
      return dataset;
    }

    let appendDataset = dataset => {
      var newNodes = {
        'nodes': []
      };
      var newEdges = {
        'edges': []
      }

      dataset['categories'].forEach(category => {
        if (cy.getElementById('cat_' + category.id).empty()) {
          newNodes.nodes.push(makeCategoryNode(category))
        }
      })
      dataset['components'].forEach(component => {
        if (cy.getElementById(component.id).empty()) {
          newNodes.nodes.push(makeComponentNode(component));
        }
      })


      cy.zoom(0.001);
      cy.pan({ x: -9999999, y: -9999999 });

      cy.add( newNodes );

      // create edges for newly added components
      dataset['components'].forEach(component => {
        var cyElem = cy.getElementById(component.id);

        var edgesTo = cyElem.data("edgesTo");
        var newEdgesTo = edgesTo.map((x) => x);
        edgesTo.forEach(edgeTo => {
          var toElem = cy.getElementById(edgeTo.id);
          if (!toElem.empty()){
            var toElem_EdgesFrom = toElem.data("edgesFrom");
            if (typeof(toElem_EdgesFrom) !== 'undefined') {
              var edgeInfo = toElem_EdgesFrom.find(x=>x.id === component.id);
              if (typeof(edgeInfo) !== 'undefined') {
                toElem_EdgesFrom = toElem_EdgesFrom.filter(x => x.id !== component.id);
                toElem.data("edgesFrom", toElem_EdgesFrom);
                if (toElem_EdgesFrom.length === 0 && toElem.data("edgesTo").length === 0) {
                  toElem.removeClass("expandableNode");
                }

                newEdgesTo = newEdgesTo.filter( x=> x.id !== edgeTo.id);

                newEdges.edges.push(makeEdge(component.id, edgeTo.id, edgeTo.type));
              }
            }
          }
        });
        cyElem.data("edgesTo", newEdgesTo);

        var edgesFrom = cyElem.data("edgesFrom");
        var newEdgesFrom = edgesFrom.map((x)=>x);
        edgesFrom.forEach(edgeFrom => {
          var fromElem = cy.getElementById(edgeFrom.id);
          if (!fromElem.empty()){
            var fromElem_EdgesTo = fromElem.data("edgesTo");
            if (typeof(fromElem_EdgesTo) !== 'undefined') {
              var edgeInfo = fromElem_EdgesTo.find(x => x.id === component.id);
              if (typeof(edgeInfo) !== 'undefined') {
                fromElem_EdgesTo = fromElem_EdgesTo.filter(x=>x.id !== component.id);
                fromElem.data("edgesTo", fromElem_EdgesTo);
                if (fromElem_EdgesTo.length === 0 && fromElem.data("edgesFrom").length === 0) {
                  fromElem.removeClass("expandableNode");
                }
                
                newEdgesFrom = newEdgesFrom.filter( x=> x.id !== edgeFrom.id);
                
                newEdges.edges.push(makeEdge(edgeFrom.id, component.id, edgeInfo.type));
              }
            }
          }
        });
        cyElem.data("edgesFrom", newEdgesFrom);

        if (cyElem.data("edgesTo").length === 0 && cyElem.data("edgesFrom").length === 0) {
          cyElem.removeClass("expandableNode");
        }
      })

      cy.add(newEdges);
    }

    let applyDatasetFromSelect = () => Promise.all( [componentDropdown.value, versionDropdown.value] ).then( getDataset ).then( clearElements ).then(appendDataset);

    let getStylesheet = fetch('/static/js/graph-style.json').then( toJson );
    let applyStylesheet = stylesheet => {
      cy.style().fromJson( stylesheet ).update();
    };
    let applyStylesheetFromSelect = () => Promise.resolve( getStylesheet ).then( applyStylesheet );
  
    let applyLayout = () => {
      let l =  cy.makeLayout( layout );

      cy.panzoom({
        // options here...
      });
  
      return l.run();
    }  
    cy = window.cy = cytoscape({
      container: $('#cy')
    });
  
    tryPromise( applyDatasetFromSelect ).then(applyStylesheetFromSelect).then( applyLayout );

    let fillComponentVersionDropdown = data => {
      // clear existing options
      for (i = versionDropdown.length-1; i > 0; i--) {
        versionDropdown.options[i] = null;
      }

      if (data.results.length > 0) {
        versionDropdown[0].text = `(Latest Version) (${data.results[0].version})`;
        versionDropdown[0].value = 0;

        let option;
        for (let i = 0; i < data.results.length; i++) {
          option = document.createElement('option');
          option.text = data.results[i].version;
          option.value = data.results[i].id;
          versionDropdown.add(option);
        }
      }
      else {
        versionDropdown[0].text = `No component version available`;
        versionDropdown[0].value = 0;
      }
    }
    let updateComponentVersion = componentId => {
      if (componentId != 0){
        fetch(`api/component_version/?format=json&ordering=-release_date&component=${componentId}`).then(toJson).then(fillComponentVersionDropdown);
      }
    }
    let updateComponentVersionFromSelect = () => Promise.resolve( componentDropdown.value ).then(updateComponentVersion);

    /* Dropdown change events */

    componentDropdown.addEventListener('change', function(){
      versionDropdown.selectedIndex = 0;
      tryPromise( updateComponentVersionFromSelect);
      tryPromise( applyDatasetFromSelect ).then(applyStylesheetFromSelect).then( applyLayout );
    });

    versionDropdown.addEventListener('change', function(){
      tryPromise( applyDatasetFromSelect ).then(applyStylesheetFromSelect).then( applyLayout );
    })

    /* Cytoscape graph interaction events */ 

    /* On click: expand nodes*/
    cy.on('tap', 'node', function(evt){
      var node = evt.target;

      if (node.hasClass("expandableNode")) {
        let getAppendDataset = fetch(`/api/graph/component/${node.id()}/?depth=1`).then( toJson );
        let appendDataSetFromTap = () => Promise.resolve(getAppendDataset).then(appendDataset);
        tryPromise(appendDataSetFromTap).then(applyLayout);
      }
    })

    /* On mouseover: show component detail + security alerts */
    cy.on('mouseover', 'node', function(evt){
      var node = evt.target;
      var data = node.data();

      // don't show tooltips on compound nodes
      if (!node.isParent()) {
        if (data["info"]){
          if (!node.tippy) {
            let ref = node.popperRef();

            node.tippy = tippy(ref, { // tippy options:
              content: () => {
                let content = document.createElement('div');
        
                if (data["info"]["desc"]) {
                  content.innerHTML += `<b>Description:</b> ${data["info"]["desc"]} <br>`
                }
                if (data["info"]["version"]) {
                  content.innerHTML += `<b>Version:</b> ${data["info"]["version"]} <br>`
                }
                if (data["info"]["privacy"]) {
                  content.innerHTML += `<b>Data Privacy:</b> ${data["info"]["privacy"]}`
                }
        
                return content;
              },
              theme: 'info',
              trigger: 'manual',
              placement: 'right',
            });

          }
          node.tippy.show();
        }

        if (data["sec"]) {
          if (!node.secTippy) {
            let ref = node.popperRef();
            node.secTippy = tippy(ref, { // tippy options:
              content: () => {
                let content = document.createElement('div');
        
                for(i = 0; i < data["sec"].length - 1; i++) {
                  content.innerHTML += `${data["sec"][i]}<br>`
                }
                content.innerHTML += `${data["sec"][data["sec"].length - 1]}<br>`
        
                return content;
              },
              theme: 'alert',
              trigger: 'manual',
              placement: 'left',
            });
          }
          node.secTippy.show();
        }
      }
    })

    /* On mouseout: hide info/alert boxes */
    cy.on('mouseout', 'node', function(evt){
      var node = evt.target;
      if (node.tippy) {
        node.tippy.hide();
      }
      if (node.secTippy) {
        node.secTippy.hide();
      }
    })

  });