var indexCtrl = PennAppsXMIT.controller('indexCtrl', ['$window', '$scope',
  function($window, $scope) {
    $scope.events = $window.events;
  }
]);
