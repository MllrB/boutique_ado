let selectedCountry = $('#id_default_country').val();

if (!selectedCountry) {
    $('#id_default_country').css('color', '#aab7c4');
}

$('#id_default_country').change(function() {
    selectedCountry = $(this).val();
    if (!selectedCountry) {
        $(this).css('color', '#aab7c4');
    } else {
        $(this).css('color', '#000');
    }
});