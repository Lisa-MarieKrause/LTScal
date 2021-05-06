

window.onload = function() {
    console.log('ready');
    calendarView();
    };

function calendarView() {
    var viewSetters = document.getElementsByClassName("btn-view active");
    var currentView = viewSetters[0];
    console.log("calendarView function running");
    console.log("currentView: " + currentView.id);
    if (currentView.id == "month") {
        document.getElementById("calendar").innerHTML="<object data='../templates/month_view.html'></object>";
        //{% include 'month_view.html' %}; //cannot include Jinja here
    };
    
    if (currentView.id == "week") {
        console.log("condition week fullfilled");
        //document.getElementById("calendar").insertAdjacentHTML("afterbegin", "<div class='calendarView'> {% include 'week_view.html' %}</div>");
        //return "week";
    };
    
    if (currentView.id == "day") {
        document.getElementById("calendar").innerHTML="<h6 Day>DAY</h6>";
    };
}
