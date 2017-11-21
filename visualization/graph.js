/*
 * Customized d3 graph 
 * 
 * 
 */

var WIDTH = 1200, HEIGHT = 1200;

var d3Graph = {
    // 
    forceDirected: function(graph) {
        var width  = WIDTH,
            height = HEIGHT;
        
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
                .range([d3.rgb('#FFF500'), d3.rgb("#007AFF")]);
        
        var force = d3.layout.force()
                .charge(-120)
                .gravity(0.2)
                .linkDistance(50)
                .size([width, height]);
        
        var svg = d3.select("#canvas-svg").append("svg")
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
    }
}; 