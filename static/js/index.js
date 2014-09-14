var indexCtrl = PennAppsXMIT.controller('indexCtrl', ['$window', '$scope',
  function($window, $scope) {
    $scope.events = $window.events;
    $scope.current = 0;
    $scope.formatTime = function(dt) {
      return moment(dt).format('llll');
    };
    $scope.mapSrc = function() {
      var location = encodeURIComponent($scope.events[$scope.current].location);
      return "https://www.google.com/maps/embed/v1/place?key=AIzaSyBvdX9-poijqyQEnkkbfjZH0y51f7xO764&q=" + location;
    };
  }
]);
