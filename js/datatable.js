$(document).ready( 
    function () {
        $('#table').DataTable({
        "iDisplayLength": 50,
        "responsive": true,
        })
        
document.getElementById("MarketCaps_All").innerHTML = '{{marketCaps.All}}';
document.getElementById("MarketCaps_All2").innerHTML = '{{marketCaps.All}}';
document.getElementById("MarketCaps_Comms").innerHTML = '{{marketCaps.Comms}}';
document.getElementById("MarketCaps_Stocks").innerHTML = '{{marketCaps.Stocks}}';
document.getElementById("MarketCaps_Currs").innerHTML = '{{marketCaps.Currs}}';
document.getElementById("MarketCaps_Cryptos").innerHTML = '{{marketCaps.Cryptos}}';

})