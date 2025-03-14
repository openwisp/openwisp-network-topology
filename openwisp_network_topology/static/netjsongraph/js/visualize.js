django.jQuery(function ($) {
  "use strict";
  var overlay = $(".djnjg-overlay"),
    body = $("body"),
    inner = overlay.find(".inner"),
    visualizeUrl = $(".visualizelink").attr("data-url");

  var disableArrowKeys = function (e) {
    var ar = [37, 38, 39, 40];
    if ($.inArray(e.keyCode, ar) >= 0) {
      e.preventDefault();
    }
  };

  var openOverlay = function () {
    // show overlay
    $.get(visualizeUrl, function (html) {
      overlay.show();
      inner.html(html);
      body.css("overflow", "hidden");
      inner.css("overflow", "hidden");

      // Check if close button already exists
      const closeBtn = document.querySelector(".closeBtn");
      if (!closeBtn) {
        const newcloseBtn = document.createElement("button");
        newcloseBtn.setAttribute("class", "closeBtn");
        newcloseBtn.innerHTML = "&times;";
        overlay.get(0).appendChild(newcloseBtn);
      }

      window.graph = window.loadNetJsonGraph(".djnjg-overlay .inner");

      overlay.find(".closeBtn").click(function (e) {
        e.preventDefault();
        closeOverlay();
      });
    });
    $(document).keydown(disableArrowKeys);
  };

  var closeOverlay = function () {
    // Make sure that whenever this function is called,
    // We first destroy the echart instance
    window.graph.echarts.dispose();
    $(document).unbind("keydown", disableArrowKeys);
    inner.empty();
    overlay.hide();
    body.attr("style", "");
  };

  $(".visualizelink").click(function (e) {
    openOverlay();
  });

  $(document).keyup(function (e) {
    // ALT+P
    if (e.altKey && e.which === 80) {
      // unfocus any active input before proceeding
      $(document.activeElement).trigger("blur");
      // corresonding raw value before proceding
      setTimeout(openOverlay, 15);
    } else if (!e.ctrlKey && e.which === 27) {
      // ESC
      closeOverlay();
    }
  });
});
