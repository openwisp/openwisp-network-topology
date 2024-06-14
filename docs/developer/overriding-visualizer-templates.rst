Overriding Visualizer Templates
===============================

.. include:: ../partials/developer-docs.rst

Follow these steps to override and customize the visualizer's default
templates:

- create a directory in your django project and put its full path in
  ``TEMPLATES['DIRS']``, which can be found in the django ``settings.py``
  file
- create a sub directory named ``netjsongraph`` and add all the templates
  which shall override the default ``netjsongraph/*`` templates
- create a template file with the same name of the template file you want
  to override

More information about the syntax used in django templates can be found in
the `django templates documentation
<https://docs.djangoproject.com/en/dev/ref/templates/>`_.

Example: Overriding the ``<script>`` Tag
----------------------------------------

Here's a step by step guide on how to change the javascript options passed
to `netjsongraph.js <https://github.com/openwisp/netjsongraph.js>`_,
remember to replace ``<project_path>`` with the absolute filesytem path of
your project.

**Step 1**: create a directory in
``<project_path>/templates/netjsongraph``

**Step 2**: open your ``settings.py`` and edit the ``TEMPLATES['DIRS']``
setting so that it looks like the following example:

.. code-block:: python

    # settings.py
    TEMPLATES = [
        {
            "DIRS": [os.path.join(BASE_DIR, "templates")],
            # ... all other lines have been omitted for brevity ...
        }
    ]

**Step 3**: create a new file named ``netjsongraph-script.html`` in the
new ``<project_path>/templates/netjsongraph/`` directory, eg:

.. code-block:: html

    <!-- <project_path>/templates/netjsongraph/netjsongraph-script.html -->
    <script>
        window.__njg_el__ = window.__njg_el__ || "body";
        window.__njg_default_url__ = "{{ graph_url }}";
        window.loadNetJsonGraph = function(graph){
            graph = graph || window.__njg_default_url__;
            d3.select("svg").remove();
            d3.select(".njg-overlay").remove();
            d3.select(".njg-metadata").remove();
            return d3.netJsonGraph(graph, {
                el: window.__njg_el__,
                // customizations of netjsongraph.js
                linkClassProperty: "status",
                defaultStyle: false,
                labelDy: "-1.4em",
                circleRadius: 8,
                charge: -100,
                gravity: 0.3,
                linkDistance: 100,
                linkStrength: 0.2,
            });
        };
        window.graph = window.loadNetJsonGraph();
        window.initTopologyHistory(jQuery);
    </script>
