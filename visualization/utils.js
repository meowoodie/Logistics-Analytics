
// Generate rgb string randomly
var dynamicColors = function() {
    var r = Math.floor(Math.random() * 255);
    var g = Math.floor(Math.random() * 255);
    var b = Math.floor(Math.random() * 255);
    return "rgb(" + r + "," + g + "," + b + ")";
};

// var colorBar = _.map(new Array(12), function(){return dynamicColors();});

// NOTE: 
// Latitude and Longitude of some cities cannot be retrieved
// by geopy. This function hard code the missing geo information.
var hardcodeMissingGeo = function (graph){
    // console.log(graph.nodes);
    _.map(graph.nodes, function(node){
    	switch (node.area_code) {
    		case "024Y":
    			node.lat = 41.8057;
            	node.lng = 123.4315;
            	break;
            case "028Y":
            	node.lat = 30.5728;
            	node.lng = 104.0668;
            	break;
            case "029Y":
            	node.lat = 34.3416;
            	node.lng = 108.9398;
            	break;
            case "760Y":
            	node.lat = 22.31;
            	node.lng = 113.23;
            	break;
            case "575Y":
            	node.lat = 29.9958;
            	node.lng = 120.5861;
            	break;
		}
    });
};