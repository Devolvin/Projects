$(document).ready(function(){


$('#main-nav').on('hidden.bs.collapse', function () {
    $('#main-nav').removeClass("main-nav-toggled");
      $('#main-nav').addClass("main-nav-untoggled");
      $('#main-nav').removeClass("text-center");
      $('.navbar-brand').addClass("mx-5");
      $('.navbar-brand').removeClass("navbar-brand-toggled");
      $('#nav-register').addClass("me-3");
      $('#nav-login').addClass("me-5");
});


$('#main-nav').on('shown.bs.collapse', function () {
      $('#main-nav').removeClass("main-nav-untoggled");
      $('#main-nav').addClass("main-nav-toggled");
      $('#main-nav').addClass("text-center");
      $('.navbar-brand').removeClass("mx-5");
      $('.navbar-brand').addClass("navbar-brand-toggled");
      $('#nav-register').removeClass("me-3");
      $('#nav-login').removeClass("me-5");

});