mapObj = null;


var createInfoWindow = function (marker, content) {
    var infoWindow    = new google.maps.InfoWindow({});
        // contentString = String.format("<div id='info_window'>{0}</div>", content);

    google.maps.event.addListener(marker, "click", function() {
        //when the infoWindow is open, close it an clear the contents
        if (content == infoWindow.getContent()) {
            infoWindow.close(mapObj, marker);
            infoWindow.setContent("");
        }
        //otherwise trigger mouseover to open the infoWindow
        else {
            infoWindow.setContent(content);
            infoWindow.open(mapObj, marker);
        }
    });

}

maps = {
    initGoogleMaps: function (domId) {
        var c = {lat: 38.7451486, lng: 99.2731433};
        mapObj = new google.maps.Map(document.getElementById(domId), {
            zoom: 4.2,
            center: c,
            scrollwheel: false //we disable de scroll over the map, it is a really annoing when you scroll through page
            // styles: [{"featureType":"water","stylers":[{"saturation":43},{"lightness":-11},{"hue":"#0088ff"}]},{"featureType":"road","elementType":"geometry.fill","stylers":[{"hue":"#ff0000"},{"saturation":-100},{"lightness":99}]},{"featureType":"road","elementType":"geometry.stroke","stylers":[{"color":"#808080"},{"lightness":54}]},{"featureType":"landscape.man_made","elementType":"geometry.fill","stylers":[{"color":"#ece2d9"}]},{"featureType":"poi.park","elementType":"geometry.fill","stylers":[{"color":"#ccdca1"}]},{"featureType":"road","elementType":"labels.text.fill","stylers":[{"color":"#767676"}]},{"featureType":"road","elementType":"labels.text.stroke","stylers":[{"color":"#ffffff"}]},{"featureType":"poi","stylers":[{"visibility":"off"}]},{"featureType":"landscape.natural","elementType":"geometry.fill","stylers":[{"visibility":"on"},{"color":"#b8cb93"}]},{"featureType":"poi.park","stylers":[{"visibility":"on"}]},{"featureType":"poi.sports_complex","stylers":[{"visibility":"on"}]},{"featureType":"poi.medical","stylers":[{"visibility":"on"}]},{"featureType":"poi.business","stylers":[{"visibility":"simplified"}]}]
        });
    },

    fitBound: function(markers){
      var bounds = new google.maps.LatLngBounds();
          // center = {lat:0, lng:0};
      for (var i = 0; i < markers.length; i++) {
        // center['lat'] = center['lat'] + pos['lat'];
        // center['lng'] = center['lng'] + pos['lng'];
        bounds.extend(markers[i].getPosition());
      }
      // center['lat'] = center['lat']/markers.length;
      // center['lng'] = center['lng']/markers.length;
      mapObj.setCenter(bounds.getCenter());
      mapObj.fitBounds(bounds);
      // console.log(bounds.getCenter())
    },

    createRecommendedMarkers: function(points, lines){
      return _.map(points, function(point){
        var marker = new google.maps.Marker({
          position: point["position"],
          map: mapObj,
          icon:{
            path: google.maps.SymbolPath.CIRCLE,
            fillOpacity: 0.7,
            fillColor: point["color"],
            strokeOpacity: 1.0,
            strokeColor: point["color"],
            strokeWeight: 1.0,
            scale: (point["weight"]+0.5) * 10
          }
        });
        // add addListener
        var infoWindowHtml = String.format('\
            <div class="content" style="height:100%">\
                <div class="row">\
                  <div class = "col-md-8 col-lg-offset-2">\
                        <div class="row"><p class="card-text">Company ID {0}</p></div>\
                        <div class="row"><p class="card-text">Main Business {1}</p></div>\
                        <div class="row"><p class="card-text">Indust_lv1 {2}</p></div>\
                        <div class="row"><p class="card-text">City {3}</p></div>\
                        <div class="row"><p class="card-text">Rank {4}</p></div>\
                        <div class="row"><p class="card-text">Score {5}</p></div>\
                  </div>\
                </div>\
            </div>',
            point["id"], point["mb"], point["ind1"], point["city"], point['rank'], point["score"]);
        createInfoWindow(marker, infoWindowHtml);
        return marker;
      })
    },


    createSimilarMarkers: function (points, lines) {
        return _.map(points, function (point) {

            var marker = new google.maps.Marker({
                position: point["position"],
                map: mapObj,
                icon: {
                  path: google.maps.SymbolPath.CIRCLE,
                  fillOpacity: 0.7,
                  fillColor: point["color"],
                  strokeOpacity: 1.0,
                  strokeColor: point["color"],
                  strokeWeight: 1.0,
                  scale: point["weight"]
                }
            });

            //add listerer
            marker.addListener("mouseover", function(){
                if (lines != null){
                    for(var i=0;i<lines.length;i++){
                        for(var j=0;j<lines[i].getPath().length;j++){
                            if(lines[i].getPath().getAt(j).lat().toFixed(5) == point["position"]["lat"] && lines[i].getPath().getAt(j).lng().toFixed(5) == point["position"]["lng"]){
                                lines[i].setMap(mapObj);
                            }
                        }
                    }
                }


            });

            marker.addListener('mouseout',function(){
                if (lines != null){
                    for(var i=0;i<lines.length;i++){
                        lines[i].setMap(null);
                    }
                }
            });

            // Create info window for the marker
            var datetime = new Date(point["date"]*1000);
            var infoWindowHtml = String.format('\
                <div class="row">\
                    <div class="col-md-8">\
                        <h3 class="card-title">Crime ID {0}</h3>\
                    </div>\
                    <div class="col-md-8">\
                        <div class="row"><p class="card-text">Priority [{4}]</p></div>\
                        <div class="row"><p class="card-text">Catagory [{1}]</p></div>\
                        <div class="row"><p class="card-text">Occurred At {2}</p></div>\
                    </div>\
                </div>\
                <a role="button" data-toggle="collapse" href="#collapse_remarks_{0}" aria-expanded="false" aria-controls="collapse_remarks_{0}">Text Details</a>\
                <div class="collapse" id="collapse_remarks_{0}"><div class="well"><p class="card-text">{3}</p></div></div>',
                point["id"], point["label"], datetime.toString(), point["text"], point["priority"]);
            createInfoWindow(marker, infoWindowHtml);
            return marker;
        });
    },
    clearMarkers: function (markers) {
        _.map(markers, function (marker) {
            marker["lines"]
            marker.setMap(null);
        });
    },

    showMarkers: function (markers) {
        _.map(markers, function (marker) {
            marker.setMap(mapObj);
        });
    },
    //highlight keywords
    highlightKeywords: function (keywords, rawText){

        //console.log(matchedItems[i]["remarks"]);
        regExpFindMatched = new RegExp(keywords,"gim");

        matchedKeywords = rawText.match(regExpFindMatched);
        for(var j=0; j<matchedKeywords.length;j++){
            regExpReplace = new RegExp(matchedKeywords[j],"gm");
            replacement = "<mark style='background-color: yellow;color: black'>" + matchedKeywords[j] + "</mark>";
            rawText = rawText.replace(regExpReplace,replacement);
        }

        return rawText;
    },

    //Create polylines

    createLines: function(points, weights) {
        if (points == null){
            return null;
        }
        lines = [];
        for(var i=0; i<points.length;i++ ){
            for(var j=points.length-1; j>i; j--){
                coordinates = [];
                coordinates.push(points[i]["position"]);
                coordinates.push(points[j]["position"]);

            var line = new google.maps.Polyline({
                path: coordinates,
                geodesic: true,
                strokeColor: '#FF0000',
                strokeOpacity: weights[i][j]*5 || 0,
                strokeWeight: 5
                });

            lines.push(line);
            }
        }
        return lines;
    },

    showLines: function(lines){
        _.map(lines, function (line) {
            line.setMap(mapObj);
        });
    },
    clearLines: function (lines) {
        _.map(lines, function (line) {
            line.setMap(null);
        });
    }

}
