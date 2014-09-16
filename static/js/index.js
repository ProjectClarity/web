var indexCtrl = PennAppsXMIT.mtroller('indexCtrl', ['$window', '$scope', '$sce', '$timeout',
  function($window, $scope, $sce, $timeout) {
    $scope.events = $window.events;
    $scope.current = 0;

    loadDistances = function(position) {
      _.each($scope.events, function(event, i, arr) {
        geocoder = new google.maps.Geocoder();
        geocoder.geocode({'address': event.location}, function(res, stat) {
          if (stat == google.maps.GeocoderStatus.OK) {
            var location = res[0].geometry.location;
            var destination = location.lat() + ',' + location.lng();
            var params = {
              current_location: position.coords.latitude + ',' + position.coords.longitude,
              destinations: destination
            }
            $.get($window.distanceURL, params)
            .then(function(data) {
              $timeout(function() {
                _.extend(arr[i], data[destination]);
              });
            });
          }
        });
      });
    };

    navigator.geolocation.getCurrentPosition(loadDistances);

    $scope.formatTime = function(dt) {
      return moment(dt).format('llll');
    };
    $scope.toggle = function(i) {
      $scope.current = i;
    };
    $scope.mapSrc = function() {
      var location = encodeURIComponent($scope.events[$scope.current].location);
      var url = "https://www.google.com/maps/embed/v1/place?key=AIzaSyBvdX9-poijqyQEnkkbfjZH0y51f7xO764&q=" + location;
      return $sce.trustAsResourceUrl(url);
    };
    $scope.destroy = function(i) {
      var event = $scope.events[i];
      var url = $window.destroyURL.replace('EVENT_ID', event.event_id);
      $.post(url)
      .then(function() {
        $timeout(function() {
          $scope.events.splice($scope.current, 1);
          $scope.current--;
        });
      });
    };
  }
]);
