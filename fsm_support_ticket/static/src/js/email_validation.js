$(document).ready(function () {
    $(".customer-email").change(function () {
        var email = $(this).val();

        var re = "/^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|" +
            "(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\." +
            "[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/";
        var res = re.test(email);
        if (email && res === false) {
            alert("You have provided an invalid email.");
        }
        return ;
    });
});
