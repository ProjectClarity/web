var indexCtrl = PennAppsXMIT.controller('indexCtrl', ['$window', '$scope', '$sce',
  function($window, $scope, $sce) {
    $scope.events = $window.events;
    $scope.current = 0;
    $scope.formatTime = function(dt) {
      return moment(dt).format('llll');
    };
    $scope.toggle = function(i) {
      if($scope.events[i].location) {
        $scope.current = i;
      }
    };
    $scope.mapSrc = function() {
      var location = encodeURIComponent($scope.events[$scope.current].location);
      var url = "https://www.google.com/maps/embed/v1/place?key=AIzaSyBvdX9-poijqyQEnkkbfjZH0y51f7xO764&q=" + location;
      return $sce.trustAsResourceUrl(url);
    };
  }
]);
