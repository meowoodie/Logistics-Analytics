/*
 * Customized d3 graph
 * 
 * 1. Force directed: 
 * 2. Map based: 
 */

// var WIDTH = 800, HEIGHT = 800;

var d3Graph = {
    // 
    forceDirected: function(dom, graph) {
        var width  = 800,
            height = 800;
        
        // Read group info from raw graph data
        var groupInfo = {};
        var index = 0;


        graph.nodes.forEach(function(d) {
            groupInfo[index] = d.group;
            index ++;
        });
        
        var newLinks   = [],
            crossLinks = [];
        graph.links.forEach(function(d) {
            if (groupInfo[d.source] === groupInfo[d.target]) {
                newLinks.push(d);
            } else {
                crossLinks.push(d);
            }
        });

        graph.links = newLinks;

        var color = d3.scale.category20();

        var length = 1000,
            link_color = d3.scale.linear().domain([1,length])
                .interpolate(d3.interpolateHcl)
                .range([d3.rgb("#FFF500"), d3.rgb("#007AFF")]);
        
        var force = d3.layout.force()
                .charge(-120)
                .gravity(0.2)
                .linkDistance(50)
                .size([width, height]);
        
        var svg = d3.select("#" + dom).append("svg")
                .attr("width", width)
                .attr("height", height);
            
        force
                .nodes(graph.nodes)
                .links(graph.links)
                .start();

        var link = svg.selectAll(".link")
                .data(graph.links)
                .enter().append("line")
                .attr("class", "link")
                .style("stroke-width", function(d) { return Math.sqrt(d.value); });
                
        var crosslink = svg.selectAll(".cross-link")
                .data(crossLinks)
                .enter().append("line")
                .attr("x1", 100)
                .attr("y1", 100)
                .attr("x2", 200)
                .attr("y2", 200)
                .attr("class", "cross-link")
                .style("stroke-width", function(d) { return Math.sqrt(d.value * 10); })
                .style("stroke", function(d){
                      return link_color(d.value * length);
                      });

        var node = svg.selectAll(".node")
                .data(graph.nodes)
                .enter().append("g").attr("class", "node-group")
                .call(force.drag);
        
        var nodeMap = {};
        node.append("circle")
                .attr("class", "node")
                .attr("r", 5)
                .style("fill", function(d) {
                    nodeMap[d.index] = d;
                    return color(d.group);
                });

        node.append("text")
                .attr("class", "force-text")
                .attr("x", 12)
                .attr("dy", ".35em")
                .style("font-size", "14px")
                .text(function(d) { return d.city_name; });

        force.on("tick", function() {
            crosslink.attr("x1", function(d) { return nodeMap[d.source].x; })
                .attr("y1", function(d) { return nodeMap[d.source].y; })
                .attr("x2", function(d) { return nodeMap[d.target].x; })
                .attr("y2", function(d) { return nodeMap[d.target].y; });
            
            link.attr("x1", function(d) { return d.source.x; })
                .attr("y1", function(d) { return d.source.y; })
                .attr("x2", function(d) { return d.target.x; })
                .attr("y2", function(d) { return d.target.y; });
            
            node.attr("transform", function(d) {
                return "translate(" + d.x + "," + d.y + ")";
            });
        });
    },


    // 
    mapBased: function(dom, graph) {

        function dottype(d) {
            d.x = +d.x;
            d.y = +d.y;
            return d;
        }

        function zoomed() {
            container.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
        }

        function dragstarted(d) {
            d3.event.sourceEvent.stopPropagation();
            d3.select(this).classed("dragging", true);
        }

        function dragged(d) {
            d3.select(this).attr("cx", d.x = d3.event.x).attr("cy", d.y = d3.event.y);
        }

        function dragended(d) {
            d3.select(this).classed("dragging", false);
        }
 
        var map = d3.map(),
            zoom = d3.behavior.zoom()
                .scaleExtent([1, 10])
                .on("zoom", zoomed),
            drag = d3.behavior.drag()
                .origin(function(d) { return d; })
                .on("dragstart", dragstarted)
                .on("drag", dragged)
                .on("dragend", dragended);
            color = d3.scale.category20();
         
        var width = 1200, height = 1200;
         
        var proj = d3.geo.mercator().center([105, 38]).scale(1000).translate([width/2, height/2]),
            path = d3.geo.path().projection(proj);
         
        var svg = d3.select("#" + dom).append("svg")
            .attr("width", width)
            .attr("height", height)
            .call(zoom);

        var rect = svg.append("rect")
            .attr("width", width)
            .attr("height", height)
            .style("fill", "none")
            .style("pointer-events", "all");

        var container = svg.append("g");

        container.append("g")
            .attr("class", "counties")
            .selectAll("path")
            .data(china_cities.features)
            .enter()
            .append("path")
            .attr("class", function(d) { return "q" + map.get(d.id); })
            .attr("d", path)
            .attr("id", function(d) {return d.id;});
            // .on("mouseover", function(d) {
            //     var m = d3.mouse(d3.select("#"+dom).node());
            //     tooltip.style("display", null)
            //         .style("left", m[0] + 10 + "px")
            //         .style("top", m[1] - 10 + "px");
            //     $("#tt_county").text(d.properties.name);
            // })
            // .on("mouseout", function() {
            //     tooltip.style("display", "none");
            // });
     
        container.append("g")
            .attr("class", "states")
            .selectAll("path")
            .data(china_provinces.features)
            .enter()
            .append("path")
            .attr("d", path);



        // Plot graph
        var force = d3.layout.force()
            .charge(-120)
            .gravity(0.2)
            .linkDistance(50)
            .size([width, height]);

        force
            .nodes(graph.nodes)
            .links(graph.links)
            .start();

        container.append("svg")
            .attr("width", width)
            .attr("height", height)

        // define the nodes

        var groupInfo = {};
        var index = 0;

        graph.nodes.forEach(function(d) {
            groupInfo[index] = d.group;
            index ++;
        });

        var node = container.selectAll(".node")
            .data(graph.nodes)
            .enter().append("g")

        var nodeMap = {};
        node.append("circle")
            .attr("class", "node")
            .attr("transform", function(d) { return "translate(" + proj([d.lng, d.lat]) + ")"; })
            .attr("r", function(d)  { return d.company_num/2000 > 8 ? 8 : (d.company_num/2000 < 1 ? 1 : d.company_num / 2000);})
            .style("fill", function(d) {
                nodeMap[d.index] = d;
                return color(d.company_num/10000);
            });

        node.append("text")
            .attr("transform", function(d) { return "translate(" + proj([d.lng, d.lat]) + ")"; })
            .attr("dx", "1em")
            .attr("dy", "-0.1em")
            .style("font-size", "5px")
            .text(function(d) { return d.city_name; });

        var newLinks   = [],
            crossLinks = [];
        graph.links.forEach(function(d) {
            if (groupInfo[d.source] === groupInfo[d.target]) {
                newLinks.push(d);
            } else {
                crossLinks.push(d);
            }
        });

        graph.links = newLinks;

        var link = container.selectAll(".link")
            .data(graph.links)
            .enter().append("line")
            .attr("class", "link")
            .style("stroke-width", function(d) { return Math.sqrt(d.value); });

        // link.attr("x1", function(d) { return d.source.x; })
        //     .attr("y1", function(d) { return d.source.y; })
        //     .attr("x2", function(d) { return d.target.x; })
        //     .attr("y2", function(d) { return d.target.y; });

        var crosslink = container.selectAll(".cross-link")
            .data(crossLinks)
            .enter().append("line")
            .attr("x1", function(d) { return nodeMap[d.source].x; })
            .attr("y1", function(d) { return nodeMap[d.source].y; })
            .attr("x2", function(d) { return nodeMap[d.target].x; })
            .attr("y2", function(d) { return nodeMap[d.target].y; })
            .attr("class", "cross-link")
            .style("stroke-width", function(d) { return Math.sqrt(d.value * 10); })
            .style("stroke", function(d){
                  return color(d.value);
                  });


    }
}; 