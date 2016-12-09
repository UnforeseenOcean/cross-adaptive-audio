(function() {
  'use strict';

  angular
    .module('crossAdaptiveAudioApp')
    .directive('speciesChart', SpeciesChart);

  function SpeciesChart() {

    function SpeciesChartCtrl($scope, statsService, $element) {
      var vm = this;
      vm.statsService = statsService;
      vm.chart = null;
      vm.chartData = null;
      vm.data = {
        speciesSeries: null
      };
      vm.isGraphAdded = false;

      $scope.$watch(function() {
        return statsService.data && statsService.data.generations;
      }, function() {
        vm.data.speciesSeries = statsService.getSpeciesSeries();
        if (vm.isGraphAdded) {
          vm.updateGraph();
        } else {
          vm.addGraph();
        }
      });

      vm.addGraph = function() {
        vm.isGraphAdded = true;
        nv.addGraph(function() {
          vm.chart = nv.models.stackedAreaChart()
            .x(function(d) {
              return d[0]
            })
            .y(function(d) {
              return d[1]
            })
            .useInteractiveGuideline(true)    // Tooltips which show all data points. Very nice!
            .rightAlignYAxis(true)      // Let's move the y-axis to the right side.
            .showControls(true)       // Allow user to choose 'Stacked', 'Stream', 'Expanded' mode.
            .clipEdge(true)
            .style('expand');

          // Format axis labels
          vm.chart.xAxis.tickFormat(d3.format("d"));
          vm.chart.yAxis.tickFormat(d3.format("d"));

          vm.chartData = d3.select($element[0])
            .select('.species-chart svg')
            .datum(vm.data.speciesSeries)
          ;
          vm.chartData.call(vm.chart);

          nv.utils.windowResize(vm.chart.update);

          return vm.chart;
        });
      };

      vm.updateGraph = function() {
        vm.chartData.datum(vm.data.speciesSeries).transition().duration(500).call(vm.chart);
        nv.utils.windowResize(vm.chart.update);
      };
    }

    return {
      restrict: 'E',
      scope: {},
      templateUrl: 'views/species-chart.html',
      controller: SpeciesChartCtrl,
      controllerAs: 'speciesChart'
    };
  }
})();
