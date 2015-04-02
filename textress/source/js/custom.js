$(document).ready(function(){
    $('a.go-back').click(function(){
        parent.history.back();
        return false;
    });
});