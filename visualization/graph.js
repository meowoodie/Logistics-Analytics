/*
 * Customized d3 graph
 * 
 * 1. Force directed
 * 2. Map based
 */

var d3Graph = {

    forceDirected: function(domId, graph) {
        var width  = 1200,
            height = 1000;

        // Collect the group tag of each of the nodes
        var groupInfo = {},
            index = 0;
        graph.nodes.forEach(function(d) {
            groupInfo[index] = d.group;
            index ++;
        });
        
        // Collect cross links and normal links
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

        // Colorbar for showing different industrial catagories
        var color = d3.scale.category20();
        
        // Init force
        var force = d3.layout.force()
                .charge(-500)
                .gravity(0.2)
                .linkDistance(130)
                .size([width, height]);
        
        var svg = d3.select("#" + domId).append("svg")
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
                .style("stroke-width", function(d) { return Math.sqrt(d.value) * 5; });
                
        var crosslink = svg.selectAll(".cross-link")
                .data(crossLinks)
                .enter().append("line")
                .attr("x1", 100)
                .attr("y1", 100)
                .attr("x2", 200)
                .attr("y2", 200)
                .attr("class", "cross-link")
                .style("stroke-width", function(d) { return Math.sqrt(d.value) * 5; })

        var node = svg.selectAll(".node")
                .data(graph.nodes)
                .enter().append("g").attr("class", "node-group")
                .call(force.drag);
        
        var nodeMap = {};
        node.append("circle")
                .attr("class", "node")
                // .attr("r", 5)
                .attr("r", function(d)  { return d.company_num/1000 > 15 ? 15 : (d.company_num/1000 < 5 ? 5 : d.company_num / 1000);})
                .style("fill", function(d) {
                    nodeMap[d.index] = d;
                    return color(d.group);
                });

        node.append("text")
                .attr("class", "force-text")
                .attr("x", 12)
                .attr("dy", ".35em")
                .style("font-size", "14px")
                .text(function(d) { return d.industry_lv3; });

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

    mapBased: function(domId, graph) {

        // Functions that supports zooming the canvas
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
        
        // Init map and zoom widgets
        var map = d3.map(),
            zoom = d3.behavior.zoom()
                .scaleExtent([1, 10])
                .on("zoom", zoomed),
            drag = d3.behavior.drag()
                .origin(function(d) { return d; })
                .on("dragstart", dragstarted)
                .on("drag", dragged)
                .on("dragend", dragended),
            colorbarDict = _.chain(graph.nodes)
                .values()
                .map(function(node_val){return _.keys(node_val.industry_lv1_dist);})
                .flatten()
                .uniq()
                .map(function(industry_name){return [industry_name, dynamicColors()]})
                .object()
                .value();
         
        var width = 1200, height = 1000;
        
        var proj = d3.geo.mercator().center([105, 38]).scale(1000).translate([width/2, height/2]),
            path = d3.geo.path().projection(proj);
         
        var svg = d3.select("#" + domId).append("svg")
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
     
        container.append("g")
            .attr("class", "states")
            .selectAll("path")
            .data(china_provinces.features)
            .enter()
            .append("path")
            .attr("d", path);

        var tip = d3.tip()
            .attr('class', 'd3-tip')
            .offset([-30, 0])
            .html(function(d) {
                return "<div><p>"+ d.city_name + '</p><canvas id="pie-chart" width="400" height="400"></canvas><div>';
            });

        container.call(tip);
        
        container.append("svg")
            .attr("width", width)
            .attr("height", height)

        graph.links.forEach(function(d) {
            d.source = graph.nodes[d.source];
            d.target = graph.nodes[d.target];
            source_cood = proj([d.source.lng, d.source.lat]);
            target_cood = proj([d.target.lng, d.target.lat]);
            d.source.x = source_cood[0];
            d.source.y = source_cood[1];
            d.target.x = target_cood[0];
            d.target.y = target_cood[1];
        });

        var link = container.append("g")
            .attr("class", "link")
            .selectAll("line")
            .data(graph.links)
            .enter().append("line")
            .attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; })
            .style("stroke-width", function(d) { return Math.sqrt(d.value); });

        var node = container.append("g")
            .attr("class", "node")
            .selectAll("circle")
            .data(graph.nodes)
            .enter().append("circle")
            .attr("transform", function(d) { return "translate(" + proj([d.lng, d.lat]) + ")"; })
            .attr("r", function(d)  { return d.company_num/2000 > 8 ? 8 : (d.company_num/2000 < 1 ? 1 : d.company_num / 2000);})
            .style("fill", "Green")
            .on("mouseover", function(d) {
                d3.select(this)
                    .transition()
                    .duration(500)
                    .style("cursor", "pointer")
                    .attr("r", 20) // The bar becomes larger
                    .style("fill", "Red");
                tip.show(d);
                // generating content of tip graph
                var ctx = $("#pie-chart");
                var industData = {
                    datasets: [{
                        data: _.values(d.industry_lv1_dist),
                        backgroundColor: _.chain(d.industry_lv1_dist) // colorBar
                            .keys()
                            .map(function(industry_name){return colorbarDict[industry_name];})
                            .value() 
                    }],
                    labels: _.keys(d.industry_lv1_dist)
                };
                var industDoughnutChart = new Chart(ctx,{
                    type: 'doughnut',
                    data: industData
                }); 
            })
            .on("mouseout", function() {
                d3.select(this)
                    .transition()
                    .duration(500)
                    .style("cursor", "normal")
                    .attr("r", function(d)  { return d.company_num/2000 > 8 ? 8 : (d.company_num/2000 < 1 ? 1 : d.company_num / 2000);})
                    .style("fill", "Green");
                tip.hide();
            });

        var text = container.append("g")
            .attr("class", "text")
            .selectAll("string")
            .data(graph.nodes)
            .enter().append("text")
            .attr("transform", function(d) { return "translate(" + proj([d.lng, d.lat]) + ")"; })
            .attr("dx", "1em")
            .attr("dy", "-0.1em")
            .style("font-size", "5px")
            .text(function(d) { return d.city_name; });

    }
}; 