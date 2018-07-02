var map, container, proj, path,
    width = 800, height = 800;

var tip = d3.tip()
    .attr('class', 'd3-tip')
    .offset([-30, 0])
    .html(function(d) {
        return String.format('\
            <div class="content">\
                <div class="row">\
                  <div class = "col-md-8 col-lg-offset-2">\
                        <div class="row"><p class="card-text">公司 ID: {0}</p></div>\
                        <div class="row"><p class="card-text">主营业务: {1}</p></div>\
                        <div class="row"><p class="card-text">行业类型_lv1: {2}</p></div>\
                        <div class="row"><p class="card-text">城市: {3}</p></div>\
                  </div>\
                </div>\
            </div>', d.id, d.mb, d.ind1, d.city);
    });

maps = {
  initD3Map: function(domId, position) {
    // Functions that supports zooming the canvas
    function dottype(d) {
        d.x = +d.x;
        d.y = +d.y;
        return d;
    };

    function zoomed() {
        container.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
    };

    function dragstarted(d) {
        d3.event.sourceEvent.stopPropagation();
        d3.select(this).classed("dragging", true);
    };

    function dragged(d) {
        d3.select(this).attr("cx", d.x = d3.event.x).attr("cy", d.y = d3.event.y);
    };

    function dragended(d) {
        d3.select(this).classed("dragging", false);
    };

    // // Function for making a star
    // function CalculateStarPoints(centerX, centerY, arms, outerRadius, innerRadius){
    //    var results = "";
    //
    //    var angle = Math.PI / arms;
    //
    //    for (var i = 0; i < 2 * arms; i++)
    //    {
    //       // Use outer or inner radius depending on what iteration we are in.
    //       var r = (i & 1) == 0 ? outerRadius : innerRadius;
    //
    //       var currX = centerX + Math.cos(i * angle) * r;
    //       var currY = centerY + Math.sin(i * angle) * r;
    //
    //       // Our first time we simply append the coordinates, subsequet times
    //       // we append a ", " to distinguish each coordinate pair.
    //       if (i == 0)
    //       {
    //          results = currX + "," + currY;
    //       }
    //       else
    //       {
    //          results += ", " + currX + "," + currY;
    //       }
    //    }
    //
    //    return results;
    // };
    // Init map and zoom widgets
    map = d3.map(),
        zoom = d3.behavior.zoom()
            .scaleExtent([1, 10])
            .on("zoom", zoomed),
        drag = d3.behavior.drag()
            .origin(function(d) { return d; })
            .on("dragstart", dragstarted)
            .on("drag", dragged)
            .on("dragend", dragended);

    // position = [105, 38]
    proj = d3.geo.mercator().center(position).scale(1000).translate([width/2, height/2]),
    path = d3.geo.path().projection(proj);

    var svg = d3.select("#" + domId).append("svg")
        .classed("svg-container", true) //container class to make it responsive
        // .attr("width", width)
        // .attr("height", height)
        .classed("svg-content-responsive", true)
        .call(zoom);

    var rect = svg.append("rect")
        .attr("width", width)
        .attr("height", height)
        .style("fill", "none")
        .style("pointer-events", "all");

    container = svg.append("g");

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

    container.call(tip);
  },

  createRecommendedMarkers: function(points) {
    var pointMax = 8;
    var node = container.append("g")
        .attr("class", "node")
        .selectAll("circle")
        .data(points.slice(0,(points.length-1)))
        .enter().append("circle")
        .attr("transform", function(d) { return "translate(" + proj([d.position.lng+Math.random()/3, d.position.lat+Math.random()/3]) + ")"; })
        .attr("r", function(d)  { return d.score/10 > pointMax ? pointMax : (d.score/10 < 2 ? 2 : d.score / 10);})
        .style("fill", function(d) { return d.color; })
        .on("mouseover", function(d) {
            d3.select(this)
                .transition()
                .duration(500)
                .style("cursor", "pointer")
                .attr("r", 20) // The bar becomes larger
                .style("fill", "green");
            tip.show(d);
        })
        .on("mouseout", function() {
            d3.select(this)
                .transition()
                .duration(500)
                .style("cursor", "normal")
                .attr("r", function(d)  { return d.score/10 > pointMax ? pointMax : (d.score/10 < 2 ? 2 : d.score / 10);})
                .style("fill", function(d) {return d.color; });
            tip.hide();
        });
    var nodeTarget = container.append("g")
        .attr("class", "node")
        .selectAll("circle")
        .data(points.slice(points.length-1, points.length))
        .enter().append("circle")
        .attr("transform", function(d) { return "translate(" + proj([d.position.lng+Math.random()/3, d.position.lat+Math.random()/3]) + ")"; })
        .attr("r", pointMax)
        .style("fill", function(d) { return d.color; })
        .on("mouseover", function(d) {
            d3.select(this)
                .transition()
                .duration(500)
                .style("cursor", "pointer")
                .attr("r", 20) // The bar becomes larger
                .style("fill", "green");
            tip.show(d);
        })
        .on("mouseout", function() {
            d3.select(this)
                .transition()
                .duration(500)
                .style("cursor", "normal")
                .attr("r", pointMax)
                .style("fill", function(d) {return d.color; });
            tip.hide();
        });


  },
  clearMarkers: function () {
      container.selectAll("circle").remove();
  }
};
