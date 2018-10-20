$(document).ready(
    function () {
        $("#state_selection_el").select2();

        /* Hiding the rows based on state */
        $('#state_selection_el').on('change', function (e) {
            if (e) {
                if (e.removed) {
                    $('table tr#'+ e.removed.id).hide();
                }
                if (e.added) {
                    $('table tr#'+ e.added.id).show();
                }
            }
        });
    }
);
