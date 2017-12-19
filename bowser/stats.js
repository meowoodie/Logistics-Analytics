
var statChart = {

	connRatioDist: function (domId, connRatioDistData) {

		var labels = ["Arrival Links", "Leaving Links", "Bidirection Links"],
			colors = [[255, 99, 132], [54, 162, 253], [125, 125, 75]],
			data   = _.values(connRatioDistData);

		// var dataset = _.chain(labels)
		// 	.zip(colors, data)
		// 	.map(function (infos) { return {
		// 		// String or array - the bar color
		// 		backgroundColor: String.format("rgba({0},{1},{2},{3})", 
		// 			infos[1][0], infos[1][1], infos[1][2], 0.2),
		// 		// String or array - bar stroke color
		// 		borderColor: String.format("rgba({0},{1},{2},{3})", 
		// 			infos[1][0], infos[1][1], infos[1][2], 1),
		// 		// String or array - fill color when hovered
		// 		hoverBackgroundColor: String.format("rgba({0},{1},{2},{3})", 
		// 			infos[1][0], infos[1][1], infos[1][2], 0.4),
		// 		// String or array - border color when hovered
		// 		hoverBorderColor: String.format("rgba({0},{1},{2},{3})", 
		// 			infos[1][0], infos[1][1], infos[1][2], 1),
		// 		// Number or array - bar border width
		// 		borderWidth: 1,
		// 		data: infos[2],
		// 		label: infos[0]}; })
		// 	.value();

		var tempPlaceholder = {
			labels:  _.map(_.range(20), function(i){return (i*0.05).toFixed(2);}),
		    datasets: [
		        {
		            label: "Arrival Links",
		            backgroundColor: "rgba(255,99,132,0.2)",
		            borderColor: "rgba(255,99,132,1)",
		            borderWidth: 1,
		            hoverBackgroundColor: "rgba(255,99,132,0.4)",
		            hoverBorderColor: "rgba(255,99,132,1)",
		            data: data[0],
		        },
		        {
		            label: "Leaving Links",
		            backgroundColor: "rgba(54,162,235,0.2)",
		            borderColor: "rgba(54,162,235,1)",
		            borderWidth: 1,
		            hoverBackgroundColor: "rgba(54,162,235,0.4)",
		            hoverBorderColor: "rgba(54,162,235,1)",
		            data: data[1]
		        },
		        {
		            label: "Bidirection Links",
		            backgroundColor: "rgba(125,125,75,0.2)",
		            borderColor: "rgba(125,125,75,1)",
		            borderWidth: 1,
		            hoverBackgroundColor: "rgba(125,125,75,0.4)",
		            hoverBorderColor: "rgba(125,125,75,1)",
		            data: data[2]
		        }
		    ]
		};

		var ctx = $('#' + domId);
		var lineChart = new Chart(ctx, {
				type: "line",
				data: tempPlaceholder
			});
	},

};