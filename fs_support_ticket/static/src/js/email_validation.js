$(document).ready(function(){
    $(".customer-email").change(function(event){
        var email = $(".customer-email").val();
        var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        var res = re.test(email);
        if(res == false){
            alert("You have provided an invalid email.")
        }
        return ;
    });
});
