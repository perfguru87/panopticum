# Component Graph Package
This package adds a component graph feature to Panopticum


## Usage
### Files in this Package
- /panopticum
    - /static
        - /css
            - graph.css
        - /fonts
            - OpenSans-Regular.ttf
        - /js
            - graph.js
            - graph-style.json
        - /vendors
            - /cytoscape.js-panzoom
                - cytoscape.js-panzoom.css
                - cytoscape-panzoom.js
            - /cytoscape-klay
                - cytoscape-klay.min.js
                - klay.js
        - /templates
            - /graph
                - graph.html
    - graph.py
- /panopticum_django
    - urls.py
- README_Graph.md (this file)


### Adding to Panopticum
Copy the folder ./Panopticum to <your git repository>/panopticum


### Wiring 
In <your git repository>/panopticum_django, adapt urls.py to expose the view and api.

Add to the import statements:
```
from panopticum import graph
```

Add to the urlpatterns:
```
url('^graph.html', graph.graph_view, name='Graph'),
path('api/graph/component/<int:componentId>/', graph.graph_component),
```

A sample is included in ./panopticum_django/urls.py


## About
The view is defined by ./panopticum/static/templates/graph.html, which in turn relies on ./panopticum/static/js/graph.js for dynamic rendering of graphical elements. This relies on the API on Panopticum /api/graph/component/<componentId> to deliver Panopticum data.

[Cytoscape.js](https://js.cytoscape.org/) is used as the main library for visualisation. 


### API
This package introduces a new API at /api/graph/component/<componentId> which returns aggregated information about the component and its immediate parent & child dependencies, for use by the frontend.

It accepts an optional parameter 'depth', to limit the search of parents & children.


### Frontend
./panopticum/static/js/graph.js handles the display of panopticum data into a cytoscape graph. Styling business logic is handled here, such as the mapping of the styling class type of a component, based on a Panopticum data field.

The following JavaScript libraries are utilised:
- [cytoscape.js](https://github.com/cytoscape/cytoscape.js)
- [cytoscape-klay](https://github.com/cytoscape/cytoscape.js-klay) (added as /static/vendor/cytoscape-klay)
- [cytoscape-panzoom](https://github.com/cytoscape/cytoscape.js-panzoom) (added as /static/vendor/cytoscape.js-panzoom)
- [popper.js](https://github.com/popperjs/popper-core)
- [cytoscape-popper](https://github.com/cytoscape/cytoscape.js-popper)
- [tippy.js](https://github.com/atomiks/tippyjs/releases)


### Configuring Styles
Cytoscape graph style configuration is managed by ./panopticum/static/js/graph-style.json. This allows for configuration of cytoscape elements, i.e. the nodes, edges and corresponding text. Elements are able to apply multiple styles. Colors, images, text size and font are able to be styled, refer to [Cytoscape Style Documentation](https://js.cytoscape.org/#style) for more.

This package provides the following style types:
    - 'node', 'edge', default styles for nodes & edges
    - '.compound', style for category nodes
    - '.type<>', styles for different component types
    - '.expandableNode', style for nodes that can be expanded
    - '.securityAlert', style for nodes that have a security alert

The latter 3 types are stackable on component nodes and are added/removed based on properties of the component and the graph.

Regular CSS styling of the view is done in ./panopticum/static/css/graph.css. For example, styling of the popper elements.


## TODO
- Option for user to click on the component (within graph) and it should land to component detail page.
- Print functionality
- Dynamically plot components and chose line styles such that there is minimum cross over lines and better usage of canvas
- Hover over the component and it shows some information about the component – make this configurable (which fields to be shown)
- Double click should preserve the previous component position (since user may have taken effort to look it beautiful)
- Security issue detection shouldn't be hardcoded and should be configurable. User should be able to select which fields to match and provide data to match against.
- Configuration file details needs to be documented (Readme?)
- Security issue red border improvement (hope this too is configurable)
    - Make red border less thicker than it is at present
    - Use cherry red color instead
- when user selects a component
    - and wants to expand parent node then
        - by default, show only directly linked dependencies to selected component.
        - show some icon/indicator around the parent indicating there are more components parent depends on. Once this icon/indicator is clicked then expand all other dependencies
    - have an option to restrict the view to selected depth of the graph. e.g. if user has chosen depth=3 then at max we show 3 levels of connected graph ensuring selecting component is part of the graph.




