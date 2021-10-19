$(document).ready(function(){
    $('nav #top-menu li').hover(function(e){
        //$('#drop' , this).css('display','block');
        $(this).children('ul').delay(50).slideDown(500);
    }, function(){
        $(this).children('ul').delay(50).slideUp(500);
    });
});
