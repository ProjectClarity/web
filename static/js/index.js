var indexCtrl = PennAppsXMIT.controller('indexCtrl', ['$window', '$scope',
  function($window, $scope) {
    $scope.events = $window.events;
    $scope.formatTime = function(dt) {
      return moment(dt).format('llll');
    };
  }
]);
