window.initTopologyHistory = function ($) {
  "use strict";
  var datepicker = $("#njg-datepicker"),
    today = new Date(),
    apiUrl = datepicker.attr("data-history-api");
  today.setHours(0, 0, 0, 0);
  datepicker.datepicker({ dateFormat: "dd/mm/yy" });
  datepicker.datepicker("setDate", today);
  datepicker.change(function () {
    var date = datepicker.val().split("/").reverse().join("-"),
      url = apiUrl + "&date=" + date;
    // load latest data when looking currentDate
    if (datepicker.datepicker("getDate").getTime() === today.getTime()) {
      url = window.__njg_default_url__;
    }
    $.ajax({
      url: url,
      dataType: "json",
      success: function (data) {
        window.graph.utils.JSONDataUpdate.call(window.graph, data);
      },
      error: function (xhr) {
        alert(xhr.responseJSON.detail);
      },
    });
  });
};
