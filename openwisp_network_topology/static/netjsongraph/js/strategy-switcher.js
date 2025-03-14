(function ($) {
  "use strict";
  $(document).ready(function () {
    var strategy = $("#id_strategy"),
      fetchRows = $("#id_url").parents(".form-row"),
      receiveRows = $("#id_key, #id_expiration_time, #id_receive_url").parents(
        ".form-row",
      );
    strategy.change(function (e) {
      if (strategy.val() === "fetch") {
        fetchRows.show();
        receiveRows.hide();
      } else {
        fetchRows.hide();
        receiveRows.show();
      }
    });
    strategy.trigger("change");
  });
})(django.jQuery);
