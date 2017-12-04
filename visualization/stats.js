
var statChart = {

	connRatioDist: function (domId, connRatioDistData) {
		console.log(connRatioDistData);
		console.log(_.values(connRatioDistData)[0]);
		var ctx = document.getElementById(domId);
		var myLineChart = new Chart(ctx, {
		    type: 'line',
		    data: _.values(connRatioDistData)[0],
		    options: {
		    	scales: {
		            yAxes: [{
		                stacked: true
		            }]
        		}
        	}
		});
	},

};